import streamlit as st
import json
import os
from datetime import datetime
import base64

st.set_page_config(
    page_title="Volley Team Manager",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════
# CSS INJECTED VIA st.html() - Streamlit 1.42+ compatible
# ═══════════════════════════════════════════════════════════════════════
css_block = """
<style>
  /* Sfondo app */
  .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%) !important; }

  /* Header animato */
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  /* Card base */
  .v-card {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    transition: all 0.4s ease;
  }
  .v-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 0 60px rgba(255,107,107,0.1);
    border-color: rgba(255,107,107,0.3);
  }

  /* Foto area */
  .v-photo-wrap {
    height: 180px;
    background: linear-gradient(135deg, rgba(255,107,107,0.15), rgba(72,219,251,0.15));
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  /* Foto cerchio */
  .v-photo {
    width: 110px; height: 110px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid rgba(255,255,255,0.2);
    box-shadow: 0 0 30px rgba(255,107,107,0.3);
    transition: all 0.4s ease;
  }
  .v-card:hover .v-photo {
    box-shadow: 0 0 50px rgba(255,107,107,0.5), 0 0 80px rgba(72,219,251,0.2);
    transform: scale(1.08);
  }

  /* Placeholder foto */
  .v-photo-placeholder {
    width: 110px; height: 110px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(72,219,251,0.2));
    display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem;
    border: 3px solid rgba(255,255,255,0.15);
    box-shadow: 0 0 25px rgba(255,107,107,0.2);
  }

  /* Numero maglia */
  .v-jersey {
    position: absolute;
    top: 10px; right: 10px;
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6b6b, #feca57);
    color: #0a0a0f;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800;
    box-shadow: 0 4px 15px rgba(255,107,107,0.5);
    border: 2px solid rgba(255,255,255,0.3);
  }

  /* Corpo card */
  .v-body { padding: 14px 18px 18px 18px; }
  .v-name { font-size: 17px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
  .v-meta { font-size: 11px; color: #8a8a9a; margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }

  /* Badge */
  .v-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .v-badge-pal { background: rgba(33,150,243,0.2); color: #64b5f6; border: 1px solid rgba(33,150,243,0.3); }
  .v-badge-sch { background: rgba(233,30,99,0.2); color: #f48fb1; border: 1px solid rgba(233,30,99,0.3); }
  .v-badge-cen { background: rgba(76,175,80,0.2); color: #81c784; border: 1px solid rgba(76,175,80,0.3); }
  .v-badge-opp { background: rgba(156,39,176,0.2); color: #ce93d8; border: 1px solid rgba(156,39,176,0.3); }
  .v-badge-lib { background: rgba(255,152,0,0.2); color: #ffb74d; border: 1px solid rgba(255,152,0,0.3); }
  .v-badge-ok { background: rgba(76,175,80,0.15); color: #81c784; border: 1px solid rgba(76,175,80,0.25); }
  .v-badge-inf { background: rgba(244,67,54,0.15); color: #ef5350; border: 1px solid rgba(244,67,54,0.25); }

  .v-note { font-size: 11px; color: #6a6a7a; margin-top: 8px; font-style: italic; line-height: 1.4; }

  /* Stat box */
  .v-statbox {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
  }
  .v-statbox:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 40px rgba(255,107,107,0.08);
  }
  .v-statnum { font-size: 3rem; font-weight: 800; line-height: 1; }
  .v-statlab { font-size: 11px; color: #6a6a7a; margin-top: 8px; text-transform: uppercase; letter-spacing: 2px; }

  /* Scoreboard */
  .v-score {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
  }
  .v-score::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,107,107,0.5), rgba(254,202,87,0.5), rgba(72,219,251,0.5), transparent);
  }
  .v-scorenum { font-size: 64px; font-weight: 800; line-height: 1; }
  .v-scoreteam { font-size: 13px; font-weight: 600; color: #7a7a8a; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 10px; }

  @keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 20px rgba(255,107,107,0.15), 0 8px 32px rgba(0,0,0,0.3); }
    50% { box-shadow: 0 0 40px rgba(255,107,107,0.3), 0 8px 32px rgba(0,0,0,0.3); }
  }
  .v-pulse { animation: pulseGlow 3s ease-in-out infinite; }

  /* Divider */
  .v-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,107,107,0.4), rgba(254,202,87,0.4), rgba(72,219,251,0.4), transparent);
    margin: 20px 0;
    border: none;
  }

  /* Leaderboard */
  .v-leader {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    transition: all 0.2s ease;
  }
  .v-leader:hover {
    background: rgba(255,255,255,0.06);
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
  }
  .v-leadername { width: 130px; font-size: 13px; font-weight: 600; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .v-leaderval { width: 32px; text-align: right; font-size: 14px; font-weight: 700; color: #feca57; }

  /* Barra stat */
  .v-barwrap { flex: 1; height: 10px; background: rgba(255,255,255,0.06); border-radius: 5px; overflow: hidden; }
  .v-bar { height: 100%; background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb); border-radius: 5px; transition: width 0.6s ease; }

  /* Stelle */
  .v-star-on { color: #feca57; text-shadow: 0 0 6px rgba(254,202,87,0.4); }
  .v-star-off { color: rgba(255,255,255,0.1); }

  /* Campo */
  .v-court {
    position: relative;
    width: 320px;
    height: 580px;
    border: 2px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    margin: 0 auto;
    background: linear-gradient(180deg, rgba(255,107,107,0.05), rgba(72,219,251,0.05));
    box-shadow: 0 0 50px rgba(255,107,107,0.06), inset 0 0 50px rgba(0,0,0,0.2);
  }
  .v-courtline { position: absolute; left: 0; right: 0; border-top: 2px dashed rgba(255,255,255,0.12); }
  .v-courtnet { position: absolute; top: 50%; left: 0; right: 0; border-top: 3px solid rgba(255,255,255,0.35); box-shadow: 0 0 15px rgba(255,255,255,0.15); }
  .v-dot {
    position: absolute;
    width: 44px; height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6b6b, #feca57);
    color: #0a0a0f;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 800;
    box-shadow: 0 4px 18px rgba(255,107,107,0.5), 0 0 25px rgba(255,107,107,0.2);
    border: 2px solid rgba(255,255,255,0.25);
    transition: all 0.3s ease;
  }
  .v-dot:hover { transform: scale(1.2); box-shadow: 0 6px 25px rgba(255,107,107,0.7); }
  .v-dot-lib { background: linear-gradient(135deg, #48dbfb, #0abde3); box-shadow: 0 4px 18px rgba(72,219,251,0.5), 0 0 25px rgba(72,219,251,0.2); }
  .v-dot-lib:hover { box-shadow: 0 6px 25px rgba(72,219,251,0.7); }
</style>
"""

# Inietta CSS con st.html() - funziona con Streamlit 1.42+
try:
    st.html(css_block)
except:
    st.markdown(css_block, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# FUNZIONI
# ═══════════════════════════════════════════════════════════════════════
DATA_FILE = "volley_data.json"
PHOTO_DIR = "player_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "squadra": {"nome": "Volley Club", "categoria": "Serie B2 Femminile", "girone": "Girone A", "allenatore": ""},
        "giocatrici": [
            {"id": 1, "nome": "Giulia", "cognome": "Bianchi", "numero": 10, "ruolo": "schiacciatrice", "altezza": 178, "stato": "attiva", "foto": "", "forza": [{"tag": "attacco potente", "val": 4}, {"tag": "muro", "val": 3}], "debolezza": [{"tag": "ricezione", "val": 2}], "note": "Migliora in allenamento"},
            {"id": 2, "nome": "Sara", "cognome": "Rossi", "numero": 7, "ruolo": "palleggiatrice", "altezza": 172, "stato": "attiva", "foto": "", "forza": [{"tag": "palleggio", "val": 5}, {"tag": "intelligenza tattica", "val": 4}], "debolezza": [{"tag": "attacco", "val": 2}], "note": "Capitano"},
            {"id": 3, "nome": "Martina", "cognome": "Verdi", "numero": 3, "ruolo": "libero", "altezza": 165, "stato": "attiva", "foto": "", "forza": [{"tag": "difesa", "val": 5}, {"tag": "ricezione", "val": 5}], "debolezza": [{"tag": "attacco", "val": 1}], "note": ""},
            {"id": 4, "nome": "Anna", "cognome": "Neri", "numero": 14, "ruolo": "centrale", "altezza": 185, "stato": "attiva", "foto": "", "forza": [{"tag": "muro", "val": 5}, {"tag": "altezza", "val": 5}], "debolezza": [{"tag": "difesa", "val": 2}], "note": ""},
            {"id": 5, "nome": "Chiara", "cognome": "Gialli", "numero": 9, "ruolo": "opposto", "altezza": 180, "stato": "infortunata", "foto": "", "forza": [{"tag": "attacco", "val": 4}, {"tag": "battuta", "val": 4}], "debolezza": [{"tag": "difesa", "val": 2}], "note": "Infortunio alla caviglia"},
            {"id": 6, "nome": "Elena", "cognome": "Blu", "numero": 5, "ruolo": "schiacciatrice", "altezza": 176, "stato": "attiva", "foto": "", "forza": [{"tag": "difesa", "val": 4}, {"tag": "ricezione", "val": 4}], "debolezza": [{"tag": "muro", "val": 2}], "note": ""}
        ],
        "formazione": [2, 4, 1, 6, 5, 3],
        "libero_id": 3,
        "partite": [],
        "stats_totali": {}
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_photo(player_id, uploaded_file):
    if uploaded_file is None:
        return ""
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        return ""
    filepath = os.path.join(PHOTO_DIR, f"player_{player_id}{ext}")
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def get_photo_base64(filepath):
    if not filepath or not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        ext = os.path.splitext(filepath)[1].lower()
        mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png" if ext == ".png" else "image/webp"
        return f"data:{mime};base64,{base64.b64encode(data).decode()}"
    except:
        return ""

def get_badge_class(ruolo):
    return {"palleggiatrice": "v-badge-pal", "schiacciatrice": "v-badge-sch", "centrale": "v-badge-cen", "opposto": "v-badge-opp", "libero": "v-badge-lib"}.get(ruolo, "v-badge-pal")

def get_emoji(ruolo):
    return {"palleggiatrice": "🏐", "schiacciatrice": "💥", "centrale": "🧱", "opposto": "⚡", "libero": "🛡️"}.get(ruolo, "🏐")

def build_photo_html(player):
    foto_b64 = get_photo_base64(player.get("foto", ""))
    if foto_b64:
        return f'<img src="{foto_b64}" class="v-photo" alt="{player["nome"]}">'
    else:
        return f'<div class="v-photo-placeholder">{get_emoji(player["ruolo"])}</div>'

# Session state
if "data" not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.current_rot = 1
    st.session_state.match = {"set": 1, "us": 0, "them": 0, "sets_us": 0, "sets_them": 0}
    st.session_state.live_stats = {}

data = st.session_state.data
RUOLI_OPTIONS = ["palleggiatrice", "schiacciatrice", "centrale", "opposto", "libero"]

# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; margin-bottom:2px;">
    <div style="font-size:4rem; margin-bottom:-10px;">🏐</div>
</div>
<div style="text-align:center; font-size:2.8rem; font-weight:800; background:linear-gradient(90deg,#ff6b6b,#feca57,#48dbfb,#ff9ff3); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:-2px; margin-bottom:4px;">Volley Team Manager</div>
<div style="text-align:center; font-size:1rem; color:#7a7a8a; margin-bottom:2rem; letter-spacing:2px; text-transform:uppercase;">""" + data["squadra"]["categoria"] + """ — Stagione 2025/26</div>
<div class="v-divider"></div>
""", unsafe_allow_html=True)

tab_roster, tab_tattica, tab_partita, tab_stats = st.tabs(["👥 Roster", "📐 Tattica", "🏆 Partita Live", "📊 Statistiche"])

# TAB ROSTER
with tab_roster:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#ffffff;'>Rosa squadra</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px; color:#6a6a7a;'>" + str(len(data['giocatrici'])) + " giocatrici registrate</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Nuova giocatrice", type="primary", use_container_width=True):
            st.session_state.show_add_player = True

    if st.session_state.get("show_add_player", False):
        with st.container():
            st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:22px; font-weight:700; color:#ff6b6b; margin-bottom:20px;'>Nuova giocatrice</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                nome = st.text_input("Nome *", key="new_nome", placeholder="es. Giulia")
            with c2:
                cognome = st.text_input("Cognome *", key="new_cognome", placeholder="es. Bianchi")
            with c3:
                numero = st.number_input("Numero maglia *", min_value=1, max_value=99, value=10, key="new_numero")
            c4, c5 = st.columns(2)
            with c4:
                ruolo = st.selectbox("Ruolo", RUOLI_OPTIONS, key="new_ruolo")
            with c5:
                altezza = st.number_input("Altezza (cm)", min_value=140, max_value=210, value=170, key="new_altezza")
            st.markdown("<div style='font-size:13px; color:#7a7a8a; margin-bottom:6px;'>Foto giocatrice</div>", unsafe_allow_html=True)
            foto_file = st.file_uploader("Carica foto", type=["jpg", "jpeg", "png", "webp"], key="new_foto", label_visibility="collapsed")
            if foto_file:
                st.image(foto_file, width=120)
            forza_tags = st.text_input("Punti di forza (separati da virgola)", placeholder="es. attacco potente, muro, difesa", key="new_forza")
            debolezza_tags = st.text_input("Punti deboli (separati da virgola)", placeholder="es. ricezione, battuta", key="new_debolezza")
            note = st.text_area("Note", placeholder="Osservazioni tecniche, caratteriali, infortuni...", key="new_note")
            c_save, c_cancel = st.columns(2)
            with c_save:
                if st.button("Salva giocatrice", type="primary", use_container_width=True):
                    if nome and cognome:
                        new_id = max([g["id"] for g in data["giocatrici"]], default=0) + 1
                        forza_list = [{"tag": t.strip(), "val": 3} for t in forza_tags.split(",") if t.strip()]
                        debolezza_list = [{"tag": t.strip(), "val": 3} for t in debolezza_tags.split(",") if t.strip()]
                        foto_path = save_photo(new_id, foto_file)
                        data["giocatrici"].append({
                            "id": new_id, "nome": nome, "cognome": cognome, "numero": int(numero),
                            "ruolo": ruolo, "altezza": int(altezza), "stato": "attiva",
                            "foto": foto_path, "forza": forza_list, "debolezza": debolezza_list, "note": note
                        })
                        save_data(data)
                        st.session_state.show_add_player = False
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Inserisci nome e cognome")
            with c_cancel:
                if st.button("Annulla", use_container_width=True):
                    st.session_state.show_add_player = False
                    st.rerun()
            st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        filtro_ruolo = st.multiselect("Filtra per ruolo", RUOLI_OPTIONS, default=[], key="filtro_ruolo")
    with c_f2:
        filtro_stato = st.multiselect("Filtra per stato", ["attiva", "infortunata", "squalificata"], default=["attiva"], key="filtro_stato")

    giocatrici_visibili = [g for g in data["giocatrici"]
                          if (not filtro_ruolo or g["ruolo"] in filtro_ruolo)
                          and (not filtro_stato or g["stato"] in filtro_stato)]

    if not giocatrici_visibili:
        st.info("Nessuna giocatrice trovata.")

    cols_per_row = 3
    for row_idx in range(0, len(giocatrici_visibili), cols_per_row):
        row_giocatrici = giocatrici_visibili[row_idx:row_idx + cols_per_row]
        cols = st.columns(len(row_giocatrici))
        for col_idx, g in enumerate(row_giocatrici):
            with cols[col_idx]:
                photo_html = build_photo_html(g)
                badge_cls = get_badge_class(g["ruolo"])
                stato_cls = "v-badge-ok" if g["stato"] == "attiva" else "v-badge-inf"
                stato_txt = "OK " + g["stato"] if g["stato"] == "attiva" else "INF " + g["stato"]
                note_block = ""
                if g["note"]:
                    note_preview = g["note"][:70] + ("..." if len(g["note"]) > 70 else "")
                    note_block = '<div class="v-note">' + note_preview + '</div>'

                card = (
                    '<div class="v-card">'
                    '  <div class="v-photo-wrap">'
                    '    <div class="v-jersey">' + str(g['numero']) + '</div>'
                    '    ' + photo_html +
                    '  </div>'
                    '  <div class="v-body">'
                    '    <div class="v-name">' + g['nome'] + ' ' + g['cognome'] + '</div>'
                    '    <div class="v-meta">'
                    '      <span class="v-badge ' + badge_cls + '">' + g['ruolo'] + '</span>'
                    '      <span style="color:#505060;">|</span>'
                    '      <span>' + str(g['altezza']) + 'cm</span>'
                    '      <span style="color:#505060;">|</span>'
                    '      <span class="v-badge ' + stato_cls + '">' + stato_txt + '</span>'
                    '    </div>'
                    '    ' + note_block +
                    '  </div>'
                    '</div>'
                )
                st.markdown(card, unsafe_allow_html=True)

                foto_key = "foto_" + str(g['id'])
                uploaded = st.file_uploader("Foto", type=["jpg", "jpeg", "png", "webp"], key=foto_key, label_visibility="collapsed")
                if uploaded:
                    g["foto"] = save_photo(g["id"], uploaded)
                    save_data(data)
                    st.rerun()

                if st.button("Elimina", key="del_" + str(g['id']), use_container_width=True):
                    data["giocatrici"] = [x for x in data["giocatrici"] if x["id"] != g["id"]]
                    if g.get("foto") and os.path.exists(g["foto"]):
                        os.remove(g["foto"])
                    save_data(data)
                    st.rerun()

                with st.expander("Dettagli - " + g['nome'] + ' ' + g['cognome']):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("<div style='font-size:15px; font-weight:700; color:#ff6b6b;'>Punti di forza</div>", unsafe_allow_html=True)
                        if g["forza"]:
                            for f in g["forza"]:
                                stars = "<span class='v-star-on'>" + "&#9733;" * f["val"] + "</span><span class='v-star-off'>" + "&#9734;" * (5 - f["val"]) + "</span>"
                                st.markdown("<div style='margin-bottom:6px; font-size:14px; color:#d0d0e0;'>- <strong>" + f['tag'] + "</strong> " + stars + "</div>", unsafe_allow_html=True)
                        else:
                            st.caption("Nessun punto di forza")
                    with c2:
                        st.markdown("<div style='font-size:15px; font-weight:700; color:#48dbfb;'>Punti deboli</div>", unsafe_allow_html=True)
                        if g["debolezza"]:
                            for d in g["debolezza"]:
                                stars = "<span class='v-star-on'>" + "&#9733;" * d["val"] + "</span><span class='v-star-off'>" + "&#9734;" * (5 - d["val"]) + "</span>"
                                st.markdown("<div style='margin-bottom:6px; font-size:14px; color:#d0d0e0;'>- <strong>" + d['tag'] + "</strong> " + stars + "</div>", unsafe_allow_html=True)
                        else:
                            st.caption("Nessun punto debole")
                    if g["note"]:
                        st.markdown("<div style='margin-top:12px; padding:12px; background:rgba(255,255,255,0.04); border-radius:10px; border-left:3px solid #feca57;'><div style='font-size:11px; color:#7a7a8a; margin-bottom:4px; text-transform:uppercase;'>Note allenatore</div><div style='font-size:14px; color:#c0c0d0;'" + g['note'] + "</div></div>", unsafe_allow_html=True)

# TAB TATTICA
with tab_tattica:
    st.markdown("<div style='font-size:24px; font-weight:700; color:#ffffff; margin-bottom:4px;'>Formazione Tattica</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#6a6a7a; margin-bottom:24px;'>Configura le 6 posizioni in campo e il libero</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:15px; font-weight:600; color:#feca57; margin-bottom:14px;'>Seleziona le giocatrici per le 6 posizioni:</div>", unsafe_allow_html=True)
    cols = st.columns(6)
    giocatrici_attive = [g for g in data["giocatrici"] if g["stato"] == "attiva"]
    nomi_giocatrici = {g["id"]: "#" + str(g["numero"]) + " " + g["nome"] for g in giocatrici_attive}

    for i, col in enumerate(cols):
        with col:
            st.markdown("<div style='text-align:center; font-weight:700; color:#ff6b6b; margin-bottom:8px; font-size:13px;'>POS " + str(i+1) + "</div>", unsafe_allow_html=True)
            sel = st.selectbox("Pos" + str(i+1), options=list(nomi_giocatrici.keys()), format_func=lambda x: nomi_giocatrici.get(x, ""), index=list(nomi_giocatrici.keys()).index(data["formazione"][i]) if data["formazione"][i] in nomi_giocatrici else 0, key="pos_" + str(i), label_visibility="collapsed")
            data["formazione"][i] = sel

    st.markdown("<div style='font-size:15px; font-weight:600; color:#48dbfb; margin:20px 0 14px;'>Libero:</div>", unsafe_allow_html=True)
    libero_sel = st.selectbox("Libero", options=list(nomi_giocatrici.keys()), format_func=lambda x: nomi_giocatrici.get(x, ""), index=list(nomi_giocatrici.keys()).index(data["libero_id"]) if data["libero_id"] in nomi_giocatrici else 0, key="libero_sel", label_visibility="collapsed")
    data["libero_id"] = libero_sel

    c_save, _ = st.columns([1, 3])
    with c_save:
        if st.button("Salva formazione", type="primary", use_container_width=True):
            save_data(data)
            st.success("Formazione salvata!")

    st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:20px; font-weight:700; color:#ffffff; margin-bottom:20px; text-align:center;'>Campo da gioco</div>", unsafe_allow_html=True)

    rot = st.session_state.current_rot
    rot_options = list(range(1, 7))
    new_rot = st.segmented_control("Rotazione", rot_options, default=rot, key="rot_control")
    if new_rot != rot:
        st.session_state.current_rot = new_rot
        st.rerun()

    positions = [{"x": 75, "y": 85}, {"x": 25, "y": 85}, {"x": 75, "y": 55}, {"x": 25, "y": 55}, {"x": 50, "y": 55}, {"x": 50, "y": 85}]
    rot_offset = st.session_state.current_rot - 1
    rotated_pos = positions[rot_offset:] + positions[:rot_offset]

    court_html = '<div class="v-court">'
    court_html += '<div class="v-courtline" style="top:33.33%;"></div>'
    court_html += '<div class="v-courtline" style="top:66.66%;"></div>'
    court_html += '<div class="v-courtnet"></div>'
    for idx, pid in enumerate(data["formazione"]):
        g = next((x for x in data["giocatrici"] if x["id"] == pid), None)
        if g:
            pos = rotated_pos[idx]
            lib_class = " v-dot-lib" if (pid == data["libero_id"]) else ""
            court_html += '<div class="v-dot' + lib_class + '" style="left:' + str(pos["x"]-6) + '%; top:' + str(pos["y"]-6) + '%;">' + str(g["numero"]) + '</div>'
    court_html += '</div>'
    st.markdown(court_html, unsafe_allow_html=True)

    st.markdown("<div style='display:flex; gap:10px; flex-wrap:wrap; margin-top:24px; justify-content:center;'><span class='v-badge v-badge-pal'>Palleggiatrice</span><span class='v-badge v-badge-sch'>Schiacciatrice</span><span class='v-badge v-badge-cen'>Centrale</span><span class='v-badge v-badge-opp'>Opposto</span><span class='v-badge v-badge-lib'>Libero</span></div>", unsafe_allow_html=True)

# TAB PARTITA LIVE
with tab_partita:
    match = st.session_state.match
    st.markdown("<div style='font-size:24px; font-weight:700; color:#ffffff; margin-bottom:4px;'>Partita in corso</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#6a6a7a; margin-bottom:24px;'>Set " + str(match['set']) + " di 5 - Parziale: " + str(match['sets_us']) + "-" + str(match['sets_them']) + "</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<div class='v-score v-pulse'><div class='v-scoreteam'>LA NOSTRA</div><div class='v-scorenum' style='color:#ff6b6b; text-shadow:0 0 40px rgba(255,107,107,0.5);'>" + str(match['us']) + "</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='text-align:center; padding-top:36px;'><div style='font-size:13px; color:#6a6a7a; font-weight:600; text-transform:uppercase; letter-spacing:2px;'>SET</div><div style='font-size:32px; font-weight:800; color:#feca57; text-shadow:0 0 20px rgba(254,202,87,0.3);'>" + str(match['set']) + "</div><div style='font-size:12px; color:#505060; margin-top:6px;'>(" + str(match['sets_us']) + "-" + str(match['sets_them']) + ")</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='v-score'><div class='v-scoreteam'>AVVERSARIO</div><div class='v-scorenum' style='color:#48dbfb; text-shadow:0 0 40px rgba(72,219,251,0.5);'>" + str(match['them']) + "</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c_p1, c_p2, c_rot, c_to = st.columns(4)
    with c_p1:
        if st.button("PUNTO NOSTRO", type="primary", use_container_width=True):
            match["us"] += 1
            if match["us"] >= 25 and match["us"] - match["them"] >= 2:
                end_set(True)
            st.rerun()
    with c_p2:
        if st.button("PUNTO LORO", use_container_width=True):
            match["them"] += 1
            if match["them"] >= 25 and match["them"] - match["us"] >= 2:
                end_set(False)
            st.rerun()
    with c_rot:
        if st.button("ROTAZIONE", use_container_width=True):
            f = data["formazione"]
            f.append(f.pop(0))
            save_data(data)
            st.rerun()
    with c_to:
        if st.button("TIME-OUT", use_container_width=True):
            st.toast("Time-out registrato!")

    def end_set(we_won):
        if we_won:
            match["sets_us"] += 1
            st.balloons()
        else:
            match["sets_them"] += 1
        partita = {"data": datetime.now().isoformat(), "set": match["set"], "risultato": str(match["us"]) + "-" + str(match["them"]), "vinto": we_won, "stats": dict(st.session_state.live_stats)}
        data["partite"].append(partita)
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
            winner = "VITTORIA!" if match["sets_us"] > match["sets_them"] else "SCONFITTA"
            st.success(winner + " Risultato finale: " + str(match["sets_us"]) + "-" + str(match["sets_them"]))
            match["set"] = 1
            match["sets_us"] = 0
            match["sets_them"] = 0
            st.session_state.live_stats = {}
        save_data(data)

    st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:20px; font-weight:700; color:#ffffff; margin-bottom:20px;'>Statistiche giocatrici in campo</div>", unsafe_allow_html=True)

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
                    st.markdown("<div style='font-size:17px; font-weight:700; color:#ffffff;'>#" + str(g['numero']) + " " + g['nome'] + "</div><div style='font-size:12px; color:#6a6a7a;'" + g['ruolo'] + "</div>", unsafe_allow_html=True)
                with col_att_pos:
                    c_btn, c_val = st.columns([1, 1])
                    with c_btn:
                        if st.button("+", key="ap_" + str(pid)):
                            s["attPos"] += 1
                            st.rerun()
                    with c_val:
                        st.markdown("<div style='text-align:center; font-weight:800; font-size:24px; color:#34c759; text-shadow:0 0 15px rgba(52,199,89,0.3);'>" + str(s['attPos']) + "</div>", unsafe_allow_html=True)
                with col_att_neg:
                    c_btn, c_val = st.columns([1, 1])
                    with c_btn:
                        if st.button("-", key="an_" + str(pid)):
                            s["attNeg"] += 1
                            st.rerun()
                    with c_val:
                        st.markdown("<div style='text-align:center; font-weight:800; font-size:24px; color:#ff3b30; text-shadow:0 0 15px rgba(255,59,48,0.3);'>" + str(s['attNeg']) + "</div>", unsafe_allow_html=True)
                with col_muro:
                    c_btn, c_val = st.columns([1, 1])
                    with c_btn:
                        if st.button("M", key="mu_" + str(pid)):
                            s["muro"] += 1
                            st.rerun()
                    with c_val:
                        st.markdown("<div style='text-align:center; font-weight:800; font-size:24px; color:#feca57; text-shadow:0 0 15px rgba(254,202,87,0.3);'>" + str(s['muro']) + "</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# TAB STATISTICHE
with tab_stats:
    st.markdown("<div style='font-size:24px; font-weight:700; color:#ffffff; margin-bottom:4px;'>Riepilogo Stagione</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#6a6a7a; margin-bottom:24px;'>Performance della squadra e classifica giocatrici</div>", unsafe_allow_html=True)

    partite = data.get("partite", [])
    vinte = sum(1 for p in partite if p.get("vinto"))
    perse = len(partite) - vinte

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='v-statbox'><div class='v-statnum' style='color:#ffffff; text-shadow:0 0 30px rgba(255,255,255,0.2);'>" + str(len(partite)) + "</div><div class='v-statlab'>Partite giocate</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='v-statbox'><div class='v-statnum' style='color:#34c759; text-shadow:0 0 30px rgba(52,199,89,0.3);'>" + str(vinte) + "</div><div class='v-statlab'>Vittorie</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='v-statbox'><div class='v-statnum' style='color:#ff3b30; text-shadow:0 0 30px rgba(255,59,48,0.3);'>" + str(perse) + "</div><div class='v-statlab'>Sconfitte</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:20px; font-weight:700; color:#ffffff; margin-bottom:20px;'>Classifica - Attacchi Positivi</div>", unsafe_allow_html=True)

    stats_totali = data.get("stats_totali", {})
    if not stats_totali:
        st.info("Nessuna statistica registrata. Inizia una partita per raccogliere dati.")
    else:
        leaderboard = []
        for pid_str, stats in stats_totali.items():
            g = next((x for x in data["giocatrici"] if str(x["id"]) == pid_str), None)
            if g:
                leaderboard.append({"nome": g['nome'] + " #" + str(g['numero']), "ruolo": g['ruolo'], "attPos": stats.get("attPos", 0), "attNeg": stats.get("attNeg", 0), "muro": stats.get("muro", 0), "totale": stats.get("attPos", 0) + stats.get("muro", 0)})

        leaderboard.sort(key=lambda x: x["attPos"], reverse=True)
        max_val = max((x["attPos"] for x in leaderboard), default=1)

        for i, item in enumerate(leaderboard):
            pct = (item["attPos"] / max_val) * 100
            medal = "1." if i == 0 else "2." if i == 1 else "3." if i == 2 else str(i+1) + "."
            st.markdown("<div class='v-leader'><div style='width:28px; font-size:16px;'>" + medal + "</div><div class='v-leadername'>" + item['nome'] + "</div><div class='v-barwrap'><div class='v-bar' style='width:" + str(pct) + "%'></div></div><div class='v-leaderval'>" + str(item['attPos']) + "</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:20px; font-weight:700; color:#ffffff; margin-bottom:20px;'>Statistiche Dettagliate</div>", unsafe_allow_html=True)

        import pandas as pd
        df = pd.DataFrame(leaderboard)
        if not df.empty:
            df = df[["nome", "ruolo", "attPos", "attNeg", "muro", "totale"]]
            df.columns = ["Giocatrice", "Ruolo", "Attacchi +", "Attacchi -", "Muri", "Totale"]
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
