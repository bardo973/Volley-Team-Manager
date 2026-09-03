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

  /* Card base */
  .v-card {
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    transition: all 0.4s ease;
    position: relative;
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

  /* ── CARD DIVERTENTI E COLORATE ── */
  .fun-card {
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 20px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    cursor: pointer;
  }
  .fun-card:hover {
    transform: translateY(-10px) rotate(-1deg);
    box-shadow: 0 25px 60px rgba(0,0,0,0.5);
  }

  /* Colori per ruolo - BLU METALLIZZATO con contorno oro */
  .fun-card {
    background: linear-gradient(160deg, #0a1628 0%, #1a3a5c 30%, #0d2137 60%, #1a3a5c 100%) !important;
    border: 2px solid rgba(212,175,55,0.6) !important;
    box-shadow: 0 0 15px rgba(212,175,55,0.2), inset 0 0 30px rgba(10,22,40,0.5) !important;
  }
  .fun-card::before {
    content: '';
    position: absolute;
    top: -2px; left: -2px; right: -2px; bottom: -2px;
    background: linear-gradient(45deg, #d4af37, #f4d03f, #d4af37, #b8860b, #d4af37);
    border-radius: 26px;
    z-index: -1;
    opacity: 0.4;
    animation: borderGlow 3s ease-in-out infinite;
  }
  @keyframes borderGlow {
    0%, 100% { opacity: 0.3; filter: brightness(1); }
    50% { opacity: 0.7; filter: brightness(1.3); }
  }
  .fun-card:hover {
    transform: translateY(-10px) rotate(-1deg);
    box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 40px rgba(212,175,55,0.3) !important;
    border-color: rgba(244,208,63,0.9) !important;
  }
  .fun-card-pal, .fun-card-sch, .fun-card-cen, .fun-card-opp, .fun-card-lib {
    background: linear-gradient(160deg, #0a1628 0%, #1a3a5c 30%, #0d2137 60%, #1a3a5c 100%) !important;
    border: 2px solid rgba(212,175,55,0.6) !important;
  }

  /* Testa card con gradiente */
  .fun-head {
    height: 140px;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 0;
  }
  .fun-head-pal, .fun-head-sch, .fun-head-cen, .fun-head-opp, .fun-head-lib {
    background: linear-gradient(135deg, rgba(26,58,92,0.5), rgba(13,33,55,0.2), rgba(212,175,55,0.08)) !important;
  }

  /* Cerchio foto grande */
  .fun-photo {
    width: 100px; height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid rgba(255,255,255,0.3);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    position: absolute;
    bottom: -50px;
    z-index: 2;
    transition: all 0.4s ease;
  }
  .fun-card:hover .fun-photo {
    transform: scale(1.15);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  }

  .fun-photo-placeholder {
    width: 100px; height: 100px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 3rem;
    position: absolute;
    bottom: -50px;
    z-index: 2;
    border: 4px solid rgba(255,255,255,0.3);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    transition: all 0.4s ease;
  }
  .fun-card:hover .fun-photo-placeholder {
    transform: scale(1.15);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  }
  .fun-ph-pal, .fun-ph-sch, .fun-ph-cen, .fun-ph-opp, .fun-ph-lib {
    background: linear-gradient(135deg, #1a3a5c, #0d2137, #2c5f8a) !important;
    border: 3px solid rgba(212,175,55,0.5) !important;
    box-shadow: 0 0 20px rgba(212,175,55,0.2) !important;
  }

  /* Numero maglia grande */
  .fun-jersey {
    position: absolute;
    top: 12px; right: 12px;
    width: 48px; height: 48px;
    border-radius: 50%;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 900;
    border: 2px solid rgba(255,255,255,0.3);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }

  /* Corpo card */
  .fun-body {
    padding: 60px 20px 20px 20px;
    text-align: center;
  }
  .fun-name {
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 2px;
    letter-spacing: -0.5px;
  }
  .fun-ruolo {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
  }
  .fun-ruolo-pal, .fun-ruolo-sch, .fun-ruolo-cen, .fun-ruolo-opp, .fun-ruolo-lib {
    color: #d4af37 !important;
    text-shadow: 0 0 8px rgba(212,175,55,0.4) !important;
  }

  .fun-meta-row {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 12px 0;
    font-size: 12px;
    color: rgba(255,255,255,0.6);
  }
  .fun-meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  /* Stato badge */
  .fun-stato {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
  }
  .fun-stato-ok {
    background: rgba(76,175,80,0.25);
    color: #a5d6a7;
    border: 1px solid rgba(76,175,80,0.4);
  }
  .fun-stato-inf {
    background: rgba(244,67,54,0.25);
    color: #ef9a9a;
    border: 1px solid rgba(244,67,54,0.4);
  }
  .fun-stato-squ {
    background: rgba(255,193,7,0.25);
    color: #ffe082;
    border: 1px solid rgba(255,193,7,0.4);
  }

  /* Note */
  .fun-note {
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    margin-top: 10px;
    font-style: italic;
    line-height: 1.5;
    padding: 0 8px;
  }

  /* Barra decorativa in basso */
  .fun-bar { height: 4px !important; width: 60% !important; margin: 10px auto 0; border-radius: 2px !important; display: block !important; background: linear-gradient(90deg, #888, #aaa) !important; }
  .fun-bar-pal, .fun-bar-sch, .fun-bar-cen, .fun-bar-opp, .fun-bar-lib {
    background: linear-gradient(90deg, #b8860b, #d4af37, #f4d03f, #d4af37, #b8860b) !important;
    box-shadow: 0 0 10px rgba(212,175,55,0.4) !important;
  }

  /* Animazione float */
  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
  }
  .fun-float { animation: float 3s ease-in-out infinite; }

  /* Punti forza/deboli in card */
  .fun-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
    margin-top: 10px;
  }
  .fun-tag {
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 10px;
    background: rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.7);
    border: 1px solid rgba(255,255,255,0.15);
  }
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

def get_fun_card_class(ruolo):
    return {"palleggiatrice": "fun-card-pal", "schiacciatrice": "fun-card-sch", "centrale": "fun-card-cen", "opposto": "fun-card-opp", "libero": "fun-card-lib"}.get(ruolo, "fun-card-pal")

def get_fun_head_class(ruolo):
    return {"palleggiatrice": "fun-head-pal", "schiacciatrice": "fun-head-sch", "centrale": "fun-head-cen", "opposto": "fun-head-opp", "libero": "fun-head-lib"}.get(ruolo, "fun-head-pal")

def get_fun_ph_class(ruolo):
    return {"palleggiatrice": "fun-ph-pal", "schiacciatrice": "fun-ph-sch", "centrale": "fun-ph-cen", "opposto": "fun-ph-opp", "libero": "fun-ph-lib"}.get(ruolo, "fun-ph-pal")

def get_fun_ruolo_class(ruolo):
    return {"palleggiatrice": "fun-ruolo-pal", "schiacciatrice": "fun-ruolo-sch", "centrale": "fun-ruolo-cen", "opposto": "fun-ruolo-opp", "libero": "fun-ruolo-lib"}.get(ruolo, "fun-ruolo-pal")

def get_fun_bar_class(ruolo):
    return {"palleggiatrice": "fun-bar-pal", "schiacciatrice": "fun-bar-sch", "centrale": "fun-bar-cen", "opposto": "fun-bar-opp", "libero": "fun-bar-lib"}.get(ruolo, "fun-bar-pal")

def build_fun_card_html(player):
    foto_b64 = get_photo_base64(player.get("foto", ""))
    card_cls = get_fun_card_class(player["ruolo"])
    head_cls = get_fun_head_class(player["ruolo"])
    ph_cls = get_fun_ph_class(player["ruolo"])
    ruolo_cls = get_fun_ruolo_class(player["ruolo"])
    bar_cls = get_fun_bar_class(player["ruolo"])
    if foto_b64:
        photo_html = f'<img src="{foto_b64}" class="fun-photo" alt="{player["nome"]}">'
    else:
        photo_html = f'<div class="fun-photo-placeholder {ph_cls}">{get_emoji(player["ruolo"])}</div>'
    stato_cls = "fun-stato-ok" if player["stato"] == "attiva" else "fun-stato-inf" if player["stato"] == "infortunata" else "fun-stato-squ"
    stato_txt = "Attiva" if player["stato"] == "attiva" else "Infortunata" if player["stato"] == "infortunata" else "Squalificata"
    tags_html = ""
    if player.get("forza"):
        for f in player["forza"][:2]:
            tags_html += f'<span class="fun-tag">{f["tag"]}</span>'
    note_html = ""
    if player.get("note"):
        note_preview = player["note"][:60] + ("..." if len(player["note"]) > 60 else "")
        note_html = f'<div class="fun-note">"{note_preview}"</div>'
    return f'''<div class="fun-card {card_cls}">
  <div class="fun-head {head_cls}">
    <div class="fun-jersey">{player['numero']}</div>
    {photo_html}
  </div>
  <div class="fun-body">
    <div class="fun-name">{player['nome']} {player['cognome']}</div>
    <div class="fun-ruolo {ruolo_cls}">{player['ruolo']}</div>
    <div class="fun-meta-row">
      <span class="fun-meta-item">📏 {player['altezza']}cm</span>
    </div>
    {tags_html}
    {note_html}
    <div style="margin-top:10px; margin-bottom:10px;">
      <span class="fun-stato {stato_cls}">{stato_txt}</span>
    </div>
    <div class="fun-bar {bar_cls}" style="margin: 8px auto 0;"></div>
  </div>
</div>'''

# Session state
if "data" not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.current_rot = 1

data = st.session_state.data
RUOLI_OPTIONS = ["palleggiatrice", "schiacciatrice", "centrale", "opposto", "libero"]

# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# HEADER CON EDITOR SQUADRA
# ═══════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown("""
    <div style="text-align:center; margin-bottom:2px;">
        <div style="font-size:4rem; margin-bottom:-10px;">🏐</div>
    </div>
    <div style="text-align:center; font-size:2.8rem; font-weight:800; background:linear-gradient(90deg,#ff6b6b,#feca57,#48dbfb,#ff9ff3); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:-2px; margin-bottom:4px;">Volley Team Manager</div>
    """, unsafe_allow_html=True)

    # Editor nome squadra e categoria
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

tab_roster, tab_tattica = st.tabs(["👥 Roster", "📐 Tattica"])

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

                card_html = build_fun_card_html(g)
                st.markdown(card_html, unsafe_allow_html=True)

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
