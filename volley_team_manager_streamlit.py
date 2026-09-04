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
# CSS MIGLIORATO - Card native Streamlit + accenti per ruolo
# ═══════════════════════════════════════════════════════════════════════
css_block = """
<style>
  .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%) !important; }

  /* ACCENTI PER RUOLO */
  :root {
    --pal: #42a5f5; --pal-glow: rgba(66,165,245,0.35);
    --sch: #ef5350; --sch-glow: rgba(239,83,80,0.35);
    --cen: #66bb6a; --cen-glow: rgba(102,187,106,0.35);
    --opp: #ab47bc; --opp-glow: rgba(171,71,188,0.35);
    --lib: #ffa726; --lib-glow: rgba(255,167,38,0.35);
  }

  /* Card container Streamlit hover */
  div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.45) !important;
  }

  /* Header card con gradiente ruolo */
  .card-header {
    height: 100px;
    border-radius: 12px 12px 0 0;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    margin: -16px -16px 0 -16px;
    padding-bottom: 0;
  }
  .card-header-pal { background: linear-gradient(135deg, rgba(66,165,245,0.25), rgba(25,55,95,0.4)); }
  .card-header-sch { background: linear-gradient(135deg, rgba(239,83,80,0.25), rgba(80,25,25,0.4)); }
  .card-header-cen { background: linear-gradient(135deg, rgba(102,187,106,0.25), rgba(25,60,25,0.4)); }
  .card-header-opp { background: linear-gradient(135deg, rgba(171,71,188,0.25), rgba(60,25,70,0.4)); }
  .card-header-lib { background: linear-gradient(135deg, rgba(255,167,38,0.25), rgba(70,50,15,0.4)); }

  /* Foto */
  .card-photo {
    width: 90px; height: 90px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    position: absolute;
    bottom: -45px;
    z-index: 5;
    transition: all 0.3s ease;
  }
  .card-photo:hover { transform: scale(1.1); }

  .card-photo-placeholder {
    width: 90px; height: 90px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    position: absolute;
    bottom: -45px;
    z-index: 5;
    border: 3px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
  }
  .ph-pal { background: linear-gradient(135deg, #1565c0, #42a5f5); }
  .ph-sch { background: linear-gradient(135deg, #c62828, #ef5350); }
  .ph-cen { background: linear-gradient(135deg, #2e7d32, #66bb6a); }
  .ph-opp { background: linear-gradient(135deg, #6a1b9a, #ab47bc); }
  .ph-lib { background: linear-gradient(135deg, #ef6c00, #ffa726); }

  /* Numero maglia */
  .card-jersey {
    position: absolute;
    top: 10px; right: 10px;
    width: 36px; height: 36px;
    border-radius: 50%;
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(8px);
    color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 900;
    border: 2px solid rgba(255,255,255,0.25);
  }

  /* Corpo card */
  .card-body {
    padding: 52px 8px 8px 8px;
    text-align: center;
  }
  .card-name {
    font-size: 17px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.3px;
    margin-bottom: 2px;
  }
  .card-ruolo {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
  }
  .ruolo-pal { color: #90caf9; text-shadow: 0 0 8px var(--pal-glow); }
  .ruolo-sch { color: #ef9a9a; text-shadow: 0 0 8px var(--sch-glow); }
  .ruolo-cen { color: #a5d6a7; text-shadow: 0 0 8px var(--cen-glow); }
  .ruolo-opp { color: #ce93d8; text-shadow: 0 0 8px var(--opp-glow); }
  .ruolo-lib { color: #ffcc80; text-shadow: 0 0 8px var(--lib-glow); }

  .card-meta {
    font-size: 12px;
    color: rgba(255,255,255,0.55);
    margin-bottom: 10px;
  }

  /* Badge stato */
  .badge-stato {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .stato-ok  { background: rgba(76,175,80,0.2);  color: #a5d6a7; border: 1px solid rgba(76,175,80,0.35); }
  .stato-inf { background: rgba(244,67,54,0.2);  color: #ef9a9a; border: 1px solid rgba(244,67,54,0.35); }
  .stato-squ { background: rgba(255,193,7,0.2);   color: #ffe082; border: 1px solid rgba(255,193,7,0.35); }

  /* Tag forza */
  .tag-box {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    margin: 8px 0;
  }
  .tag {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 8px;
    background: rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.65);
    border: 1px solid rgba(255,255,255,0.1);
  }

  /* Note */
  .card-note {
    font-size: 11px;
    color: rgba(255,255,255,0.45);
    font-style: italic;
    margin-top: 8px;
    line-height: 1.4;
    padding: 0 4px;
  }

  /* Barra colore ruolo in fondo */
  .card-bar {
    height: 3px;
    width: 50%;
    margin: 12px auto 0;
    border-radius: 2px;
  }
  .bar-pal { background: linear-gradient(90deg, #1565c0, #42a5f5); box-shadow: 0 0 10px var(--pal-glow); }
  .bar-sch { background: linear-gradient(90deg, #c62828, #ef5350); box-shadow: 0 0 10px var(--sch-glow); }
  .bar-cen { background: linear-gradient(90deg, #2e7d32, #66bb6a); box-shadow: 0 0 10px var(--cen-glow); }
  .bar-opp { background: linear-gradient(90deg, #6a1b9a, #ab47bc); box-shadow: 0 0 10px var(--opp-glow); }
  .bar-lib { background: linear-gradient(90deg, #ef6c00, #ffa726); box-shadow: 0 0 10px var(--lib-glow); }

  /* Stat box */
  .v-statbox {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
  }
  .v-statbox:hover {
    transform: translateY(-4px);
    background: rgba(255,255,255,0.06);
  }
  .v-statnum { font-size: 2.6rem; font-weight: 800; line-height: 1; }
  .v-statlab { font-size: 11px; color: #6a6a7a; margin-top: 6px; text-transform: uppercase; letter-spacing: 2px; }

  /* Divider */
  .v-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,107,107,0.4), rgba(254,202,87,0.4), rgba(72,219,251,0.4), transparent);
    margin: 20px 0;
    border: none;
  }

  /* Court */
  .v-court {
    position: relative;
    width: 320px;
    height: 580px;
    border: 2px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    margin: 0 auto;
    background: linear-gradient(180deg, rgba(255,107,107,0.04), rgba(72,219,251,0.04));
  }
  .v-courtline { position: absolute; left: 5%; right: 5%; border-top: 2px dashed rgba(255,255,255,0.12); }
  .v-courtnet  { position: absolute; top: 50%; left: 0; right: 0; border-top: 3px solid rgba(255,255,255,0.35); box-shadow: 0 0 15px rgba(255,255,255,0.15); }
  .v-dot {
    position: absolute;
    width: 44px; height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6b6b, #feca57);
    color: #0a0a0f;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 800;
    box-shadow: 0 4px 18px rgba(255,107,107,0.5);
    border: 2px solid rgba(255,255,255,0.25);
    transition: all 0.3s ease;
    transform: translate(-50%, -50%);
  }
  .v-dot:hover { transform: translate(-50%, -50%) scale(1.2); }
  .v-dot-lib { background: linear-gradient(135deg, #48dbfb, #0abde3); box-shadow: 0 4px 18px rgba(72,219,251,0.5); }
  .v-dot-lib:hover { transform: translate(-50%, -50%) scale(1.2); box-shadow: 0 6px 25px rgba(72,219,251,0.7); }

  /* Stelle */
  .v-star-on { color: #feca57; text-shadow: 0 0 6px rgba(254,202,87,0.4); }
  .v-star-off { color: rgba(255,255,255,0.1); }

  /* Nascondi label file uploader */
  div[data-testid="stFileUploader"] > label { display: none !important; }
  div[data-testid="stFileUploader"] { margin-top: -8px; }
</style>
"""

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

