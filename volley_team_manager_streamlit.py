import streamlit as st
import json
import os
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Volley Team Manager",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1c1c1e;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #8e8e93;
        margin-bottom: 1.5rem;
    }
    .player-card {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .player-card:hover {
        background: #f9f9fb;
        border-color: #c7c7cc;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-palleggiatrice { background: #e3f2fd; color: #1565c0; }
    .badge-schiacciatrice { background: #fce4ec; color: #c2185b; }
    .badge-centrale { background: #e8f5e9; color: #2e7d32; }
    .badge-opposto { background: #f3e5f5; color: #7b1fa2; }
    .badge-libero { background: #f5f5f5; color: #616161; }
    .badge-attiva { background: #e8f5e9; color: #2e7d32; }
    .badge-infortunata { background: #ffebee; color: #c62828; }
    .stat-box {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }
    .court-container {
        position: relative;
        width: 320px;
        height: 576px;
        border: 2px solid #1c1c1e;
        border-radius: 4px;
        margin: 0 auto;
        background: #fafafa;
    }
    .court-line {
        position: absolute;
        left: 0;
        right: 0;
        border-top: 1px solid #1c1c1e;
    }
    .court-net {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        border-top: 3px solid #1c1c1e;
    }
    .player-dot {
        position: absolute;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #1c1c1e;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        transition: transform 0.2s ease;
        z-index: 10;
    }
    .player-dot:hover {
        transform: scale(1.15);
    }
    .player-dot.libero {
        background: #636366;
    }
    .star-filled { color: #ff9500; }
    .star-empty { color: #e5e5ea; }
</style>
""", unsafe_allow_html=True)

# File di persistenza
DATA_FILE = "volley_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "squadra": {
            "nome": "Volley Club",
            "categoria": "Serie B2 Femminile",
            "girone": "Girone A",
            "allenatore": ""
        },
        "giocatrici": [
            {"id": 1, "nome": "Giulia", "cognome": "Bianchi", "numero": 10, "ruolo": "schiacciatrice", "altezza": 178, "stato": "attiva",
             "forza": [{"tag": "attacco potente", "val": 4}, {"tag": "muro", "val": 3}],
             "debolezza": [{"tag": "ricezione", "val": 2}], "note": "Migliora in allenamento"},
            {"id": 2, "nome": "Sara", "cognome": "Rossi", "numero": 7, "ruolo": "palleggiatrice", "altezza": 172, "stato": "attiva",
             "forza": [{"tag": "palleggio", "val": 5}, {"tag": "intelligenza tattica", "val": 4}],
             "debolezza": [{"tag": "attacco", "val": 2}], "note": "Capitano"},
            {"id": 3, "nome": "Martina", "cognome": "Verdi", "numero": 3, "ruolo": "libero", "altezza": 165, "stato": "attiva",
             "forza": [{"tag": "difesa", "val": 5}, {"tag": "ricezione", "val": 5}],
             "debolezza": [{"tag": "attacco", "val": 1}], "note": ""},
            {"id": 4, "nome": "Anna", "cognome": "Neri", "numero": 14, "ruolo": "centrale", "altezza": 185, "stato": "attiva",
             "forza": [{"tag": "muro", "val": 5}, {"tag": "altezza", "val": 5}],
             "debolezza": [{"tag": "difesa", "val": 2}], "note": ""},
            {"id": 5, "nome": "Chiara", "cognome": "Gialli", "numero": 9, "ruolo": "opposto", "altezza": 180, "stato": "infortunata",
             "forza": [{"tag": "attacco", "val": 4}, {"tag": "battuta", "val": 4}],
             "debolezza": [{"tag": "difesa", "val": 2}], "note": "Infortunio alla caviglia"},
            {"id": 6, "nome": "Elena", "cognome": "Blu", "numero": 5, "ruolo": "schiacciatrice", "altezza": 176, "stato": "attiva",
             "forza": [{"tag": "difesa", "val": 4}, {"tag": "ricezione", "val": 4}],
             "debolezza": [{"tag": "muro", "val": 2}], "note": ""}
        ],
        "formazione": [2, 4, 1, 6, 5, 3],
        "libero_id": 3,
        "partite": [],
        "stats_totali": {}
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Inizializza session state
if "data" not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.current_rot = 1
    st.session_state.match = {"set": 1, "us": 0, "them": 0, "sets_us": 0, "sets_them": 0}
    st.session_state.live_stats = {}

data = st.session_state.data

# Mappatura colori ruoli
RUOLI_BADGE = {
    "palleggiatrice": "badge-palleggiatrice",
    "schiacciatrice": "badge-schiacciatrice",
    "centrale": "badge-centrale",
    "opposto": "badge-opposto",
    "libero": "badge-libero"
}

RUOLI_OPTIONS = ["palleggiatrice", "schiacciatrice", "centrale", "opposto", "libero"]

# ==================== HEADER ====================
st.markdown('<div class="main-header">🏐 Volley Team Manager</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{data["squadra"]["categoria"]} — Stagione 2025/26</div>', unsafe_allow_html=True)

# ==================== NAVIGAZIONE ====================
tab_roster, tab_tattica, tab_partita, tab_stats = st.tabs(["👥 Roster", "📐 Tattica", "🏆 Partita Live", "📊 Statistiche"])

# ==================== TAB ROSTER ====================
with tab_roster:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{len(data['giocatrici'])}** giocatrici in rosa")
    with col2:
        if st.button("➕ Aggiungi giocatrice", type="primary", use_container_width=True):
            st.session_state.show_add_player = True

    # Form aggiungi giocatrice
    if st.session_state.get("show_add_player", False):
        with st.container():
            st.markdown("---")
            st.subheader("Nuova giocatrice")
            c1, c2, c3 = st.columns(3)
            with c1:
                nome = st.text_input("Nome", key="new_nome")
            with c2:
                cognome = st.text_input("Cognome", key="new_cognome")
            with c3:
                numero = st.number_input("Numero maglia", min_value=1, max_value=99, value=10, key="new_numero")

            c4, c5 = st.columns(2)
            with c4:
                ruolo = st.selectbox("Ruolo", RUOLI_OPTIONS, key="new_ruolo")
            with c5:
                altezza = st.number_input("Altezza (cm)", min_value=140, max_value=210, value=170, key="new_altezza")

            forza_tags = st.text_input("Punti di forza (separati da virgola)", placeholder="es. attacco potente, muro, difesa", key="new_forza")
            debolezza_tags = st.text_input("Punti deboli (separati da virgola)", placeholder="es. ricezione, battuta", key="new_debolezza")
            note = st.text_area("Note", placeholder="Osservazioni tecniche, caratteriali...", key="new_note")

            c_save, c_cancel = st.columns(2)
            with c_save:
                if st.button("💾 Salva giocatrice", type="primary", use_container_width=True):
                    if nome and cognome:
                        new_id = max([g["id"] for g in data["giocatrici"]], default=0) + 1
                        forza_list = [{"tag": t.strip(), "val": 3} for t in forza_tags.split(",") if t.strip()]
                        debolezza_list = [{"tag": t.strip(), "val": 3} for t in debolezza_tags.split(",") if t.strip()]
                        data["giocatrici"].append({
                            "id": new_id, "nome": nome, "cognome": cognome, "numero": int(numero),
                            "ruolo": ruolo, "altezza": int(altezza), "stato": "attiva",
                            "forza": forza_list, "debolezza": debolezza_list, "note": note
                        })
                        save_data(data)
                        st.session_state.show_add_player = False
                        st.rerun()
                    else:
                        st.error("Inserisci nome e cognome")
            with c_cancel:
                if st.button("❌ Annulla", use_container_width=True):
                    st.session_state.show_add_player = False
                    st.rerun()
            st.markdown("---")

    # Filtri
    filtro_ruolo = st.multiselect("Filtra per ruolo", RUOLI_OPTIONS, default=[], key="filtro_ruolo")
    filtro_stato = st.multiselect("Filtra per stato", ["attiva", "infortunata", "squalificata"], default=["attiva"], key="filtro_stato")

    giocatrici_visibili = [g for g in data["giocatrici"]
                          if (not filtro_ruolo or g["ruolo"] in filtro_ruolo)
                          and (not filtro_stato or g["stato"] in filtro_stato)]

    if not giocatrici_visibili:
        st.info("Nessuna giocatrice trovata con i filtri selezionati.")

    for g in giocatrici_visibili:
        with st.container():
            col_info, col_actions = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div class="player-card">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="width:44px; height:44px; border-radius:50%; background:#1c1c1e; color:#fff; display:flex; align-items:center; justify-content:center; font-size:15px; font-weight:700;">{g['numero']}</div>
                        <div style="flex:1;">
                            <div style="font-size:16px; font-weight:600;">{g['nome']} {g['cognome']}</div>
                            <div style="font-size:13px; color:#636366; margin-top:2px;">
                                <span class="badge {RUOLI_BADGE.get(g['ruolo'], '')}">{g['ruolo']}</span>
                                <span style="margin:0 4px;">·</span>
                                <span>{g['altezza']}cm</span>
                                <span style="margin:0 4px;">·</span>
                                <span class="badge badge-{g['stato']}">{g['stato']}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_actions:
                if st.button("🗑️", key=f"del_{g['id']}", help="Elimina giocatrice"):
                    data["giocatrici"] = [x for x in data["giocatrici"] if x["id"] != g["id"]]
                    save_data(data)
                    st.rerun()

            # Dettaglio espandibile
            with st.expander("Dettagli"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Punti di forza**")
                    if g["forza"]:
                        for f in g["forza"]:
                            stars = "⭐" * f["val"] + "☆" * (5 - f["val"])
                            st.markdown(f"• {f['tag']} {stars}")
                    else:
                        st.caption("Nessuno inserito")
                with c2:
                    st.markdown("**Punti deboli**")
                    if g["debolezza"]:
                        for d in g["debolezza"]:
                            stars = "⭐" * d["val"] + "☆" * (5 - d["val"])
                            st.markdown(f"• {d['tag']} {stars}")
                    else:
                        st.caption("Nessuno inserito")
                if g["note"]:
                    st.markdown(f"**Note:** {g['note']}")

# ==================== TAB TATTICA ====================
with tab_tattica:
    st.subheader("Formazione 5-1")

    # Selezione giocatrici per posizioni
    st.markdown("**Seleziona le giocatrici per le 6 posizioni:**")
    cols = st.columns(6)
    giocatrici_attive = [g for g in data["giocatrici"] if g["stato"] == "attiva"]
    nomi_giocatrici = {g["id"]: f"#{g['numero']} {g['nome']} ({g['ruolo'][:3]})" for g in giocatrici_attive}

    for i, col in enumerate(cols):
        with col:
            st.markdown(f"<div style='text-align:center; font-weight:600; margin-bottom:4px;'>Pos {i+1}</div>", unsafe_allow_html=True)
            sel = st.selectbox(
                f"Pos{i+1}",
                options=list(nomi_giocatrici.keys()),
                format_func=lambda x: nomi_giocatrici.get(x, ""),
                index=list(nomi_giocatrici.keys()).index(data["formazione"][i]) if data["formazione"][i] in nomi_giocatrici else 0,
                key=f"pos_{i}",
                label_visibility="collapsed"
            )
            data["formazione"][i] = sel

    # Selezione libero
    st.markdown("**Libero:**")
    libero_sel = st.selectbox(
        "Libero",
        options=list(nomi_giocatrici.keys()),
        format_func=lambda x: nomi_giocatrici.get(x, ""),
        index=list(nomi_giocatrici.keys()).index(data["libero_id"]) if data["libero_id"] in nomi_giocatrici else 0,
        key="libero_sel",
        label_visibility="collapsed"
    )
    data["libero_id"] = libero_sel

    if st.button("💾 Salva formazione", type="primary"):
        save_data(data)
        st.success("Formazione salvata!")

    # Campo visivo
    st.markdown("---")
    st.markdown("**Visualizzazione campo**")

    rot = st.session_state.current_rot
    rot_options = list(range(1, 7))
    new_rot = st.segmented_control("Rotazione", rot_options, default=rot, key="rot_control")
    if new_rot != rot:
        st.session_state.current_rot = new_rot
        st.rerun()

    # Disegna campo con HTML/CSS
    positions = [
        {"x": 75, "y": 85}, {"x": 25, "y": 85},
        {"x": 75, "y": 55}, {"x": 25, "y": 55},
        {"x": 50, "y": 55}, {"x": 50, "y": 85},
    ]
    rot_offset = st.session_state.current_rot - 1
    rotated_pos = positions[rot_offset:] + positions[:rot_offset]

    court_html = '<div class="court-container">'
    court_html += '<div class="court-line" style="top:33.33%;"></div>'
    court_html += '<div class="court-line" style="top:66.66%;"></div>'
    court_html += '<div class="court-net"></div>'

    for idx, pid in enumerate(data["formazione"]):
        g = next((x for x in data["giocatrici"] if x["id"] == pid), None)
        if g:
            pos = rotated_pos[idx]
            is_libero = (pid == data["libero_id"])
            court_html += f'<div class="player-dot{" libero" if is_libero else ""}" style="left:{pos["x"]-5}%; top:{pos["y"]-5}%;" title="{g["nome"]} {g["cognome"]} ({g["ruolo"]})">{g["numero"]}</div>'

    court_html += '</div>'
    st.markdown(court_html, unsafe_allow_html=True)

    # Legenda
    st.markdown("""
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:16px; justify-content:center;">
        <span class="badge badge-palleggiatrice">Palleggiatrice</span>
        <span class="badge badge-schiacciatrice">Schiacciatrice</span>
        <span class="badge badge-centrale">Centrale</span>
        <span class="badge badge-opposto">Opposto</span>
        <span class="badge badge-libero">Libero</span>
    </div>
    """, unsafe_allow_html=True)

# ==================== TAB PARTITA LIVE ====================
with tab_partita:
    match = st.session_state.match

    # Scoreboard
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:14px; color:#636366;'>La Nostra</div><div style='font-size:56px; font-weight:700; font-variant-numeric:tabular-nums;'>{match['us']}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align:center; padding-top:20px;'><div style='font-size:13px; color:#8e8e93;'>SET {match['set']}</div><div style='font-size:24px; color:#c7c7cc;'>-</div><div style='font-size:13px; color:#8e8e93; margin-top:4px;'>({match['sets_us']}-{match['sets_them']})</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:14px; color:#636366;'>Avversario</div><div style='font-size:56px; font-weight:700; font-variant-numeric:tabular-nums;'>{match['them']}</div></div>", unsafe_allow_html=True)

    # Controlli
    c_p1, c_p2, c_rot, c_to = st.columns(4)
    with c_p1:
        if st.button("➕ Punto nostro", type="primary", use_container_width=True):
            match["us"] += 1
            if match["us"] >= 25 and match["us"] - match["them"] >= 2:
                end_set(True)
            st.rerun()
    with c_p2:
        if st.button("➕ Punto loro", use_container_width=True):
            match["them"] += 1
            if match["them"] >= 25 and match["them"] - match["us"] >= 2:
                end_set(False)
            st.rerun()
    with c_rot:
        if st.button("🔄 Rotazione", use_container_width=True):
            f = data["formazione"]
            f.append(f.pop(0))
            save_data(data)
            st.rerun()
    with c_to:
        if st.button("⏸️ Time-out", use_container_width=True):
            st.toast("Time-out registrato!")

    def end_set(we_won):
        if we_won:
            match["sets_us"] += 1
        else:
            match["sets_them"] += 1

        # Salva stats della partita
        partita = {
            "data": datetime.now().isoformat(),
            "set": match["set"],
            "risultato": f"{match['us']}-{match['them']}",
            "vinto": we_won,
            "stats": dict(st.session_state.live_stats)
        }
        data["partite"].append(partita)

        # Aggiorna stats totali
        for pid, stats in st.session_state.live_stats.items():
            pid_str = str(pid)
            if pid_str not in data["stats_totali"]:
                data["stats_totali"][pid_str] = {"attPos": 0, "attNeg": 0, "muro": 0, "battAce": 0}
            for k, v in stats.items():
                data["stats_totali"][pid_str][k] = data["stats_totali"][pid_str].get(k, 0) + v

        match["set"] += 1
        match["us"] = 0
        match["them"] = 0

        if match["sets_us"] == 3 or match["sets_them"] == 3:
            st.success(f"Partita finita! {match['sets_us']}-{match['sets_them']}")
            match["set"] = 1
            match["sets_us"] = 0
            match["sets_them"] = 0
            st.session_state.live_stats = {}

        save_data(data)

    # Stats live
    st.markdown("---")
    st.subheader("Statistiche giocatrici in campo")

    on_field = [g for g in data["giocatrici"] if g["id"] in data["formazione"]]
    if not on_field:
        st.info("Nessuna giocatrice in campo. Configura la formazione nella scheda Tattica.")
    else:
        for g in on_field:
            pid = g["id"]
            if pid not in st.session_state.live_stats:
                st.session_state.live_stats[pid] = {"attPos": 0, "attNeg": 0, "attErr": 0, "muro": 0, "battAce": 0, "battErr": 0}
            s = st.session_state.live_stats[pid]

            with st.container():
                col_name, col_att_pos, col_att_neg, col_muro = st.columns([3, 1, 1, 1])
                with col_name:
                    st.markdown(f"**#{g['numero']}** {g['nome']} <span style='font-size:12px;color:#8e8e93;'>({g['ruolo']})</span>", unsafe_allow_html=True)
                with col_att_pos:
                    c_btn, c_val = st.columns([1, 1])
                    with c_btn:
                        if st.button("➕", key=f"ap_{pid}"):
                            s["attPos"] += 1
                            st.rerun()
                    with c_val:
                        st.markdown(f"<div style='text-align:center; font-weight:700; font-size:18px;'>{s['attPos']}</div>", unsafe_allow_html=True)
                with col_att_neg:
                    c_btn, c_val = st.columns([1, 1])
                    with c_btn:
                        if st.button("➖", key=f"an_{pid}"):
                            s["attNeg"] += 1
                            st.rerun()
                    with c_val:
                        st.markdown(f"<div style='text-align:center; font-weight:700; font-size:18px;'>{s['attNeg']}</div>", unsafe_allow_html=True)
                with col_muro:
                    c_btn, c_val = st.columns([1, 1])
                    with c_btn:
                        if st.button("🧱", key=f"mu_{pid}"):
                            s["muro"] += 1
                            st.rerun()
                    with c_val:
                        st.markdown(f"<div style='text-align:center; font-weight:700; font-size:18px;'>{s['muro']}</div>", unsafe_allow_html=True)

# ==================== TAB STATISTICHE ====================
with tab_stats:
    st.subheader("Riepilogo stagione")

    partite = data.get("partite", [])
    vinte = sum(1 for p in partite if p.get("vinto"))
    perse = len(partite) - vinte

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number" style="color:#1c1c1e;">{len(partite)}</div>
            <div style="font-size:13px; color:#8e8e93; margin-top:4px;">Partite giocate</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number" style="color:#34c759;">{vinte}</div>
            <div style="font-size:13px; color:#8e8e93; margin-top:4px;">Vinte</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number" style="color:#ff3b30;">{perse}</div>
            <div style="font-size:13px; color:#8e8e93; margin-top:4px;">Perse</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Classifica giocatrici — Attacchi positivi")

    stats_totali = data.get("stats_totali", {})
    if not stats_totali:
        st.info("Nessuna statistica registrata. Inizia una partita per raccogliere dati.")
    else:
        leaderboard = []
        for pid_str, stats in stats_totali.items():
            g = next((x for x in data["giocatrici"] if str(x["id"]) == pid_str), None)
            if g:
                leaderboard.append({
                    "nome": f"{g['nome']} #{g['numero']}",
                    "attPos": stats.get("attPos", 0),
                    "attNeg": stats.get("attNeg", 0),
                    "muro": stats.get("muro", 0),
                    "totale": stats.get("attPos", 0) + stats.get("muro", 0)
                })

        leaderboard.sort(key=lambda x: x["attPos"], reverse=True)
        max_val = max((x["attPos"] for x in leaderboard), default=1)

        for item in leaderboard:
            pct = (item["attPos"] / max_val) * 100
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <div style="width:120px; font-size:14px; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{item['nome']}</div>
                <div style="flex:1; height:12px; background:#f2f2f7; border-radius:6px; overflow:hidden;">
                    <div style="width:{pct}%; height:100%; background:linear-gradient(90deg, #007aff, #5ac8fa); border-radius:6px;"></div>
                </div>
                <div style="width:30px; text-align:right; font-size:14px; font-weight:700; font-variant-numeric:tabular-nums;">{item['attPos']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Tabella completa
        st.markdown("---")
        st.subheader("Statistiche dettagliate")
        import pandas as pd
        df = pd.DataFrame(leaderboard)
        if not df.empty:
            df = df[["nome", "attPos", "attNeg", "muro", "totale"]]
            df.columns = ["Giocatrice", "Attacchi +", "Attacchi -", "Muri", "Totale"]
            st.dataframe(df, use_container_width=True, hide_index=True)
