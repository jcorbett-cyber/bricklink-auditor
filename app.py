import streamlit as st
import requests
from requests_oauthlib import OAuth1
import pandas as pd
from itertools import groupby
from supabase import create_client
from datetime import datetime
import time
import re

st.set_page_config(page_title="Brick Audit", page_icon="🧱", layout="wide")

# ── Lucide icon helper ────────────────────────────────────────────────────────
def icon(name, size=16, color="currentColor"):
    icons = {
        "package":        '<path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
        "bar-chart-2":    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        "calendar":       '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "tag":            '<path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
        "key":            '<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
        "sliders":        '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
        "archive":        '<polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/>',
        "activity":       '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        "upload-cloud":   '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/>',
        "save":           '<path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>',
        "trash-2":        '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
        "download":       '<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
        "check-circle":   '<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "alert-circle":   '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        "alert-triangle": '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        "trending-up":    '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
        "file-text":      '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
        "check":          '<polyline points="20 6 9 17 4 12"/>',
        "rotate-ccw":     '<polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/>',
        "x":              '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "dollar-sign":    '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>',
        "layers":         '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
        "search":         '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        "flag":           '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
        "grid":           '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
        "box":            '<path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>',
        "refresh-cw":     '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>',
    }
    paths = icons.get(name, "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'style="display:inline-block;vertical-align:middle;margin-right:5px;">'
            f'{paths}</svg>')

def ic(name, size=14, color="#6d7a8f"):
    return icon(name, size=size, color=color)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.block-container { padding-top: 0rem !important; background: transparent; }
header[data-testid="stHeader"] { background: transparent !important; height: 0rem !important; }
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
  border: 1px solid #1e2d45; border-radius: 16px;
  padding: 14px 10px; text-align: center; margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.2);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.part-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); border-color: #2a3f5f; }