def get_emoji(ruolo):
    return {"palleggiatrice": "🏐", "schiacciatrice": "💥", "centrale": "🧱", "opposto": "⚡", "libero": "🛡️"}.get(ruolo, "🏐")

ROLE_MAP = {
    "palleggiatrice": ("card-header-pal", "ph-pal", "ruolo-pal", "bar-pal"),
    "schiacciatrice": ("card-header-sch", "ph-sch", "ruolo-sch", "bar-sch"),
    "centrale":       ("card-header-cen", "ph-cen", "ruolo-cen", "bar-cen"),
    "opposto":        ("card-header-opp", "ph-opp", "ruolo-opp", "bar-opp"),
    "libero":         ("card-header-lib", "ph-lib", "ruolo-lib", "bar-lib"),
}

# ═══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
if "data" not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.current_rot = 1

data = st.session_state.data
RUOLI_OPTIONS = ["palleggiatrice", "schiacciatrice", "centrale", "opposto", "libero"]

# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown("""
    <div style="text-align:center; margin-bottom:2px;">
        <div style="font-size:4rem; margin-bottom:-10px;">🏐</div>
    </div>
    <div style="text-align:center; font-size:2.8rem; font-weight:800; background:linear-gradient(90deg,#ff6b6b,#feca57,#48dbfb,#ff9ff3); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:-2px; margin-bottom:4px;">Volley Team Manager</div>
    """, unsafe_allow_html=True)

    c_team1, c_team2 = st.columns(2)
    with c_team1:
        nome_squadra = st.text_input("Nome squadra", value=data["squadra"].get("nome", "Volley Club"), key="team_name")
        data["squadra"]["nome"] = nome_squadra
    with c_team2:
        categoria_squadra = st.text_input("Categoria", value=data["squadra"].get("categoria", "Serie B2 Femminile"), key="team_cat")
        data["squadra"]["categoria"] = categoria_squadra

    if st.button("💾 Salva squadra", type="primary", key="save_team"):
        save_data(data)
        st.success("Squadra salvata!")

    st.markdown("""
    <div style="text-align:center; font-size:1rem; color:#7a7a8a; margin-bottom:2rem; letter-spacing:2px; text-transform:uppercase;">""" + data["squadra"]["categoria"] + """ — Stagione 2025/26</div>
    <div class="v-divider"></div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# STATISTICHE RAPIDE
