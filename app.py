import streamlit as st
import requests
from requests_oauthlib import OAuth1
import pandas as pd

st.set_page_config(page_title="Brick Audit", page_icon="🧱", layout="wide")

st.markdown("""
<style>
.part-card { background:#1e1e2e; border:1px solid #313244; border-radius:12px; padding:14px; text-align:center; margin-bottom:8px; }
.part-card.found { border-color:#a6e3a1; background:#1a2e1a; }
.part-card.flagged { border-color:#f38ba8; background:#2e1a1a; }
.part-img { width:100%; max-height:110px; object-fit:contain; margin-bottom:8px; }
.part-name { font-size:0.8rem; color:#cdd6f4; font-weight:700; margin-bottom:3px; }
.part-meta { font-size:0.72rem; color:#a6adc8; }
.badge { display:inline-block; border-radius:6px; padding:2px 8px; font-size:0.68rem; font-weight:700; margin-top:4px; }
.badge-n { background:#313244; color:#cdd6f4; }
.badge-u { background:#45475a; color:#f9e2af; }
.badge-found { background:#a6e3a1; color:#1e1e2e; }
.badge-flagged { background:#f38ba8; color:#1e1e2e; }
.bin-header { background:#181825; border-left:4px solid #cba6f7; border-radius:8px; padding:10px 16px; margin:18px 0 10px 0; }
.bin-title { font-size:1.1rem; font-weight:800; color:#cba6f7; margin:0; }
.bin-stats { font-size:0.78rem; color:#a6adc8; margin:2px 0 0 0; }
</style>
""", unsafe_allow_html=True)

LOGO = "https://raw.githubusercontent.com/jcorbett-cyber/bricklink-auditor/main/Gemini_Generated_Image_mqazexmqazexmqaz.png"

try:
    CK = st.secrets["BL_CONSUMER_KEY"]
    CS = st.secrets["BL_CONSUMER_SECRET"]
    TV = st.secrets["BL_TOKEN_VALUE"]
    TS = st.secrets["BL_TOKEN_SECRET"]
    SECRETS_LOADED = True
except Exception:
    SECRETS_LOADED = False