.part-card.found { background: linear-gradient(145deg, #0d2818, #112d1c); border-color: #2d6a4f; }
.part-card.found:hover { border-color: #40916c; box-shadow: 0 8px 25px rgba(45,106,79,0.3); }
.part-card.flagged { background: linear-gradient(145deg, #2d0d1a, #331220); border-color: #7f1d35; }
.part-card.flagged:hover { border-color: #be2d52; box-shadow: 0 8px 25px rgba(127,29,53,0.3); }
.part-card.lowstock { background: linear-gradient(145deg, #2d1a08, #331f0c); border-color: #7c3d0e; }
.part-card.lowstock:hover { border-color: #c2601a; }
.part-card.highlight { background: linear-gradient(145deg, #2a2208, #32290d); border-color: #b5860d; box-shadow: 0 4px 20px rgba(181,134,13,0.25); }
.part-card.highlight:hover { border-color: #d4a017; box-shadow: 0 8px 30px rgba(181,134,13,0.35); }
.part-card.overpriced { background: linear-gradient(145deg, #1e0d2d, #241035); border-color: #5b21b6; }
.part-card.overpriced:hover { border-color: #7c3aed; box-shadow: 0 8px 25px rgba(91,33,182,0.3); }

.part-img { width:100%; max-height:110px; object-fit:contain; margin-bottom:10px; filter:drop-shadow(0 2px 4px rgba(0,0,0,0.4)); }
.part-name { font-size:0.78rem; color:#e2e8f0; font-weight:700; margin-bottom:4px; letter-spacing:0.01em; }
.part-meta { font-size:0.68rem; color:#64748b; line-height:1.5; }

.badge {
  display:inline-flex; align-items:center; gap:3px;
  border-radius:20px; padding:3px 9px;
  font-size:0.6rem; font-weight:700; margin-top:6px;
  letter-spacing:0.04em; text-transform:uppercase;
}
.badge svg { margin-right:0 !important; }
.badge-n       { background:rgba(30,42,61,0.8);  color:#94a3b8; border:1px solid #1e2d45; }
.badge-u       { background:rgba(45,35,10,0.8);  color:#f59e0b; border:1px solid #78450a; }
.badge-found   { background:rgba(13,40,24,0.9);  color:#4ade80; border:1px solid #2d6a4f; }
.badge-flagged { background:rgba(45,13,26,0.9);  color:#fb7185; border:1px solid #7f1d35; }
.badge-low     { background:rgba(45,26,8,0.9);   color:#fb923c; border:1px solid #7c3d0e; }
.badge-over    { background:rgba(30,13,45,0.9);  color:#a78bfa; border:1px solid #5b21b6; }

.bin-header {
  background:linear-gradient(135deg,#161b27,#1a2235);
  border-left:3px solid #6d28d9; border-radius:12px;
  padding:12px 20px; margin:24px 0 12px 0;
  box-shadow:0 2px 10px rgba(0,0,0,0.2);
}
.bin-title { font-size:1rem; font-weight:700; color:#a78bfa; margin:0; letter-spacing:0.02em; }
.bin-stats { font-size:0.72rem; color:#475569; margin:3px 0 0 0; font-weight:500; }

.zone-card {
  background:linear-gradient(145deg,#161b27,#1a2235);
  border:1px solid #1e2d45; border-radius:16px;
  padding:16px; text-align:center; margin-bottom:8px;
  box-shadow:0 4px 15px rgba(0,0,0,0.25);
  transition:transform 0.15s ease, box-shadow 0.15s ease;
  cursor:pointer;
}
.zone-card:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(0,0,0,0.35); border-color:#6d28d9; }
.zone-card-value { font-size:1.6rem; font-weight:800; color:#a78bfa; }
.zone-card-label { font-size:0.7rem; color:#475569; margin-top:4px; text-transform:uppercase; letter-spacing:0.06em; font-weight:600; }

.restock-table-header {
  background:linear-gradient(135deg,#2d1a08,#331f0c);
  border-left:3px solid #fb923c; border-radius:12px;
  padding:12px 20px; margin:20px 0 10px 0;
}
.restock-title { font-size:1rem; font-weight:700; color:#fb923c; margin:0; }

.scan-bar {
  background:linear-gradient(135deg,#161b27,#1a2235);
  border:1px solid #1e2d45; border-radius:14px;
  padding:14px 20px; margin-bottom:20px;
  box-shadow:0 2px 10px rgba(0,0,0,0.2);
}

.metric-card {
  background:linear-gradient(145deg,#161b27,#1a2235);
  border:1px solid #1e2d45; border-radius:16px;
  padding:20px 16px; text-align:center; margin-bottom:10px;
  box-shadow:0 4px 15px rgba(0,0,0,0.25);
  transition:transform 0.15s ease, box-shadow 0.15s ease;
}
.metric-card:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(0,0,0,0.35); }
.metric-value { font-size:2rem; font-weight:800; color:#a78bfa; letter-spacing:-0.02em; }
.metric-label { font-size:0.72rem; color:#475569; margin-top:6px; font-weight:500; text-transform:uppercase; letter-spacing:0.06em; }

.section-label {
  display:flex; align-items:center; gap:8px;
  font-size:0.7rem; font-weight:600; color:#475569;
  text-transform:uppercase; letter-spacing:0.07em; margin-bottom:6px;
}

.stButton > button {
  font-family:'Inter',sans-serif !important; font-weight:600 !important;
  border-radius:10px !important; border:1px solid #1e2d45 !important;
  background:linear-gradient(135deg,#161b27,#1a2235) !important;
  color:#94a3b8 !important; transition:all 0.15s ease !important;
  font-size:0.78rem !important;
}
.stButton > button:hover {
  border-color:#6d28d9 !important; color:#a78bfa !important;
  transform:translateY(-1px) !important;
  box-shadow:0 4px 12px rgba(109,40,217,0.2) !important;
}
.stButton > button[kind="primary"] {
  background:linear-gradient(135deg,#5b21b6,#6d28d9) !important;
  border-color:#7c3aed !important; color:#f5f3ff !important;
}
.stButton > button[kind="primary"]:hover {
  background:linear-gradient(135deg,#6d28d9,#7c3aed) !important;
  box-shadow:0 4px 15px rgba(109,40,217,0.4) !important;
}
.stTextInput > div > div > input {
  font-family:'Inter',sans-serif !important;
  background:#161b27 !important; border:1px solid #1e2d45 !important;
  border-radius:10px !important; color:#e2e8f0 !important;
}
.stTextInput > div > div > input:focus {
  border-color:#6d28d9 !important; box-shadow:0 0 0 2px rgba(109,40,217,0.2) !important;
}
.stSelectbox > div > div {
  background:#161b27 !important; border:1px solid #1e2d45 !important;
  border-radius:10px !important; color:#e2e8f0 !important;
}
.stMultiSelect > div {
  background:#161b27 !important; border:1px solid #1e2d45 !important; border-radius:10px !important;
}
.stProgress > div > div > div {
  background:linear-gradient(90deg,#5b21b6,#7c3aed) !important; border-radius:10px !important;
}
div[data-testid="stExpander"] {
  background:#161b27 !important; border:1px solid #1e2d45 !important; border-radius:10px !important;
}
.stDataFrame { border-radius:12px !important; overflow:hidden; border:1px solid #1e2d45 !important; }
h1 { font-family:'Inter',sans-serif !important; font-weight:800 !important; color:#e2e8f0 !important; letter-spacing:-0.03em !important; }
h2, h3 { font-family:'Inter',sans-serif !important; font-weight:700 !important; color:#cbd5e1 !important; letter-spacing:-0.02em !important; }
.stCaption, .stMarkdown p { color:#475569 !important; font-family:'Inter',sans-serif !important; }
div[data-testid="stSuccess"] { background:rgba(13,40,24,0.8) !important; border:1px solid #2d6a4f !important; border-radius:10px !important; }
div[data-testid="stWarning"] { background:rgba(45,26,8,0.8) !important; border:1px solid #7c3d0e !important; border-radius:10px !important; }
div[data-testid="stError"]   { background:rgba(45,13,26,0.8) !important; border:1px solid #7f1d35 !important; border-radius:10px !important; }
div[data-testid="stInfo"]    { background:rgba(13,22,40,0.8) !important; border:1px solid #1e3a5f !important; border-radius:10px !important; }

@media (max-width:768px) {
  .block-container { padding-left:0.5rem !important; padding-right:0.5rem !important; }
  .part-card { padding:10px 8px; border-radius:12px; }
  .part-img { max-height:80px; }
  .part-name { font-size:0.72rem; }
  .part-meta { font-size:0.62rem; }
  .badge { font-size:0.58rem; padding:2px 7px; }
  .bin-header { padding:10px 14px; margin:16px 0 8px 0; }
  .bin-title { font-size:0.9rem; }
  .metric-value { font-size:1.5rem; }
  .stButton > button { font-size:0.8rem !important; min-height:44px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Screen detection ──────────────────────────────────────────────────────────
st.components.v1.html("""
<script>
function sendScreenWidth() {
  window.parent.postMessage(JSON.stringify({type:"screen_width",width:window.innerWidth}),"*");
}
sendScreenWidth();
window.addEventListener("resize", sendScreenWidth);
</script>
""", height=0)

if "screen_width" not in st.session_state:
    st.session_state.screen_width = 1200
is_mobile = st.session_state.get("screen_width", 1200) < 768
COLS      = 3 if is_mobile else 6

LOGO                = "https://raw.githubusercontent.com/jcorbett-cyber/bricklink-auditor/main/iTunesArtwork%402x.png"
LOW_STOCK_THRESHOLD = 2
PRICE_FLAG_PCT      = 25
MARKUP              = 1.25
SALE_DISCOUNT       = 0.70

# ── Zone detection ────────────────────────────────────────────────────────────
def detect_zone(remarks):
    if not remarks:
        return "other"
    r = remarks.strip()
    if r.upper().startswith("TUB"):
        return "tub"
    if r.upper().startswith("TRAY"):
        return "tray"
    if len(r) >= 2 and r[:2].isalpha() and r[:2].isupper():
        return "bin"
    return "other"

def get_bin_code(remarks):
    if not remarks: return ""
    return remarks.strip()[:2].upper()

def get_zone_number(remarks):
    if not remarks: return ""
    parts = remarks.strip().split()
    return parts[1] if len(parts) > 1 else ""

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
    ("inventory", []), ("checked", set()), ("flagged", {}), ("notes", {}),
    ("loaded", False), ("auth", None), ("show_bulk_confirm", False),
    ("scan_query", ""), ("page", "audit"), ("price_cache", {}),
    ("price_results", []), ("screen_width", 1200),
]:
    if key not in st.session_state:
        st.session_state[key] = default

BASE = "https://api.bricklink.com/api/store/v1"

# ── BrickLink helpers ─────────────────────────────────────────────────────────
def make_auth(ck, cs, tv, ts):
    return OAuth1(ck, cs, tv, ts)
    
@st.cache_data(ttl=3600)
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
    r = requests.get(f"{BASE}/items/part/{part_no}/price", auth=auth,
                     params={"color_id": color_id, "guide_type": "sold",
                             "new_or_used": condition}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        return None
    pg = data.get("data", {})
    return {"avg_price": float(pg.get("avg_price", 0) or 0),
            "qty_avg_price": float(pg.get("qty_avg_price", 0) or 0)}

# ── Supabase helpers ──────────────────────────────────────────────────────────
def save_progress(inventory_id, status, flag_reason=None, actual_qty=None,
                  correct_bin=None, notes=None):
    if not DB_LOADED: return
    try:
        supabase.table("audit_progress").upsert({
            "inventory_id": inventory_id, "status": status,
            "flag_reason": flag_reason, "actual_qty": actual_qty,
            "correct_bin": correct_bin, "notes": notes,
        }, on_conflict="inventory_id").execute()
    except Exception as e:
        st.warning(f"Could not save progress: {e}")

def delete_progress(inventory_id):
    if not DB_LOADED: return
    try:
        supabase.table("audit_progress").delete().eq("inventory_id", inventory_id).execute()
    except Exception as e:
        st.warning(f"Could not delete progress: {e}")

@st.cache_data(ttl=300)
def load_progress():
    if not DB_LOADED: return set(), {}, {}
    try:
        result = supabase.table("audit_progress").select("*").execute()
        checked, flagged, notes = set(), {}, {}
        for row in result.data:
            lid = row["inventory_id"]
            if row.get("notes"): notes[lid] = row["notes"]
            if row["status"] == "checked":
                checked.add(lid)
            elif row["status"] == "flagged":
                flagged[lid] = {"reason": row.get("flag_reason", ""),
                                "actual_qty": row.get("actual_qty"),
                                "correct_bin": row.get("correct_bin", "")}
        return checked, flagged, notes
    except Exception as e:
        st.warning(f"Could not load progress: {e}")
        return set(), {}, {}

def clear_all_progress():
    if not DB_LOADED: return
    try:
        supabase.table("audit_progress").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000").execute()
    except Exception as e:
        st.warning(f"Could not clear progress: {e}")

def save_audit_snapshot():
    if not DB_LOADED or not st.session_state.inventory: return
    try:
        inv, checked, flagged = st.session_state.inventory, st.session_state.checked, st.session_state.flagged
        val_checked   = sum(float(i.get("unit_price",0) or 0)*int(i.get("quantity",0) or 0)
                            for i in inv if i.get("inventory_id") in checked)
        val_unchecked = sum(float(i.get("unit_price",0) or 0)*int(i.get("quantity",0) or 0)
                            for i in inv if i.get("inventory_id") not in checked)
        discrepancies = [{"inventory_id": i.get("inventory_id"),
                          "part_no": i.get("item",{}).get("no",""),
                          "name": i.get("item",{}).get("name",""),
                          "reason": flagged[i.get("inventory_id")].get("reason",""),
                          "actual_qty": flagged[i.get("inventory_id")].get("actual_qty"),
                          "correct_bin": flagged[i.get("inventory_id")].get("correct_bin","")}
                         for i in inv if i.get("inventory_id") in flagged]
        supabase.table("audit_history").insert({
            "audit_date": datetime.now().isoformat(),
            "total_lots": len(inv), "total_checked": len(checked),
            "total_flagged": len(flagged),
            "total_value_checked": round(val_checked, 2),
            "total_value_unchecked": round(val_unchecked, 2),
            "discrepancies": discrepancies,
        }).execute()
        return True
    except Exception as e:
        st.warning(f"Could not save snapshot: {e}")
        return False

def load_audit_history():
    if not DB_LOADED: return []
    try:
        return supabase.table("audit_history").select("*").order(
            "audit_date", desc=True).execute().data
    except Exception as e:
        st.warning(f"Could not load history: {e}")
        return []

@st.cache_data(ttl=3600)
def load_price_cache():
    if not DB_LOADED: return {}
    try:
        result = supabase.table("price_cache").select("*").execute()
        return {f"{r['part_no']}_{r['color_id']}_{r['condition']}":
                {"avg_price": r["avg_price"], "qty_avg_price": r["qty_avg_price"],
                 "last_fetched": r["last_fetched"]}
                for r in result.data}
    except Exception as e:
        st.warning(f"Could not load price cache: {e}")
        return {}

def save_price_to_cache(part_no, color_id, condition, avg_price, qty_avg_price):
    if not DB_LOADED: return
    try:
        supabase.table("price_cache").upsert({
            "part_no": part_no, "color_id": color_id, "condition": condition,
            "avg_price": avg_price, "qty_avg_price": qty_avg_price,
            "last_fetched": datetime.now().isoformat(),
        }, on_conflict="part_no,color_id,condition").execute()
    except Exception as e:
        st.warning(f"Could not save price: {e}")

# ── Bulk push helpers ─────────────────────────────────────────────────────────
def get_pushable_flags():
    pushable = []
    for lot in st.session_state.inventory:
        lid  = lot.get("inventory_id")
        flag = st.session_state.flagged.get(lid)
        if not flag: continue
        reason = flag.get("reason", "")
        if reason in ("Qty updated", "Bin updated"): continue
        if reason == "Wrong qty" and "actual_qty" in flag:
            pushable.append({"lid": lid, "pno": lot.get("item",{}).get("no",""),
                             "name": lot.get("item",{}).get("name",""),
                             "bin": lot.get("remarks",""),
                             "change": f"Qty: {lot.get('quantity')} → {flag['actual_qty']}",
                             "type": "qty", "value": flag["actual_qty"]})
        elif reason == "Wrong bin" and flag.get("correct_bin"):
            pushable.append({"lid": lid, "pno": lot.get("item",{}).get("no",""),
                             "name": lot.get("item",{}).get("name",""),
                             "bin": lot.get("remarks",""),
                             "change": f"Bin: '{lot.get('remarks','')}' → '{flag['correct_bin']}'",
                             "type": "bin", "value": flag["correct_bin"]})
    return pushable

def push_all_flags(auth):
    results = {"success": [], "failed": []}
    for item in get_pushable_flags():
        try:
            if item["type"] == "qty":
                update_quantity_on_bricklink(auth, item["lid"], item["value"])
                st.session_state.flagged[item["lid"]]["reason"] = "Qty updated"
                for x in st.session_state.inventory:
                    if x.get("inventory_id") == item["lid"]: x["quantity"] = item["value"]
                save_progress(item["lid"], "flagged", "Qty updated", item["value"], None)
            elif item["type"] == "bin":
                update_remarks_on_bricklink(auth, item["lid"], item["value"])
                st.session_state.flagged[item["lid"]]["reason"] = "Bin updated"
                for x in st.session_state.inventory:
                    if x.get("inventory_id") == item["lid"]: x["remarks"] = item["value"]
                save_progress(item["lid"], "flagged", "Bin updated", None, item["value"])
            results["success"].append(item)
        except Exception as e:
            results["failed"].append({**item, "error": str(e)})
    return results

# ── Card renderer (shared between Audit and Stockroom) ────────────────────────
def render_card_grid(lots, cols_count, show_flag_controls=True):
    for row_start in range(0, len(lots), cols_count):
        row_items = lots[row_start:row_start+cols_count]
        cols      = st.columns(cols_count)
        for col, lot in zip(cols, row_items):
            lid       = lot.get("inventory_id", "unknown")
            item      = lot.get("item", {})
            pno       = item.get("no", "")
            pname     = item.get("name", "N/A")
            color     = lot.get("color_name", "")
            color_id  = lot.get("color_id", 0)
            qty       = lot.get("quantity", 0)
            price     = lot.get("unit_price", "")
            remarks   = lot.get("remarks", "")
            cond      = "New" if lot.get("new_or_used") == "N" else "Used"
            is_found  = lid in st.session_state.checked
            is_flagged= lid in st.session_state.flagged
            is_low    = 0 < qty <= LOW_STOCK_THRESHOLD
            flag_info = st.session_state.flagged.get(lid, {})
            note_val  = st.session_state.notes.get(lid, "")

            price_data = st.session_state.price_cache.get(f"{pno}_{color_id}_N")
            is_over    = False
            if price_data and float(price or 0) > 0:
                mkt = float(price_data.get("avg_price",0) or 0)
                if mkt > 0: is_over = ((float(price)-mkt)/mkt*100) > PRICE_FLAG_PCT

            if is_flagged:   card_cls = "part-card flagged"
            elif is_found:   card_cls = "part-card found"
            elif is_over:    card_cls = "part-card overpriced"
            elif is_low:     card_cls = "part-card lowstock"
            else:            card_cls = "part-card"

            if is_flagged:
                b_cls, b_svg, b_lbl = "badge-flagged", icon("alert-circle",10,"#fb7185"), flag_info.get("reason","Flagged")
            elif is_found:
                b_cls, b_svg, b_lbl = "badge-found",   icon("check-circle",10,"#4ade80"), "Found"
            elif is_over:
                b_cls, b_svg, b_lbl = "badge-over",    icon("trending-up",10,"#a78bfa"),  "Overpriced"
            elif is_low:
                b_cls, b_svg, b_lbl = "badge-low",     icon("alert-triangle",10,"#fb923c"), f"Low ({qty})"
            else:
                b_cls = "badge-n" if cond == "New" else "badge-u"
                b_svg, b_lbl = "", cond

            note_html = (f'<div class="part-meta" style="margin-top:4px;color:#f59e0b;">'
                         f'{icon("file-text",10,"#f59e0b")} {note_val[:20]}</div>'
                         if note_val else "")

            with col:
                st.markdown(
                    f'<div class="{card_cls}">'
                    f'<div style="position:relative;display:inline-block;width:100%;">'
f'<img class="part-img" src="https://img.bricklink.com/ItemImage/PN/{color_id}/{pno}.png" '
f'onerror="this.style.opacity=\'0.15\'"/>'
f'<span style="position:absolute;top:4px;left:6px;font-size:1.4rem;font-weight:800;'
f'color:#e2e8f0;text-shadow:0 1px 4px rgba(0,0,0,0.9),0 0 8px rgba(0,0,0,0.8);">'
f'{qty}</span></div>'
                    f'<div class="part-name">{pno}</div>'
                    f'<div class="part-meta">{pname[:26] if not is_mobile else pname[:18]}</div>'
                    f'<div class="part-meta">{color} · ×{qty}</div>'
                    f'<div class="part-meta">${price}</div>'
                    f'<span class="badge {b_cls}">{b_svg}{b_lbl}</span>'
                    f'{note_html}</div>', unsafe_allow_html=True)

                if is_flagged:
                    if col.button("Unflag", key=f"unflag_{lid}", use_container_width=True):
                        del st.session_state.flagged[lid]; delete_progress(lid); st.rerun()
                elif is_found:
                    if col.button("Unmark", key=f"unmark_{lid}", use_container_width=True):
                        st.session_state.checked.discard(lid); delete_progress(lid); st.rerun()
                else:
                    if col.button("Found", key=f"found_{lid}", use_container_width=True):
                        st.session_state.checked.add(lid)
                        save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        st.rerun()

                with col.expander("Note"):
                    new_note = st.text_area("Note", value=note_val, key=f"note_{lid}",
                                            height=80, label_visibility="collapsed",
                                            placeholder="e.g. found in back of bin…")
                    if st.button("Save note", key=f"savenote_{lid}", use_container_width=True):
                        st.session_state.notes[lid] = new_note
                        flag   = st.session_state.flagged.get(lid, {})
                        status = "checked" if is_found else "flagged" if is_flagged else "unchecked"
                        save_progress(lid, status, flag.get("reason"), flag.get("actual_qty"),
                                      flag.get("correct_bin"), new_note)
                        st.rerun()

                if show_flag_controls and not is_found and not is_flagged:
                    with col.expander("Flag issue"):
                        reason = st.radio("Issue type",
                                          ["Wrong quantity","Wrong part in bin","Wrong bin"],
                                          key=f"reason_{lid}")
                        if reason == "Wrong quantity":
                            actual_qty = st.number_input(f"Actual qty (listed: {qty})",
                                                          min_value=0, value=qty, key=f"qty_{lid}")
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong qty","actual_qty":actual_qty}
                                save_progress(lid,"flagged","Wrong qty",actual_qty,None,
                                              st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth:
                                if st.button("Update on BrickLink", key=f"update_{lid}",
                                             use_container_width=True, type="primary"):
                                    try:
                                        update_quantity_on_bricklink(
                                            make_auth(*st.session_state.auth), lid, actual_qty)
                                        st.session_state.flagged[lid] = {"reason":"Qty updated","actual_qty":actual_qty}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id")==lid: x["quantity"]=actual_qty
                                        save_progress(lid,"flagged","Qty updated",actual_qty,None,
                                                      st.session_state.notes.get(lid))
                                        st.success("Updated"); st.rerun()
                                    except Exception as e: st.error(f"Failed: {e}")
                        elif reason == "Wrong bin":
                            correct_bin = st.text_input(
                                f"Correct bin (current: {remarks or 'none'})", key=f"bin_{lid}")
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong bin","correct_bin":correct_bin}
                                save_progress(lid,"flagged","Wrong bin",None,correct_bin,
                                              st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth and correct_bin:
                                if st.button("Update on BrickLink", key=f"updatebin_{lid}",
                                             use_container_width=True, type="primary"):
                                    try:
                                        update_remarks_on_bricklink(
                                            make_auth(*st.session_state.auth), lid, correct_bin)
                                        st.session_state.flagged[lid] = {"reason":"Bin updated","correct_bin":correct_bin}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id")==lid: x["remarks"]=correct_bin
                                        save_progress(lid,"flagged","Bin updated",None,correct_bin,
                                                      st.session_state.notes.get(lid))
                                        st.success("Bin updated"); st.rerun()
                                    except Exception as e: st.error(f"Failed: {e}")
                        else:
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong part"}
                                save_progress(lid,"flagged","Wrong part",None,None,
                                              st.session_state.notes.get(lid)); st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(LOGO, width=200)

    if not SECRETS_LOADED:
        st.warning("No saved credentials found.")
        ck = st.text_input("Consumer Key",    type="password")
        cs = st.text_input("Consumer Secret", type="password")
        tv = st.text_input("Token Value",     type="password")
        ts = st.text_input("Token Secret",    type="password")
    else:
        ck, cs, tv, ts = CK, CS, TV, TS
        st.success("Credentials loaded")

    load_btn = st.button("Load Inventory", use_container_width=True, type="primary")

    st.divider()
    st.markdown(f'<div class="section-label">{ic("package")} Pages</div>',
                unsafe_allow_html=True)
    if st.button("Audit",         use_container_width=True):
        st.session_state.page = "audit";     st.rerun()
    if st.button("Summary",       use_container_width=True):
        st.session_state.page = "summary";   st.rerun()
    if st.button("Stockroom",     use_container_width=True):
        st.session_state.page = "stockroom"; st.rerun()
    if st.button("Audit History", use_container_width=True):
        st.session_state.page = "history";   st.rerun()
    if st.button("Price Checker", use_container_width=True):
        st.session_state.page = "prices";    st.rerun()

    st.divider()
    if st.session_state.page == "audit":
        st.markdown(f'<div class="section-label">{ic("sliders")} Filters</div>',
                    unsafe_allow_html=True)
        search_term = st.text_input("Search part # or name")
        cond_filter = st.multiselect("Condition", ["New", "Used"], default=["New", "Used"])
        show_filter = st.radio("Show", ["All", "Found", "Flagged", "Not yet found", "Low stock"])
        all_remarks = sorted(set(i.get("remarks","") or "(no remarks)"
                                 for i in st.session_state.inventory))
        remarks_filter = "All"
        if len(all_remarks) > 1:
            remarks_filter = st.selectbox("Jump to bin", ["All"] + all_remarks)
    else:
        search_term = ""; cond_filter = ["New","Used"]; show_filter = "All"; remarks_filter = "All"

    st.divider()
    if st.session_state.inventory:
        total     = len(st.session_state.inventory)
        found_n   = len(st.session_state.checked)
        flagged_n = len(st.session_state.flagged)
        low_n     = sum(1 for i in st.session_state.inventory
                        if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD)
        pct       = int(found_n / total * 100) if total else 0

        st.markdown(f'<div class="section-label">{ic("activity")} Progress</div>',
                    unsafe_allow_html=True)
        st.progress(pct / 100)
        st.markdown(f"**{found_n}/{total}** found · {pct}%")
        if flagged_n:
            st.markdown(f'<span style="color:#fb7185;font-size:0.82rem;">'
                        f'{ic("alert-circle",13,"#fb7185")} {flagged_n} flagged</span>',
                        unsafe_allow_html=True)
        if low_n:
            st.markdown(f'<span style="color:#fb923c;font-size:0.82rem;">'
                        f'{ic("alert-triangle",13,"#fb923c")} {low_n} low stock</span>',
                        unsafe_allow_html=True)

        pushable = get_pushable_flags()
        if pushable:
            if st.button(f"Push {len(pushable)} fixes to BrickLink",
                         use_container_width=True, type="primary"):
                st.session_state.show_bulk_confirm = True

        if st.button("Save Audit Snapshot", use_container_width=True):
            if save_audit_snapshot(): st.success("Snapshot saved")

        if st.button("Reset All Checkmarks", use_container_width=True):
            st.session_state.checked = set(); st.session_state.flagged = {}
            st.session_state.notes = {}; st.session_state.show_bulk_confirm = False
            clear_all_progress(); st.rerun()

        remaining = [i for i in st.session_state.inventory
                     if i.get("inventory_id") not in st.session_state.checked]
        if remaining:
            st.download_button("Export Remaining CSV",
                pd.DataFrame([{"Inventory ID": r.get("inventory_id",""),
                    "Part #": r.get("item",{}).get("no",""),
                    "Name": r.get("item",{}).get("name",""),
                    "Color": r.get("color_name",""),
                    "Condition": "New" if r.get("new_or_used")=="N" else "Used",
                    "Quantity": r.get("quantity",0), "Price": r.get("unit_price",""),
                    "Bin": r.get("remarks",""),
                    "Notes": st.session_state.notes.get(r.get("inventory_id"),""),
                } for r in remaining]).to_csv(index=False),
                "remaining_lots.csv", "text/csv", use_container_width=True)

        flagged_lots = [{**i, **st.session_state.flagged.get(i.get("inventory_id"),{})}
                        for i in st.session_state.inventory
                        if i.get("inventory_id") in st.session_state.flagged]
        if flagged_lots:
            st.download_button("Export Flagged CSV",
                pd.DataFrame([{"Inventory ID": f.get("inventory_id",""),
                    "Part #": f.get("item",{}).get("no",""),
                    "Name": f.get("item",{}).get("name",""),
                    "Color": f.get("color_name",""),
                    "Listed Qty": f.get("quantity",0), "Actual Qty": f.get("actual_qty",""),
                    "Current Bin": f.get("remarks",""), "Correct Bin": f.get("correct_bin",""),
                    "Flag Reason": f.get("reason",""),
                    "Notes": st.session_state.notes.get(f.get("inventory_id"),""),
                } for f in flagged_lots]).to_csv(index=False),
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
                st.success(f"Loaded {len(inv)} lots")
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
                    st.success(f"Restored {len(checked)} checked, {len(flagged)} flagged")
                else:
                    st.info("Starting fresh.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "summary":
    st.markdown(f'{icon("bar-chart-2",22,"#a78bfa")} '
                f'<span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;'
                f'vertical-align:middle;">Audit Summary</span>', unsafe_allow_html=True)
    st.write("")

    inv, checked, flagged = st.session_state.inventory, st.session_state.checked, st.session_state.flagged
    total     = len(inv)
    n_checked = len(checked)
    n_flagged = len(flagged)
    pct       = int(n_checked / total * 100) if total else 0
    low_lots  = [i for i in inv if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD]
    val_checked   = sum(float(i.get("unit_price",0) or 0)*int(i.get("quantity",0) or 0)
                        for i in inv if i.get("inventory_id") in checked)
    val_unchecked = sum(float(i.get("unit_price",0) or 0)*int(i.get("quantity",0) or 0)
                        for i in inv if i.get("inventory_id") not in checked)

    c1,c2,c3,c4 = st.columns(4)
    for col, val, label, color in [
        (c1, f"{pct}%",              "Audit Complete", "#a78bfa"),
        (c2, f"{n_checked}/{total}", "Lots Found",     "#a78bfa"),
        (c3, str(n_flagged),         "Lots Flagged",   "#fb7185"),
        (c4, str(len(low_lots)),     "Low Stock",      "#fb923c"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value" '
                        f'style="color:{color}">{val}</div>'
                        f'<div class="metric-label">{label}</div></div>',
                        unsafe_allow_html=True)

    st.divider()
    st.markdown(f'{icon("dollar-sign",18,"#a78bfa")} '
                f'<span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;'
                f'vertical-align:middle;">Inventory Value</span>', unsafe_allow_html=True)
    st.write("")
    v1,v2,v3 = st.columns(3)
    for col, val, label, color in [
        (v1, f"${val_checked:,.2f}",              "Value Checked",    "#4ade80"),
        (v2, f"${val_unchecked:,.2f}",             "Not Yet Checked",  "#fb7185"),
        (v3, f"${val_checked+val_unchecked:,.2f}", "Total Store Value","#a78bfa"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value" '
                        f'style="color:{color}">{val}</div>'
                        f'<div class="metric-label">{label}</div></div>',
                        unsafe_allow_html=True)

    st.divider()
    st.markdown(f'{icon("layers",18,"#a78bfa")} '
                f'<span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;'
                f'vertical-align:middle;">Progress by Bin</span>', unsafe_allow_html=True)
    st.write("")
    bin_data = []
    for bn, lots in groupby(sorted(inv, key=lambda x: x.get("remarks","") or ""),
                            key=lambda x: x.get("remarks","") or "(no remarks)"):
        lots = list(lots)
        bt = len(lots)
        bc = sum(1 for x in lots if x.get("inventory_id") in checked)
        bf = sum(1 for x in lots if x.get("inventory_id") in flagged)
        bv = sum(float(x.get("unit_price",0) or 0)*int(x.get("quantity",0) or 0) for x in lots)
        bin_data.append({"Bin": bn, "Total": bt, "Found": bc, "Flagged": bf,
                         "Remaining": bt-bc-bf,
                         "% Done": int(bc/bt*100) if bt else 0,
                         "Value": f"${bv:,.2f}"})
    st.dataframe(pd.DataFrame(bin_data), use_container_width=True, hide_index=True)

    if n_flagged:
        st.divider()
        st.markdown(f'{icon("flag",18,"#fb7185")} '
                    f'<span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;'
                    f'vertical-align:middle;">Flagged Lots</span>', unsafe_allow_html=True)
        st.write("")
        st.dataframe(pd.DataFrame([{
            "Part #": i.get("item",{}).get("no",""), "Name": i.get("item",{}).get("name",""),
            "Color": i.get("color_name",""), "Bin": i.get("remarks",""),
            "Listed Qty": i.get("quantity",0),
            "Actual Qty": flagged[i.get("inventory_id")].get("actual_qty",""),
            "Correct Bin": flagged[i.get("inventory_id")].get("correct_bin",""),
            "Reason": flagged[i.get("inventory_id")].get("reason",""),
            "Notes": st.session_state.notes.get(i.get("inventory_id"),""),
        } for i in inv if i.get("inventory_id") in flagged]),
            use_container_width=True, hide_index=True)

    if low_lots:
        st.divider()
        st.markdown(f'{icon("alert-triangle",18,"#fb923c")} '
                    f'<span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;'
                    f'vertical-align:middle;">Low Stock Lots</span>', unsafe_allow_html=True)
        st.write("")
        st.dataframe(pd.DataFrame([{
            "Part #": i.get("item",{}).get("no",""), "Name": i.get("item",{}).get("name",""),
            "Color": i.get("color_name",""), "Bin": i.get("remarks",""),
            "Quantity": i.get("quantity",0), "Price": f"${i.get('unit_price','')}",
        } for i in low_lots]), use_container_width=True, hide_index=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STOCKROOM
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "stockroom":
    st.markdown(f'{icon("grid",22,"#a78bfa")} '
                f'<span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;'
                f'vertical-align:middle;">Stockroom</span>', unsafe_allow_html=True)
    st.write("")

    inv = st.session_state.inventory

    # ── Zone overview metrics ──
    bins_lots  = [i for i in inv if detect_zone(i.get("remarks","")) == "bin"]
    tubs_lots  = [i for i in inv if detect_zone(i.get("remarks","")) == "tub"]
    trays_lots = [i for i in inv if detect_zone(i.get("remarks","")) == "tray"]

    def zone_low(lots):
        return sum(1 for i in lots if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD)
    def zone_pct(lots):
        if not lots: return 0
        return int(sum(1 for i in lots if i.get("inventory_id") in st.session_state.checked) / len(lots) * 100)

    z1, z2, z3 = st.columns(3)
    for col, label, lots, color in [
        (z1, "Bins (AA–AT)",  bins_lots,  "#a78bfa"),
        (z2, "Tubs (01–28)",  tubs_lots,  "#60a5fa"),
        (z3, "Trays (01–26)", trays_lots, "#34d399"),
    ]:
        with col:
            low = zone_low(lots)
            pct = zone_pct(lots)
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value" style="color:{color}">{len(lots)}</div>'
                f'<div class="metric-label">{label}</div>'
                f'<div style="font-size:0.7rem;color:#475569;margin-top:6px;">'
                f'{pct}% audited'
                f'{" · " + str(low) + " low stock" if low else ""}'
                f'</div></div>', unsafe_allow_html=True)

    st.divider()

    # ── Zone tabs ──
    tab_bins, tab_tubs, tab_trays = st.tabs(["Bins", "Tubs", "Trays"])

    # ── BINS TAB ──
    with tab_bins:
        all_bin_codes = sorted(set(get_bin_code(i.get("remarks",""))
                                   for i in bins_lots if get_bin_code(i.get("remarks",""))))
        selected_bin  = st.selectbox("Select bin", ["All bins"] + all_bin_codes,
                                     key="stockroom_bin_select")

        filtered = bins_lots if selected_bin == "All bins" else [
            i for i in bins_lots if get_bin_code(i.get("remarks","")) == selected_bin]

        if filtered:
            total_f  = len(filtered)
            found_f  = sum(1 for i in filtered if i.get("inventory_id") in st.session_state.checked)
            flagged_f= sum(1 for i in filtered if i.get("inventory_id") in st.session_state.flagged)
            low_f    = [i for i in filtered if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD]
            pct_f    = int(found_f / total_f * 100) if total_f else 0

            m1,m2,m3,m4 = st.columns(4)
            for col, val, label, color in [
                (m1, str(total_f),  "Total Lots",  "#a78bfa"),
                (m2, str(found_f),  "Found",       "#4ade80"),
                (m3, str(flagged_f),"Flagged",     "#fb7185"),
                (m4, str(len(low_f)),"Low Stock",  "#fb923c"),
            ]:
                with col:
                    st.markdown(f'<div class="metric-card" style="padding:12px 8px;">'
                                f'<div class="metric-value" style="font-size:1.4rem;color:{color}">{val}</div>'
                                f'<div class="metric-label">{label}</div></div>',
                                unsafe_allow_html=True)

            st.write("")
            sorted_filtered = sorted(filtered, key=lambda x: x.get("remarks","") or "")
            for group_name, group_items in groupby(sorted_filtered,
                                                    key=lambda x: x.get("remarks","") or "(no bin)"):
                group_lots  = list(group_items)
                bin_found   = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
                bin_flagged = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
                bin_pct     = int(bin_found / len(group_lots) * 100) if group_lots else 0
                flagged_note = (f'&nbsp;&nbsp;{icon("alert-circle",11,"#fb7185")}'
                                f'<span style="font-size:0.7rem;color:#fb7185;">'
                                f'{bin_flagged} flagged</span>' if bin_flagged else "")
                ct, cb = st.columns([4,1])
                with ct:
                    st.markdown(f'<div class="bin-header">'
                                f'<p class="bin-title">{icon("archive",14,"#a78bfa")} {group_name}</p>'
                                f'<p class="bin-stats">{bin_found}/{len(group_lots)} found · {bin_pct}%'
                                f'{flagged_note}</p></div>', unsafe_allow_html=True)
                with cb:
                    st.write(""); st.write("")
                    if st.button("Mark all found", key=f"srmkall_{group_name}", use_container_width=True):
                        for x in group_lots:
                            lid = x.get("inventory_id")
                            st.session_state.checked.add(lid)
                            save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        st.rerun()
                render_card_grid(group_lots, COLS)
                st.divider()

            # Restock section
            if low_f:
                st.markdown(
                    f'<div class="restock-table-header">'
                    f'<p class="restock-title">{icon("alert-triangle",16,"#fb923c")} '
                    f'Restock List — {len(low_f)} lots need attention</p></div>',
                    unsafe_allow_html=True)
                restock_df = pd.DataFrame([{
                    "Part #":   i.get("item",{}).get("no",""),
                    "Name":     i.get("item",{}).get("name",""),
                    "Color":    i.get("color_name",""),
                    "Bin":      i.get("remarks",""),
                    "Qty Left": i.get("quantity",0),
                    "Price":    f"${i.get('unit_price','')}",
                } for i in sorted(low_f, key=lambda x: x.get("remarks","") or "")])
                st.dataframe(restock_df, use_container_width=True, hide_index=True)
                st.download_button("Export Restock List CSV",
                                   restock_df.to_csv(index=False),
                                   f"restock_bins{'_'+selected_bin if selected_bin != 'All bins' else ''}.csv",
                                   "text/csv", use_container_width=True)
        else:
            st.info("No lots found in this bin.")

    # ── TUBS TAB ──
    with tab_tubs:
        all_tub_nums = sorted(set(get_zone_number(i.get("remarks",""))
                                  for i in tubs_lots if get_zone_number(i.get("remarks",""))),
                              key=lambda x: int(x) if x.isdigit() else 0)
        selected_tub = st.selectbox("Select tub", ["All tubs"] + all_tub_nums,
                                    key="stockroom_tub_select")

        filtered = tubs_lots if selected_tub == "All tubs" else [
            i for i in tubs_lots if get_zone_number(i.get("remarks","")) == selected_tub]

        if filtered:
            total_f  = len(filtered)
            found_f  = sum(1 for i in filtered if i.get("inventory_id") in st.session_state.checked)
            flagged_f= sum(1 for i in filtered if i.get("inventory_id") in st.session_state.flagged)
            low_f    = [i for i in filtered if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD]

            m1,m2,m3,m4 = st.columns(4)
            for col, val, label, color in [
                (m1, str(total_f),  "Total Lots", "#60a5fa"),
                (m2, str(found_f),  "Found",      "#4ade80"),
                (m3, str(flagged_f),"Flagged",    "#fb7185"),
                (m4, str(len(low_f)),"Low Stock", "#fb923c"),
            ]:
                with col:
                    st.markdown(f'<div class="metric-card" style="padding:12px 8px;">'
                                f'<div class="metric-value" style="font-size:1.4rem;color:{color}">{val}</div>'
                                f'<div class="metric-label">{label}</div></div>',
                                unsafe_allow_html=True)

            st.write("")
            for group_name, group_items in groupby(
                    sorted(filtered, key=lambda x: x.get("remarks","") or ""),
                    key=lambda x: x.get("remarks","") or "(no tub)"):
                group_lots  = list(group_items)
                bin_found   = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
                bin_flagged = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
                bin_pct     = int(bin_found / len(group_lots) * 100) if group_lots else 0
                flagged_note = (f'&nbsp;&nbsp;{icon("alert-circle",11,"#fb7185")}'
                                f'<span style="font-size:0.7rem;color:#fb7185;">'
                                f'{bin_flagged} flagged</span>' if bin_flagged else "")
                ct, cb = st.columns([4,1])
                with ct:
                    st.markdown(f'<div class="bin-header" style="border-left-color:#60a5fa;">'
                                f'<p class="bin-title" style="color:#60a5fa;">'
                                f'{icon("box",14,"#60a5fa")} {group_name}</p>'
                                f'<p class="bin-stats">{bin_found}/{len(group_lots)} found · {bin_pct}%'
                                f'{flagged_note}</p></div>', unsafe_allow_html=True)
                with cb:
                    st.write(""); st.write("")
                    if st.button("Mark all found", key=f"tubmkall_{group_name}", use_container_width=True):
                        for x in group_lots:
                            lid = x.get("inventory_id")
                            st.session_state.checked.add(lid)
                            save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        st.rerun()
                render_card_grid(group_lots, COLS)
                st.divider()

            if low_f:
                st.markdown(
                    f'<div class="restock-table-header">'
                    f'<p class="restock-title">{icon("alert-triangle",16,"#fb923c")} '
                    f'Restock List — {len(low_f)} lots need attention</p></div>',
                    unsafe_allow_html=True)
                restock_df = pd.DataFrame([{
                    "Part #": i.get("item",{}).get("no",""), "Name": i.get("item",{}).get("name",""),
                    "Color": i.get("color_name",""), "Tub": i.get("remarks",""),
                    "Qty Left": i.get("quantity",0), "Price": f"${i.get('unit_price','')}",
                } for i in sorted(low_f, key=lambda x: x.get("remarks","") or "")])
                st.dataframe(restock_df, use_container_width=True, hide_index=True)
                st.download_button("Export Restock List CSV",
                                   restock_df.to_csv(index=False),
                                   f"restock_tubs.csv", "text/csv", use_container_width=True)
        else:
            st.info("No lots found in this tub.")

    # ── TRAYS TAB ──
    with tab_trays:
        all_tray_nums = sorted(set(get_zone_number(i.get("remarks",""))
                                   for i in trays_lots if get_zone_number(i.get("remarks",""))),
                               key=lambda x: int(x) if x.isdigit() else 0)
        selected_tray = st.selectbox("Select tray", ["All trays"] + all_tray_nums,
                                     key="stockroom_tray_select")

        filtered = trays_lots if selected_tray == "All trays" else [
            i for i in trays_lots if get_zone_number(i.get("remarks","")) == selected_tray]

        if filtered:
            total_f  = len(filtered)
            found_f  = sum(1 for i in filtered if i.get("inventory_id") in st.session_state.checked)
            flagged_f= sum(1 for i in filtered if i.get("inventory_id") in st.session_state.flagged)
            low_f    = [i for i in filtered if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD]

            m1,m2,m3,m4 = st.columns(4)
            for col, val, label, color in [
                (m1, str(total_f),  "Total Lots", "#34d399"),
                (m2, str(found_f),  "Found",      "#4ade80"),
                (m3, str(flagged_f),"Flagged",    "#fb7185"),
                (m4, str(len(low_f)),"Low Stock", "#fb923c"),
            ]:
                with col:
                    st.markdown(f'<div class="metric-card" style="padding:12px 8px;">'
                                f'<div class="metric-value" style="font-size:1.4rem;color:{color}">{val}</div>'
                                f'<div class="metric-label">{label}</div></div>',
                                unsafe_allow_html=True)

            st.write("")
            for group_name, group_items in groupby(
                    sorted(filtered, key=lambda x: x.get("remarks","") or ""),
                    key=lambda x: x.get("remarks","") or "(no tray)"):
                group_lots  = list(group_items)
                bin_found   = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
                bin_flagged = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
                bin_pct     = int(bin_found / len(group_lots) * 100) if group_lots else 0
                flagged_note = (f'&nbsp;&nbsp;{icon("alert-circle",11,"#fb7185")}'
                                f'<span style="font-size:0.7rem;color:#fb7185;">'
                                f'{bin_flagged} flagged</span>' if bin_flagged else "")
                ct, cb = st.columns([4,1])
                with ct:
                    st.markdown(f'<div class="bin-header" style="border-left-color:#34d399;">'
                                f'<p class="bin-title" style="color:#34d399;">'
                                f'{icon("layers",14,"#34d399")} {group_name}</p>'
                                f'<p class="bin-stats">{bin_found}/{len(group_lots)} found · {bin_pct}%'
                                f'{flagged_note}</p></div>', unsafe_allow_html=True)
                with cb:
                    st.write(""); st.write("")
                    if st.button("Mark all found", key=f"traymkall_{group_name}", use_container_width=True):
                        for x in group_lots:
                            lid = x.get("inventory_id")
                            st.session_state.checked.add(lid)
                            save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        st.rerun()
                render_card_grid(group_lots, COLS)
                st.divider()

            if low_f:
                st.markdown(
                    f'<div class="restock-table-header">'
                    f'<p class="restock-title">{icon("alert-triangle",16,"#fb923c")} '
                    f'Restock List — {len(low_f)} lots need attention</p></div>',
                    unsafe_allow_html=True)
                restock_df = pd.DataFrame([{
                    "Part #": i.get("item",{}).get("no",""), "Name": i.get("item",{}).get("name",""),
                    "Color": i.get("color_name",""), "Tray": i.get("remarks",""),
                    "Qty Left": i.get("quantity",0), "Price": f"${i.get('unit_price','')}",
                } for i in sorted(low_f, key=lambda x: x.get("remarks","") or "")])
                st.dataframe(restock_df, use_container_width=True, hide_index=True)
                st.download_button("Export Restock List CSV",
                                   restock_df.to_csv(index=False),
                                   f"restock_trays.csv", "text/csv", use_container_width=True)
        else:
            st.info("No lots found in this tray.")

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "history":
    st.markdown(f'{icon("calendar",22,"#a78bfa")} '
                f'<span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;'
                f'vertical-align:middle;">Audit History</span>', unsafe_allow_html=True)
    st.write("")
    
    @st.cache_data(ttl=300)
    history = load_audit_history()
    if not history:
        st.info("No snapshots yet. Click Save Audit Snapshot in the sidebar.")
        st.stop()

    st.dataframe(pd.DataFrame([{
        "Date": h["audit_date"][:16].replace("T"," "),
        "Total Lots": h["total_lots"], "Checked": h["total_checked"],
        "Flagged": h["total_flagged"],
        "% Complete": int(h["total_checked"]/h["total_lots"]*100) if h["total_lots"] else 0,
        "Value Checked": f"${h['total_value_checked']:,.2f}",
        "Value Remaining": f"${h['total_value_unchecked']:,.2f}",
    } for h in history]), use_container_width=True, hide_index=True)

    if len(history) > 1:
        st.divider()
        st.markdown(f'{icon("activity",18,"#a78bfa")} '
                    f'<span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;'
                    f'vertical-align:middle;">Completion Over Time</span>',
                    unsafe_allow_html=True)
        st.write("")
        st.line_chart(pd.DataFrame([{
            "Date": h["audit_date"][:10],
            "% Complete": int(h["total_checked"]/h["total_lots"]*100) if h["total_lots"] else 0,
            "Flagged": h["total_flagged"],
        } for h in reversed(history)]).set_index("Date"))

    st.divider()
    audit_labels = [h["audit_date"][:16].replace("T"," ") for h in history]
    selected_h   = history[audit_labels.index(
        st.selectbox("Drill into an audit", audit_labels))]
    pct = int(selected_h["total_checked"]/selected_h["total_lots"]*100) \
          if selected_h["total_lots"] else 0
    c1,c2,c3 = st.columns(3)
    for col, val, label, color in [
        (c1, f"{pct}%",                                    "Complete",      "#a78bfa"),
        (c2, str(selected_h["total_flagged"]),             "Flagged",       "#fb7185"),
        (c3, f"${selected_h['total_value_checked']:,.2f}", "Value Checked", "#4ade80"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value" '
                        f'style="color:{color}">{val}</div>'
                        f'<div class="metric-label">{label}</div></div>',
                        unsafe_allow_html=True)
    discreps = selected_h.get("discrepancies", [])
    if discreps:
        st.markdown(f"**{len(discreps)} discrepancies:**")
        st.dataframe(pd.DataFrame(discreps), use_container_width=True, hide_index=True)
    else:
        st.success("No discrepancies recorded")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRICE CHECKER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "prices":
    st.markdown(f'{icon("tag",22,"#a78bfa")} '
                f'<span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;'
                f'vertical-align:middle;">Price Checker</span>', unsafe_allow_html=True)
    st.caption(f"Flags lots priced more than {PRICE_FLAG_PCT}% above BrickLink market average. "
               f"Your strategy: +{int((MARKUP-1)*100)}% markup, "
               f"{int((1-SALE_DISCOUNT)*100)}% sale = "
               f"{int((MARKUP*SALE_DISCOUNT-1)*100):+d}% vs market.")

    inv = st.session_state.inventory
    col_a, col_b, col_c = st.columns([2,2,1])
    with col_a:
        all_remarks = sorted(set(i.get("remarks","") or "(no remarks)" for i in inv))
        bin_select  = st.selectbox("Check prices for bin", ["All bins"] + all_remarks)
    with col_b:
        batch_size = st.selectbox("Batch size", [25, 50, 100], index=0)
    with col_c:
        force_refresh = st.checkbox("Force refresh")

    lots_to_check = inv if bin_select == "All bins" else [
        i for i in inv if (i.get("remarks","") or "(no remarks)") == bin_select]
    cached_count  = sum(1 for i in lots_to_check
                        if f"{i.get('item',{}).get('no','')}_{i.get('color_id',0)}_N"
                        in st.session_state.price_cache)
    st.caption(f"{len(lots_to_check)} lots selected · {cached_count} cached · "
               f"{len(lots_to_check)-cached_count} need fetching")

    if st.button(f"Fetch prices — next {batch_size} uncached lots",
                 type="primary", use_container_width=True):
        auth, to_fetch = make_auth(*st.session_state.auth), []
        for lot in lots_to_check:
            pno, color_id = lot.get("item",{}).get("no",""), lot.get("color_id",0)
            if force_refresh or f"{pno}_{color_id}_N" not in st.session_state.price_cache:
                to_fetch.append(lot)
            if len(to_fetch) >= batch_size: break
        if not to_fetch:
            st.success("All cached! Check Force refresh to re-fetch.")
        else:
            pb, st_txt = st.progress(0), st.empty()
            for idx, lot in enumerate(to_fetch):
                pno, color_id = lot.get("item",{}).get("no",""), lot.get("color_id",0)
                st_txt.text(f"Fetching {idx+1}/{len(to_fetch)}: {pno}…")
                try:
                    pg = fetch_price_guide(auth, pno, color_id, "N")
                    if pg:
                        st.session_state.price_cache[f"{pno}_{color_id}_N"] = pg
                        save_price_to_cache(pno, color_id, "N", pg["avg_price"], pg["qty_avg_price"])
                except Exception:
                    pass
                pb.progress((idx+1)/len(to_fetch))
                time.sleep(0.3)
            st_txt.text("Done!")
            st.success(f"Fetched {len(to_fetch)} lots")
            st.rerun()

    st.divider()
    rows = []
    for lot in lots_to_check:
        pno, color_id = lot.get("item",{}).get("no",""), lot.get("color_id",0)
        cache_hit = st.session_state.price_cache.get(f"{pno}_{color_id}_N")
        if not cache_hit: continue
        my_price = float(lot.get("unit_price",0) or 0)
        mkt_avg  = float(cache_hit.get("avg_price",0) or 0)
        if mkt_avg == 0: continue
        pct_diff = ((my_price - mkt_avg) / mkt_avg) * 100
        rows.append({"lot": lot, "pno": pno, "name": lot.get("item",{}).get("name",""),
                     "color": lot.get("color_name",""), "bin": lot.get("remarks",""),
                     "my_price": my_price, "mkt_avg": mkt_avg,
                     "target": round(mkt_avg * MARKUP * SALE_DISCOUNT, 4),
                     "pct_diff": pct_diff, "flagged": pct_diff > PRICE_FLAG_PCT,
                     "lid": lot.get("inventory_id")})

    if rows:
        flagged_rows = [r for r in rows if r["flagged"]]
        ok_rows      = [r for r in rows if not r["flagged"]]
        tab1, tab2   = st.tabs([f"Overpriced ({len(flagged_rows)})", f"OK ({len(ok_rows)})"])

        def render_price_table(price_rows, tab):
            with tab:
                if not price_rows:
                    st.success("Nothing here!"); return
                st.dataframe(pd.DataFrame([{
                    "Part #": r["pno"], "Name": r["name"], "Color": r["color"],
                    "Bin": r["bin"], "My Price": f"${r['my_price']:.4f}",
                    "Market Avg": f"${r['mkt_avg']:.4f}",
                    "% vs Market": f"{r['pct_diff']:+.1f}%",
                    "Suggested": f"${r['target']:.4f}",
                } for r in price_rows]), use_container_width=True, hide_index=True)
                st.divider()
                st.markdown("**Update a price**")
                part_labels  = [f"{r['pno']} — {r['name']} ({r['color']})" for r in price_rows]
                selected_row = price_rows[part_labels.index(
                    st.selectbox("Select lot", part_labels, key=f"sel_{id(tab)}"))]
                c1, c2 = st.columns([2,1])
                with c1:
                    new_price = st.number_input(
                        f"New price (market: ${selected_row['mkt_avg']:.4f}, "
                        f"suggested: ${selected_row['target']:.4f})",
                        min_value=0.0001, value=float(selected_row["target"]),
                        format="%.4f", key=f"newprice_{selected_row['lid']}")
                with c2:
                    st.write(""); st.write("")
                    if st.button("Update on BrickLink",
                                 key=f"updateprice_{selected_row['lid']}",
                                 use_container_width=True, type="primary"):
                        try:
                            update_price_on_bricklink(
                                make_auth(*st.session_state.auth),
                                selected_row["lid"], new_price)
                            for x in st.session_state.inventory:
                                if x.get("inventory_id") == selected_row["lid"]:
                                    x["unit_price"] = str(new_price)
                            st.success(f"Price updated to ${new_price:.4f}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

        render_price_table(flagged_rows, tab1)
        render_price_table(ok_rows, tab2)
        st.divider()
        st.download_button("Download Price Report CSV",
            pd.DataFrame([{"Part #": r["pno"], "Name": r["name"], "Color": r["color"],
                           "Bin": r["bin"], "My Price": r["my_price"],
                           "Market Avg": r["mkt_avg"], "% vs Market": round(r["pct_diff"],1),
                           "Suggested": r["target"],
                           "Flagged": "Yes" if r["flagged"] else "No"}
                          for r in rows]).to_csv(index=False),
            "price_report.csv", "text/csv", use_container_width=True)
    else:
        st.info("No cached prices yet — fetch some lots above to see results.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT (main)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scan-bar">', unsafe_allow_html=True)
sc1, sc2 = st.columns([5,1])
with sc1:
    scan_query = st.text_input("Scan / quick find",
                                value=st.session_state.scan_query,
                                placeholder="Type or scan a part number…",
                                label_visibility="collapsed", key="scan_input")
with sc2:
    if st.button("Clear", use_container_width=True):
        st.session_state.scan_query = ""; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if scan_query != st.session_state.scan_query:
    st.session_state.scan_query = scan_query; st.rerun()

if st.session_state.show_bulk_confirm:
    pushable = get_pushable_flags()
    if pushable:
        st.warning(f"Ready to push {len(pushable)} fix(es) to BrickLink — review below:")
        st.dataframe(pd.DataFrame([{"Part #": p["pno"], "Name": p["name"],
                                    "Bin": p["bin"], "Change": p["change"]}
                                   for p in pushable]),
                     use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Confirm — push all", type="primary", use_container_width=True):
                with st.spinner("Pushing…"):
                    results = push_all_flags(make_auth(*st.session_state.auth))
                st.session_state.show_bulk_confirm = False
                if results["success"]: st.success(f"{len(results['success'])} update(s) pushed")
                for f in results.get("failed",[]): st.error(f"Failed for {f['pno']}: {f['error']}")
                st.rerun()
        with c2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_bulk_confirm = False; st.rerun()
    else:
        st.session_state.show_bulk_confirm = False

inv = st.session_state.inventory
if "New" not in cond_filter: inv = [i for i in inv if i.get("new_or_used") != "N"]
if "Used" not in cond_filter: inv = [i for i in inv if i.get("new_or_used") != "U"]
if search_term:
    q = search_term.lower()
    inv = [i for i in inv if q in i.get("item",{}).get("no","").lower()
           or q in i.get("item",{}).get("name","").lower()]
if show_filter == "Found":
    inv = [i for i in inv if i.get("inventory_id") in st.session_state.checked]
elif show_filter == "Flagged":
    inv = [i for i in inv if i.get("inventory_id") in st.session_state.flagged]
elif show_filter == "Not yet found":
    inv = [i for i in inv if i.get("inventory_id") not in st.session_state.checked
           and i.get("inventory_id") not in st.session_state.flagged]
elif show_filter == "Low stock":
    inv = [i for i in inv if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD]
if remarks_filter != "All":
    inv = [i for i in inv if (i.get("remarks","") or "(no remarks)") == remarks_filter]

scan_ids = set()
if st.session_state.scan_query:
    sq = st.session_state.scan_query.lower()
    for lot in inv:
        if sq in lot.get("item",{}).get("no","").lower():
            scan_ids.add(lot.get("inventory_id"))
    if not scan_ids:
        st.warning(f"No parts found matching {st.session_state.scan_query}")

inv = sorted(inv, key=lambda x: (0 if x.get("inventory_id") in scan_ids else 1,
                                  x.get("remarks","") or ""))
st.caption(f"Showing {len(inv)} lots"
           + (f" · {len(scan_ids)} highlighted" if scan_ids else "")
           + (" · Mobile" if is_mobile else " · Desktop"))

for group_name, group_items in groupby(inv, key=lambda x: x.get("remarks","") or "(no remarks)"):
    group_lots  = list(group_items)
    bin_total   = len(group_lots)
    bin_found   = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
    bin_flagged = sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
    bin_pct     = int(bin_found / bin_total * 100) if bin_total else 0

    col_title, col_btn = st.columns([4,1])
    with col_title:
        flagged_note = (f'&nbsp;&nbsp;{icon("alert-circle",11,"#fb7185")}'
                        f'<span style="font-size:0.7rem;color:#fb7185;">'
                        f'{bin_flagged} flagged</span>' if bin_flagged else "")
        st.markdown(f'<div class="bin-header">'
                    f'<p class="bin-title">{icon("archive",14,"#a78bfa")} {group_name}</p>'
                    f'<p class="bin-stats">{bin_found}/{bin_total} found · {bin_pct}%'
                    f'{flagged_note}</p></div>', unsafe_allow_html=True)
    with col_btn:
        st.write(""); st.write("")
        if st.button("Mark all found", key=f"markall_{group_name}", use_container_width=True):
            for x in group_lots:
                lid = x.get("inventory_id")
                st.session_state.checked.add(lid)
                save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
            st.rerun()

    # Pass scan_ids context to highlight cards on audit page
    for row_start in range(0, len(group_lots), COLS):
        row_items = group_lots[row_start:row_start+COLS]
        cols      = st.columns(COLS)
        for col, lot in zip(cols, row_items):
            lid       = lot.get("inventory_id", "unknown")
            item      = lot.get("item", {})
            pno       = item.get("no", "")
            pname     = item.get("name", "N/A")
            color     = lot.get("color_name", "")
            color_id  = lot.get("color_id", 0)
            qty       = lot.get("quantity", 0)
            price     = lot.get("unit_price", "")
            remarks   = lot.get("remarks", "")
            cond      = "New" if lot.get("new_or_used") == "N" else "Used"
            is_found  = lid in st.session_state.checked
            is_flagged= lid in st.session_state.flagged
            is_low    = 0 < qty <= LOW_STOCK_THRESHOLD
            is_scan   = lid in scan_ids
            flag_info = st.session_state.flagged.get(lid, {})
            note_val  = st.session_state.notes.get(lid, "")

            price_data = st.session_state.price_cache.get(f"{pno}_{color_id}_N")
            is_over    = False
            if price_data and float(price or 0) > 0:
                mkt = float(price_data.get("avg_price",0) or 0)
                if mkt > 0: is_over = ((float(price)-mkt)/mkt*100) > PRICE_FLAG_PCT

            if is_scan:      card_cls = "part-card highlight"
            elif is_flagged: card_cls = "part-card flagged"
            elif is_found:   card_cls = "part-card found"
            elif is_over:    card_cls = "part-card overpriced"
            elif is_low:     card_cls = "part-card lowstock"
            else:            card_cls = "part-card"

            if is_flagged:
                b_cls, b_svg, b_lbl = "badge-flagged", icon("alert-circle",10,"#fb7185"), flag_info.get("reason","Flagged")
            elif is_found:
                b_cls, b_svg, b_lbl = "badge-found",   icon("check-circle",10,"#4ade80"), "Found"
            elif is_over:
                b_cls, b_svg, b_lbl = "badge-over",    icon("trending-up",10,"#a78bfa"),  "Overpriced"
            elif is_low:
                b_cls, b_svg, b_lbl = "badge-low",     icon("alert-triangle",10,"#fb923c"), f"Low ({qty})"
            else:
                b_cls = "badge-n" if cond == "New" else "badge-u"
                b_svg, b_lbl = "", cond

            note_html = (f'<div class="part-meta" style="margin-top:4px;color:#f59e0b;">'
                         f'{icon("file-text",10,"#f59e0b")} {note_val[:20]}</div>'
                         if note_val else "")

            with col:
                st.markdown(
                    f'<div class="{card_cls}">'
                    f'<div style="position:relative;display:inline-block;width:100%;">'
f'<img class="part-img" src="https://img.bricklink.com/ItemImage/PN/{color_id}/{pno}.png" '
f'onerror="this.style.opacity=\'0.15\'"/>'
f'<span style="position:absolute;top:4px;left:6px;font-size:1.4rem;font-weight:800;'
f'color:#e2e8f0;text-shadow:0 1px 4px rgba(0,0,0,0.9),0 0 8px rgba(0,0,0,0.8);">'
f'{qty}</span></div>'
                    f'<div class="part-name">{pno}</div>'
                    f'<div class="part-meta">{pname[:26] if not is_mobile else pname[:18]}</div>'
                    f'<div class="part-meta">{color} · ×{qty}</div>'
                    f'<div class="part-meta">${price}</div>'
                    f'<span class="badge {b_cls}">{b_svg}{b_lbl}</span>'
                    f'{note_html}</div>', unsafe_allow_html=True)

                if is_flagged:
                    if col.button("Unflag", key=f"unflag_{lid}", use_container_width=True):
                        del st.session_state.flagged[lid]; delete_progress(lid); st.rerun()
                elif is_found:
                    if col.button("Unmark", key=f"unmark_{lid}", use_container_width=True):
                        st.session_state.checked.discard(lid); delete_progress(lid); st.rerun()
                else:
                    if col.button("Found", key=f"found_{lid}", use_container_width=True):
                        st.session_state.checked.add(lid)
                        save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        st.rerun()

                with col.expander("Note"):
                    new_note = st.text_area("Note", value=note_val, key=f"note_{lid}",
                                            height=80, label_visibility="collapsed",
                                            placeholder="e.g. found in back of bin…")
                    if st.button("Save note", key=f"savenote_{lid}", use_container_width=True):
                        st.session_state.notes[lid] = new_note
                        flag   = st.session_state.flagged.get(lid, {})
                        status = "checked" if is_found else "flagged" if is_flagged else "unchecked"
                        save_progress(lid, status, flag.get("reason"), flag.get("actual_qty"),
                                      flag.get("correct_bin"), new_note)
                        st.rerun()

                if not is_found and not is_flagged:
                    with col.expander("Flag issue"):
                        reason = st.radio("Issue type",
                                          ["Wrong quantity","Wrong part in bin","Wrong bin"],
                                          key=f"reason_{lid}")
                        if reason == "Wrong quantity":
                            actual_qty = st.number_input(f"Actual qty (listed: {qty})",
                                                          min_value=0, value=qty, key=f"qty_{lid}")
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong qty","actual_qty":actual_qty}
                                save_progress(lid,"flagged","Wrong qty",actual_qty,None,
                                              st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth:
                                if st.button("Update on BrickLink", key=f"update_{lid}",
                                             use_container_width=True, type="primary"):
                                    try:
                                        update_quantity_on_bricklink(
                                            make_auth(*st.session_state.auth), lid, actual_qty)
                                        st.session_state.flagged[lid] = {"reason":"Qty updated","actual_qty":actual_qty}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id")==lid: x["quantity"]=actual_qty
                                        save_progress(lid,"flagged","Qty updated",actual_qty,None,
                                                      st.session_state.notes.get(lid))
                                        st.success("Updated"); st.rerun()
                                    except Exception as e: st.error(f"Failed: {e}")
                        elif reason == "Wrong bin":
                            correct_bin = st.text_input(
                                f"Correct bin (current: {remarks or 'none'})", key=f"bin_{lid}")
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong bin","correct_bin":correct_bin}
                                save_progress(lid,"flagged","Wrong bin",None,correct_bin,
                                              st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth and correct_bin:
                                if st.button("Update on BrickLink", key=f"updatebin_{lid}",
                                             use_container_width=True, type="primary"):
                                    try:
                                        update_remarks_on_bricklink(
                                            make_auth(*st.session_state.auth), lid, correct_bin)
                                        st.session_state.flagged[lid] = {"reason":"Bin updated","correct_bin":correct_bin}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id")==lid: x["remarks"]=correct_bin
                                        save_progress(lid,"flagged","Bin updated",None,correct_bin,
                                                      st.session_state.notes.get(lid))
                                        st.success("Bin updated"); st.rerun()
                                    except Exception as e: st.error(f"Failed: {e}")
                        else:
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong part"}
                                save_progress(lid,"flagged","Wrong part",None,None,
                                              st.session_state.notes.get(lid)); st.rerun()

    st.divider()
