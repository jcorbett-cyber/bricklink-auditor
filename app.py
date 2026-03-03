import streamlit as st
import requests
from requests_oauthlib import OAuth1
import pandas as pd
from itertools import groupby
from supabase import create_client
from datetime import datetime
import time

st.set_page_config(page_title="Brick Audit", page_icon="🧱", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.block-container {
  padding-top: 0rem !important;
  background: transparent;
}
header[data-testid="stHeader"] {
  background: transparent !important;
  height: 0rem !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
button[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0d1117 0%, #161b27 100%) !important;
  border-right: 1px solid #1e2a3a;
}
section[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0d1117 0%, #111827 50%, #0f172a 100%); }

.part-card {
  background: linear-gradient(145deg, #161b27, #1a2235);
  border: 1px solid #1e2d45;
  border-radius: 16px;
  padding: 14px 10px;
  text-align: center;
  margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.2);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.part-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.3);
  border-color: #2a3f5f;
}
.part-card.found {
  background: linear-gradient(145deg, #0d2818, #112d1c);
  border-color: #2d6a4f;
  box-shadow: 0 4px 15px rgba(45,106,79,0.2);
}
.part-card.found:hover { border-color: #40916c; box-shadow: 0 8px 25px rgba(45,106,79,0.3); }
.part-card.flagged {
  background: linear-gradient(145deg, #2d0d1a, #331220);
  border-color: #7f1d35;
  box-shadow: 0 4px 15px rgba(127,29,53,0.2);
}
.part-card.flagged:hover { border-color: #be2d52; box-shadow: 0 8px 25px rgba(127,29,53,0.3); }
.part-card.lowstock {
  background: linear-gradient(145deg, #2d1a08, #331f0c);
  border-color: #7c3d0e;
}
.part-card.lowstock:hover { border-color: #c2601a; }
.part-card.highlight {
  background: linear-gradient(145deg, #2a2208, #32290d);
  border-color: #b5860d;
  box-shadow: 0 4px 20px rgba(181,134,13,0.25);
}
.part-card.highlight:hover { border-color: #d4a017; box-shadow: 0 8px 30px rgba(181,134,13,0.35); }
.part-card.overpriced {
  background: linear-gradient(145deg, #1e0d2d, #241035);
  border-color: #5b21b6;
}
.part-card.overpriced:hover { border-color: #7c3aed; box-shadow: 0 8px 25px rgba(91,33,182,0.3); }

.part-img {
  width: 100%; max-height: 110px; object-fit: contain; margin-bottom: 10px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));
}
.part-name { font-size:0.78rem; color:#e2e8f0; font-weight:700; margin-bottom:4px; letter-spacing:0.01em; }
.part-meta { font-size:0.68rem; color:#64748b; line-height:1.5; }

.badge {
  display: inline-block; border-radius: 20px; padding: 3px 10px;
  font-size: 0.62rem; font-weight: 700; margin-top: 6px;
  letter-spacing: 0.04em; text-transform: uppercase;
}
.badge-n       { background:rgba(30,42,61,0.8);  color:#94a3b8; border:1px solid #1e2d45; }
.badge-u       { background:rgba(45,35,10,0.8);  color:#f59e0b; border:1px solid #78450a; }
.badge-found   { background:rgba(13,40,24,0.9);  color:#4ade80; border:1px solid #2d6a4f; }
.badge-flagged { background:rgba(45,13,26,0.9);  color:#fb7185; border:1px solid #7f1d35; }
.badge-low     { background:rgba(45,26,8,0.9);   color:#fb923c; border:1px solid #7c3d0e; }
.badge-over    { background:rgba(30,13,45,0.9);  color:#a78bfa; border:1px solid #5b21b6; }

.bin-header {
  background: linear-gradient(135deg, #161b27, #1a2235);
  border-left: 3px solid #6d28d9; border-radius: 12px;
  padding: 12px 20px; margin: 24px 0 12px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.bin-title { font-size:1rem; font-weight:700; color:#a78bfa; margin:0; letter-spacing:0.02em; }
.bin-stats { font-size:0.72rem; color:#475569; margin:3px 0 0 0; font-weight:500; }

.scan-bar {
  background: linear-gradient(135deg, #161b27, #1a2235);
  border: 1px solid #1e2d45; border-radius: 14px;
  padding: 14px 20px; margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.metric-card {
  background: linear-gradient(145deg, #161b27, #1a2235);
  border: 1px solid #1e2d45; border-radius: 16px;
  padding: 20px 16px; text-align: center; margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.35); }
.metric-value { font-size:2rem; font-weight:800; color:#a78bfa; letter-spacing:-0.02em; }
.metric-label { font-size:0.72rem; color:#475569; margin-top:6px; font-weight:500; text-transform:uppercase; letter-spacing:0.06em; }

.stButton > button {
  font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
  border-radius: 10px !important; border: 1px solid #1e2d45 !important;
  background: linear-gradient(135deg, #161b27, #1a2235) !important;
  color: #94a3b8 !important; transition: all 0.15s ease !important;
  font-size: 0.75rem !important;
}
.stButton > button:hover {
  border-color: #6d28d9 !important; color: #a78bfa !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(109,40,217,0.2) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #5b21b6, #6d28d9) !important;
  border-color: #7c3aed !important; color: #f5f3ff !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #6d28d9, #7c3aed) !important;
  box-shadow: 0 4px 15px rgba(109,40,217,0.4) !important;
}
.stTextInput > div > div > input {
  font-family: 'Inter', sans-serif !important;
  background: #161b27 !important; border: 1px solid #1e2d45 !important;
  border-radius: 10px !important; color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus {
  border-color: #6d28d9 !important;
  box-shadow: 0 0 0 2px rgba(109,40,217,0.2) !important;
}
.stSelectbox > div > div {
  background: #161b27 !important; border: 1px solid #1e2d45 !important;
  border-radius: 10px !important; color: #e2e8f0 !important;
}
.stMultiSelect > div {
  background: #161b27 !important; border: 1px solid #1e2d45 !important;
  border-radius: 10px !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, #5b21b6, #7c3aed) !important;
  border-radius: 10px !important;
}
div[data-testid="stExpander"] {
  background: #161b27 !important; border: 1px solid #1e2d45 !important;
  border-radius: 10px !important;
}
.stDataFrame { border-radius: 12px !important; overflow: hidden; border: 1px solid #1e2d45 !important; }
h1 { font-family:'Inter',sans-serif !important; font-weight:800 !important; color:#e2e8f0 !important; letter-spacing:-0.03em !important; }
h2, h3 { font-family:'Inter',sans-serif !important; font-weight:700 !important; color:#cbd5e1 !important; letter-spacing:-0.02em !important; }
.stCaption, .stMarkdown p { color:#475569 !important; font-family:'Inter',sans-serif !important; }
div[data-testid="stSuccess"] { background:rgba(13,40,24,0.8) !important; border:1px solid #2d6a4f !important; border-radius:10px !important; }
div[data-testid="stWarning"] { background:rgba(45,26,8,0.8) !important; border:1px solid #7c3d0e !important; border-radius:10px !important; }
div[data-testid="stError"]   { background:rgba(45,13,26,0.8) !important; border:1px solid #7f1d35 !important; border-radius:10px !important; }
div[data-testid="stInfo"]    { background:rgba(13,22,40,0.8) !important; border:1px solid #1e3a5f !important; border-radius:10px !important; }

/* ── Mobile ── */
@media (max-width: 768px) {
  .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
  .part-card { padding: 10px 8px; border-radius: 12px; }
  .part-img { max-height: 80px; }
  .part-name { font-size: 0.72rem; }
  .part-meta { font-size: 0.62rem; }
  .badge { font-size: 0.58rem; padding: 2px 7px; }
  .bin-header { padding: 10px 14px; margin: 16px 0 8px 0; }
  .bin-title { font-size: 0.9rem; }
  .metric-value { font-size: 1.5rem; }
  .stButton > button { font-size: 0.8rem !important; padding: 0.5rem !important; min-height: 44px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Screen size detection ─────────────────────────────────────────────────────
st.components.v1.html("""
<script>
function sendScreenWidth() {
  const w = window.innerWidth;
  const data = {type: "screen_width", width: w};
  window.parent.postMessage(JSON.stringify(data), "*");
}
sendScreenWidth();
window.addEventListener("resize", sendScreenWidth);
</script>
""", height=0)

if "screen_width" not in st.session_state:
    st.session_state.screen_width = 1200

screen_w = st.session_state.get("screen_width", 1200)
is_mobile = screen_w < 768
COLS = 3 if is_mobile else 6

LOGO                = "https://raw.githubusercontent.com/jcorbett-cyber/bricklink-auditor/main/iTunesArtwork%402x.png"
LOW_STOCK_THRESHOLD = 2
PRICE_FLAG_PCT      = 25
MARKUP              = 1.25
SALE_DISCOUNT       = 0.70

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
    ("price_cache", {}),
    ("price_results", []),
    ("screen_width", 1200),
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

def update_price_on_bricklink(auth, inventory_id, new_price):
    r = requests.put(f"{BASE}/inventories/{inventory_id}", auth=auth,
                     json={"unit_price": str(new_price)}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "Price update failed"))
    return True

def fetch_price_guide(auth, part_no, color_id, condition="N"):
    url    = f"{BASE}/items/part/{part_no}/price"
    params = {"color_id": color_id, "guide_type": "sold", "new_or_used": condition}
    r      = requests.get(url, auth=auth, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        return None
    pg = data.get("data", {})
    return {
        "avg_price":     float(pg.get("avg_price", 0) or 0),
        "qty_avg_price": float(pg.get("qty_avg_price", 0) or 0),
    }

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
            for i in inv if i.get("inventory_id") in checked)
        val_unchecked = sum(
            float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
            for i in inv if i.get("inventory_id") not in checked)
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
            "audit_date":            datetime.now().isoformat(),
            "total_lots":            total,
            "total_checked":         n_checked,
            "total_flagged":         n_flagged,
            "total_value_checked":   round(val_checked, 2),
            "total_value_unchecked": round(val_unchecked, 2),
            "discrepancies":         discrepancies,
        }).execute()
        return True
    except Exception as e:
        st.warning(f"Could not save snapshot: {e}")
        return False

def load_audit_history():
    if not DB_LOADED:
        return []
    try:
        result = supabase.table("audit_history").select("*").order(
            "audit_date", desc=True).execute()
        return result.data
    except Exception as e:
        st.warning(f"Could not load history: {e}")
        return []

def load_price_cache():
    if not DB_LOADED:
        return {}
    try:
        result = supabase.table("price_cache").select("*").execute()
        cache  = {}
        for row in result.data:
            key        = f"{row['part_no']}_{row['color_id']}_{row['condition']}"
            cache[key] = {
                "avg_price":     row["avg_price"],
                "qty_avg_price": row["qty_avg_price"],
                "last_fetched":  row["last_fetched"],
            }
        return cache
    except Exception as e:
        st.warning(f"Could not load price cache: {e}")
        return {}

def save_price_to_cache(part_no, color_id, condition, avg_price, qty_avg_price):
    if not DB_LOADED:
        return
    try:
        supabase.table("price_cache").upsert({
            "part_no":       part_no,
            "color_id":      color_id,
            "condition":     condition,
            "avg_price":     avg_price,
            "qty_avg_price": qty_avg_price,
            "last_fetched":  datetime.now().isoformat(),
        }, on_conflict="part_no,color_id,condition").execute()
    except Exception as e:
        st.warning(f"Could not save price cache: {e}")

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
    if st.button("🧱 Audit",         use_container_width=True):
        st.session_state.page = "audit"
        st.rerun()
    if st.button("📊 Summary",       use_container_width=True):
        st.session_state.page = "summary"
        st.rerun()
    if st.button("📅 Audit History", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()
    if st.button("💲 Price Checker", use_container_width=True):
        st.session_state.page = "prices"
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
            for i in st.session_state.inventory))
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
                st.session_state.checked     = checked
                st.session_state.flagged     = flagged
                st.session_state.notes       = notes
                st.session_state.price_cache = load_price_cache()
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
    pct       = int(n_checked / total * 100) if total else 0
    low_lots  = [i for i in inv if 0 < i.get("quantity", 0) <= LOW_STOCK_THRESHOLD]

    val_checked   = sum(
        float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
        for i in inv if i.get("inventory_id") in checked)
    val_unchecked = sum(
        float(i.get("unit_price", 0) or 0) * int(i.get("quantity", 0) or 0)
        for i in inv if i.get("inventory_id") not in checked)
    val_total = val_checked + val_unchecked

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
          <div class="metric-value" style="color:#fb7185">{n_flagged}</div>
          <div class="metric-label">Lots Flagged</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#fb923c">{len(low_lots)}</div>
          <div class="metric-label">Low Stock Lots</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("💰 Inventory Value Tracking")
    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#4ade80">${val_checked:,.2f}</div>
          <div class="metric-label">Value Checked ✅</div>
        </div>""", unsafe_allow_html=True)
    with v2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#fb7185">${val_unchecked:,.2f}</div>
          <div class="metric-label">Value Not Yet Checked</div>
        </div>""", unsafe_allow_html=True)
    with v3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">${val_total:,.2f}</div>
          <div class="metric-label">Total Store Value</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📦 Progress by Bin")
    bin_data = []
    for bin_name, lots in groupby(
        sorted(inv, key=lambda x: x.get("remarks", "") or ""),
        key=lambda x: x.get("remarks", "") or "(no remarks)"
    ):
        lots      = list(lots)
        b_total   = len(lots)
        b_checked = sum(1 for x in lots if x.get("inventory_id") in checked)
        b_flagged = sum(1 for x in lots if x.get("inventory_id") in flagged)
        b_val     = sum(
            float(x.get("unit_price", 0) or 0) * int(x.get("quantity", 0) or 0)
            for x in lots)
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
        st.info("No snapshots yet. Click **📸 Save Audit Snapshot** in the sidebar.")
        st.stop()

    st.subheader("Past Audits")
    df_hist = pd.DataFrame([{
        "Date":            h["audit_date"][:16].replace("T", " "),
        "Total Lots":      h["total_lots"],
        "Checked":         h["total_checked"],
        "Flagged":         h["total_flagged"],
        "% Complete":      int(h["total_checked"] / h["total_lots"] * 100)
                           if h["total_lots"] else 0,
        "Value Checked":   f"${h['total_value_checked']:,.2f}",
        "Value Remaining": f"${h['total_value_unchecked']:,.2f}",
    } for h in history])
    st.dataframe(df_hist, use_container_width=True, hide_index=True)

    if len(history) > 1:
        st.divider()
        st.subheader("📈 Audit Completion Over Time")
        chart_data = pd.DataFrame([{
            "Date":       h["audit_date"][:10],
            "% Complete": int(h["total_checked"] / h["total_lots"] * 100)
                          if h["total_lots"] else 0,
            "Flagged":    h["total_flagged"],
        } for h in reversed(history)])
        st.line_chart(chart_data.set_index("Date"))

    st.divider()
    st.subheader("🔎 Drill into an audit")
    audit_labels = [h["audit_date"][:16].replace("T", " ") for h in history]
    selected     = st.selectbox("Select an audit", audit_labels)
    selected_h   = history[audit_labels.index(selected)]
    col1, col2, col3 = st.columns(3)
    pct = int(selected_h["total_checked"] / selected_h["total_lots"] * 100) \
          if selected_h["total_lots"] else 0
    with col1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value">{pct}%</div>
          <div class="metric-label">Complete</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#fb7185">{selected_h['total_flagged']}</div>
          <div class="metric-label">Flagged</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-value" style="color:#4ade80">${selected_h['total_value_checked']:,.2f}</div>
          <div class="metric-label">Value Checked</div>
        </div>""", unsafe_allow_html=True)
    discreps = selected_h.get("discrepancies", [])
    if discreps:
        st.markdown(f"**{len(discreps)} discrepancies:**")
        st.dataframe(pd.DataFrame(discreps), use_container_width=True, hide_index=True)
    else:
        st.success("No discrepancies recorded!")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRICE CHECKER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "prices":
    st.header("💲 Price Checker")
    st.caption(f"Flags lots priced more than {PRICE_FLAG_PCT}% above BrickLink market average. "
               f"Your pricing strategy: +{int((MARKUP-1)*100)}% markup, "
               f"{int((1-SALE_DISCOUNT)*100)}% sale = "
               f"{int((MARKUP*SALE_DISCOUNT-1)*100):+d}% vs market.")

    inv = st.session_state.inventory
    col_a, col_b, col_c = st.columns([2, 2, 1])
    with col_a:
        all_remarks = sorted(set(i.get("remarks", "") or "(no remarks)" for i in inv))
        bin_select  = st.selectbox("Check prices for bin", ["All bins"] + all_remarks)
    with col_b:
        batch_size = st.selectbox("Batch size", [25, 50, 100], index=0)
    with col_c:
        force_refresh = st.checkbox("Force refresh")

    lots_to_check = inv if bin_select == "All bins" else [
        i for i in inv if (i.get("remarks", "") or "(no remarks)") == bin_select]

    cached_count = sum(
        1 for i in lots_to_check
        if f"{i.get('item',{}).get('no','')}_{i.get('color_id',0)}_N"
        in st.session_state.price_cache)
    st.caption(f"{len(lots_to_check)} lots selected · "
               f"{cached_count} cached · "
               f"{len(lots_to_check)-cached_count} need fetching")

    if st.button(f"🔍 Fetch prices for next {batch_size} uncached lots",
                 type="primary", use_container_width=True):
        auth     = make_auth(*st.session_state.auth)
        to_fetch = []
        for lot in lots_to_check:
            pno      = lot.get("item", {}).get("no", "")
            color_id = lot.get("color_id", 0)
            key      = f"{pno}_{color_id}_N"
            if force_refresh or key not in st.session_state.price_cache:
                to_fetch.append(lot)
            if len(to_fetch) >= batch_size:
                break

        if not to_fetch:
            st.success("All cached! Check 'Force refresh' to re-fetch.")
        else:
            progress_bar = st.progress(0)
            status_text  = st.empty()
            for idx, lot in enumerate(to_fetch):
                pno      = lot.get("item", {}).get("no", "")
                color_id = lot.get("color_id", 0)
                key      = f"{pno}_{color_id}_N"
                status_text.text(f"Fetching {idx+1}/{len(to_fetch)}: {pno}…")
                try:
                    pg = fetch_price_guide(auth, pno, color_id, "N")
                    if pg:
                        st.session_state.price_cache[key] = pg
                        save_price_to_cache(pno, color_id, "N",
                                            pg["avg_price"], pg["qty_avg_price"])
                except Exception:
                    pass
                progress_bar.progress((idx + 1) / len(to_fetch))
                time.sleep(0.3)
            status_text.text("Done!")
            st.success(f"✅ Fetched {len(to_fetch)} lots!")
            st.rerun()

    st.divider()
    rows = []
    for lot in lots_to_check:
        pno       = lot.get("item", {}).get("no", "")
        color_id  = lot.get("color_id", 0)
        key       = f"{pno}_{color_id}_N"
        my_price  = float(lot.get("unit_price", 0) or 0)
        cache_hit = st.session_state.price_cache.get(key)
        if not cache_hit:
            continue
        mkt_avg = float(cache_hit.get("avg_price", 0) or 0)
        if mkt_avg == 0:
            continue
        pct_diff = ((my_price - mkt_avg) / mkt_avg) * 100
        target   = round(mkt_avg * MARKUP * SALE_DISCOUNT, 4)
        rows.append({
            "lot": lot, "pno": pno,
            "name":     lot.get("item", {}).get("name", ""),
            "color":    lot.get("color_name", ""),
            "bin":      lot.get("remarks", ""),
            "my_price": my_price,
            "mkt_avg":  mkt_avg,
            "mkt_qty":  float(cache_hit.get("qty_avg_price", 0) or 0),
            "pct_diff": pct_diff,
            "target":   target,
            "flagged":  pct_diff > PRICE_FLAG_PCT,
            "lid":      lot.get("inventory_id"),
        })

    if rows:
        flagged_rows = [r for r in rows if r["flagged"]]
        ok_rows      = [r for r in rows if not r["flagged"]]
        price_tab1, price_tab2 = st.tabs([
            f"🚩 Overpriced ({len(flagged_rows)})",
            f"✅ OK ({len(ok_rows)})"
        ])

        def render_price_table(price_rows, tab):
            with tab:
                if not price_rows:
                    st.success("Nothing here!")
                    return
                st.dataframe(pd.DataFrame([{
                    "Part #":      r["pno"],
                    "Name":        r["name"],
                    "Color":       r["color"],
                    "Bin":         r["bin"],
                    "My Price":    f"${r['my_price']:.4f}",
                    "Market Avg":  f"${r['mkt_avg']:.4f}",
                    "% vs Market": f"{r['pct_diff']:+.1f}%",
                    "Suggested":   f"${r['target']:.4f}",
                } for r in price_rows]), use_container_width=True, hide_index=True)

                st.divider()
                st.markdown("#### 💲 Update a price")
                part_labels  = [f"{r['pno']} — {r['name']} ({r['color']})" for r in price_rows]
                selected_lbl = st.selectbox("Select lot", part_labels, key=f"sel_{id(tab)}")
                selected_row = price_rows[part_labels.index(selected_lbl)]
                col1, col2   = st.columns([2, 1])
                with col1:
                    new_price = st.number_input(
                        f"New price (market: ${selected_row['mkt_avg']:.4f}, "
                        f"suggested: ${selected_row['target']:.4f})",
                        min_value=0.0001,
                        value=float(selected_row["target"]),
                        format="%.4f",
                        key=f"newprice_{selected_row['lid']}")
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("💾 Update on BrickLink",
                                 key=f"updateprice_{selected_row['lid']}",
                                 use_container_width=True, type="primary"):
                        try:
                            auth = make_auth(*st.session_state.auth)
                            update_price_on_bricklink(auth, selected_row["lid"], new_price)
                            for x in st.session_state.inventory:
                                if x.get("inventory_id") == selected_row["lid"]:
                                    x["unit_price"] = str(new_price)
                            st.success(f"✅ Price updated to ${new_price:.4f}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

        render_price_table(flagged_rows, price_tab1)
        render_price_table(ok_rows,      price_tab2)

        st.divider()
        df_export = pd.DataFrame([{
            "Part #":      r["pno"],
            "Name":        r["name"],
            "Color":       r["color"],
            "Bin":         r["bin"],
            "My Price":    r["my_price"],
            "Market Avg":  r["mkt_avg"],
            "% vs Market": round(r["pct_diff"], 1),
            "Suggested":   r["target"],
            "Flagged":     "Yes" if r["flagged"] else "No",
        } for r in rows])
        st.download_button("📥 Download Price Report CSV",
                           df_export.to_csv(index=False),
                           "price_report.csv", "text/csv",
                           use_container_width=True)
    else:
        st.info("No cached prices yet — fetch some lots above to see results.")
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
           + (f" · 🔍 {len(scan_ids)} match(es) highlighted" if scan_ids else "")
           + (f" · 📱 Mobile ({COLS} cols)" if is_mobile else f" · 🖥️ Desktop ({COLS} cols)"))

def get_group(lot):
    return lot.get("remarks", "") or "(no remarks)"

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

            price_key  = f"{pno}_{color_id}_N"
            price_data = st.session_state.price_cache.get(price_key)
            is_over    = False
            if price_data and float(price or 0) > 0:
                mkt = float(price_data.get("avg_price", 0) or 0)
                if mkt > 0:
                    is_over = ((float(price) - mkt) / mkt * 100) > PRICE_FLAG_PCT

            if is_scan:       card_cls = "part-card highlight"
            elif is_flagged:  card_cls = "part-card flagged"
            elif is_found:    card_cls = "part-card found"
            elif is_over:     card_cls = "part-card overpriced"
            elif is_low:      card_cls = "part-card lowstock"
            else:             card_cls = "part-card"

            if is_flagged:
                badge_cls = "badge-flagged"
                badge_lbl = "🚩 " + flag_info.get("reason", "Flagged")
            elif is_found:
                badge_cls = "badge-found"
                badge_lbl = "✅ Found"
            elif is_over:
                badge_cls = "badge-over"
                badge_lbl = "💲 Overpriced"
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
                  <div class="part-meta">{pname[:26] if not is_mobile else pname[:18]}</div>
                  <div class="part-meta">{color} · ×{qty}</div>
                  <div class="part-meta">${price}</div>
                  <span class="badge {badge_cls}">{badge_lbl}</span>
                  {f'<div class="part-meta" style="margin-top:4px;color:#f59e0b;">📝 {note_val[:20]}</div>' if note_val else ''}
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
                                      flag.get("actual_qty"),
                                      flag.get("correct_bin"), new_note)
                        st.rerun()

                if not is_found and not is_flagged:
                    with col.expander("🚩 Flag issue"):
                        reason = st.radio(
                            "Issue type",
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