for key, default in [
    ("inventory", []),
    ("checked", set()),
    ("flagged", {}),
    ("loaded", False),
    ("auth", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

BASE = "https://api.bricklink.com/api/store/v1"

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
    url = f"{BASE}/inventories/{inventory_id}"
    r = requests.put(url, auth=auth, json={"quantity": new_qty}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "Update failed"))
    return True

with st.sidebar:
    st.image(LOGO, width=200)

    if not SECRETS_LOADED:
        st.warning("⚠️ No saved credentials found. Enter them manually below.")
        st.markdown("### 🔑 API Credentials")
        st.caption("Keys are never saved — session only.")
        ck = st.text_input("Consumer Key",    type="password")
        cs = st.text_input("Consumer Secret", type="password")
        tv = st.text_input("Token Value",     type="password")
        ts = st.text_input("Token Secret",    type="password")
    else:
        ck, cs, tv, ts = CK, CS, TV, TS
        st.success("🔑 Credentials loaded automatically!")

    load_btn = st.button("🔄 Load My Inventory", use_container_width=True, type="primary")

    st.divider()
    st.markdown("### 🔍 Filters")
    search_term = st.text_input("Search part # or name")
    cond_filter = st.multiselect("Condition", ["New", "Used"], default=["New", "Used"])
    show_filter = st.radio("Show", ["All", "✅ Found", "🚩 Flagged", "⬜ Not yet found"])

    all_remarks = sorted(set(i.get("remarks", "") or "(no remarks)" for i in st.session_state.inventory))
    remarks_filter = "All"
    if len(all_remarks) > 1:
        remarks_filter = st.selectbox("📦 Jump to bin", ["All"] + all_remarks)

    st.divider()
    if st.session_state.inventory:
        total     = len(st.session_state.inventory)
        found_n   = len(st.session_state.checked)
        flagged_n = len(st.session_state.flagged)
        pct       = int(found_n / total * 100) if total else 0
        st.markdown("### 📊 Audit Progress")
        st.progress(pct / 100)
        st.markdown(f"**{found_n}/{total}** found · {pct}%")
        if flagged_n:
            st.markdown(f"🚩 **{flagged_n}** lots flagged")

        if st.button("🗑️ Reset All Checkmarks", use_container_width=True):
            st.session_state.checked = set()
            st.session_state.flagged = {}
            st.rerun()

        remaining = [i for i in st.session_state.inventory if i.get("inventory_id") not in st.session_state.checked]
        if remaining:
            df_remaining = pd.DataFrame([{
                "Inventory ID": r.get("inventory_id", ""),
                "Part #":       r.get("item", {}).get("no", ""),
                "Name":         r.get("item", {}).get("name", ""),
                "Color":        r.get("color_name", ""),
                "Condition":    "New" if r.get("new_or_used") == "N" else "Used",
                "Quantity":     r.get("quantity", 0),
                "Price":        r.get("unit_price", ""),
                "Bin":          r.get("remarks", ""),
            } for r in remaining])
            st.download_button("📥 Export Remaining CSV", df_remaining.to_csv(index=False),
                               "remaining_lots.csv", "text/csv", use_container_width=True)

        flagged_lots = [
            {**i, **st.session_state.flagged.get(i.get("inventory_id"), {})}
            for i in st.session_state.inventory
            if i.get("inventory_id") in st.session_state.flagged
        ]
        if flagged_lots:
            df_flagged = pd.DataFrame([{
                "Inventory ID": f.get("inventory_id", ""),
                "Part #":       f.get("item", {}).get("no", ""),
                "Name":         f.get("item", {}).get("name", ""),
                "Color":        f.get("color_name", ""),
                "Listed Qty":   f.get("quantity", 0),
                "Actual Qty":   f.get("actual_qty", ""),
                "Flag Reason":  f.get("reason", ""),
                "Bin":          f.get("remarks", ""),
            } for f in flagged_lots])
            st.download_button("🚩 Export Flagged CSV", df_flagged.to_csv(index=False),
                               "flagged_lots.csv", "text/csv", use_container_width=True)

if load_btn:
    if not all([ck, cs, tv, ts]):
        st.error("Please fill in all four credential fields.")
    else:
        with st.spinner("Loading inventory from BrickLink…"):
            try:
                auth = make_auth(ck, cs, tv, ts)
                inv  = fetch_inventory(auth)
                st.session_state.inventory = inv
                st.session_state.checked   = set()
                st.session_state.flagged   = {}
                st.session_state.loaded    = True
                st.session_state.auth      = (ck, cs, tv, ts)
                st.success(f"✅ Loaded {len(inv)} lots!")
            except Exception as e:
                st.error(f"Error loading inventory: {e}")

col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(LOGO, width=70)
with col_title:
    st.title("🧱 Brick Audit")

if not st.session_state.loaded:
    st.info("👈 Click **Load My Inventory** in the sidebar to get started.")
    st.stop()

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
if remarks_filter != "All":
    inv = [i for i in inv if (i.get("remarks", "") or "(no remarks)") == remarks_filter]

inv = sorted(inv, key=lambda x: (x.get("remarks", "") or ""))

st.caption(f"Showing {len(inv)} lots")

# ── Group lots by bin before drawing ─────────────────────────────────────────
from itertools import groupby

def get_group(lot):
    return lot.get("remarks", "") or "(no remarks)"

COLS = 6

for group_name, group_items in groupby(inv, key=get_group):
    group_lots = list(group_items)
    bin_total   = len(group_lots)
    bin_found   = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
    bin_flagged = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
    bin_pct     = int(bin_found / bin_total * 100) if bin_total else 0

    # Bin header
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
        if st.button("✅ Mark all found", key=f"markall_{group_name}", use_container_width=True):
            for x in group_lots:
                st.session_state.checked.add(x.get("inventory_id"))
            st.rerun()

    # Draw cards in rows of COLS, strictly within this bin only
    for row_start in range(0, len(group_lots), COLS):
        row_items = group_lots[row_start:row_start + COLS]
        cols = st.columns(COLS)

        for col, lot in zip(cols, row_items):
            lid        = lot.get("inventory_id", "unknown")
            item       = lot.get("item", {})
            pno        = item.get("no", "")
            pname      = item.get("name", "N/A")
            color      = lot.get("color_name", "")
            color_id   = lot.get("color_id", 0)
            qty        = lot.get("quantity", 0)
            price      = lot.get("unit_price", "")
            cond       = "New" if lot.get("new_or_used") == "N" else "Used"
            is_found   = lid in st.session_state.checked
            is_flagged = lid in st.session_state.flagged
            flag_info  = st.session_state.flagged.get(lid, {})

            if is_flagged:
                card_cls  = "part-card flagged"
                badge_cls = "badge-flagged"
                badge_lbl = "🚩 " + flag_info.get("reason", "Flagged")
            elif is_found:
                card_cls  = "part-card found"
                badge_cls = "badge-found"
                badge_lbl = "✅ Found"
            else:
                card_cls  = "part-card"
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
                </div>""", unsafe_allow_html=True)

                if is_flagged:
                    if col.button("↩ Unflag", key=f"unflag_{lid}", use_container_width=True):
                        del st.session_state.flagged[lid]
                        st.rerun()
                elif is_found:
                    if col.button("Unmark", key=f"unmark_{lid}", use_container_width=True):
                        st.session_state.checked.discard(lid)
                        st.rerun()
                else:
                    if col.button("✓ Found", key=f"found_{lid}", use_container_width=True):
                        st.session_state.checked.add(lid)
                        st.rerun()

                if not is_found and not is_flagged:
                    with col.expander("🚩 Flag issue"):
                        reason = st.radio(
                            "Issue type",
                            ["Wrong quantity", "Wrong part in bin"],
                            key=f"reason_{lid}"
                        )
                        if reason == "Wrong quantity":
                            actual_qty = st.number_input(
                                f"Actual qty (listed: {qty})",
                                min_value=0, value=qty,
                                key=f"qty_{lid}"
                            )
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {
                                    "reason": "Wrong qty",
                                    "actual_qty": actual_qty,
                                }
                                st.rerun()
                            if st.session_state.auth:
                                if st.button("💾 Update on BrickLink", key=f"update_{lid}", use_container_width=True):
                                    try:
                                        auth = make_auth(*st.session_state.auth)
                                        update_quantity_on_bricklink(auth, lid, actual_qty)
                                        st.session_state.flagged[lid] = {
                                            "reason": "Qty updated ✓",
                                            "actual_qty": actual_qty,
                                        }
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id") == lid:
                                                x["quantity"] = actual_qty
                                        st.success("Updated on BrickLink!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                        else:
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason": "Wrong part"}
                                st.rerun()

    st.divider()
