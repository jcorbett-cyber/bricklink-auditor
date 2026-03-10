import streamlit as st
import requests
from requests_oauthlib import OAuth1
import pandas as pd
from itertools import groupby
from supabase import create_client
from datetime import datetime
import time

st.set_page_config(page_title="Brick Audit", page_icon="🧱", layout="wide")

def icon(name, size=16, color="currentColor"):
    icons = {
        "package":        '<path d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
        "bar-chart-2":    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        "calendar":       '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "tag":            '<path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
        "sliders":        '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
        "archive":        '<polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/>',
        "activity":       '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
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
        "zap":            '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        "skip-forward":   '<polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19"/>',
        "log-out":        '<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
        "copy":           '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>',
        "home":           '<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
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
  background: linear-gradient(145deg, #1a2236, #1e2640);
  border: 1px solid #2a3f5f; border-radius: 16px;
  padding: 14px 10px; text-align: center; margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.part-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); border-color: #2a3f5f; }
.part-card.found { background: linear-gradient(145deg, #0d2818, #112d1c); border-color: #2d6a4f; }
.part-card.found:hover { border-color: #40916c; box-shadow: 0 8px 25px rgba(45,106,79,0.3); }
.part-card.flagged { background: linear-gradient(145deg, #2d0d1a, #331220); border-color: #7f1d35; }
.part-card.flagged:hover { border-color: #be2d52; }
.part-card.lowstock { background: linear-gradient(145deg, #2d1a08, #331f0c); border-color: #7c3d0e; }
.part-card.highlight { background: linear-gradient(145deg, #2a2208, #32290d); border-color: #b5860d; box-shadow: 0 4px 20px rgba(181,134,13,0.25); }
.part-card.overpriced { background: linear-gradient(145deg, #1e0d2d, #241035); border-color: #5b21b6; }
.part-img-wrap { position:relative; display:block; width:100%; margin-bottom:10px; }
.part-img { width:100%; max-height:110px; object-fit:contain; display:block; filter:drop-shadow(0 2px 4px rgba(0,0,0,0.4)); }
.qty-badge {
  position:absolute; top:4px; left:6px;
  font-size:1.3rem; font-weight:800; color:#e2e8f0;
  text-shadow: 0 1px 4px rgba(0,0,0,0.9), 0 0 8px rgba(0,0,0,0.8); line-height:1;
}
.part-name { font-size:0.78rem; color:#f1f5f9; font-weight:800; margin-bottom:4px; letter-spacing:0.01em; }
.part-meta { font-size:0.68rem; color:#94a3b8; line-height:1.5; }
.badge {
  display:inline-flex; align-items:center; gap:3px; border-radius:20px; padding:3px 9px;
  font-size:0.6rem; ; margin-top:6px; letter-spacing:0.04em; text-transform:uppercase;
}
.badge svg { margin-right:0 !important; }
.badge-n       { background:rgba(30,42,61,0.8);  color:#94a3b8; border:1px solid #1e2d45; }
.badge-u       { background:rgba(45,35,10,0.8);  color:#f59e0b; border:1px solid #78450a; }
.badge-found   { background:rgba(13,40,24,0.9);  color:#4ade80; border:1px solid #2d6a4f; }
.badge-flagged { background:rgba(45,13,26,0.9);  color:#fb7185; border:1px solid #7f1d35; }
.badge-low     { background:rgba(45,26,8,0.9);   color:#fb923c; border:1px solid #7c3d0e; }
.badge-over    { background:rgba(30,13,45,0.9);  color:#a78bfa; border:1px solid #5b21b6; }
.bin-header {
  background:linear-gradient(135deg,#161b27,#1a2235); border-left:3px solid #6d28d9;
  border-radius:12px; padding:12px 20px; margin:24px 0 12px 0; box-shadow:0 2px 10px rgba(0,0,0,0.2);
}
.bin-title { font-size:1rem; ; color:#a78bfa; margin:0; letter-spacing:0.02em; }
.bin-stats { font-size:0.72rem; color:#475569; margin:3px 0 0 0; font-weight:500; }
.dup-group {
  background:linear-gradient(145deg,#1a1225,#1e1535); border:1px solid #4c1d95;
  border-radius:16px; padding:16px 20px; margin-bottom:16px; box-shadow:0 4px 15px rgba(0,0,0,0.25);
}
.dup-group-header { display:flex; align-items:center; gap:12px; margin-bottom:14px; }
.dup-part-img {
  width:64px; height:64px; object-fit:contain; border-radius:10px;
  background:rgba(255,255,255,0.04); border:1px solid #2d1f4a; flex-shrink:0;
}
.dup-part-info { flex:1; }
.dup-part-name { font-size:0.9rem; ; color:#e2e8f0; margin:0 0 2px 0; }
.dup-part-sub  { font-size:0.72rem; color:#6d28d9; font-weight:600; }
.dup-bin-row {
  display:flex; align-items:center; justify-content:space-between;
  background:rgba(109,40,217,0.08); border:1px solid #2d1f4a;
  border-radius:10px; padding:8px 14px; margin-bottom:6px; font-size:0.78rem;
}
.dup-bin-name  { color:#a78bfa; ; }
.dup-bin-qty   { color:#e2e8f0; font-weight:600; }
.dup-bin-price { color:#475569; }
.action-card {
  background:linear-gradient(145deg,#161b27,#1a2235); border:1px solid #1e2d45;
  border-radius:20px; padding:28px 20px; text-align:center; margin-bottom:12px;
  box-shadow:0 4px 15px rgba(0,0,0,0.25); cursor:pointer;
  transition:transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.action-card:hover { transform:translateY(-4px); box-shadow:0 10px 30px rgba(0,0,0,0.4); border-color:#6d28d9; }
.action-card-icon { font-size:2rem; margin-bottom:10px; }
.action-card-title { font-size:1rem; ; color:#e2e8f0; margin-bottom:4px; }
.action-card-sub { font-size:0.72rem; color:#475569; }
.audit-mode-header {
  background:linear-gradient(135deg,#1a0a2e,#2d1060); border:1px solid #6d28d9;
  border-radius:16px; padding:20px 24px; margin-bottom:20px; box-shadow:0 4px 20px rgba(109,40,217,0.3);
}
.audit-mode-title { font-size:1.6rem; font-weight:800; color:#a78bfa; letter-spacing:-0.02em; margin:0 0 4px 0; }
.audit-mode-sub   { font-size:0.8rem; color:#6d28d9; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; }
.audit-complete {
  background:linear-gradient(135deg,#0d2818,#112d1c); border:2px solid #2d6a4f;
  border-radius:20px; padding:40px; text-align:center; box-shadow:0 8px 30px rgba(45,106,79,0.3);
}
.restock-table-header {
  background:linear-gradient(135deg,#2d1a08,#331f0c); border-left:3px solid #fb923c;
  border-radius:12px; padding:12px 20px; margin:20px 0 10px 0;
}
.restock-title { font-size:1rem; ; color:#fb923c; margin:0; }
.color-filter-bar {
  background:linear-gradient(135deg,#161b27,#1a2235); border:1px solid #1e2d45;
  border-radius:14px; padding:10px 20px; margin-bottom:16px; box-shadow:0 2px 10px rgba(0,0,0,0.2);
}
.scan-bar {
  background:linear-gradient(135deg,#161b27,#1a2235); border:1px solid #1e2d45;
  border-radius:14px; padding:14px 20px; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.2);
}
.metric-card {
  background:linear-gradient(145deg,#161b27,#1a2235); border:1px solid #1e2d45;
  border-radius:16px; padding:20px 16px; text-align:center; margin-bottom:10px;
  box-shadow:0 4px 15px rgba(0,0,0,0.25); transition:transform 0.15s ease;
}
.metric-card:hover { transform:translateY(-2px); }
.metric-value { font-size:2rem; font-weight:800; color:#a78bfa; letter-spacing:-0.02em; }
.metric-label { font-size:0.72rem; color:#475569; margin-top:6px; font-weight:500; text-transform:uppercase; letter-spacing:0.06em; }
.section-label {
  display:flex; align-items:center; gap:8px; font-size:0.7rem; font-weight:600; color:#475569;
  text-transform:uppercase; letter-spacing:0.07em; margin-bottom:6px;
}
.stButton > button {
  font-family:'Inter',sans-serif !important; font-weight:600 !important;
  border-radius:10px !important; border:1px solid #1e2d45 !important;
  background:linear-gradient(135deg,#161b27,#1a2235) !important;
  color:#94a3b8 !important; transition:all 0.15s ease !important; font-size:0.78rem !important;
}
.stButton > button:hover {
  border-color:#6d28d9 !important; color:#a78bfa !important;
  transform:translateY(-1px) !important; box-shadow:0 4px 12px rgba(109,40,217,0.2) !important;
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
  font-family:'Inter',sans-serif !important; background:#161b27 !important;
  border:1px solid #1e2d45 !important; border-radius:10px !important; color:#e2e8f0 !important;
}
.stTextInput > div > div > input:focus { border-color:#6d28d9 !important; }
.stSelectbox > div > div {
  background:#161b27 !important; border:1px solid #1e2d45 !important;
  border-radius:10px !important; color:#e2e8f0 !important;
}
.stMultiSelect > div { background:#161b27 !important; border:1px solid #1e2d45 !important; border-radius:10px !important; }
.stProgress > div > div > div { background:linear-gradient(90deg,#5b21b6,#7c3aed) !important; border-radius:10px !important; }
div[data-testid="stExpander"] { background:#161b27 !important; border:1px solid #1e2d45 !important; border-radius:10px !important; }
.stDataFrame { border-radius:12px !important; overflow:hidden; border:1px solid #1e2d45 !important; }
h1 { font-family:'Inter',sans-serif !important; font-weight:800 !important; color:#e2e8f0 !important; }
h2, h3 { font-family:'Inter',sans-serif !important;  !important; color:#cbd5e1 !important; }
.stCaption, .stMarkdown p { color:#475569 !important; font-family:'Inter',sans-serif !important; }
div[data-testid="stSuccess"] { background:rgba(13,40,24,0.8) !important; border:1px solid #2d6a4f !important; border-radius:10px !important; }
div[data-testid="stWarning"] { background:rgba(45,26,8,0.8) !important; border:1px solid #7c3d0e !important; border-radius:10px !important; }
div[data-testid="stError"]   { background:rgba(45,13,26,0.8) !important; border:1px solid #7f1d35 !important; border-radius:10px !important; }
div[data-testid="stInfo"]    { background:rgba(13,22,40,0.8) !important; border:1px solid #1e3a5f !important; border-radius:10px !important; }
@media (max-width:768px) {
  .block-container { padding-left:0.5rem !important; padding-right:0.5rem !important; }
  .part-card { padding:10px 8px; border-radius:12px; }
  .part-img { max-height:80px; }
  .qty-badge { font-size:1rem; }
  .part-name { font-size:0.72rem; }
  .part-meta { font-size:0.62rem; }
  .badge { font-size:0.58rem; padding:2px 7px; }
  .bin-header { padding:10px 14px; margin:16px 0 8px 0; }
  .metric-value { font-size:1.5rem; }
  .stButton > button { font-size:0.8rem !important; min-height:44px !important; }
  .action-card { padding:20px 14px; }
  .action-card-title { font-size:0.9rem; }
}
</style>
""", unsafe_allow_html=True)

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

def detect_zone(remarks):
    if not remarks: return "other"
    r = remarks.strip()
    if r.upper().startswith("WD"):   return "wd"
    if r.upper().startswith("TUB"):  return "tub"
    if r.upper().startswith("TRAY"): return "tray"
    if len(r) >= 2 and r[:2].isalpha() and r[:2].isupper(): return "bin"
    return "other"

def get_bin_code(remarks):
    if not remarks: return ""
    return remarks.strip()[:2].upper()

def get_zone_number(remarks):
    if not remarks: return ""
    parts = remarks.strip().split()
    return parts[1] if len(parts) > 1 else ""

try:
    CK = st.secrets["BL_CONSUMER_KEY"]
    CS = st.secrets["BL_CONSUMER_SECRET"]
    TV = st.secrets["BL_TOKEN_VALUE"]
    TS = st.secrets["BL_TOKEN_SECRET"]
    BO_KEY = st.secrets.get("BRICKOWL_API_KEY", "")
    SECRETS_LOADED = True
except Exception:
    SECRETS_LOADED = False
    BO_KEY = ""

try:
    supabase  = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    DB_LOADED = True
except Exception:
    DB_LOADED = False

for key, default in [
    ("inventory", []), ("checked", set()), ("flagged", {}), ("notes", {}),
    ("loaded", False), ("auth", None), ("show_bulk_confirm", False),
    ("scan_query", ""), ("page", "dashboard"), ("price_cache", {}),
    ("price_results", []), ("screen_width", 1200),
    ("audit_mode", False), ("audit_mode_queue", []), ("audit_mode_index", 0),
    ("bin_audit_dates", {}),
    ("orders_data", []), ("pick_mode", False), ("pick_queue", []),
    ("pick_index", 0), ("picked_items", set()), ("fulfilled_orders", set()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

BASE = "https://api.bricklink.com/api/store/v1"

def make_auth(ck, cs, tv, ts):
    return OAuth1(ck, cs, tv, ts)

@st.cache_data(ttl=1800)
def fetch_inventory(_auth):
    r = requests.get(f"{BASE}/inventories", auth=_auth, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "API error"))
    return data["data"]

def update_quantity_on_bricklink(auth, inventory_id, new_qty, old_qty=0):
    delta = new_qty - old_qty
    r = requests.put(f"{BASE}/inventories/{inventory_id}", auth=auth,
                     json={"quantity": delta}, timeout=30)
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

def move_to_stockroom_a(auth, inventory_id):
    r = requests.put(f"{BASE}/inventories/{inventory_id}", auth=auth,
                     json={"is_stock_room": True, "stock_room_id": "A"}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200:
        raise ValueError(data.get("meta", {}).get("description", "Stockroom move failed"))
    return True

def fetch_price_guide(auth, part_no, color_id, condition="N"):
    r = requests.get(f"{BASE}/items/part/{part_no}/price", auth=auth,
                     params={"color_id": color_id, "guide_type": "sold",
                             "new_or_used": condition}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("meta", {}).get("code") != 200: return None
    pg = data.get("data", {})
    return {"avg_price": float(pg.get("avg_price", 0) or 0),
            "qty_avg_price": float(pg.get("qty_avg_price", 0) or 0)}

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

@st.cache_data(ttl=300)
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

def save_bin_audit_date(bin_name):
    if not DB_LOADED: return
    try:
        supabase.table("bin_audit_dates").upsert({
            "bin_name": bin_name,
            "last_audited": datetime.now().isoformat(),
        }, on_conflict="bin_name").execute()
    except Exception as e:
        st.warning(f"Could not save bin audit date: {e}")

@st.cache_data(ttl=300)
def load_bin_audit_dates():
    if not DB_LOADED: return {}
    try:
        result = supabase.table("bin_audit_dates").select("*").execute()
        return {r["bin_name"]: r["last_audited"][:10] for r in result.data}
    except Exception as e:
        st.warning(f"Could not load bin audit dates: {e}")
        return {}

def find_duplicates(inventory):
    from collections import defaultdict
    groups = defaultdict(list)
    for lot in inventory:
        pno      = lot.get("item", {}).get("no", "")
        color_id = lot.get("color_id", 0)
        key      = f"{pno}_{color_id}"
        groups[key].append(lot)
    return {k: v for k, v in groups.items() if len(v) > 1}

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

def img_with_qty(pno, color_id, qty):
    return (f'<div class="part-img-wrap">'
            f'<img class="part-img" src="https://img.bricklink.com/ItemImage/PN/{color_id}/{pno}.png" '
            f'onerror="this.style.opacity=\'0.15\'"/>'
            f'<span class="qty-badge">{qty}</span></div>')

def render_card_grid(lots, cols_count):
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
            if is_flagged:   b_cls,b_svg,b_lbl = "badge-flagged",icon("alert-circle",10,"#fb7185"),flag_info.get("reason","Flagged")
            elif is_found:   b_cls,b_svg,b_lbl = "badge-found",icon("check-circle",10,"#4ade80"),"Found"
            elif is_over:    b_cls,b_svg,b_lbl = "badge-over",icon("trending-up",10,"#a78bfa"),"Overpriced"
            elif is_low:     b_cls,b_svg,b_lbl = "badge-low",icon("alert-triangle",10,"#fb923c"),f"Low ({qty})"
            else:            b_cls = "badge-n" if cond == "New" else "badge-u"; b_svg,b_lbl = "",cond
            note_html = (f'<div class="part-meta" style="margin-top:4px;color:#f59e0b;">'
                         f'{icon("file-text",10,"#f59e0b")} {note_val[:20]}</div>' if note_val else "")
            with col:
                st.markdown(
                    f'<div class="{card_cls}">{img_with_qty(pno,color_id,qty)}'
                    f'<div class="part-name">{pno}</div>'
                    f'<div class="part-meta">{pname[:26] if not is_mobile else pname[:18]}</div>'
                    f'<div class="part-meta">{color}</div>'
                    f'<div class="part-meta">${price}</div>'
                    f'<span class="badge {b_cls}">{b_svg}{b_lbl}</span>{note_html}</div>',
                    unsafe_allow_html=True)
                if is_flagged:
                    if col.button("Unflag", key=f"unflag_{lid}", use_container_width=True):
                        del st.session_state.flagged[lid]; delete_progress(lid); st.rerun()
                elif is_found:
                    if col.button("Unmark", key=f"unmark_{lid}", use_container_width=True):
                        st.session_state.checked.discard(lid); delete_progress(lid); st.rerun()
                else:
                    if col.button("Found", key=f"found_{lid}_{row_start}", use_container_width=True):
                        st.session_state.checked.add(lid)
                        save_progress(lid, "checked", notes=st.session_state.notes.get(lid))
                        bin_name = lot.get("remarks","") or "(no remarks)"
                        bin_lots = [i for i in st.session_state.inventory
                                    if (i.get("remarks","") or "(no remarks)") == bin_name]
                        if all(i.get("inventory_id") in st.session_state.checked or
                               i.get("inventory_id") in st.session_state.flagged for i in bin_lots):
                            save_bin_audit_date(bin_name)
                            st.session_state.bin_audit_dates[bin_name] = datetime.now().strftime("%Y-%m-%d")
                        st.rerun()
                with col.expander("Note"):
                    new_note = st.text_area("Note", value=note_val, key=f"note_{lid}_{row_start}",
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
                                                          min_value=0, value=qty, step=1, key=f"qty_{lid}_{row_start}")
                            if st.button("Save flag", key=f"saveflag_{lid}", use_container_width=True):
                                st.session_state.flagged[lid] = {"reason":"Wrong qty","actual_qty":actual_qty}
                                save_progress(lid,"flagged","Wrong qty",actual_qty,None,
                                              st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth:
                                if st.button("Update on BrickLink", key=f"update_{lid}",
                                             use_container_width=True, type="primary"):
                                    try:
                                        update_quantity_on_bricklink(
                                            make_auth(*st.session_state.auth), lid, actual_qty, qty)
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

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(LOGO, width=200)

    if st.session_state.audit_mode:
        queue = st.session_state.audit_mode_queue
        idx   = st.session_state.audit_mode_index
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1a0a2e,#2d1060);border:1px solid #6d28d9;'
            f'border-radius:12px;padding:14px 16px;margin-bottom:12px;">'
            f'<div style="font-size:0.65rem;font-weight:700;color:#6d28d9;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-bottom:6px;">{icon("zap",12,"#6d28d9")} Audit Mode</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#a78bfa;">'
            f'{queue[idx] if idx < len(queue) else "Done"}</div>'
            f'<div style="font-size:0.7rem;color:#475569;margin-top:4px;">Bin {idx+1} of {len(queue)}</div>'
            f'</div>', unsafe_allow_html=True)
        if idx < len(queue):
            current_remarks = queue[idx]
            current_lots    = sorted(
                [i for i in st.session_state.inventory
                 if (i.get("remarks","") or "(no remarks)") == current_remarks],
                key=lambda x: (x.get("item",{}).get("no",""), x.get("color_name",""))
            )
            done_count  = sum(1 for i in current_lots
                              if i.get("inventory_id") in st.session_state.checked
                              or i.get("inventory_id") in st.session_state.flagged)
            total_count = len(current_lots)
            pct = int(done_count / total_count * 100) if total_count else 0
            st.progress(min(max(pct / 100, 0.0), 1.0))
            st.caption(f"{done_count}/{total_count} lots done · {pct}%")
        if st.button("Skip to Next Bin", use_container_width=True):
            st.session_state.audit_mode_index += 1; st.rerun()
        if st.button("Exit Audit Mode", use_container_width=True, type="primary"):
            st.session_state.audit_mode       = False
            st.session_state.audit_mode_queue = []
            st.session_state.audit_mode_index = 0
            st.session_state.page             = "dashboard"
            st.rerun()
    else:
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
        st.markdown(f'<div class="section-label">{ic("package")} Pages</div>', unsafe_allow_html=True)
        if st.button("Dashboard",        use_container_width=True): st.session_state.page = "dashboard"; st.rerun()
        if st.button("Browse Inventory", use_container_width=True): st.session_state.page = "browse";    st.rerun()
        if st.button("Summary",          use_container_width=True): st.session_state.page = "summary";   st.rerun()
        if st.button("Stockroom",        use_container_width=True): st.session_state.page = "stockroom"; st.rerun()
        if st.button("Duplicates",       use_container_width=True): st.session_state.page = "dupes";     st.rerun()
        if st.button("Audit History",    use_container_width=True): st.session_state.page = "history";   st.rerun()
        if st.button("Price Checker",    use_container_width=True): st.session_state.page = "prices";    st.rerun()
        if st.button("Pull Orders",      use_container_width=True): st.session_state.page = "orders";    st.rerun()

        st.divider()
        if st.session_state.page == "browse":
            st.markdown(f'<div class="section-label">{ic("sliders")} Filters</div>', unsafe_allow_html=True)
            search_term    = st.text_input("Search part # or name")
            cond_filter    = st.multiselect("Condition", ["New", "Used"], default=["New", "Used"])
            show_filter    = st.radio("Show", ["All", "Found", "Flagged", "Not yet found", "Low stock"])
            all_remarks    = sorted(set(i.get("remarks","") or "(no remarks)" for i in st.session_state.inventory))
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
            low_n     = sum(1 for i in st.session_state.inventory if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD)
            pct       = min(int(found_n / total * 100) if total else 0, 100)
            st.markdown(f'<div class="section-label">{ic("activity")} Progress</div>', unsafe_allow_html=True)
            st.progress(min(max(pct / 100, 0.0), 1.0))
            st.markdown(f"**{found_n}/{total}** found · {pct}%")
            if flagged_n:
                st.markdown(f'<span style="color:#fb7185;font-size:0.82rem;">{ic("alert-circle",13,"#fb7185")} {flagged_n} flagged</span>', unsafe_allow_html=True)
            if low_n:
                st.markdown(f'<span style="color:#fb923c;font-size:0.82rem;">{ic("alert-triangle",13,"#fb923c")} {low_n} low stock</span>', unsafe_allow_html=True)
            st.divider()
            pushable = get_pushable_flags()
            if pushable:
                if st.button(f"Push {len(pushable)} fixes to BrickLink", use_container_width=True, type="primary"):
                    st.session_state.show_bulk_confirm = True
            if st.button("Save Audit Snapshot", use_container_width=True):
                if save_audit_snapshot(): st.success("Snapshot saved")
            if st.button("Reset All Checkmarks", use_container_width=True):
                st.session_state.checked = set(); st.session_state.flagged = {}
                st.session_state.notes = {}; st.session_state.show_bulk_confirm = False
                clear_all_progress(); st.rerun()
            remaining = [i for i in st.session_state.inventory if i.get("inventory_id") not in st.session_state.checked]
            if remaining:
                st.download_button("Export Remaining CSV",
                    pd.DataFrame([{"Inventory ID": r.get("inventory_id",""),
                        "Part #": r.get("item",{}).get("no",""), "Name": r.get("item",{}).get("name",""),
                        "Color": r.get("color_name",""),
                        "Condition": "New" if r.get("new_or_used")=="N" else "Used",
                        "Quantity": r.get("quantity",0), "Price": r.get("unit_price",""),
                        "Bin": r.get("remarks",""),
                        "Notes": st.session_state.notes.get(r.get("inventory_id"),""),
                    } for r in remaining]).to_csv(index=False),
                    "remaining_lots.csv", "text/csv", use_container_width=True)
            flagged_lots = [{**i, **st.session_state.flagged.get(i.get("inventory_id"),{})}
                            for i in st.session_state.inventory if i.get("inventory_id") in st.session_state.flagged]
            if flagged_lots:
                st.download_button("Export Flagged CSV",
                    pd.DataFrame([{"Inventory ID": f.get("inventory_id",""),
                        "Part #": f.get("item",{}).get("no",""), "Name": f.get("item",{}).get("name",""),
                        "Color": f.get("color_name",""),
                        "Listed Qty": f.get("quantity",0), "Actual Qty": f.get("actual_qty",""),
                        "Current Bin": f.get("remarks",""), "Correct Bin": f.get("correct_bin",""),
                        "Flag Reason": f.get("reason",""),
                        "Notes": st.session_state.notes.get(f.get("inventory_id"),""),
                    } for f in flagged_lots]).to_csv(index=False),
                    "flagged_lots.csv", "text/csv", use_container_width=True)

# ── Load inventory ────────────────────────────────────────────────────────────
if not st.session_state.audit_mode:
    if 'load_btn' in dir() and load_btn:
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
                    st.session_state.checked         = checked
                    st.session_state.flagged         = flagged
                    st.session_state.notes           = notes
                    st.session_state.price_cache     = load_price_cache()
                    st.session_state.bin_audit_dates = load_bin_audit_dates()
                    if checked or flagged:
                        st.success(f"Restored {len(checked)} checked, {len(flagged)} flagged")
                    else:
                        st.info("Starting fresh.")
            st.session_state.page = "dashboard"
            st.rerun()

if not st.session_state.loaded:
    st.info("Click Load Inventory in the sidebar to get started.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AUDIT MODE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.audit_mode:
    queue = st.session_state.audit_mode_queue
    idx   = st.session_state.audit_mode_index
    if idx >= len(queue):
        st.markdown(
            f'<div class="audit-complete">'
            f'<div style="font-size:3rem;margin-bottom:12px;">🎉</div>'
            f'<div style="font-size:2rem;font-weight:800;color:#4ade80;margin-bottom:8px;">Audit Complete!</div>'
            f'<div style="font-size:1rem;color:#475569;">All {len(queue)} bins have been audited.</div>'
            f'</div>', unsafe_allow_html=True)
        st.stop()
    current_remarks = queue[idx]
    current_lots    = sorted(
        [i for i in st.session_state.inventory
         if (i.get("remarks","") or "(no remarks)") == current_remarks],
        key=lambda x: (x.get("item",{}).get("no",""), x.get("quantity",0))
    )
    done_count    = sum(1 for i in current_lots
                        if i.get("inventory_id") in st.session_state.checked
                        or i.get("inventory_id") in st.session_state.flagged)
    total_count   = len(current_lots)
    flagged_count = sum(1 for i in current_lots if i.get("inventory_id") in st.session_state.flagged)
    pct           = int(done_count / total_count * 100) if total_count else 0
    if total_count > 0 and done_count == total_count:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#0d2818,#112d1c);border:2px solid #2d6a4f;'
            f'border-radius:16px;padding:24px;text-align:center;margin-bottom:20px;">'
            f'<div style="font-size:1.8rem;margin-bottom:8px;">✅</div>'
            f'<div style="font-size:1.2rem;font-weight:800;color:#4ade80;">{current_remarks} complete!</div>'
            f'<div style="font-size:0.8rem;color:#475569;margin-top:6px;">'
            f'{total_count} lots · {flagged_count} flagged</div></div>', unsafe_allow_html=True)
        time.sleep(1.2)
        st.session_state.audit_mode_index += 1
        st.rerun()
    st.markdown(
        f'<div class="audit-mode-header">'
        f'<div class="audit-mode-sub">{icon("zap",14,"#6d28d9")} Audit Mode · Bin {idx+1} of {len(queue)}</div>'
        f'<div class="audit-mode-title">{current_remarks}</div>'
        f'<div style="margin-top:12px;">', unsafe_allow_html=True)
    st.progress(min(max(pct / 100, 0.0), 1.0))
    st.markdown(
        f'<div style="font-size:0.75rem;color:#6d7a8f;margin-top:6px;">'
        f'{done_count}/{total_count} lots done · {pct}%'
        f'{" · "+str(flagged_count)+" flagged" if flagged_count else ""}'
        f'</div></div></div>', unsafe_allow_html=True)
    visible_lots = [i for i in current_lots if i.get("inventory_id") not in st.session_state.checked]
    render_card_grid(visible_lots, COLS)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":
    inv       = st.session_state.inventory
    total     = len(inv)
    found_n   = len(st.session_state.checked)
    flagged_n = len(st.session_state.flagged)
    low_n     = sum(1 for i in inv if 0 < i.get("quantity",0) <= LOW_STOCK_THRESHOLD)
    pct       = min(int(found_n / total * 100) if total else 0, 100)
    n_bins    = len(set(i.get("remarks","") or "(no remarks)" for i in inv))
    dupes     = find_duplicates(inv)

    st.markdown(
        f'<div style="padding:24px 0 16px 0;">'
        f'<div style="font-size:0.7rem;font-weight:700;color:#6d28d9;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:6px;">Welcome back</div>'
        f'<div style="font-size:2.2rem;font-weight:800;color:#e2e8f0;letter-spacing:-0.03em;'
        f'line-height:1.1;">Brick Audit</div>'
        f'<div style="font-size:0.85rem;color:#475569;margin-top:6px;">'
        f'{total:,} lots across {n_bins} bins · {pct}% audited</div>'
        f'</div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Inventory", key="refresh_inv"):
        fetch_inventory.clear()
        st.session_state.inventory = fetch_inventory(make_auth(*st.session_state.auth))
        st.rerun()

    s1,s2,s3,s4,s5 = st.columns(5)
    for col, val, label, color in [
        (s1, f"{pct}%",      "Audited",    "#a78bfa"),
        (s2, f"{found_n}",   "Found",      "#4ade80"),
        (s3, f"{flagged_n}", "Flagged",    "#fb7185"),
        (s4, f"{low_n}",     "Low Stock",  "#fb923c"),
        (s5, f"{len(dupes)}","Duplicates", "#60a5fa"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card" style="padding:14px 10px;">'
                f'<div class="metric-value" style="font-size:1.6rem;color:{color}">{val}</div>'
                f'<div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.progress(min(max(pct / 100, 0.0), 1.0))
    st.write("")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1a0a2e,#2d1060);border:1px solid #6d28d9;'
        f'border-radius:20px;padding:24px 28px;margin-bottom:20px;'
        f'box-shadow:0 4px 24px rgba(109,40,217,0.35);">'
        f'<div style="font-size:0.7rem;font-weight:700;color:#6d28d9;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:8px;">{icon("zap",14,"#6d28d9")} Start Auditing</div>'
        f'<div style="font-size:1.3rem;font-weight:800;color:#f5f3ff;margin-bottom:4px;">Audit Mode</div>'
        f'<div style="font-size:0.8rem;color:#a78bfa;margin-bottom:16px;">'
        f'Walk bin-by-bin through your stockroom. Auto-advances when each bin is complete.</div>'
        f'</div>', unsafe_allow_html=True)

    am_col1, am_col2, am_col3 = st.columns([2,2,1])
    with am_col1:
        zone_choice = st.selectbox("Zone", ["All zones","Bins only","Tubs only","Trays only","White Drawers only"], key="dash_zone")
        zone_map    = {"All zones":"all","Bins only":"bin","Tubs only":"tub","Trays only":"tray","White Drawers only":"wd"}
    with am_col2:
        zone_key = zone_map[zone_choice]
        all_remarks_sorted = sorted(set(i.get("remarks","") or "(no remarks)" for i in inv))
        filtered_remarks   = [r for r in all_remarks_sorted if zone_key=="all" or detect_zone(r)==zone_key]
        with st.form("audit_start_form"):
            start_from = st.selectbox("Start from bin", filtered_remarks, key="dash_start") if filtered_remarks else None
            submitted = st.form_submit_button("Start Audit", use_container_width=True, type="primary")
            if submitted and start_from:
                start_idx = filtered_remarks.index(start_from)
                st.session_state.audit_mode       = True
                st.session_state.audit_mode_queue = filtered_remarks
                st.session_state.audit_mode_index = start_idx
                st.rerun()
    with am_col3:
        st.write("")
        
    st.divider()
    st.markdown(f'<div style="font-size:0.7rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">Quick Access</div>', unsafe_allow_html=True)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    actions = [
        (c1, "browse",    "package",  "#a78bfa", "Browse Inventory", f"{total:,} lots"),
        (c2, "stockroom", "grid",     "#60a5fa", "Stockroom",        f"{n_bins} bins"),
        (c3, "dupes",     "copy",     "#fb923c", "Duplicates",       f"{len(dupes)} groups"),
        (c4, "prices",    "tag",      "#4ade80", "Price Checker",    "Check market rates"),
        (c5, "orders",    "box",      "#f472b6", "Pull Orders",      "Pick open orders"),
        (c6, "history",   "calendar", "#94a3b8", "Audit History",    "View past audits"),
    ]
    for col, page, ico, color, title, sub in actions:
        with col:
            st.markdown(
                f'<div class="action-card">'
                f'<div style="margin-bottom:10px;">{icon(ico,28,color)}</div>'
                f'<div class="action-card-title">{title}</div>'
                f'<div class="action-card-sub">{sub}</div>'
                f'</div>', unsafe_allow_html=True)
            if st.button(title, key=f"dash_{page}", use_container_width=True):
                st.session_state.page = page; st.rerun()

    history = load_audit_history()
    if history:
        st.divider()
        last = history[0]
        last_pct = int(last["total_checked"]/last["total_lots"]*100) if last["total_lots"] else 0
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#161b27,#1a2235);border:1px solid #1e2d45;'
            f'border-radius:14px;padding:14px 20px;">'
            f'<div style="font-size:0.65rem;font-weight:700;color:#475569;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-bottom:6px;">{icon("calendar",12,"#475569")} Last Audit Snapshot</div>'
            f'<div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;">'
            f'{last["audit_date"][:10]} · {last_pct}% complete · {last["total_flagged"]} flagged</div>'
            f'</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "summary":
    st.markdown(f'{icon("bar-chart-2",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Audit Summary</span>', unsafe_allow_html=True)
    st.write("")
    inv, checked, flagged = st.session_state.inventory, st.session_state.checked, st.session_state.flagged
    total=len(inv); n_checked=len(checked); n_flagged=len(flagged)
    pct=int(n_checked/total*100) if total else 0
    low_lots=[i for i in inv if 0<i.get("quantity",0)<=LOW_STOCK_THRESHOLD]
    val_checked  =sum(float(i.get("unit_price",0) or 0)*int(i.get("quantity",0) or 0) for i in inv if i.get("inventory_id") in checked)
    val_unchecked=sum(float(i.get("unit_price",0) or 0)*int(i.get("quantity",0) or 0) for i in inv if i.get("inventory_id") not in checked)
    c1,c2,c3,c4=st.columns(4)
    for col,val,label,color in [(c1,f"{pct}%","Audit Complete","#a78bfa"),(c2,f"{n_checked}/{total}","Lots Found","#a78bfa"),(c3,str(n_flagged),"Lots Flagged","#fb7185"),(c4,str(len(low_lots)),"Low Stock","#fb923c")]:
        with col: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown(f'{icon("dollar-sign",18,"#a78bfa")} <span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;vertical-align:middle;">Inventory Value</span>', unsafe_allow_html=True)
    st.write("")
    v1,v2,v3=st.columns(3)
    for col,val,label,color in [(v1,f"${val_checked:,.2f}","Value Checked","#4ade80"),(v2,f"${val_unchecked:,.2f}","Not Yet Checked","#fb7185"),(v3,f"${val_checked+val_unchecked:,.2f}","Total Store Value","#a78bfa")]:
        with col: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown(f'{icon("layers",18,"#a78bfa")} <span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;vertical-align:middle;">Progress by Bin</span>', unsafe_allow_html=True)
    st.write("")
    bin_data=[]
    for bn,lots in groupby(sorted(inv,key=lambda x:x.get("remarks","") or ""),key=lambda x:x.get("remarks","") or "(no remarks)"):
        lots=list(lots); bt=len(lots)
        bc=sum(1 for x in lots if x.get("inventory_id") in checked)
        bf=sum(1 for x in lots if x.get("inventory_id") in flagged)
        bv=sum(float(x.get("unit_price",0) or 0)*int(x.get("quantity",0) or 0) for x in lots)
        last_aud=st.session_state.bin_audit_dates.get(bn,"—")
        bin_data.append({"Bin":bn,"Total":bt,"Found":bc,"Flagged":bf,"Remaining":bt-bc-bf,"% Done":int(bc/bt*100) if bt else 0,"Value":f"${bv:,.2f}","Last Audited":last_aud})
    st.dataframe(pd.DataFrame(bin_data),use_container_width=True,hide_index=True)
    if n_flagged:
        st.divider()
        st.markdown(f'{icon("flag",18,"#fb7185")} <span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;vertical-align:middle;">Flagged Lots</span>', unsafe_allow_html=True)
        st.write("")
        st.dataframe(pd.DataFrame([{"Part #":i.get("item",{}).get("no",""),"Name":i.get("item",{}).get("name",""),"Color":i.get("color_name",""),"Bin":i.get("remarks",""),"Listed Qty":i.get("quantity",0),"Actual Qty":flagged[i.get("inventory_id")].get("actual_qty",""),"Correct Bin":flagged[i.get("inventory_id")].get("correct_bin",""),"Reason":flagged[i.get("inventory_id")].get("reason",""),"Notes":st.session_state.notes.get(i.get("inventory_id"),""),} for i in inv if i.get("inventory_id") in flagged]),use_container_width=True,hide_index=True)
    if low_lots:
        st.divider()
        st.markdown(f'{icon("alert-triangle",18,"#fb923c")} <span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;vertical-align:middle;">Low Stock Lots</span>', unsafe_allow_html=True)
        st.write("")
        st.dataframe(pd.DataFrame([{"Part #":i.get("item",{}).get("no",""),"Name":i.get("item",{}).get("name",""),"Color":i.get("color_name",""),"Bin":i.get("remarks",""),"Quantity":i.get("quantity",0),"Price":f"${i.get('unit_price','')}",} for i in low_lots]),use_container_width=True,hide_index=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STOCKROOM
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "stockroom":
    st.markdown(f'{icon("grid",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Stockroom</span>', unsafe_allow_html=True)
    st.write("")
    inv=st.session_state.inventory
    bins_lots =[i for i in inv if detect_zone(i.get("remarks",""))=="bin"]
    tubs_lots =[i for i in inv if detect_zone(i.get("remarks",""))=="tub"]
    trays_lots=[i for i in inv if detect_zone(i.get("remarks",""))=="tray"]
    wd_lots   =[i for i in inv if detect_zone(i.get("remarks",""))=="wd"]
    def zone_low(lots): return sum(1 for i in lots if 0<i.get("quantity",0)<=LOW_STOCK_THRESHOLD)
    def zone_pct(lots):
        if not lots: return 0
        return int(sum(1 for i in lots if i.get("inventory_id") in st.session_state.checked)/len(lots)*100)
    z1,z2,z3,z4=st.columns(4)
    for col,label,lots,color in [(z1,"Bins (AA–AT)",bins_lots,"#a78bfa"),(z2,"Tubs (01–28)",tubs_lots,"#60a5fa"),(z3,"Trays (01–26)",trays_lots,"#34d399"),(z4,"White Drawers",wd_lots,"#f472b6")]:
        with col:
            low=zone_low(lots); pct=zone_pct(lots)
            st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{len(lots)}</div><div class="metric-label">{label}</div><div style="font-size:0.7rem;color:#475569;margin-top:6px;">{pct}% audited{" · "+str(low)+" low stock" if low else ""}</div></div>', unsafe_allow_html=True)
    st.divider()
    tab_bins,tab_tubs,tab_trays,tab_wd=st.tabs(["Bins","Tubs","Trays","White Drawers"])
    def render_zone_tab(zone_lots,zone_key,zone_label_singular,select_label,all_options,header_color,header_icon):
        selected=st.selectbox(select_label,["All "+zone_label_singular+"s"]+all_options,key=f"stockroom_{zone_key}_select")
        filtered=zone_lots if selected.startswith("All") else [i for i in zone_lots if (get_bin_code(i.get("remarks",""))==selected if zone_key=="bin" else get_zone_number(i.get("remarks",""))==selected)]
        if not filtered: st.info("No lots found."); return
        total_f=len(filtered)
        found_f=sum(1 for i in filtered if i.get("inventory_id") in st.session_state.checked)
        flagged_f=sum(1 for i in filtered if i.get("inventory_id") in st.session_state.flagged)
        low_f=[i for i in filtered if 0<i.get("quantity",0)<=LOW_STOCK_THRESHOLD]
        m1,m2,m3,m4=st.columns(4)
        for col,val,label,color in [(m1,str(total_f),"Total Lots",header_color),(m2,str(found_f),"Found","#4ade80"),(m3,str(flagged_f),"Flagged","#fb7185"),(m4,str(len(low_f)),"Low Stock","#fb923c")]:
            with col: st.markdown(f'<div class="metric-card" style="padding:12px 8px;"><div class="metric-value" style="font-size:1.4rem;color:{color}">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
        st.write("")
        for group_name,group_items in groupby(sorted(filtered,key=lambda x:x.get("remarks","") or ""),key=lambda x:x.get("remarks","") or f"(no {zone_label_singular})"):
            group_lots=list(group_items)
            bin_found=sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
            bin_flagged=sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
            bin_pct=int(bin_found/len(group_lots)*100) if group_lots else 0
            flagged_note=(f'&nbsp;&nbsp;{icon("alert-circle",11,"#fb7185")}<span style="font-size:0.7rem;color:#fb7185;">{bin_flagged} flagged</span>' if bin_flagged else "")
            last_audited=st.session_state.bin_audit_dates.get(group_name,"")
            audited_html=f'&nbsp;&nbsp;<span style="color:#2d6a4f;font-size:0.68rem;">✓ audited {last_audited}</span>' if last_audited else ""
            ct,cb=st.columns([4,1])
            with ct: st.markdown(f'<div class="bin-header" style="border-left-color:{header_color};"><p class="bin-title" style="color:{header_color};">{icon(header_icon,14,header_color)} {group_name}</p><p class="bin-stats">{bin_found}/{len(group_lots)} found · {bin_pct}%{flagged_note}{audited_html}</p></div>', unsafe_allow_html=True)
            with cb:
                st.write(""); st.write("")
                if st.button("Mark all found",key=f"{zone_key}mkall_{group_name}",use_container_width=True):
                    for x in group_lots:
                        lid=x.get("inventory_id"); st.session_state.checked.add(lid)
                        save_progress(lid,"checked",notes=st.session_state.notes.get(lid))
                    save_bin_audit_date(group_name)
                    st.session_state.bin_audit_dates[group_name]=datetime.now().strftime("%Y-%m-%d")
                    st.rerun()
            render_card_grid(group_lots,COLS); st.divider()
        if low_f:
            st.markdown(f'<div class="restock-table-header"><p class="restock-title">{icon("alert-triangle",16,"#fb923c")} Restock List — {len(low_f)} lots need attention</p></div>', unsafe_allow_html=True)
            restock_df=pd.DataFrame([{"Part #":i.get("item",{}).get("no",""),"Name":i.get("item",{}).get("name",""),"Color":i.get("color_name",""),"Location":i.get("remarks",""),"Qty Left":i.get("quantity",0),"Price":f"${i.get('unit_price','')}"}for i in sorted(low_f,key=lambda x:x.get("remarks","") or "")])
            st.dataframe(restock_df,use_container_width=True,hide_index=True)
            st.download_button("Export Restock List CSV",restock_df.to_csv(index=False),f"restock_{zone_key}.csv","text/csv",use_container_width=True)
    with tab_bins:
        all_bin_codes=sorted(set(get_bin_code(i.get("remarks","")) for i in bins_lots if get_bin_code(i.get("remarks",""))))
        render_zone_tab(bins_lots,"bin","bin","Select bin",all_bin_codes,"#a78bfa","archive")
    with tab_tubs:
        all_tub_nums=sorted(set(get_zone_number(i.get("remarks","")) for i in tubs_lots if get_zone_number(i.get("remarks",""))),key=lambda x:int(x) if x.isdigit() else 0)
        render_zone_tab(tubs_lots,"tub","tub","Select tub",all_tub_nums,"#60a5fa","box")
    with tab_trays:
        all_tray_nums=sorted(set(get_zone_number(i.get("remarks","")) for i in trays_lots if get_zone_number(i.get("remarks",""))),key=lambda x:int(x) if x.isdigit() else 0)
        render_zone_tab(trays_lots,"tray","tray","Select tray",all_tray_nums,"#34d399","layers")
    with tab_wd:
        all_wd_nums=sorted(set(i.get("remarks","").strip() for i in wd_lots if i.get("remarks","")))
        render_zone_tab(wd_lots,"wd","drawer","Select drawer",all_wd_nums,"#f472b6","inbox")
    st.stop()
# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DUPLICATES
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dupes":
    st.markdown(f'{icon("copy",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Duplicate Lots</span>', unsafe_allow_html=True)
    st.caption("Parts with the same part # and color listed in more than one bin.")
    st.write("")
    dupes=find_duplicates(st.session_state.inventory)
    if not dupes: st.success("No duplicates found — your inventory is clean!"); st.stop()
    total_dup_lots=sum(len(v) for v in dupes.values())
    all_dup_lids=[lot.get("inventory_id") for lots in dupes.values() for lot in lots]
    def run_stockroom_move(lids):
        if not st.session_state.auth: st.error("No credentials loaded."); return
        auth=make_auth(*st.session_state.auth); success=[]; failed=[]
        pb=st.progress(0); txt=st.empty()
        for i,lid in enumerate(lids):
            txt.text(f"Moving {i+1}/{len(lids)} to Stockroom A…")
            try:
                move_to_stockroom_a(auth,lid); success.append(lid)
                for lot in st.session_state.inventory:
                    if lot.get("inventory_id")==lid:
                        lot["is_stock_room"]=True; lot["stock_room_id"]="A"
            except Exception as e: failed.append({"lid":lid,"error":str(e)})
            pb.progress((i+1)/len(lids)); time.sleep(0.2)
        txt.empty(); pb.empty()
        if success: st.success(f"✅ {len(success)} lot(s) moved to Stockroom A")
        for f in failed: st.error(f"Failed for lot {f['lid']}: {f['error']}")
    d1,d2,d3=st.columns(3)
    with d1: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#a78bfa">{len(dupes)}</div><div class="metric-label">Duplicate Groups</div></div>', unsafe_allow_html=True)
    with d2: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#fb923c">{total_dup_lots}</div><div class="metric-label">Affected Lots</div></div>', unsafe_allow_html=True)
    with d3:
        in_stockroom=sum(1 for lots in dupes.values() for lot in lots if lot.get("is_stock_room"))
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#60a5fa">{in_stockroom}</div><div class="metric-label">Already in Stockroom</div></div>', unsafe_allow_html=True)
    st.write("")
    not_yet_moved=[lid for lid in all_dup_lids if not next((lot.get("is_stock_room") for lot in st.session_state.inventory if lot.get("inventory_id")==lid),False)]
    if not_yet_moved:
        st.markdown(f'<div style="background:linear-gradient(135deg,#1a0a2e,#2d1060);border:1px solid #6d28d9;border-radius:14px;padding:16px 20px;margin-bottom:16px;"><div style="font-size:0.85rem;font-weight:600;color:#a78bfa;margin-bottom:6px;">{icon("archive",16,"#a78bfa")} Move all duplicate lots to Stockroom A</div><div style="font-size:0.72rem;color:#475569;">Hides them from buyers until you resolve each duplicate during your next audit.</div></div>', unsafe_allow_html=True)
        if st.button(f"Move all {len(not_yet_moved)} lots to Stockroom A",type="primary",use_container_width=True,key="move_all_stockroom"):
            run_stockroom_move(not_yet_moved); st.rerun()
    else:
        st.success("All duplicate lots are already in Stockroom A.")
    st.divider()
    dup_search=st.text_input("Filter by part # or name",placeholder="e.g. 3001 or Brick…",key="dup_search")
    export_rows=[]
    for key,lots in dupes.items():
        for lot in lots:
            export_rows.append({"Part #":lot.get("item",{}).get("no",""),"Name":lot.get("item",{}).get("name",""),"Color":lot.get("color_name",""),"Bin":lot.get("remarks",""),"Qty":lot.get("quantity",0),"Price":lot.get("unit_price",""),"Condition":"New" if lot.get("new_or_used")=="N" else "Used","In Stockroom":"Yes" if lot.get("is_stock_room") else "No",})
    if export_rows:
        st.download_button("Export Duplicates CSV",pd.DataFrame(export_rows).to_csv(index=False),"duplicates.csv","text/csv",use_container_width=False)
    st.divider()
    shown=0
    for key,lots in sorted(dupes.items(),key=lambda x:-len(x[1])):
        pno=lots[0].get("item",{}).get("no",""); pname=lots[0].get("item",{}).get("name","")
        color=lots[0].get("color_name",""); color_id=lots[0].get("color_id",0)
        if dup_search:
            q=dup_search.lower()
            if q not in pno.lower() and q not in pname.lower(): continue
        shown+=1
        bins_list=[l.get("remarks","") or "(no bin)" for l in lots]
        group_lids=[l.get("inventory_id") for l in lots]
        group_not_moved=[lid for lid in group_lids if not next((lot.get("is_stock_room") for lot in st.session_state.inventory if lot.get("inventory_id")==lid),False)]
        st.markdown(f'<div class="dup-group"><div class="dup-group-header"><img class="dup-part-img" src="https://img.bricklink.com/ItemImage/PN/{color_id}/{pno}.png" onerror="this.style.opacity=\'0.15\'"/><div class="dup-part-info"><div class="dup-part-name">{pno} — {pname}</div><div class="dup-part-sub">{color} · {len(lots)} lots in {len(set(bins_list))} bins</div></div></div>', unsafe_allow_html=True)
        for lot in sorted(lots,key=lambda x:x.get("remarks","") or ""):
            lid=lot.get("inventory_id"); remarks=lot.get("remarks","") or "(no bin)"
            qty=lot.get("quantity",0); price=lot.get("unit_price","")
            cond="New" if lot.get("new_or_used")=="N" else "Used"
            in_stock_a=lot.get("is_stock_room") and lot.get("stock_room_id")=="A"
            is_flagged=lid in st.session_state.flagged; is_found=lid in st.session_state.checked
            if in_stock_a: status_html='<span style="color:#60a5fa;font-size:0.7rem;font-weight:700;">● Stockroom A</span>'
            elif is_flagged: status_html='<span style="color:#fb7185;font-size:0.7rem;font-weight:600;">● Flagged</span>'
            elif is_found: status_html='<span style="color:#4ade80;font-size:0.7rem;font-weight:600;">● Found</span>'
            else: status_html='<span style="color:#475569;font-size:0.7rem;">● Active</span>'
            st.markdown(f'<div class="dup-bin-row"><span class="dup-bin-name">{remarks}</span><span class="dup-bin-qty">×{qty}</span><span class="dup-bin-price">${price}</span><span style="color:#475569;font-size:0.72rem;">{cond}</span>{status_html}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        btn_col,flag_col=st.columns([1,1])
        with btn_col:
            if group_not_moved:
                if st.button(f"Move group to Stockroom A ({len(group_not_moved)} lots)",key=f"stockroom_{key}",use_container_width=True):
                    run_stockroom_move(group_not_moved); st.rerun()
            else:
                st.markdown('<div style="font-size:0.72rem;color:#60a5fa;padding:8px 0;">✓ All in Stockroom A</div>', unsafe_allow_html=True)
        with flag_col:
            with st.expander("Flag a lot in this group"):
                lot_labels=[f"{l.get('remarks','(no bin)')} — ×{l.get('quantity',0)} @ ${l.get('unit_price','')}" for l in lots]
                selected_idx=st.selectbox("Select lot to flag",range(len(lots)),format_func=lambda i:lot_labels[i],key=f"dup_sel_{key}")
                selected_lot=lots[selected_idx]; lid_s=selected_lot.get("inventory_id")
                qty_s=selected_lot.get("quantity",0); rem_s=selected_lot.get("remarks","")
                reason_d=st.radio("Issue",["Wrong bin","Wrong quantity","Wrong part in bin"],key=f"dup_reason_{key}")
                if reason_d=="Wrong bin":
                    correct_bin_d=st.text_input(f"Correct bin (current: {rem_s or 'none'})",key=f"dup_bin_{key}")
                    if st.button("Save flag",key=f"dup_saveflag_{key}",use_container_width=True):
                        st.session_state.flagged[lid_s]={"reason":"Wrong bin","correct_bin":correct_bin_d}
                        save_progress(lid_s,"flagged","Wrong bin",None,correct_bin_d,st.session_state.notes.get(lid_s)); st.rerun()
                elif reason_d=="Wrong quantity":
                    actual_qty_d=st.number_input(f"Actual qty (listed: {qty_s})",min_value=0,value=qty_s,key=f"dup_qty_{key}")
                    if st.button("Save flag",key=f"dup_saveflag_{key}",use_container_width=True):
                        st.session_state.flagged[lid_s]={"reason":"Wrong qty","actual_qty":actual_qty_d}
                        save_progress(lid_s,"flagged","Wrong qty",actual_qty_d,None,st.session_state.notes.get(lid_s)); st.rerun()
                else:
                    if st.button("Save flag",key=f"dup_saveflag_{key}",use_container_width=True):
                        st.session_state.flagged[lid_s]={"reason":"Wrong part"}
                        save_progress(lid_s,"flagged","Wrong part",None,None,st.session_state.notes.get(lid_s)); st.rerun()
    if shown==0: st.info("No duplicates match your search.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUDIT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "history":
    st.markdown(f'{icon("calendar",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Audit History</span>', unsafe_allow_html=True)
    st.write("")
    history=load_audit_history()
    if not history: st.info("No snapshots yet. Click Save Audit Snapshot in the sidebar."); st.stop()
    st.dataframe(pd.DataFrame([{"Date":h["audit_date"][:16].replace("T"," "),"Total Lots":h["total_lots"],"Checked":h["total_checked"],"Flagged":h["total_flagged"],"% Complete":int(h["total_checked"]/h["total_lots"]*100) if h["total_lots"] else 0,"Value Checked":f"${h['total_value_checked']:,.2f}","Value Remaining":f"${h['total_value_unchecked']:,.2f}",} for h in history]),use_container_width=True,hide_index=True)
    if len(history)>1:
        st.divider()
        st.markdown(f'{icon("activity",18,"#a78bfa")} <span style="font-size:1.1rem;font-weight:700;color:#cbd5e1;vertical-align:middle;">Completion Over Time</span>', unsafe_allow_html=True)
        st.write("")
        st.line_chart(pd.DataFrame([{"Date":h["audit_date"][:10],"% Complete":int(h["total_checked"]/h["total_lots"]*100) if h["total_lots"] else 0,"Flagged":h["total_flagged"],} for h in reversed(history)]).set_index("Date"))
    st.divider()
    audit_labels=[h["audit_date"][:16].replace("T"," ") for h in history]
    selected_h=history[audit_labels.index(st.selectbox("Drill into an audit",audit_labels))]
    pct=int(selected_h["total_checked"]/selected_h["total_lots"]*100) if selected_h["total_lots"] else 0
    c1,c2,c3=st.columns(3)
    for col,val,label,color in [(c1,f"{pct}%","Complete","#a78bfa"),(c2,str(selected_h["total_flagged"]),"Flagged","#fb7185"),(c3,f"${selected_h['total_value_checked']:,.2f}","Value Checked","#4ade80")]:
        with col: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    discreps=selected_h.get("discrepancies",[])
    if discreps:
        st.markdown(f"**{len(discreps)} discrepancies:**")
        st.dataframe(pd.DataFrame(discreps),use_container_width=True,hide_index=True)
    else: st.success("No discrepancies recorded")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRICE CHECKER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "prices":
    st.markdown(f'{icon("tag",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Price Checker</span>', unsafe_allow_html=True)
    st.caption(f"Flags lots priced more than {PRICE_FLAG_PCT}% above BrickLink market average. Your strategy: +{int((MARKUP-1)*100)}% markup, {int((1-SALE_DISCOUNT)*100)}% sale = {int((MARKUP*SALE_DISCOUNT-1)*100):+d}% vs market.")
    inv=st.session_state.inventory
    col_a,col_b,col_c=st.columns([2,2,1])
    with col_a:
        all_remarks=sorted(set(i.get("remarks","") or "(no remarks)" for i in inv))
        bin_select=st.selectbox("Check prices for bin",["All bins"]+all_remarks)
    with col_b: batch_size=st.selectbox("Batch size",[25,50,100],index=0)
    with col_c: force_refresh=st.checkbox("Force refresh")
    lots_to_check=inv if bin_select=="All bins" else [i for i in inv if (i.get("remarks","") or "(no remarks)")==bin_select]
    cached_count=sum(1 for i in lots_to_check if f"{i.get('item',{}).get('no','')}_{i.get('color_id',0)}_N" in st.session_state.price_cache)
    st.caption(f"{len(lots_to_check)} lots selected · {cached_count} cached · {len(lots_to_check)-cached_count} need fetching")
    if st.button(f"Fetch prices — next {batch_size} uncached lots",type="primary",use_container_width=True):
        auth,to_fetch=make_auth(*st.session_state.auth),[]
        for lot in lots_to_check:
            pno,color_id=lot.get("item",{}).get("no",""),lot.get("color_id",0)
            if force_refresh or f"{pno}_{color_id}_N" not in st.session_state.price_cache: to_fetch.append(lot)
            if len(to_fetch)>=batch_size: break
        if not to_fetch: st.success("All cached! Check Force refresh to re-fetch.")
        else:
            pb,st_txt=st.progress(0),st.empty()
            for idx,lot in enumerate(to_fetch):
                pno,color_id=lot.get("item",{}).get("no",""),lot.get("color_id",0)
                st_txt.text(f"Fetching {idx+1}/{len(to_fetch)}: {pno}…")
                try:
                    pg=fetch_price_guide(auth,pno,color_id,"N")
                    if pg:
                        st.session_state.price_cache[f"{pno}_{color_id}_N"]=pg
                        save_price_to_cache(pno,color_id,"N",pg["avg_price"],pg["qty_avg_price"])
                except Exception: pass
                pb.progress((idx+1)/len(to_fetch)); time.sleep(0.3)
            st_txt.text("Done!"); st.success(f"Fetched {len(to_fetch)} lots"); st.rerun()
    st.divider()
    rows=[]
    for lot in lots_to_check:
        pno,color_id=lot.get("item",{}).get("no",""),lot.get("color_id",0)
        cache_hit=st.session_state.price_cache.get(f"{pno}_{color_id}_N")
        if not cache_hit: continue
        my_price=float(lot.get("unit_price",0) or 0); mkt_avg=float(cache_hit.get("avg_price",0) or 0)
        if mkt_avg==0: continue
        pct_diff=((my_price-mkt_avg)/mkt_avg)*100
        rows.append({"lot":lot,"pno":pno,"name":lot.get("item",{}).get("name",""),"color":lot.get("color_name",""),"bin":lot.get("remarks",""),"my_price":my_price,"mkt_avg":mkt_avg,"target":round(mkt_avg*MARKUP*SALE_DISCOUNT,4),"pct_diff":pct_diff,"flagged":pct_diff>PRICE_FLAG_PCT,"lid":lot.get("inventory_id")})
    if rows:
        flagged_rows=[r for r in rows if r["flagged"]]; ok_rows=[r for r in rows if not r["flagged"]]
        tab1,tab2=st.tabs([f"Overpriced ({len(flagged_rows)})",f"OK ({len(ok_rows)})"])
        def render_price_table(price_rows,tab):
            with tab:
                if not price_rows: st.success("Nothing here!"); return
                st.dataframe(pd.DataFrame([{"Part #":r["pno"],"Name":r["name"],"Color":r["color"],"Bin":r["bin"],"My Price":f"${r['my_price']:.4f}","Market Avg":f"${r['mkt_avg']:.4f}","% vs Market":f"{r['pct_diff']:+.1f}%","Suggested":f"${r['target']:.4f}"}for r in price_rows]),use_container_width=True,hide_index=True)
                st.divider(); st.markdown("**Update a price**")
                part_labels=[f"{r['pno']} — {r['name']} ({r['color']})" for r in price_rows]
                selected_row=price_rows[part_labels.index(st.selectbox("Select lot",part_labels,key=f"sel_{id(tab)}"))]
                c1,c2=st.columns([2,1])
                with c1: new_price=st.number_input(f"New price (market: ${selected_row['mkt_avg']:.4f}, suggested: ${selected_row['target']:.4f})",min_value=0.0001,value=float(selected_row["target"]),format="%.4f",key=f"newprice_{selected_row['lid']}")
                with c2:
                    st.write(""); st.write("")
                    if st.button("Update on BrickLink",key=f"updateprice_{selected_row['lid']}",use_container_width=True,type="primary"):
                        try:
                            update_price_on_bricklink(make_auth(*st.session_state.auth),selected_row["lid"],new_price)
                            for x in st.session_state.inventory:
                                if x.get("inventory_id")==selected_row["lid"]: x["unit_price"]=str(new_price)
                            st.success(f"Price updated to ${new_price:.4f}"); st.rerun()
                        except Exception as e: st.error(f"Failed: {e}")
        render_price_table(flagged_rows,tab1); render_price_table(ok_rows,tab2)
        st.divider()
        st.download_button("Download Price Report CSV",pd.DataFrame([{"Part #":r["pno"],"Name":r["name"],"Color":r["color"],"Bin":r["bin"],"My Price":r["my_price"],"Market Avg":r["mkt_avg"],"% vs Market":round(r["pct_diff"],1),"Suggested":r["target"],"Flagged":"Yes" if r["flagged"] else "No"}for r in rows]).to_csv(index=False),"price_report.csv","text/csv",use_container_width=True)
    else: st.info("No cached prices yet — fetch some lots above to see results.")
    st.stop()
# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ORDERS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "orders":
    st.markdown(f'{icon("box",22,"#f472b6")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Pull Orders</span>', unsafe_allow_html=True)
    st.write("")

    ORDER_COLORS = ["#f472b6","#60a5fa","#4ade80","#fb923c","#a78bfa","#f87171","#34d399","#fbbf24"]

    @st.cache_data(ttl=60)
    def fetch_orders(_auth):
        r = requests.get(f"{BASE}/orders", auth=_auth,
                         params={"direction":"in"},
                         timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("meta",{}).get("code") != 200:
            raise ValueError(data.get("meta",{}).get("description","API error"))
        return data.get("data",[])

    @st.cache_data(ttl=60)
    def fetch_brickowl_orders(_key):
        if not _key: return []
        r = requests.get("https://api.brickowl.com/v1/order/list",
                         params={"key": _key},
                         timeout=30)
        r.raise_for_status()
        data = r.json()
        all_bo = data if isinstance(data, list) else data.get("orders", [])
        KEEP_BO = {"payment_received", "processing", "paid"}
        orders = [o for o in all_bo if o.get("status","").lower() in KEEP_BO]
        result = []
        for order in orders:
            oid = order.get("order_id")
            # fetch order items
            r2 = requests.get("https://api.brickowl.com/v1/order/items",
                              params={"key": _key, "order_id": oid},
                              timeout=30)
            r2.raise_for_status()
            items_data = r2.json()
            items = items_data if isinstance(items_data, list) else items_data.get("items", [])
            # normalize items to match BrickLink format
            normalized = []
            for item in items:
                normalized.append({
                    "item": {"no": item.get("bl_id", item.get("boid","")), "name": item.get("name","")},
                    "color_id":   item.get("bl_color_id", 0),
                    "color_name": item.get("color_name",""),
                    "quantity":   int(item.get("ordered_quantity", 1)),
                    "bin_location": "(not in inventory)"
                })
            result.append({
                "order_id":   f"BO-{oid}",
                "buyer_name": order.get("username", order.get("name","BrickOwl Buyer")),
                "source":     "brickowl",
                "cost":       {"grand_total": order.get("total_quantity", "?")},
                "items":      normalized
            })
        return result
        
    @st.cache_data(ttl=300)
    def fetch_order_items(_auth, order_id):
        r = requests.get(f"{BASE}/orders/{order_id}/items", auth=_auth, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("meta",{}).get("code") != 200: return []
        raw = data.get("data",[])
        if isinstance(raw, list) and raw and isinstance(raw[0], list):
            items = [item for sublist in raw for item in sublist]
        else:
            items = raw
        return items

    def get_bin_for_part(part_no, color_id):
        for lot in st.session_state.inventory:
            if (lot.get("item",{}).get("no","") == part_no and
                lot.get("color_id",0) == color_id):
                return lot.get("remarks","") or "(no bin)"
        return "(not in inventory)"

    # ── Load orders button ────────────────────────────────────────────────────
    if not st.session_state.pick_mode:
        if st.button("Load Open Orders", type="primary", use_container_width=False):
            if not st.session_state.auth:
                st.error("No credentials loaded — load inventory first.")
            else:
                with st.spinner("Fetching open orders from BrickLink…"):
                    try:
                        auth = make_auth(*st.session_state.auth)
                        all_orders = fetch_orders(auth)
                        KEEP_STATUSES = {"PAID","PENDING","UPDATED","PROCESSING","PACKED","READY"}
                        bl_orders = [o for o in all_orders if o.get("status","").upper() in KEEP_STATUSES]
                        bo_orders = fetch_brickowl_orders(BO_KEY) if BO_KEY else []
                        orders = bl_orders + bo_orders
                        enriched = []
                        pb = st.progress(0)
                        for i, order in enumerate(orders):
                            oid = order.get("order_id")
                            items = fetch_order_items(auth, oid)
                            for item in items:
                                pno      = item.get("item",{}).get("no","")
                                color_id = item.get("color_id",0)
                                item["bin_location"] = get_bin_for_part(pno, color_id)
                            enriched.append({**order, "items": items})
                            pb.progress(min((i+1)/len(orders), 1.0) if orders else 1.0)
                        pb.empty()
                        st.session_state.orders_data     = enriched
                        st.session_state.picked_items    = set()
                        st.session_state.fulfilled_orders= set()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not load orders: {e}")

        if not st.session_state.orders_data:
            st.info("Click Load Open Orders to fetch from BrickLink.")
            st.stop()

        orders = st.session_state.orders_data
        letter_map = {o["order_id"]: chr(65+i) for i,o in enumerate(orders)}

        # ── Order overview cards ──────────────────────────────────────────────
        st.markdown(f'<div style="font-size:0.7rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">{len(orders)} Open Orders</div>', unsafe_allow_html=True)

        for order in orders:
            oid     = order.get("order_id")
            letter  = letter_map[oid]
            color   = ORDER_COLORS[ord(letter)-65 if ord(letter)-65 < len(ORDER_COLORS) else 0]
            buyer   = order.get("buyer_name","Unknown")
            total   = order.get("cost",{}).get("grand_total","?")
            items   = order.get("items",[])
            n_items = sum(i.get("quantity",1) for i in items)
            is_done = oid in st.session_state.fulfilled_orders
            picked_count = sum(1 for i in items
                               if f"{oid}_{i.get('item',{}).get('no','')}_{i.get('color_id',0)}" in st.session_state.picked_items)

            done_html = '<span style="color:#4ade80;font-size:0.72rem;font-weight:700;">✓ Fulfilled</span>' if is_done else f'<span style="font-size:0.72rem;color:#475569;">{picked_count}/{len(items)} picked</span>'
            st.markdown(
                f'<div style="background:linear-gradient(145deg,#161b27,#1a2235);border:1px solid #1e2d45;'
                f'border-left:4px solid {color};border-radius:14px;padding:14px 20px;margin-bottom:10px;'
                f'display:flex;align-items:center;gap:16px;">'
                f'<div style="background:{color};color:#0d1117;font-size:1.1rem;font-weight:900;'
                f'width:36px;height:36px;border-radius:50%;display:flex;align-items:center;'
                f'justify-content:center;flex-shrink:0;">{letter}</div>'
                f'<div style="flex:1;">'
                f'<div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;">{buyer} — #{oid}</div>'
                f'<div style="font-size:0.72rem;color:#475569;margin-top:2px;">{n_items} pieces · {len(items)} lots · ${total}</div>'
                f'</div>{done_html}</div>', unsafe_allow_html=True)
            if st.button(f"▶ Pick Order {letter} — {buyer}", key=f"pickone_{oid}", use_container_width=True, type="primary"):
                single_bins = []
                raw_items = [i for order in st.session_state.orders_data for i in order.get("items",[]) if order.get("order_id")==oid]
                single_items = []
                for item in raw_items:
                    pno      = item.get("item",{}).get("no","")
                    color_id = item.get("color_id",0)
                    pick_key = f"{oid}_{pno}_{color_id}"
                    single_items.append({
                        "order_id":     oid,
                        "order_letter": letter,
                        "order_color":  color,
                        "buyer":        order.get("buyer_name",""),
                        "pno":          pno,
                        "pname":        item.get("item",{}).get("name",""),
                        "color_id":     color_id,
                        "color_name":   item.get("color_name",""),
                        "quantity":     item.get("quantity",1),
                        "bin":          item.get("bin_location","(no bin)"),
                        "pick_key":     pick_key,
                    })
                single_items.sort(key=lambda x: (x["bin"], x["pno"]))
                from itertools import groupby as igrp
                for bin_name, bin_items in igrp(single_items, key=lambda x: x["bin"]):
                    single_bins.append({"bin": bin_name, "items": list(bin_items)})

        st.write("")

        # ── Build pick queue ──────────────────────────────────────────────────
        all_pick_items = []
        for order in orders:
            oid    = order.get("order_id")
            letter = letter_map[oid]
            color  = ORDER_COLORS[ord(letter)-65 if ord(letter)-65 < len(ORDER_COLORS) else 0]
            for item in order.get("items",[]):
                pno      = item.get("item",{}).get("no","")
                color_id = item.get("color_id",0)
                pick_key = f"{oid}_{pno}_{color_id}"
                all_pick_items.append({
                    "order_id":   oid,
                    "order_letter": letter,
                    "order_color":  color,
                    "buyer":      order.get("buyer_name",""),
                    "pno":        pno,
                    "pname":      item.get("item",{}).get("name",""),
                    "color_id":   color_id,
                    "color_name": item.get("color_name",""),
                    "quantity":   item.get("quantity",1),
                    "bin":        item.get("bin_location","(no bin)"),
                    "pick_key":   pick_key,
                })

        # Sort by bin, then part number
        all_pick_items.sort(key=lambda x: (x["bin"], x["pno"]))

        # Group into bins for pick mode queue
        from itertools import groupby as igrp
        pick_bins = []
        for bin_name, bin_items in igrp(all_pick_items, key=lambda x: x["bin"]):
            pick_bins.append({"bin": bin_name, "items": list(bin_items)})

        col_all, col_spacer = st.columns([2,4])
        with col_all:
            if st.button("Start Full Pick Run", type="primary", use_container_width=True):
                st.session_state.pick_mode   = True
                st.session_state.pick_queue  = pick_bins
                st.session_state.pick_index  = 0
                st.rerun()

        
        st.divider()

        # ── Full pick list preview ────────────────────────────────────────────
        st.markdown(f'<div style="font-size:0.7rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">Full Pick List</div>', unsafe_allow_html=True)
        for bin_group in pick_bins:
            bin_name  = bin_group["bin"]
            bin_items = bin_group["items"]
            st.markdown(f'<div class="bin-header" style="border-left-color:#f472b6;"><p class="bin-title" style="color:#f472b6;">{icon("box",14,"#f472b6")} {bin_name}</p></div>', unsafe_allow_html=True)
            cols = st.columns(COLS)
            for i, item in enumerate(bin_items):
                col = cols[i % COLS]
                pick_key   = item.get("pick_key","")
                is_picked  = pick_key in st.session_state.picked_items
                order_color= item["order_color"]
                card_cls   = "part-card found" if is_picked else "part-card"
                with col:
                    st.markdown(
                        f'<div class="{card_cls}">'
                        f'{img_with_qty(item["pno"],item["color_id"],item["quantity"])}'
                        f'<div class="part-name">{item["pno"]}</div>'
                        f'<div class="part-meta">{item["pname"][:24]}</div>'
                        f'<div class="part-meta">{item["color_name"]}</div>'
                        f'<span class="badge" style="background:{order_color}22;color:{order_color};border:1px solid {order_color}55;">'
                        f'Order {item["order_letter"]} · {item["buyer"][:12]}</span>'
                        f'</div>', unsafe_allow_html=True)

    # ── PICK MODE ─────────────────────────────────────────────────────────────
    else:
        queue = st.session_state.pick_queue
        idx   = st.session_state.pick_index
        orders= st.session_state.orders_data
        letter_map = {o["order_id"]: chr(65+i) for i,o in enumerate(orders)}

        # Legend in sidebar-style info box
        legend_html = " &nbsp;·&nbsp; ".join(
            f'<span style="color:{ORDER_COLORS[i if i<len(ORDER_COLORS) else 0]};font-weight:700;">'
            f'{chr(65+i)}</span> <span style="color:#94a3b8;font-size:0.72rem;">'
            f'{o.get("buyer_name","")} #{o.get("order_id","")}</span>'
            for i,o in enumerate(orders))
        st.markdown(
            f'<div style="background:#161b27;border:1px solid #1e2d45;border-radius:12px;'
            f'padding:10px 16px;margin-bottom:16px;font-size:0.78rem;">'
            f'{legend_html}</div>', unsafe_allow_html=True)

        if idx >= len(queue):
            # All bins picked
            all_items  = [i for b in queue for i in b["items"]]
            total_items= len(all_items)
            picked_n   = sum(1 for i in all_items if i.get("pick_key","") in st.session_state.picked_items)
            st.markdown(
                f'<div class="audit-complete">'
                f'<div style="font-size:3rem;margin-bottom:12px;">📦</div>'
                f'<div style="font-size:2rem;font-weight:800;color:#4ade80;margin-bottom:8px;">Pick Run Complete!</div>'
                f'<div style="font-size:1rem;color:#475569;">{picked_n}/{total_items} items picked across {len(orders)} orders.</div>'
                f'</div>', unsafe_allow_html=True)
            st.write("")
            for order in orders:
                oid    = order.get("order_id")
                letter = letter_map[oid]
                color  = ORDER_COLORS[ord(letter)-65 if ord(letter)-65 < len(ORDER_COLORS) else 0]
                o_items= [i for b in queue for i in b["items"] if i["order_id"]==oid]
                o_picked=sum(1 for i in o_items if i.get("pick_key","") in st.session_state.picked_items)
                status = "✓ Complete" if o_picked==len(o_items) else f"{o_picked}/{len(o_items)} picked"
                st.markdown(
                    f'<div style="background:#161b27;border:1px solid #1e2d45;border-left:4px solid {color};'
                    f'border-radius:12px;padding:12px 16px;margin-bottom:8px;">'
                    f'<span style="color:{color};font-weight:800;margin-right:10px;">{letter}</span>'
                    f'<span style="color:#e2e8f0;font-weight:600;">{order.get("buyer_name","")} #{oid}</span>'
                    f'<span style="float:right;color:#4ade80;">{status}</span></div>', unsafe_allow_html=True)
            if st.button("Mark All Orders Fulfilled", type="primary"):
                for order in orders:
                    st.session_state.fulfilled_orders.add(order.get("order_id"))
                st.session_state.pick_mode = False
                st.rerun()
            if st.button("Back to Orders", use_container_width=False):
                st.session_state.pick_mode = False; st.rerun()
            st.stop()

        current_bin   = queue[idx]["bin"]
        current_items = queue[idx]["items"]
        done_count    = sum(1 for i in current_items if i.get("pick_key","") in st.session_state.picked_items)
        total_count   = len(current_items)
        pct           = int(done_count/total_count*100) if total_count else 0

        # Auto-advance when bin complete
        if total_count > 0 and done_count == total_count:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#0d2818,#112d1c);border:2px solid #2d6a4f;'
                f'border-radius:16px;padding:24px;text-align:center;margin-bottom:20px;">'
                f'<div style="font-size:1.8rem;margin-bottom:8px;">✅</div>'
                f'<div style="font-size:1.2rem;font-weight:800;color:#4ade80;">{current_bin} complete!</div>'
                f'</div>', unsafe_allow_html=True)
            time.sleep(1.2)
            st.session_state.pick_index += 1; st.rerun()

        # Header
        all_total  = sum(len(b["items"]) for b in queue)
        all_picked = sum(1 for b in queue for i in b["items"] if i.get("pick_key","") in st.session_state.picked_items)
        st.markdown(
            f'<div class="audit-mode-header">'
            f'<div class="audit-mode-sub">{icon("box",14,"#f472b6")} Pick Mode · Bin {idx+1} of {len(queue)}</div>'
            f'<div class="audit-mode-title" style="color:#f472b6;">{current_bin}</div>'
            f'<div style="margin-top:12px;">', unsafe_allow_html=True)
        st.progress(min(max(all_picked / all_total if all_total else 0, 0.0), 1.0))
        st.markdown(
            f'<div style="font-size:0.75rem;color:#6d7a8f;margin-top:6px;">'
            f'{all_picked}/{all_total} total items picked · bin {done_count}/{total_count}</div>'
            f'</div></div>', unsafe_allow_html=True)

        # Cards for this bin
        for row_start in range(0, len(current_items), COLS):
            row_items = current_items[row_start:row_start+COLS]
            cols      = st.columns(COLS)
            for col, item in zip(cols, row_items):
                pick_key    = item.get("pick_key","")
                is_picked   = pick_key in st.session_state.picked_items
                order_color = item["order_color"]
                card_cls    = "part-card found" if is_picked else "part-card"
                with col:
                    st.markdown(
                        f'<div class="{card_cls}">'
                        f'{img_with_qty(item["pno"],item["color_id"],item["quantity"])}'
                        f'<div class="part-name">{item["pno"]}</div>'
                        f'<div class="part-meta">{item["pname"][:24]}</div>'
                        f'<div class="part-meta">{item["color_name"]}</div>'
                        f'<span class="badge" style="background:{order_color}22;color:{order_color};'
                        f'border:1px solid {order_color}55;font-size:0.65rem;font-weight:800;">'
                        f'Order {item["order_letter"]}</span>'
                        f'</div>', unsafe_allow_html=True)
                    if is_picked:
                        if col.button("Unpick", key=f"unpick_{pick_key}", use_container_width=True):
                            st.session_state.picked_items.discard(pick_key); st.rerun()
                    else:
                        if col.button("Picked", key=f"pick_{pick_key}", use_container_width=True):
                            st.session_state.picked_items.add(pick_key); st.rerun()

        st.write("")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("Skip to Next Bin", use_container_width=True):
                st.session_state.pick_index += 1; st.rerun()
        with c2:
            if st.button("Exit Pick Mode", use_container_width=True, type="primary"):
                st.session_state.pick_mode = False; st.rerun()

    st.stop()
    
# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BROWSE INVENTORY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "browse":
    h1, h2 = st.columns([8,1])
    with h1:
        st.markdown(f'{icon("package",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Browse Inventory</span>', unsafe_allow_html=True)
    with h2:
        if st.button("🏠", key="home_browse", help="Back to Dashboard"):
            st.session_state.page = "dashboard"; st.rerun()
    st.write("")
    
    st.markdown('<div class="color-filter-bar">', unsafe_allow_html=True)
all_colors=sorted(set(i.get("color_name","") for i in st.session_state.inventory if i.get("color_name")))
color_filter=st.multiselect("Filter by color",options=all_colors,default=[],
    placeholder="All colors — type to search…",label_visibility="collapsed",key="color_filter")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="scan-bar">', unsafe_allow_html=True)
sc1,sc2=st.columns([5,1])
with sc1:
    scan_query=st.text_input("Scan / quick find",value=st.session_state.scan_query,
                              placeholder="Type or scan a part number…",
                              label_visibility="collapsed",key="scan_input")
with sc2:
    if st.button("Clear",use_container_width=True): st.session_state.scan_query=""; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
if scan_query != st.session_state.scan_query:
    st.session_state.scan_query=scan_query; st.rerun()

if st.session_state.show_bulk_confirm:
    pushable=get_pushable_flags()
    if pushable:
        st.warning(f"Ready to push {len(pushable)} fix(es) to BrickLink — review below:")
        st.dataframe(pd.DataFrame([{"Part #":p["pno"],"Name":p["name"],"Bin":p["bin"],"Change":p["change"]}for p in pushable]),use_container_width=True,hide_index=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("Confirm — push all",type="primary",use_container_width=True):
                with st.spinner("Pushing…"):
                    results=push_all_flags(make_auth(*st.session_state.auth))
                st.session_state.show_bulk_confirm=False
                if results["success"]: st.success(f"{len(results['success'])} update(s) pushed")
                for f in results.get("failed",[]): st.error(f"Failed for {f['pno']}: {f['error']}")
                st.rerun()
        with c2:
            if st.button("Cancel",use_container_width=True): st.session_state.show_bulk_confirm=False; st.rerun()
    else: st.session_state.show_bulk_confirm=False

inv=st.session_state.inventory
if "New" not in cond_filter: inv=[i for i in inv if i.get("new_or_used")!="N"]
if "Used" not in cond_filter: inv=[i for i in inv if i.get("new_or_used")!="U"]
if color_filter: inv=[i for i in inv if i.get("color_name","") in color_filter]
if search_term:
    q=search_term.lower()
    inv=[i for i in inv if q in i.get("item",{}).get("no","").lower() or q in i.get("item",{}).get("name","").lower()]
if show_filter=="Found":           inv=[i for i in inv if i.get("inventory_id") in st.session_state.checked]
elif show_filter=="Flagged":       inv=[i for i in inv if i.get("inventory_id") in st.session_state.flagged]
elif show_filter=="Not yet found": inv=[i for i in inv if i.get("inventory_id") not in st.session_state.checked and i.get("inventory_id") not in st.session_state.flagged]
elif show_filter=="Low stock":     inv=[i for i in inv if 0<i.get("quantity",0)<=LOW_STOCK_THRESHOLD]
if remarks_filter!="All":          inv=[i for i in inv if (i.get("remarks","") or "(no remarks)")==remarks_filter]

scan_ids=set()
if st.session_state.scan_query:
    sq=st.session_state.scan_query.lower()
    for lot in inv:
        if sq in lot.get("item",{}).get("no","").lower(): scan_ids.add(lot.get("inventory_id"))
    if not scan_ids: st.warning(f"No parts found matching {st.session_state.scan_query}")

inv=sorted(inv,key=lambda x:(0 if x.get("inventory_id") in scan_ids else 1,x.get("remarks","") or ""))
st.caption(f"Showing {len(inv)} lots"+(f" · {len(scan_ids)} highlighted" if scan_ids else "")+(" · Mobile" if is_mobile else " · Desktop"))

for group_name,group_items in groupby(inv,key=lambda x:x.get("remarks","") or "(no remarks)"):
    group_lots=list(group_items)
    bin_total=len(group_lots)
    bin_found=sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.checked)
    bin_flagged=sum(1 for x in group_lots if x.get("inventory_id") in st.session_state.flagged)
    bin_pct=int(bin_found/bin_total*100) if bin_total else 0
    last_audited=st.session_state.bin_audit_dates.get(group_name,"")
    audited_html=f'&nbsp;&nbsp;<span style="color:#2d6a4f;font-size:0.68rem;">✓ audited {last_audited}</span>' if last_audited else ""
    col_title,col_btn=st.columns([4,1])
    with col_title:
        flagged_note=(f'&nbsp;&nbsp;{icon("alert-circle",11,"#fb7185")}<span style="font-size:0.7rem;color:#fb7185;">{bin_flagged} flagged</span>' if bin_flagged else "")
        st.markdown(f'<div class="bin-header"><p class="bin-title">{icon("archive",14,"#a78bfa")} {group_name}</p><p class="bin-stats">{bin_found}/{bin_total} found · {bin_pct}%{flagged_note}{audited_html}</p></div>', unsafe_allow_html=True)
    with col_btn:
        st.write(""); st.write("")
        if st.button("Mark all found",key=f"markall_{group_name}",use_container_width=True):
            for x in group_lots:
                lid=x.get("inventory_id"); st.session_state.checked.add(lid)
                save_progress(lid,"checked",notes=st.session_state.notes.get(lid))
            save_bin_audit_date(group_name)
            st.session_state.bin_audit_dates[group_name]=datetime.now().strftime("%Y-%m-%d")
            st.rerun()

    for row_start in range(0,len(group_lots),COLS):
        row_items=group_lots[row_start:row_start+COLS]
        cols=st.columns(COLS)
        for col,lot in zip(cols,row_items):
            lid=lot.get("inventory_id","unknown"); item=lot.get("item",{})
            pno=item.get("no",""); pname=item.get("name","N/A")
            color=lot.get("color_name",""); color_id=lot.get("color_id",0)
            qty=lot.get("quantity",0); price=lot.get("unit_price","")
            remarks=lot.get("remarks",""); cond="New" if lot.get("new_or_used")=="N" else "Used"
            is_found=lid in st.session_state.checked; is_flagged=lid in st.session_state.flagged
            is_low=0<qty<=LOW_STOCK_THRESHOLD; is_scan=lid in scan_ids
            flag_info=st.session_state.flagged.get(lid,{}); note_val=st.session_state.notes.get(lid,"")
            price_data=st.session_state.price_cache.get(f"{pno}_{color_id}_N"); is_over=False
            if price_data and float(price or 0)>0:
                mkt=float(price_data.get("avg_price",0) or 0)
                if mkt>0: is_over=((float(price)-mkt)/mkt*100)>PRICE_FLAG_PCT
            if is_scan:      card_cls="part-card highlight"
            elif is_flagged: card_cls="part-card flagged"
            elif is_found:   card_cls="part-card found"
            elif is_over:    card_cls="part-card overpriced"
            elif is_low:     card_cls="part-card lowstock"
            else:            card_cls="part-card"
            if is_flagged:   b_cls,b_svg,b_lbl="badge-flagged",icon("alert-circle",10,"#fb7185"),flag_info.get("reason","Flagged")
            elif is_found:   b_cls,b_svg,b_lbl="badge-found",icon("check-circle",10,"#4ade80"),"Found"
            elif is_over:    b_cls,b_svg,b_lbl="badge-over",icon("trending-up",10,"#a78bfa"),"Overpriced"
            elif is_low:     b_cls,b_svg,b_lbl="badge-low",icon("alert-triangle",10,"#fb923c"),f"Low ({qty})"
            else:            b_cls="badge-n" if cond=="New" else "badge-u"; b_svg,b_lbl="",cond
            note_html=(f'<div class="part-meta" style="margin-top:4px;color:#f59e0b;">{icon("file-text",10,"#f59e0b")} {note_val[:20]}</div>' if note_val else "")
            with col:
                st.markdown(f'<div class="{card_cls}">{img_with_qty(pno,color_id,qty)}<div class="part-name">{pno}</div><div class="part-meta">{pname[:26] if not is_mobile else pname[:18]}</div><div class="part-meta">{color}</div><div class="part-meta">${price}</div><span class="badge {b_cls}">{b_svg}{b_lbl}</span>{note_html}</div>', unsafe_allow_html=True)
                if is_flagged:
                    if col.button("Unflag",key=f"unflag_{lid}",use_container_width=True):
                        del st.session_state.flagged[lid]; delete_progress(lid); st.rerun()
                elif is_found:
                    if col.button("Unmark",key=f"unmark_{lid}",use_container_width=True):
                        st.session_state.checked.discard(lid); delete_progress(lid); st.rerun()
                else:
                    if col.button("Found",key=f"found_{lid}_{row_start}",use_container_width=True):
                        st.session_state.checked.add(lid)
                        save_progress(lid,"checked",notes=st.session_state.notes.get(lid))
                        bin_name=lot.get("remarks","") or "(no remarks)"
                        bin_lots=[i for i in st.session_state.inventory if (i.get("remarks","") or "(no remarks)")==bin_name]
                        if all(i.get("inventory_id") in st.session_state.checked or i.get("inventory_id") in st.session_state.flagged for i in bin_lots):
                            save_bin_audit_date(bin_name)
                            st.session_state.bin_audit_dates[bin_name]=datetime.now().strftime("%Y-%m-%d")
                        st.rerun()
                with col.expander("Note"):
                    new_note=st.text_area("Note",value=note_val,key=f"note_{lid}",height=80,label_visibility="collapsed",placeholder="e.g. found in back of bin…")
                    if st.button("Save note",key=f"savenote_{lid}",use_container_width=True):
                        st.session_state.notes[lid]=new_note
                        flag=st.session_state.flagged.get(lid,{})
                        status="checked" if is_found else "flagged" if is_flagged else "unchecked"
                        save_progress(lid,status,flag.get("reason"),flag.get("actual_qty"),flag.get("correct_bin"),new_note); st.rerun()
                if not is_found and not is_flagged:
                    with col.expander("Flag issue"):
                        reason=st.radio("Issue type",["Wrong quantity","Wrong part in bin","Wrong bin"],key=f"reason_{lid}")
                        if reason=="Wrong quantity":
                            actual_qty=st.number_input(f"Actual qty (listed: {qty})",min_value=0,value=qty,key=f"qty_{lid}")
                            if st.button("Save flag",key=f"saveflag_{lid}",use_container_width=True):
                                st.session_state.flagged[lid]={"reason":"Wrong qty","actual_qty":actual_qty}
                                save_progress(lid,"flagged","Wrong qty",actual_qty,None,st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth:
                                if st.button("Update on BrickLink",key=f"update_{lid}",use_container_width=True,type="primary"):
                                    try:
                                        update_quantity_on_bricklink(make_auth(*st.session_state.auth),lid,actual_qty)
                                        st.session_state.flagged[lid]={"reason":"Qty updated","actual_qty":actual_qty}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id")==lid: x["quantity"]=actual_qty
                                        save_progress(lid,"flagged","Qty updated",actual_qty,None,st.session_state.notes.get(lid))
                                        st.success("Updated"); st.rerun()
                                    except Exception as e: st.error(f"Failed: {e}")
                        elif reason=="Wrong bin":
                            correct_bin=st.text_input(f"Correct bin (current: {remarks or 'none'})",key=f"bin_{lid}")
                            if st.button("Save flag",key=f"saveflag_{lid}",use_container_width=True):
                                st.session_state.flagged[lid]={"reason":"Wrong bin","correct_bin":correct_bin}
                                save_progress(lid,"flagged","Wrong bin",None,correct_bin,st.session_state.notes.get(lid)); st.rerun()
                            if st.session_state.auth and correct_bin:
                                if st.button("Update on BrickLink",key=f"updatebin_{lid}",use_container_width=True,type="primary"):
                                    try:
                                        update_remarks_on_bricklink(make_auth(*st.session_state.auth),lid,correct_bin)
                                        st.session_state.flagged[lid]={"reason":"Bin updated","correct_bin":correct_bin}
                                        for x in st.session_state.inventory:
                                            if x.get("inventory_id")==lid: x["remarks"]=correct_bin
                                        save_progress(lid,"flagged","Bin updated",None,correct_bin,st.session_state.notes.get(lid))
                                        st.success("Bin updated"); st.rerun()
                                    except Exception as e: st.error(f"Failed: {e}")
                        else:
                            if st.button("Save flag",key=f"saveflag_{lid}",use_container_width=True):
                                st.session_state.flagged[lid]={"reason":"Wrong part"}
                                save_progress(lid,"flagged","Wrong part",None,None,st.session_state.notes.get(lid)); st.rerun()
    st.divider()
