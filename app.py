# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DUPLICATES
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dupes":
    st.markdown(f'{icon("copy",22,"#a78bfa")} <span style="font-size:1.4rem;font-weight:800;color:#e2e8f0;vertical-align:middle;">Duplicate Lots</span>', unsafe_allow_html=True)
    st.caption("Parts with the same part # and color listed in more than one bin.")
    st.write("")

    dupes = find_duplicates(st.session_state.inventory)

    if not dupes:
        st.success("No duplicates found — your inventory is clean!")
        st.stop()

    total_dup_lots = sum(len(v) for v in dupes.values())
    all_dup_lids   = [lot.get("inventory_id") for lots in dupes.values() for lot in lots]

    # ── Stockroom helper ──────────────────────────────────────────────────────
    def move_to_stockroom_a(auth, inventory_id):
        r = requests.put(f"{BASE}/inventories/{inventory_id}", auth=auth,
                         json={"is_stockroom": True, "stockroom_id": "A"}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("meta", {}).get("code") != 200:
            raise ValueError(data.get("meta", {}).get("description", "Stockroom move failed"))
        return True

    def run_stockroom_move(lids):
        if not st.session_state.auth:
            st.error("No credentials loaded."); return
        auth    = make_auth(*st.session_state.auth)
        success = []
        failed  = []
        pb      = st.progress(0)
        txt     = st.empty()
        for i, lid in enumerate(lids):
            txt.text(f"Moving {i+1}/{len(lids)} to Stockroom A…")
            try:
                move_to_stockroom_a(auth, lid)
                success.append(lid)
                # Mark in local inventory so UI updates
                for lot in st.session_state.inventory:
                    if lot.get("inventory_id") == lid:
                        lot["is_stockroom"]  = True
                        lot["stockroom_id"]  = "A"
            except Exception as e:
                failed.append({"lid": lid, "error": str(e)})
            pb.progress((i + 1) / len(lids))
            time.sleep(0.2)
        txt.empty(); pb.empty()
        if success: st.success(f"✅ {len(success)} lot(s) moved to Stockroom A")
        for f in failed: st.error(f"Failed for lot {f['lid']}: {f['error']}")

    # ── Top metrics ───────────────────────────────────────────────────────────
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#a78bfa">{len(dupes)}</div><div class="metric-label">Duplicate Groups</div></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#fb923c">{total_dup_lots}</div><div class="metric-label">Affected Lots</div></div>', unsafe_allow_html=True)
    with d3:
        in_stockroom = sum(1 for lots in dupes.values() for lot in lots if lot.get("is_stockroom"))
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#60a5fa">{in_stockroom}</div><div class="metric-label">Already in Stockroom</div></div>', unsafe_allow_html=True)

    st.write("")

    # ── Top-level move all button ─────────────────────────────────────────────
    not_yet_moved = [lid for lid in all_dup_lids
                     if not next((lot.get("is_stockroom") for lot in st.session_state.inventory
                                  if lot.get("inventory_id") == lid), False)]
    if not_yet_moved:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1a0a2e,#2d1060);'
            f'border:1px solid #6d28d9;border-radius:14px;padding:16px 20px;margin-bottom:16px;">'
            f'<div style="font-size:0.85rem;font-weight:600;color:#a78bfa;margin-bottom:10px;">'
            f'{icon("archive",16,"#a78bfa")} Move all {len(not_yet_moved)} duplicate lots to Stockroom A</div>'
            f'<div style="font-size:0.72rem;color:#475569;">Hides them from buyers until you resolve each duplicate during your next audit.</div>'
            f'</div>', unsafe_allow_html=True)
        if st.button(f"Move all {len(not_yet_moved)} lots to Stockroom A",
                     type="primary", use_container_width=True, key="move_all_stockroom"):
            run_stockroom_move(not_yet_moved)
            st.rerun()
    else:
        st.success("All duplicate lots are already in Stockroom A.")

    st.divider()

    # ── Search + export ───────────────────────────────────────────────────────
    dup_search = st.text_input("Filter by part # or name", placeholder="e.g. 3001 or Brick…", key="dup_search")

    export_rows = []
    for key, lots in dupes.items():
        for lot in lots:
            export_rows.append({
                "Part #":      lot.get("item",{}).get("no",""),
                "Name":        lot.get("item",{}).get("name",""),
                "Color":       lot.get("color_name",""),
                "Bin":         lot.get("remarks",""),
                "Qty":         lot.get("quantity",0),
                "Price":       lot.get("unit_price",""),
                "Condition":   "New" if lot.get("new_or_used")=="N" else "Used",
                "In Stockroom":"Yes" if lot.get("is_stockroom") else "No",
            })
    if export_rows:
        st.download_button("Export Duplicates CSV",
                           pd.DataFrame(export_rows).to_csv(index=False),
                           "duplicates.csv", "text/csv",
                           use_container_width=False)

    st.divider()

    # ── Per-group cards ───────────────────────────────────────────────────────
    shown = 0
    for key, lots in sorted(dupes.items(), key=lambda x: -len(x[1])):
        pno      = lots[0].get("item",{}).get("no","")
        pname    = lots[0].get("item",{}).get("name","")
        color    = lots[0].get("color_name","")
        color_id = lots[0].get("color_id",0)

        if dup_search:
            q = dup_search.lower()
            if q not in pno.lower() and q not in pname.lower():
                continue

        shown += 1
        bins_list    = [l.get("remarks","") or "(no bin)" for l in lots]
        group_lids   = [l.get("inventory_id") for l in lots]
        group_not_moved = [lid for lid in group_lids
                           if not next((lot.get("is_stockroom") for lot in st.session_state.inventory
                                        if lot.get("inventory_id") == lid), False)]

        st.markdown(
            f'<div class="dup-group">'
            f'<div class="dup-group-header">'
            f'<img class="dup-part-img" '
            f'src="https://img.bricklink.com/ItemImage/PN/{color_id}/{pno}.png" '
            f'onerror="this.style.opacity=\'0.15\'"/>'
            f'<div class="dup-part-info">'
            f'<div class="dup-part-name">{pno} — {pname}</div>'
            f'<div class="dup-part-sub">{color} · {len(lots)} lots in {len(set(bins_list))} bins</div>'
            f'</div></div>', unsafe_allow_html=True)

        for lot in sorted(lots, key=lambda x: x.get("remarks","") or ""):
            lid        = lot.get("inventory_id")
            remarks    = lot.get("remarks","") or "(no bin)"
            qty        = lot.get("quantity",0)
            price      = lot.get("unit_price","")
            cond       = "New" if lot.get("new_or_used")=="N" else "Used"
            in_stock_a = lot.get("is_stockroom") and lot.get("stockroom_id") == "A"
            is_flagged = lid in st.session_state.flagged
            is_found   = lid in st.session_state.checked

            if in_stock_a:
                status_html = f'<span style="color:#60a5fa;font-size:0.7rem;font-weight:700;">● Stockroom A</span>'
            elif is_flagged:
                status_html = f'<span style="color:#fb7185;font-size:0.7rem;font-weight:600;">● Flagged</span>'
            elif is_found:
                status_html = f'<span style="color:#4ade80;font-size:0.7rem;font-weight:600;">● Found</span>'
            else:
                status_html = f'<span style="color:#475569;font-size:0.7rem;">● Active</span>'

            st.markdown(
                f'<div class="dup-bin-row">'
                f'<span class="dup-bin-name">{remarks}</span>'
                f'<span class="dup-bin-qty">×{qty}</span>'
                f'<span class="dup-bin-price">${price}</span>'
                f'<span style="color:#475569;font-size:0.72rem;">{cond}</span>'
                f'{status_html}'
                f'</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Per-group move button + flag controls
        btn_col, flag_col = st.columns([1, 1])
        with btn_col:
            if group_not_moved:
                if st.button(f"Move group to Stockroom A ({len(group_not_moved)} lots)",
                             key=f"stockroom_{key}", use_container_width=True):
                    run_stockroom_move(group_not_moved)
                    st.rerun()
            else:
                st.markdown('<div style="font-size:0.72rem;color:#60a5fa;padding:8px 0;">✓ All in Stockroom A</div>', unsafe_allow_html=True)

        with flag_col:
            with st.expander(f"Flag a lot in this group"):
                lot_labels   = [f"{l.get('remarks','(no bin)')} — ×{l.get('quantity',0)} @ ${l.get('unit_price','')}" for l in lots]
                selected_idx = st.selectbox("Select lot to flag", range(len(lots)),
                                            format_func=lambda i: lot_labels[i],
                                            key=f"dup_sel_{key}")
                selected_lot = lots[selected_idx]
                lid_s  = selected_lot.get("inventory_id")
                qty_s  = selected_lot.get("quantity",0)
                rem_s  = selected_lot.get("remarks","")
                reason_d = st.radio("Issue", ["Wrong bin","Wrong quantity","Wrong part in bin"],
                                    key=f"dup_reason_{key}")
                if reason_d == "Wrong bin":
                    correct_bin_d = st.text_input(f"Correct bin (current: {rem_s or 'none'})", key=f"dup_bin_{key}")
                    if st.button("Save flag", key=f"dup_saveflag_{key}", use_container_width=True):
                        st.session_state.flagged[lid_s] = {"reason":"Wrong bin","correct_bin":correct_bin_d}
                        save_progress(lid_s,"flagged","Wrong bin",None,correct_bin_d,st.session_state.notes.get(lid_s)); st.rerun()
                elif reason_d == "Wrong quantity":
                    actual_qty_d = st.number_input(f"Actual qty (listed: {qty_s})", min_value=0, value=qty_s, key=f"dup_qty_{key}")
                    if st.button("Save flag", key=f"dup_saveflag_{key}", use_container_width=True):
                        st.session_state.flagged[lid_s] = {"reason":"Wrong qty","actual_qty":actual_qty_d}
                        save_progress(lid_s,"flagged","Wrong qty",actual_qty_d,None,st.session_state.notes.get(lid_s)); st.rerun()
                else:
                    if st.button("Save flag", key=f"dup_saveflag_{key}", use_container_width=True):
                        st.session_state.flagged[lid_s] = {"reason":"Wrong part"}
                        save_progress(lid_s,"flagged","Wrong part",None,None,st.session_state.notes.get(lid_s)); st.rerun()

    if shown == 0:
        st.info("No duplicates match your search.")
    st.stop()
