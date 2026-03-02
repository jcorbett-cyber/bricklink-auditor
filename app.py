import streamlit as st
import requests
from requests_oauthlib import OAuth1
import pandas as pd

st.set_page_config(page_title="BrickLink Inventory Auditor", page_icon="🧱", layout="wide")

st.markdown("""
<style>
.part-card { background:#1e1e2e; border:1px solid #313244; border-radius:12px; padding:14px; text-align:center; margin-bottom:8px; }
.part-card.found { border-color:#a6e3a1; background:#1a2e1a; }
.part-img { width:100%; max-height:110px; object-fit:contain; margin-bottom:8px; }
.part-name { font-size:0.8rem; color:#cdd6f4; font-weight:700; margin-bottom:3px; }
.part-meta { font-size:0.72rem; color:#a6adc8; }
.badge { display:inline-block; border-radius:6px; padding:2px 8px; font-size:0.68rem; font-weight:700; margin-top:4px; }
.badge-n { background:#313244; color:#cdd6f4; }
.badge-u { background:#45475a; color:#f9e2af; }
.badge-found { background:#a6e3a1; color:#1e1e2e; }
</style>
""", unsafe_allow_html=True)

if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "checked" not in st.session_state:
    st.session_state.checked = set()
if "loaded" not in st.session_state:
    st.session_state.loaded = False

with st.sidebar:
    st.markdown("## 🔑 API Credentials")
    st.caption("Keys are never saved — session only.")
    ck = st.text_input("Consumer Key",    type="password")
    cs = st.text_input("Consumer Secret", type="password")
    tv = st.text_input("Token Value",     type="password")
    ts = st.text_input("Token Secret",    type="password")
    load_btn = st.button("🔄 Load My Inventory", use_container_width=True, type="primary")

    st.divider()
    st.markdown("### 🔍 Filters")
    search_term = st.text_input("Search part # or name")
    cond_filter = st.multiselect("Condition", ["New","Used"], default=["New","Used"])
    show_filter = st.radio("Show", ["All","✅ Found","⬜ Not yet found"])

    st.divider()
    if st.session_state.inventory:
        total = len(st.session_state.inventory)
        found = len(st.session_state.checked)
        pct   = int(found/total*100) if total else 0
        st.markdown("### 📊 Progress")
        st.progress(pct/100)
        st.markdown(f"**{found}/{total}** lots · {pct}%")
        if st.button("🗑️ Reset All Checkmarks", use_container_width=True):
            st.session_state.checked = set()
            st.rerun()
        remaining = [i for i in st.session_state.inventory if i.get("inventory_id") not in st.session_state.checked]
        if remaining:
            df = pd.DataFrame([{
                "Inventory ID": r.get("inventory_id",""),
                "Part #":       r.get("item",{}).get("no",""),
                "Name":         r.get("item",{}).get("name",""),
                "Color":        r.get("color_name",""),
                "Condition":    "New" if r.get("new_or_used")=="N" else "Used",
                "Quantity":     r.get("quantity",0),
                "Price":        r.get("unit_price",""),
            } for r in remaining])
            st.download_button("📥 Export Remaining CSV", df.to_csv(index=False),
                               "remaining_lots.csv", "text/csv", use_container_width=True)

BASE = "https://api.bricklink.com/api/store/v1"

if load_btn:
    if not all([ck, cs, tv, ts]):
        st.error("Please fill in all four credential fields.")
    else:
        with st.spinner("Loading inventory from BrickLink…"):
            try:
                auth = OAuth1(ck, cs, tv, ts)
                r = requests.get(f"{BASE}/inventories", auth=auth, timeout=30)
                r.raise_for_status()
                data = r.json()
                if data.get("meta",{}).get("code") != 200:
                    raise ValueError(data.get("meta",{}).get("description","API error"))
                st.session_state.inventory = data["data"]
                st.session_state.checked   = set()
                st.session_state.loaded    = True
                st.success(f"✅ Loaded {len(data['data'])} lots!")
            except Exception as e:
                st.error(f"Error: {e}")

# Show raw field names from first lot to help debug
if st.session_state.loaded and st.session_state.inventory:
    with st.expander("🔧 Debug: field names from first lot (you can delete this later)"):
        st.write(list(st.session_state.inventory[0].keys()))

st.title("🧱 BrickLink Inventory Auditor")

if not st.session_state.loaded:
    st.info("👈 Enter your API credentials in the sidebar and click Load My Inventory.")
    st.stop()

inv = st.session_state.inventory
if "New" not in cond_filter:
    inv = [i for i in inv if i.get("new_or_used") != "N"]
if "Used" not in cond_filter:
    inv = [i for i in inv if i.get("new_or_used") != "U"]
if search_term:
    q = search_term.lower()
    inv = [i for i in inv if q in i.get("item",{}).get("no","").lower()
           or q in i.get("item",{}).get("name","").lower()]
if show_filter == "✅ Found":
    inv = [i for i in inv if i.get("inventory_id") in st.session_state.checked]
elif show_filter == "⬜ Not yet found":
    inv = [i for i in inv if i.get("inventory_id") not in st.session_state.checked]

st.caption(f"Showing {len(inv)} lots")

COLS = 6
for row_items in [inv[i:i+COLS] for i in range(0, len(inv), COLS)]:
    cols = st.columns(COLS)
    for col, lot in zip(cols, row_items):
        lid      = lot.get("inventory_id", lot.get("lot_id", "unknown"))
        item     = lot.get("item", {})
        pno      = item.get("no","")
        pname    = item.get("name","N/A")
        color    = lot.get("color_name","")
        qty      = lot.get("quantity",0)
        price    = lot.get("unit_price","")
        cond     = "New" if lot.get("new_or_used")=="N" else "Used"
        is_found = lid in st.session_state.checked
        card_cls = "part-card found" if is_found else "part-card"
        badge_cls= "badge-found" if is_found else ("badge-n" if cond=="New" else "badge-u")
        badge_lbl= "✅ Found" if is_found else cond
        img      = f"https://img.bricklink.com/ItemImage/PN/0/{pno}.png"

        with col:
            st.markdown(f"""
            <div class="{card_cls}">
              <img class="part-img" src="{img}"/>
              <div class="part-name">{pno}</div>
              <div class="part-meta">{pname[:26]}</div>
              <div class="part-meta">{color} · ×{qty}</div>
              <div class="part-meta">${price}</div>
              <span class="badge {badge_cls}">{badge_lbl}</span>
            </div>""", unsafe_allow_html=True)

            if col.button("Unmark" if is_found else "✓ Found", key=f"b{lid}", use_container_width=True):
                if is_found:
                    st.session_state.checked.discard(lid)
                else:
                    st.session_state.checked.add(lid)
                st.rerun()