# ═══════════════════════════════════════════════════════════════════════
attive = sum(1 for g in data["giocatrici"] if g["stato"] == "attiva")
infort = sum(1 for g in data["giocatrici"] if g["stato"] == "infortunata")
tot = len(data["giocatrici"])
alt_media = int(sum(g["altezza"] for g in data["giocatrici"]) / tot) if tot else 0

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f'<div class="v-statbox"><div class="v-statnum" style="color:#42a5f5;">{tot}</div><div class="v-statlab">Giocatrici</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="v-statbox"><div class="v-statnum" style="color:#66bb6a;">{attive}</div><div class="v-statlab">Attive</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="v-statbox"><div class="v-statnum" style="color:#ef5350;">{infort}</div><div class="v-statlab">Infortunate</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown(f'<div class="v-statbox"><div class="v-statnum" style="color:#ffa726;">{alt_media}</div><div class="v-statlab">Altezza media</div></div>', unsafe_allow_html=True)

st.markdown("<div class='v-divider'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════
tab_roster, tab_tattica = st.tabs(["👥 Roster", "📐 Tattica"])

# ═══════════════════════════════════════════════════════════════════════
# TAB ROSTER
# ═══════════════════════════════════════════════════════════════════════
with tab_roster:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div style='font-size:20px; font-weight:700; color:#ffffff;'>Rosa squadra</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px; color:#6a6a7a;'>{len(data['giocatrici'])} giocatrici registrate</div>", unsafe_allow_html=True)
    with col2:
        if st.button("➕ Nuova giocatrice", type="primary", use_container_width=True):
            st.session_state.show_add_player = True

    # ── FORM NUOVA GIOCATRICE ──
    if st.session_state.get("show_add_player", False):
        with st.container(border=True):
            st.markdown("<div style='font-size:20px; font-weight:700; color:#ff6b6b; margin-bottom:16px;'>✨ Nuova giocatrice</div>", unsafe_allow_html=True)
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
            foto_file = st.file_uploader("📷 Foto giocatrice", type=["jpg", "jpeg", "png", "webp"], key="new_foto")
            if foto_file:
                st.image(foto_file, width=120)
            forza_tags = st.text_input("Punti di forza (separati da virgola)", placeholder="es. attacco potente, muro, difesa", key="new_forza")
            debolezza_tags = st.text_input("Punti deboli (separati da virgola)", placeholder="es. ricezione, battuta", key="new_debolezza")
            note = st.text_area("Note", placeholder="Osservazioni tecniche, caratteriali, infortuni...", key="new_note")
            c_save, c_cancel = st.columns(2)
            with c_save:
                if st.button("💾 Salva giocatrice", type="primary", use_container_width=True):
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
                if st.button("❌ Annulla", use_container_width=True):
                    st.session_state.show_add_player = False
                    st.rerun()

    # ── FILTRI ──
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        filtro_ruolo = st.multiselect("Filtra per ruolo", RUOLI_OPTIONS, default=[], key="filtro_ruolo")
    with c_f2:
        filtro_stato = st.multiselect("Filtra per stato", ["attiva", "infortunata", "squalificata"], default=["attiva"], key="filtro_stato")

    giocatrici_visibili = [g for g in data["giocatrici"]
                          if (not filtro_ruolo or g["ruolo"] in filtro_ruolo)
                          and (not filtro_stato or g["stato"] in filtro_stato)]

    if not giocatrici_visibili:
        st.info("Nessuna giocatrice trovata con i filtri selezionati.")

    # ── GRIGLIA CARD ──
    cols_per_row = 3
    for row_idx in range(0, len(giocatrici_visibili), cols_per_row):
        row_giocatrici = giocatrici_visibili[row_idx:row_idx + cols_per_row]
        cols = st.columns(len(row_giocatrici))
        for col_idx, g in enumerate(row_giocatrici):
            with cols[col_idx]:
                head_cls, ph_cls, ruolo_cls, bar_cls = ROLE_MAP.get(g["ruolo"], ROLE_MAP["palleggiatrice"])
                foto_b64 = get_photo_base64(g.get("foto", ""))

                if foto_b64:
                    photo_html = f'<img src="{foto_b64}" class="card-photo" alt="{g["nome"]}">'
                else:
                    photo_html = f'<div class="card-photo-placeholder {ph_cls}">{get_emoji(g["ruolo"])}</div>'

                stato_cls = "stato-ok" if g["stato"] == "attiva" else "stato-inf" if g["stato"] == "infortunata" else "stato-squ"
                stato_txt = "Attiva" if g["stato"] == "attiva" else "Infortunata" if g["stato"] == "infortunata" else "Squalificata"

                tags_html = ""
                if g.get("forza"):
                    for f in g["forza"][:3]:
                        tags_html += f'<span class="tag">{f["tag"]}</span>'

                note_html = ""
                if g.get("note"):
                    note_preview = g["note"][:55] + ("..." if len(g["note"]) > 55 else "")
                    note_html = f'<div class="card-note">"{note_preview}"</div>'

                # Card container Streamlit (border=True)
                with st.container(border=True):
                    st.markdown(
                        f'<div class="card-header {head_cls}">'
                        f'  <div class="card-jersey">{g["numero"]}</div>'
                        f'  {photo_html}'
                        f'</div>'
                        f'<div class="card-body">'
                        f'  <div class="card-name">{g["nome"]} {g["cognome"]}</div>'
                        f'  <div class="card-ruolo {ruolo_cls}">{g["ruolo"]}</div>'
                        f'  <div class="card-meta">📏 {g["altezza"]} cm</div>'
                        f'  <div class="tag-box">{tags_html}</div>'
                        f'  {note_html}'
                        f'  <div style="margin-top:10px;">'
                        f'    <span class="badge-stato {stato_cls}">{stato_txt}</span>'
                        f'  </div>'
                        f'  <div class="card-bar {bar_cls}"></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # Azioni integrate
                    a1, a2 = st.columns(2)
                    with a1:
                        uploaded = st.file_uploader("📷", type=["jpg", "jpeg", "png", "webp"], key=f"foto_{g['id']}", label_visibility="collapsed")
                        if uploaded:
                            g["foto"] = save_photo(g["id"], uploaded)
                            save_data(data)
                            st.rerun()
                    with a2:
                        if st.button("🗑️ Elimina", key=f"del_{g['id']}", use_container_width=True):
                            data["giocatrici"] = [x for x in data["giocatrici"] if x["id"] != g["id"]]
                            if g.get("foto") and os.path.exists(g["foto"]):
                                os.remove(g["foto"])
                            save_data(data)
                            st.rerun()

                    # Dettagli / Modifica
                    with st.expander(f"✏️ Dettagli — {g['nome']} {g['cognome']}"):
                        e1, e2, e3 = st.columns(3)
                        with e1:
                            g["nome"] = st.text_input("Nome", value=g["nome"], key=f"edit_nome_{g['id']}")
                        with e2:
                            g["cognome"] = st.text_input("Cognome", value=g["cognome"], key=f"edit_cogn_{g['id']}")
                        with e3:
                            g["numero"] = st.number_input("N°", min_value=1, max_value=99, value=g["numero"], key=f"edit_num_{g['id']}")
                        e4, e5 = st.columns(2)
                        with e4:
                            g["ruolo"] = st.selectbox("Ruolo", RUOLI_OPTIONS, index=RUOLI_OPTIONS.index(g["ruolo"]), key=f"edit_ruolo_{g['id']}")
                        with e5:
                            g["stato"] = st.selectbox("Stato", ["attiva", "infortunata", "squalificata"], index=["attiva", "infortunata", "squalificata"].index(g["stato"]), key=f"edit_stato_{g['id']}")

                        st.markdown("<div style='font-size:13px; font-weight:700; color:#ff6b6b; margin-top:10px;'>Punti di forza</div>", unsafe_allow_html=True)
                        if g["forza"]:
                            for f in g["forza"]:
                                stars = "<span class='v-star-on'>" + "&#9733;" * f["val"] + "</span><span class='v-star-off'>" + "&#9734;" * (5 - f["val"]) + "</span>"
                                st.markdown(f"<div style='margin-bottom:4px; font-size:13px; color:#d0d0e0;'>• <strong>{f['tag']}</strong> {stars}</div>", unsafe_allow_html=True)
                        else:
                            st.caption("Nessun punto di forza")

                        st.markdown("<div style='font-size:13px; font-weight:700; color:#48dbfb; margin-top:10px;'>Punti deboli</div>", unsafe_allow_html=True)
                        if g["debolezza"]:
                            for d in g["debolezza"]:
                                stars = "<span class='v-star-on'>" + "&#9733;" * d["val"] + "</span><span class='v-star-off'>" + "&#9734;" * (5 - d["val"]) + "</span>"
                                st.markdown(f"<div style='margin-bottom:4px; font-size:13px; color:#d0d0e0;'>• <strong>{d['tag']}</strong> {stars}</div>", unsafe_allow_html=True)
                        else:
                            st.caption("Nessun punto debole")

                        g["note"] = st.text_area("Note allenatore", value=g.get("note", ""), key=f"edit_note_{g['id']}")

                        if st.button("💾 Salva modifiche", key=f"save_edit_{g['id']}", type="primary"):
                            save_data(data)
                            st.success("Modifiche salvate!")
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# TAB TATTICA
# ═══════════════════════════════════════════════════════════════════════
with tab_tattica:
    st.markdown("<div style='font-size:24px; font-weight:700; color:#ffffff; margin-bottom:4px;'>Formazione Tattica</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#6a6a7a; margin-bottom:24px;'>Configura le 6 posizioni in campo e il libero</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:15px; font-weight:600; color:#feca57; margin-bottom:14px;'>Seleziona le giocatrici per le 6 posizioni:</div>", unsafe_allow_html=True)
    cols = st.columns(6)
    giocatrici_attive = [g for g in data["giocatrici"] if g["stato"] == "attiva"]
    nomi_giocatrici = {g["id"]: f"#{g['numero']} {g['nome']}" for g in giocatrici_attive}

    for i, col in enumerate(cols):
        with col:
            st.markdown(f"<div style='text-align:center; font-weight:700; color:#ff6b6b; margin-bottom:8px; font-size:13px;'>POS {i+1}</div>", unsafe_allow_html=True)
            ids = list(nomi_giocatrici.keys())
            current = data["formazione"][i]
            idx = ids.index(current) if current in ids else 0
            sel = st.selectbox(f"Pos{i+1}", options=ids, format_func=lambda x: nomi_giocatrici.get(x, ""), index=idx, key=f"pos_{i}", label_visibility="collapsed")
            data["formazione"][i] = sel

    st.markdown("<div style='font-size:15px; font-weight:600; color:#48dbfb; margin:20px 0 14px;'>Libero:</div>", unsafe_allow_html=True)
    ids = list(nomi_giocatrici.keys())
    current_lib = data["libero_id"]
    idx_lib = ids.index(current_lib) if current_lib in ids else 0
    libero_sel = st.selectbox("Libero", options=ids, format_func=lambda x: nomi_giocatrici.get(x, ""), index=idx_lib, key="libero_sel", label_visibility="collapsed")
    data["libero_id"] = libero_sel

    c_save, _ = st.columns([1, 3])
    with c_save:
        if st.button("💾 Salva formazione", type="primary", use_container_width=True):
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

    # Coordinate corrette (percentuali del contenitore, già centrate con translate)
    positions = [
        {"x": 75, "y": 18},   # Pos 1 (posteriore dx)
        {"x": 25, "y": 18},   # Pos 6 (posteriore sx)
        {"x": 75, "y": 42},   # Pos 5 (centrale dx)
        {"x": 25, "y": 42},   # Pos 4 (centrale sx)
        {"x": 50, "y": 42},   # Pos 3 (centro)
        {"x": 50, "y": 18},   # Pos 2 (posteriore centro)
    ]
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
            court_html += f'<div class="v-dot{lib_class}" style="left:{pos["x"]}%; top:{pos["y"]}%;">{g["numero"]}</div>'
    court_html += '</div>'
    st.markdown(court_html, unsafe_allow_html=True)

    # Legenda ruoli
    st.markdown("""
    <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:24px; justify-content:center;">
        <span style="display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700; background:rgba(66,165,245,0.15); color:#90caf9; border:1px solid rgba(66,165,245,0.3);">Palleggiatrice</span>
        <span style="display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700; background:rgba(239,83,80,0.15); color:#ef9a9a; border:1px solid rgba(239,83,80,0.3);">Schiacciatrice</span>
        <span style="display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700; background:rgba(102,187,106,0.15); color:#a5d6a7; border:1px solid rgba(102,187,106,0.3);">Centrale</span>
        <span style="display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700; background:rgba(171,71,188,0.15); color:#ce93d8; border:1px solid rgba(171,71,188,0.3);">Opposto</span>
        <span style="display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700; background:rgba(255,167,38,0.15); color:#ffcc80; border:1px solid rgba(255,167,38,0.3);">Libero</span>
    </div>
    """, unsafe_allow_html=True)
