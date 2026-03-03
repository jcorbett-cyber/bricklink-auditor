import streamlit as st
import requests
from requests_oauthlib import OAuth1
import pandas as pd
from itertools import groupby
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Brick Audit", page_icon="🧱", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1rem; }
.part-card { background:#1e1e2e; border:1px solid #313244; border-radius:12px; padding:14px; text-align:center; margin-bottom:8px; }
.part-card.found { border-color:#a6e3a1; background:#1a2e1a; }
.part-card.flagged { border-color:#f38ba8; background:#2e1a1a; }
.part-card.lowstock { border-color:#fab387; background:#2e2010; }
.part-card.highlight { border-color:#f9e2af; background:#2e2a10; box-shadow:0 0 12px #f9e2af88; }
.part-img { width:100%; max-height:110px; object-fit:contain; margin-bottom:8px; }
.part-name { font-size:0.8rem; color:#cdd6f4; font-weight:700; margin-bottom:3px; }
.part-meta { font-size:0.72rem; color:#a6adc8; }
.badge { display:inline-block; border-radius:6px; padding:2px 8px; font-size:0.68rem; font-weight:700; margin-top:4px; }
.badge-n { background:#313244; color:#cdd6f4; }
.badge-u { background:#45475a; color:#f9e2af; }
.badge-found { background:#a6e3a1; color:#1e1e2e; }
.badge-flagged { background:#f38ba8; color:#1e1e2e; }
.badge-low { background:#fab387; color:#1e1e2e; }
.bin-header { background:#181825; border-left:4px solid #cba6f7; border-radius:8px; padding:10px 16px; margin:18px 0 10px 0; }
.bin-title { font-size:1.1rem; font-weight:800; color:#cba6f7; margin:0; }
.bin-stats { font-size:0.78rem; color:#a6adc8; margin:2px 0 0 0; }
.scan-bar { background:#181825; border:2px solid #cba6f7; border-radius:12px; padding:12px 18px; margin-bottom:18px; }
.metric-card { background:#181825; border:1px solid #313244; border-radius:12px; padding:16px; text-align:center; margin-bottom:8px; }
.metric-value { font-size:1.8rem; font-weight:800; color:#cba6f7; }
.metric-label { font-size:0.78rem; color:#a6adc8; margin-top:4px; }
@media (max-width:768px) {
  .part-card { padding:8px; }
  .part-img { max-height:70px; }
  .part-name { font-size:0.7rem; }
  .part-meta { font-size:0.62rem; }
  .badge { font-size:0.6rem; padding:1px 5px; }
}
</style>
""", unsafe_allow_html=True)

LOGO                = "https://raw.githubusercontent.com/jcorbett-cyber/bricklink-auditor/main/iTunesArtwork%402x.png"
LOW_STOCK_THRESHOLD = 2

# ── Secrets ───────────────────────────────────────────────────────────────────
try:
    CK = st.secrets["BL_CONSUMER_KEY"]
    CS = st.secrets["BL_CONSUMER_SECRET"]
    TV = st.secrets["BL_TOKEN_VALUE"]
    TS = st.secrets["BL_TOKEN_SECRET"]
    SECRETS_LOADED = True
except Exception:
    SECRETS_LOADED = False

try:
    supabase  = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    DB_LOADED = True
except Exception:
    DB_LOADED = False

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("inventory", []),
    ("checked", set()),
    ("flagged", {}),
    ("notes", {}),
    ("loaded", False),
    ("auth", None),
    ("show_bulk_confirm", False),
    ("scan_query", ""),
    ("page", "audit"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

BASE = "https://api.bricklink.com/api/store/v1"

# ── BrickLink helpers ─────────────────────────────────────────────────────────
def make_auth(ck, cs, tv, ts):
    return OAuth1(ck, cs, tv, ts)

def fetch_inventory(auth):
    r = requests.get(f"{BASE}/inventories", auth=auth, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "API error"))
    return data["data"]

def update_quantity_on_bricklink(auth, inventory_id, new_qty):
    r = requests.put(f"{BASE}/inventories/{inventory_id}", auth=auth,
                     json={"quantity": new_qty}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "Update failed"))
    return True

def update_remarks_on_bricklink(auth, inventory_id, new_remarks):
    r = requests.put(f"{BASE}/inventories/{inventory_id}", auth=auth,
                     json={"remarks": new_remarks}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "Update failed"))
    return True

# ── Supabase helpers ──────────────────────────────────────────────────────────
def save_progress(inventory_id, status, flag_reason=None, actual_qty=None,
                  correct_bin=None, notes=None):
    if not DB_LOADED:
        return
    try:
        supabase.table("audit_progress").upsert({
            "inventory_id": inventory_id,
            "status":       status,
            "flag_reason":  flag_reason,
            "actual_qty":   actual_qty,
            "correct_bin":  correct_bin,
            "notes":        notes,
        }, on_conflict="inventory_id").execute()
    except Exception as e:
        st.warning(f"Could not save progress: {e}")

def delete_progress(inventory_id):
    if not DB_LOADED:
        return
    try:
        supabase.table("audit_progress").delete().eq("inventory_id", inventory_id).execute()
    except Exception as e:
        st.warning(f"Could not delete progress: {e}")

def load_progress():
    if not DB_LOADED:
        return set(), {}, {}
    try:
        result  = supabase.table("audit_progress").select("*").execute()
        checked = set()
        flagged = {}
        notes   = {}
        for row in result.data:
            lid = row["inventory_id"]
            if row.get("notes"):
                notes[lid] = row["notes"]
            if row["status"] == "checked":
                checked.add(lid)
            elif row["status"] == "flagged":
                flagged[lid] = {
                    "reason":      row.get("flag_reason", ""),
                    "actual_qty":  row.get("actual_qty"),
                    "correct_bin": row.get("correct_bin", ""),
                }
        return checked, flagged, notes
    except Exception as e:
        st.warning(f"Could not load saved progress: {e}")
        return set(), {}, {}

def clear_all_progress():
    if not DB_LOADED:
        return
    try:
        supabase.table("audit_progress").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000").execute()
    except Exception as e:
        st.warning(f"Could not clear progress: {e}")

def save_audit_snapshot():
    if not DB_LOADED or not st.session_state.inventory:
        return
    try:
        inv       = st.session_state.inventory
        checked   = st.session_state.checked
        flagged   = st.session_state.flagged
        total     = len(inv)
        n_checked = len(checked)
        n_flagged = len(flagged)

        val_checked   = sum(
            float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
            for i in inv if i.get("inventory_id") in checked
        )
        val_unchecked = sum(
            float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
            for i in inv if i.get("inventory_id") not in checked
        )

        discrepancies = []
        for i in inv:
            lid  = i.get("inventory_id")
            flag = flagged.get(lid)
            if flag:
                discrepancies.append({
                    "inventory_id": lid,
                    "part_no":      i.get("item", {}).get("no", ""),
                    "name":         i.get("item", {}).get("name", ""),
                    "reason":       flag.get("reason", ""),
                    "actual_qty":   flag.get("actual_qty"),
                    "correct_bin":  flag.get("correct_bin", ""),
                })

        supabase.table("audit_history").insert({
            "audit_date":           datetime.now().isoformat(),
            "total_lots":           total,
            "total_checked":        n_checked,
            "total_flagged":        n_flagged,
            "total_value_checked":  round(val_checked, 2),
            "total_value_unchecked":round(val_unchecked, 2),
            "discrepancies":        discrepancies,
        }).execute()
        return True
    except Exception as e:
        st.warning(f"Could not save audit snapshot: {e}")
        return False

def load_audit_history():
    if not DB_LOADED:
        return []
    try:
        result = supabase.table("audit_history").select("*").order(
            "audit_date", desc=True).execute()
        return result.data
    except Exception as e:
        st.warning(f"Could not load audit history: {e}")
        return []

# ── Bulk push helpers ─────────────────────────────────────────────────────────
def get_pushable_flags():
    pushable = []
    for lot in st.session_state.inventory:
        lid    = lot.get("inventory_id")
        flag   = st.session_state.flagged.get(lid)
        if not flag:
            continue
        reason = flag.get("reason", "")
        if reason in ("Qty updated ✓", "Bin updated ✓"):
            continue
        if reason == "Wrong qty" and "actual_qty" in flag:
            pushable.append({
                "lid":    lid,
                "pno":    lot.get("item", {}).get("no", ""),
                "name":   lot.get("item", {}).get("name", ""),
                "bin":    lot.get("remarks", ""),
                "change": f"Qty: {lot.get('quantity')} → {flag['actual_qty']}",
                "type":   "qty",
                "value":  flag["actual_qty"],
            })
        elif reason == "Wrong bin" and flag.get("correct_bin"):
            pushable.append({
                "lid":    lid,
                "pno":    lot.get("item", {}).get("no", ""),
                "name":   lot.get("item", {}).get("name", ""),
                "bin":    lot.get("remarks", ""),
                "change": f"Bin: '{lot.get('remarks', '')}' → '{flag['correct_bin']}'",
                "type":   "bin",
                "value":  flag["correct_bin"],
            })
    return pushable

def push_all_flags(auth):
    pushable = get_pushable_flags()
    results  = {"success": [], "failed": []}
    for item in pushable:
        try:
            if item["type"] == "qty":
                update_quantity_on_bricklink(auth, item["lid"], item["value"])
                st.session_state.flagged[item["lid"]]["reason"] = "Qty updated ✓"
                for x in st.session_state.inventory:
                    if x.get("inventory_id") == item["lid"]:
                        x["quantity"] = item["value"]
                save_progress(item["lid"], "flagged", "Qty updated ✓", item["value"], None)
            elif item["type"] == "bin":
                update_remarks_on_bricklink(auth, item["lid"], item["value"])
                st.session_state.flagged[item["lid"]]["reason"] = "Bin updated ✓"
                for x in st.session_state.inventory:
                    if x.get("inventory_id") == item["lid"]:
                        x["remarks"] = item["value"]
                save_progress(item["lid"], "flagged", "Bin updated ✓", None, item["value"])
            results["success"].append(item)
        except Exception as e:
            results["failed"].append({**item, "error": str(e)})
    return results

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(LOGO, width=200)

    if not SECRETS_LOADED:
        st.warning("⚠️ No saved credentials found.")
        st.markdown("### 🔑 API Credentials")
        ck = st.text_input("Consumer Key",    type="password")
        cs = st.text_input("Consumer Secret", type="password")
        tv = st.text_input("Token Value",     type="password")
        ts = st.text_input("Token Secret",    type="password")
    else:
        ck, cs, tv, ts = CK, CS, TV, TS
        st.success("🔑 Credentials loaded!")

    load_btn = st.button("🔄 Load My Inventory", use_container_width=True, type="primary")

    st.divider()
    st.markdown("### 📄 Pages")
    if st.button("🧱 Audit",          use_container_width=True):
        st.session_state.page = "audit"
        st.rerun()
    if st.button("📊 Summary",        use_container_width=True):
        st.session_state.page = "summary"
        st.rerun()
    if st.button("📅 Audit History",  use_container_width=True):
        st.session_state.page = "history"
        st.rerun()

    st.divider()
    if st.session_state.page == "audit":
        st.markdown("### 🔍 Filters")
        search_term = st.text_input("Search part # or name")
        cond_filter = st.multiselect("Condition", ["New", "Used"], default=["New", "Used"])
        show_filter = st.radio("Show", ["All", "✅ Found", "🚩 Flagged",
                                        "⬜ Not yet found", "🔴 Low stock"])
        all_remarks = sorted(set(
            i.get("remarks", "") or "(no remarks)"
            for i in st.session_state.inventory
        ))
        remarks_filter = "All"
        if len(all_remarks) > 1:
            remarks_filter = st.selectbox("📦 Jump to bin", ["All"] + all_remarks)
    else:
        search_term    = ""
        cond_filter    = ["New", "Used"]
        show_filter    = "All"
        remarks_filter = "All"

    st.divider()
    if st.session_state.inventory:
        total     = len(st.session_state.inventory)
        found_n   = len(st.session_state.checked)
        flagged_n = len(st.session_state.flagged)
        low_n     = sum(1 for i in st.session_state.inventory
                        if 0 < i.get("quantity", 0) <= LOW_STOCK_THRESHOLD)
        pct       = int(found_n / total * 100) if total else 0

        st.markdown("### 📊 Progress")
        st.progress(pct / 100)
        st.markdown(f"**{found_n}/{total}** found · {pct}%")
        if flagged_n:
            st.markdown(f"🚩 **{flagged_n}** flagged")
        if low_n:
            st.markdown(f"🔴 **{low_n}** low stock")

        pushable = get_pushable_flags()
        if pushable:
            if st.button(f"🚀 Push {len(pushable)} fixes to BrickLink",
                         use_container_width=True, type="primary"):
                st.session_state.show_bulk_confirm = True

        if st.button("📸 Save Audit Snapshot", use_container_width=True):
            if save_audit_snapshot():
                st.success("Snapshot saved!")

        if st.button("🗑️ Reset All Checkmarks", use_container_width=True):
            st.session_state.checked = set()
            st.session_state.flagged = {}
            st.session_state.notes   = {}
            st.session_state.show_bulk_confirm = False
            clear_all_progress()
            st.rerun()

        remaining = [i for i in st.session_state.inventory
                     if i.get("inventory_id") not in st.session_state.checked]
        if remaining:
            df_r = pd.DataFrame([{
                "Inventory ID": r.get("inventory_id", ""),
                "Part #":       r.get("item", {}).get("no", ""),
                "Name":         r.get("item", {}).get("name", ""),
                "Color":        r.get("color_name", ""),
                "Condition":    "New" if r.get("new_or_used") == "N" else "Used",
                "Quantity":     r.get("quantity", 0),
                "Price":        r.get("unit_price", ""),
                "Bin":          r.get("remarks", ""),
                "Notes":        st.session_state.notes.get(r.get("inventory_id"), ""),
            } for r in remaining])
            st.download_button("📥 Export Remaining CSV", df_r.to_csv(index=False),
                               "remaining_lots.csv", "text/csv", use_container_width=True)

        flagged_lots = [
            {**i, **st.session_state.flagged.get(i.get("inventory_id"), {})}
            for i in st.session_state.inventory
            if i.get("inventory_id") in st.session_state.flagged
        ]
        if flagged_lots:
            df_f = pd.DataFrame([{
                "Inventory ID": f.get("inventory_id", ""),
                "Part #":       f.get("item", {}).get("no", ""),
                "Name":         f.get("item", {}).get("name", ""),
                "Color":        f.get("color_name", ""),
                "Listed Qty":   f.get("quantity", 0),
                "Actual Qty":   f.get("actual_qty", ""),
                "Current Bin":  f.get("remarks", ""),
                "Correct Bin":  f.get("correct_bin", ""),
                "Flag Reason":  f.get("reason", ""),
                "Notes":        st.session_state.notes.get(f.get("inventory_id"), ""),
            } for f in flagged_lots])
            st.download_button("🚩 Export Flagged CSV", df_f.to_csv(index=False),
                               "flagged_lots.csv", "text/csv", use_container_width=True)

# ── Load inventory ────────────────────────────────────────────────────────────
if load_btn:
    if not all([ck, cs, tv, ts]):
        st.error("Please fill in all four credential fields.")
    else:
        with st.spinner("Loading inventory from BrickLink…"):
            try:
                auth = make_auth(ck, cs, tv, ts)
                inv  = fetch_inventory(auth)
                st.session_state.inventory = inv
                st.session_state.loaded    = True
                st.session_state.auth      = (ck, cs, tv, ts)
                st.success(f"✅ Loaded {len(inv)} lots!")
            except Exception as e:
                st.error(f"Error: {e}")
        if DB_LOADED and st.session_state.loaded:
            with st.spinner("Restoring saved progress…"):
                checked, flagged, notes = load_progress()
                st.session_state.checked = checked
                st.session_state.flagged = flagged
                st.session_state.notes   = notes
                if checked or flagged:
                    st.success(f"✅ Restored {len(checked)} checked, {len(flagged)} flagged!")
                else:
                    st.info("Starting fresh.")

# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(LOGO, width=70)
with col_title:
    st.title("🧱 Brick Audit")

if not st.session_state.loaded:
    st.info("👈 Click **Load My Inventory** to get started.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "summary":
    st.header("📊 Audit Summary")
    inv       = st.session_state.inventory
    checked   = st.session_state.checked
    flagged   = st.session_state.flagged
    total     = len(inv)
    n_checked = len(checked)
    n_flagged = len(flagged)
    n_remain  = total - n_checked - n_flagged
    pct       = int(n_checked / total * 100) if total else 0
    low_lots  = [i for i in inv if 0 < i.get("quantity", 0) <= LOW_STOCK_THRESHOLD]

    val_checked   = sum(
        float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
        for i in inv if i.get("inventory_id") in checked
    )
    val_unchecked = sum(
        float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
        for i in inv if i.get("inventory_id") not in checked
    )
    val_total = val_checked + val_unchecked

    # ── Metric cards ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">{pct}%</div>
          <div class="metric-label">Audit Complete</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">{n_checked}/{total}</div>
          <div class="metric-label">Lots Found</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#f38ba8">{n_flagged}</div>
          <div class="metric-label">Lots Flagged</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#fab387">{len(low_lots)}</div>
          <div class="metric-label">Low Stock Lots</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Value tracking ──
    st.subheader("💰 Inventory Value Tracking")
    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#a6e3a1">${val_checked:,.2f}</div>
          <div class="metric-label">Value Checked ✅</div>
        </div>""", unsafe_allow_html=True)
    with v2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#f38ba8">${val_unchecked:,.2f}</div>
          <div class="metric-label">Value Not Yet Checked</div>
        </div>""", unsafe_allow_html=True)
    with v3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">${val_total:,.2f}</div>
          <div class="metric-label">Total Store Value</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Progress by bin ──
    st.subheader("📦 Progress by Bin")
    bin_data = []
    for bin_name, lots in groupby(
        sorted(inv, key=lambda x: x.get("remarks", "") or ""),
        key=lambda x: x.get("remarks", "") or "(no remarks)"
    ):
        lots        = list(lots)
        b_total     = len(lots)
        b_checked   = sum(1 for x in lots if x.get("inventory_id") in checked)
        b_flagged   = sum(1 for x in lots if x.get("inventory_id") in flagged)
        b_val       = sum(
            float(x.get("unit_price", 0) or 0) * int(x.get("quantity", 0) or 0)
            for x in lots
        )
        bin_data.append({
            "Bin":        bin_name,
            "Total Lots": b_total,
            "Found":      b_checked,
            "Flagged":    b_flagged,
            "Remaining":  b_total - b_checked - b_flagged,
            "% Done":     int(b_checked / b_total * 100) if b_total else 0,
            "Bin Value":  f"${b_val:,.2f}",
        })
    st.dataframe(pd.DataFrame(bin_data), use_container_width=True, hide_index=True)

    st.divider()

    # ── Flagged lots detail ──
    if n_flagged:
        st.subheader("🚩 Flagged Lots Detail")
        flag_rows = []
        for i in inv:
            lid  = i.get("inventory_id")
            flag = flagged.get(lid)
            if flag:
                flag_rows.append({
                    "Part #":      i.get("item", {}).get("no", ""),
                    "Name":        i.get("item", {}).get("name", ""),
                    "Color":       i.get("color_name", ""),
                    "Bin":         i.get("remarks", ""),
                    "Listed Qty":  i.get("quantity", 0),
                    "Actual Qty":  flag.get("actual_qty", ""),
                    "Correct Bin": flag.get("correct_bin", ""),
                    "Reason":      flag.get("reason", ""),
                    "Notes":       st.session_state.notes.get(lid, ""),
                })
        st.dataframe(pd.DataFrame(flag_rows), use_container_width=True, hide_index=True)

    st.divider()

    # ── Low stock detail ──
    if low_lots:
        st.subheader("🔴 Low Stock Lots")
        st.dataframe(pd.DataFrame([{
            "Part #":   i.get("item", {}).get("no", ""),
            "Name":     i.get("item", {}).get("name", ""),
            "Color":    i.get("color_name", ""),
            "Bin":      i.get("remarks", ""),
            "Quantity": i.get("quantity", 0),
            "Price":    f"${i.get('unit_price', '')}",
        } for i in low_lots]), use_container_width=True, hide_index=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "history":
    st.header("📅 Audit History")
    history = load_audit_history()

    if not history:
        st.info("No audit snapshots saved yet. Complete an audit and click **📸 Save Audit Snapshot** in the sidebar to record it.")
        st.stop()

    # ── Summary table ──
    st.subheader("Past Audits")
    df_hist = pd.DataFrame([{
        "Date":             h["audit_date"][:16].replace("T", " "),
        "Total Lots":       h["total_lots"],
        "Checked":          h["total_checked"],
        "Flagged":          h["total_flagged"],
        "% Complete":       int(h["total_checked"] / h["total_lots"] * 100)
                            if h["total_lots"] else 0,
        "Value Checked":    f"${h['total_value_checked']:,.2f}",
        "Value Remaining":  f"${h['total_value_unchecked']:,.2f}",
    } for h in history])
    st.dataframe(df_hist, use_container_width=True, hide_index=True)

    st.divider()

    # ── Trend chart ──
    if len(history) > 1:
        st.subheader("📈 Audit Completion Over Time")
        chart_data = pd.DataFrame([{
            "Date":       h["audit_date"][:10],
            "% Complete": int(h["total_checked"] / h["total_lots"] * 100)
                          if h["total_lots"] else 0,
            "Flagged":    h["total_flagged"],
        } for h in reversed(history)])
        st.line_chart(chart_data.set_index("Date"))

    st.divider()

    # ── Drill into a specific audit ──
    st.subheader("🔎 Drill into an audit")
    audit_labels = [h["audit_date"][:16].replace("T", " ") for h in history]
    selected     = st.selectbox("Select an audit to review", audit_labels)
    selected_h   = history[audit_labels.index(selected)]

    col1, col2, col3 = st.columns(3)
    with col1:
        pct = int(selected_h["total_checked"] / selected_h["total_lots"] * 100) \
              if selected_h["total_lots"] else 0
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">{pct}%</div>
          <div class="metric-label">Complete</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#f38ba8">{selected_h['total_flagged']}</div>
          <div class="metric-label">Flagged</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#a6e3a1">${selected_h['total_value_checked']:,.2f}</div>
          <div class="metric-label">Value Checked</div>
        </div>""", unsafe_allow_html=True)

    discreps = selected_h.get("discrepancies", [])
    if discreps:
        st.markdown(f"**{len(discreps)} discrepancies recorded in this audit:**")
        st.dataframe(pd.DataFrame(discreps), use_container_width=True, hide_index=True)
    else:
        st.success("No discrepancies recorded in this audit!")

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT (main)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scan-bar">', unsafe_allow_html=True)
sc1, sc2 = st.columns([5, 1])
with sc1:
    scan_query = st.text_input("🔍 Scan / quick find",
                                value=st.session_state.scan_query,
                                placeholder="Type or scan a part number…",
                                label_visibility="collapsed",
                                key="scan_input")
with sc2:
    if st.button("✖ Clear", use_container_width=True):
        st.session_state.scan_query = ""
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if scan_query != st.session_state.scan_query:
    st.session_state.scan_query = scan_query
    st.rerun()

if st.session_state.show_bulk_confirm:
    pushable = get_pushable_flags()
    if pushable:
        st.warning(f"### 🚀 Ready to push {len(pushable)} fix(es) to BrickLink")
        st.dataframe(pd.DataFrame([{
            "Part #": p["pno"], "Name": p["name"],
            "Bin": p["bin"],    "Change": p["change"],
        } for p in pushable]), use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Confirm — push all", type="primary", use_container_width=True):
                auth = make_auth(*st.session_state.auth)
                with st.spinner("Pushing…"):
                    results = push_all_flags(auth)
                st.session_state.show_bulk_confirm = False
                if results["success"]:
                    st.success(f"✅ {len(results['success'])} update(s) pushed!")
                for f in results.get("failed", []):
                    st.error(f"❌ {f['pno']}: {f['error']}")
                st.rerun()
        with c2:
            if st.button("✖ Cancel", use_container_width=True):
                st.session_state.show_bulk_confirm = False
                st.rerun()
    else:
        st.session_state.show_bulk_confirm = False

inv = st.session_state.inventory
if "New" not in cond_filter:
    inv = [i for i in inv if i.get("new_or_used") != "N"]
if "Used" not in cond_filter:
    inv = [i for i in inv if i.get("new_or_used") != "U"]
if search_term:
    q = search_term.lower()
    inv = [i for i in inv if q in i.get("item", {}).get("no", "").lower()
           or q in i.get("item", {}).get("name", "").lower()]
if show_filter == "✅ Found":
    inv = [i for i in inv if i.get("inventory_id") in st.session_state.checked]
elif show_filter == "🚩 Flagged":
    inv = [i for i in inv if i.get("inventory_id") in st.session_state.flagged]
elif show_filter == "⬜ Not yet found":
    inv = [i for i in inv if i.get("inventory_id") not in st.session_state.checked
           and i.get("inventory_id") not in st.session_state.flagged]
elif show_filter == "🔴 Low stock":
    inv = [i for i in inv if 0 < i.get("quantity", 0) <= LOW_STOCK_THRESHOLD]
if remarks_filter != "All":
    inv = [i for i in inv if (i.get("remarks", "") or "(no remarks)") == remarks_filter]

scan_ids = set()
if st.session_state.scan_query:
    sq = st.session_state.scan_query.lower()
    for lot in inv:
        if sq in lot.get("item", {}).get("no", "").lower():
            scan_ids.add(lot.get("inventory_id"))
    if not scan_ids:
        st.warning(f"No parts found matching **{st.session_state.scan_query}**")

inv = sorted(inv, key=lambda x: (
    0 if x.get("inventory_id") in scan_ids else 1,
    x.get("remarks", "") or ""
))

st.caption(f"Showing {len(inv)} lots"
           + (f" · 🔍 {len(scan_ids)} match(es) highlighted" if scan_ids else ""))

def get_group(lot):
    return lot.get("remarks", "") or "(no remarks)"

COLS = 6

for group_name, group_items in groupby(inv, key=get_group):
    group_lots  = list(group_items)
    bin_total   = len(group_lots)
    bin_found   = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
    bin_flagged = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
    bin_pct     = int(bin_found / bin_total * 100) if bin_total else 0

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown(f"""
        <div class="bin-header">
          <p class="bin-title">📦 {group_name}</p>
          <p class="bin-stats">{bin_found}/{bin_total} found · {bin_pct}%{"&nbsp;&nbsp;🚩 "+str(bin_flagged)+" flagged" if bin_flagged else ""}</p>
        </div>""", unsafe_allow_html=True)
    with col_btn:
        st.write("")
        st.write("")
        if st.button("✅ Mark all found", key=f"markall_{group_name}",
                     use_container_width=True):
            for x in group_lots:
                lid = x.get("inventory_id")
                st.session_state.checked.add(lid)
                save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
            st.rerun()

    for row_start in range(0, len(group_lots), COLS):
        row_items = group_lots[row_start:row_start + COLS]
        cols      = st.columns(COLS)

        for col, lot in zip(cols, row_items):
            lid        = lot.get("inventory_id", "unknown")
            item       = lot.get("item", {})
            pno        = item.get("no", "")
            pname      = item.get("name", "N/A")
            color      = lot.get("color_name", "")
            color_id   = lot.get("color_id", 0)
            qty        = lot.get("quantity", 0)
            price      = lot.get("unit_price", "")
            remarks    = lot.get("remarks", "")
            cond       = "New" if lot.get("new_or_used") == "N" else "Used"
            is_found   = lid in st.session_state.checked
            is_flagged = lid in st.session_state.flagged
            is_low     = 0 < qty <= LOW_STOCK_THRESHOLD
            is_scan    = lid in scan_ids
            flag_info  = st.session_state.flagged.get(lid, {})
            note_val   = st.session_state.notes.get(lid, "")

            if is_scan:       card_cls = "part-card highlight"
            elif is_flagged:  card_cls = "part-card flagged"
            elif is_found:    card_cls = "part-card found"
            elif is_low:      card_cls = "part-card lowstock"
            else:             card_cls = "part-card"

            if is_flagged:
                badge_cls = "badge-flagged"
                badge_lbl = "🚩 " + flag_info.get("reason", "Flagged")
            elif is_found:
                badge_cls = "badge-found"
                badge_lbl = "✅ Found"
            elif is_low:
                badge_cls = "badge-low"
                badge_lbl = f"🔴 Low ({qty})"
            else:
                badge_cls = "badge-n" if cond == "New" else "badge-u"
                badge_lbl = cond

            img = f"https://img.bricklink.com/ItemImage/PN/{color_id}/{pno}.png"

            with col:
                st.markdown(f"""
                <div class="{card_cls}">
                  <img class="part-img" src="{img}" onerror="this.style.opacity='0.15'"/>
                  <div class="part-name">{pno}</div>
                  <div class="part-meta">{pname[:26]}</div>
                  <div class="part-meta">{color} · ×{qty}</div>
                  <div class="part-meta">${price}</div>
                  <span class="badge {badge_cls}">{badge_lbl}</span>
                  {f'<div class="part-meta" style="margin-top:4px;color:#f9e2af;">📝 {note_val[:30]}</div>' if note_val else ''}
                </div>""", unsafe_allow_html=True)

                if is_flagged:
                    if col.button("↩ Unflag", key=f"unflag_{lid}", use_container_width=True):
                        del st.session_state.flagged[lid]
                        delete_progress(lid)
                        st.rerun()
                elif is_found:
                    if col.button("Unmark", key=f"unmark_{lid}", use_container_width=True):
                        st.session_state.checked.discard(lid)
                        delete_progress(lid)
                        st.rerun()
                else:
                    if col.button("✓ Found", key=f"found_{lid}", use_container_width=True):
                        st.session_state.checked.add(lid)
                        save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        st.rerun()

                with col.expander("📝 Note"):
                    new_note = st.text_area("Note", value=note_val,
                                            key=f"note_{lid}", height=80,
                                            label_visibility="collapsed",
                                            placeholder="e.g. found in back of bin…")
                    if st.button("💾 Save note", key=f"savenote_{lid}",
                                 use_container_width=True):
                        st.session_state.notes[lid] = new_note
                        status = ("checked" if is_found else
                                  "flagged" if is_flagged else "unchecked")
                        flag   = st.session_state.flagged.get(lid, {})
                        save_progress(lid, status, flag.get("reason"),
                                      flag.get("actual_qty"), flag.get("correct_bin"),
                                      new_note)
                        st.rerun()

                if not is_found and not is_flagged:
                    with col.expander("🚩 Flag issue"):
                        reason = st.radio("Issue type",
                                          ["Wrong quantity", "Wrong part in bin", "Wrong bin"],
                                          key=f"reason_{lid}")
                        if reason == "Wrong quantity":
                            actual_qty = st.number_input(
                                f"Actual qty (listed: {qty})",
                                min_value=0, value=qty, key=f"qty_{lid}")
                            if st.button("Save flag", key=f"saveflag_{lid}",
                                         use_container_width=True):
                                st.session_state.flagged[lid] = {
                                    "reason": "Wrong qty", "actual_qty": actual_qty}
                                save_progress(lid, "flagged", "Wrong qty", actual_qty,
                                              None, st.session_state.notes.get(lid))
                                st.rerun()
                            if st.session_state.auth:
                                if st.button("💾 Update on BrickLink", key=f"update_{lid}",
                                             use_container_width=True):
                                    try:
                                        auth = make_auth(*st.session_state.auth)
                                        update_quantity_on_bricklink(auth, lid, actual_qty)
                                        st.session_state.flagged[lid] = {
                                            "reason": "Qty updated ✓", "actual_qty": actual_qty}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id") == lid:
                                                x["quantity"] = actual_qty
                                        save_progress(lid, "flagged", "Qty updated ✓",
                                                      actual_qty, None,
                                                      st.session_state.notes.get(lid))
                                        st.success("Updated!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                        elif reason == "Wrong bin":
                            correct_bin = st.text_input(
                                f"Correct bin (current: {remarks or 'none'})",
                                key=f"bin_{lid}")
                            if st.button("Save flag", key=f"saveflag_{lid}",
                                         use_container_width=True):
                                st.session_state.flagged[lid] = {
                                    "reason": "Wrong bin", "correct_bin": correct_bin}
                                save_progress(lid, "flagged", "Wrong bin", None,
                                              correct_bin, st.session_state.notes.get(lid))
                                st.rerun()
                            if st.session_state.auth and correct_bin:
                                if st.button("💾 Update on BrickLink", key=f"updatebin_{lid}",
                                             use_container_width=True):
                                    try:
                                        auth = make_auth(*st.session_state.auth)
                                        update_remarks_on_bricklink(auth, lid, correct_bin)
                                        st.session_state.flagged[lid] = {
                                            "reason": "Bin updated ✓", "correct_bin": correct_bin}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id") == lid:
                                                x["remarks"] = correct_bin
                                        save_progress(lid, "flagged", "Bin updated ✓",
                                                      None, correct_bin,
                                                      st.session_state.notes.get(lid))
                                        st.success("Bin updated!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                        else:
                            if st.button("Save flag", key=f"saveflag_{lid}",
                                         use_container_width=True):
                                st.session_state.flagged[lid] = {"reason": "Wrong part"}
                                save_progress(lid, "flagged", "Wrong part", None, None,
                                              st.session_state.notes.get(lid))
                                st.rerun()

    st.divider()
