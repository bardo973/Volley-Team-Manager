import streamlit as st
import pandas as pd
import json
import os
import pickle
import tempfile
import shutil
import random
import urllib.request
import urllib.parse
import re
import html as _html
import base64
import streamlit.components.v1 as components
from datetime import datetime, date, timedelta

# ============================================================
# CONFIGURAZIONE
# ============================================================
st.set_page_config(
    page_title="VolleyCoach Manager",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAVE_FILE = "volleycoach_state.pkl"

# Ruoli pallavolo
RUOLI = {
    "P": "Palleggiatrice",
    "S": "Schiacciatrice (banda)",
    "C": "Centrale",
    "O": "Opposto",
    "L": "Libero",
}

FONDAMENTALI = ["Battuta", "Ricezione", "Palleggio", "Attacco", "Muro", "Difesa", "Fisico"]

OBIETTIVI = [
    "Ricezione", "Battuta", "Attacco", "Muro-Difesa",
    "Fase break (cambio palla)", "Fase side-out", "Condizione fisica", "Tecnica generale",
]

INTENSITA = ["Scarico", "Medio", "Carico", "Pre-partita"]

# Aree di sviluppo per il programma a lungo termine
AREE_SVILUPPO = {
    "Fisico": ["Forza", "Potenza / salto", "Rapidit\u00e0 / agilit\u00e0", "Resistenza", "Mobilit\u00e0 / prevenzione"],
    "Tecnico": ["Battuta", "Ricezione", "Palleggio / alzata", "Attacco", "Muro", "Difesa"],
    "Tattico": ["Cambio palla (side-out)", "Fase break", "Lettura / anticipo", "Rotazioni", "Sistemi di ricezione", "Comunicazione"],
}

# Lavagna tattica (canvas HTML self-contained, nessuna libreria esterna)
TACTIC_BOARD_HTML = """
<div style="font-family:Segoe UI,Arial,sans-serif;color:#eaf1ff">
  <div style="margin-bottom:8px;display:flex;gap:14px;align-items:center;flex-wrap:wrap">
    <label>Colore <input type="color" id="col" value="#ff9f1c"></label>
    <label>Spessore <input type="range" id="siz" min="1" max="14" value="3"></label>
    <button id="clr" style="padding:4px 12px;border-radius:8px;border:none;background:#26334f;color:#eaf1ff;cursor:pointer">Pulisci</button>
    <button id="dl" style="padding:4px 12px;border-radius:8px;border:none;background:#ff9f1c;color:#1a1000;font-weight:700;cursor:pointer">Scarica PNG</button>
  </div>
  <canvas id="cv" width="700" height="400" style="border-radius:10px;border:1px solid #26334f;background:#0f6b3f;touch-action:none;max-width:100%"></canvas>
</div>
<script>
(function(){
  var cv=document.getElementById('cv'), ctx=cv.getContext('2d');
  function court(){
    ctx.clearRect(0,0,cv.width,cv.height);
    ctx.fillStyle='#0f6b3f'; ctx.fillRect(0,0,cv.width,cv.height);
    ctx.strokeStyle='#ffffff'; ctx.lineWidth=2;
    var m=40; ctx.strokeRect(m,m,cv.width-2*m,cv.height-2*m);
    ctx.beginPath(); ctx.moveTo(cv.width/2,m); ctx.lineTo(cv.width/2,cv.height-m); ctx.stroke();
    var a3=(cv.width/2-m)/3;
    ctx.setLineDash([6,6]);
    ctx.beginPath(); ctx.moveTo(cv.width/2-a3,m); ctx.lineTo(cv.width/2-a3,cv.height-m); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cv.width/2+a3,m); ctx.lineTo(cv.width/2+a3,cv.height-m); ctx.stroke();
    ctx.setLineDash([]);
  }
  court();
  var drawing=false;
  function pos(e){var r=cv.getBoundingClientRect();var t=e.touches?e.touches[0]:e;return{x:t.clientX-r.left,y:t.clientY-r.top};}
  function start(e){drawing=true;var p=pos(e);ctx.beginPath();ctx.moveTo(p.x,p.y);e.preventDefault();}
  function move(e){if(!drawing)return;var p=pos(e);ctx.strokeStyle=document.getElementById('col').value;ctx.lineWidth=document.getElementById('siz').value;ctx.lineCap='round';ctx.lineTo(p.x,p.y);ctx.stroke();e.preventDefault();}
  function end(){drawing=false;}
  cv.addEventListener('mousedown',start);cv.addEventListener('mousemove',move);window.addEventListener('mouseup',end);
  cv.addEventListener('touchstart',start);cv.addEventListener('touchmove',move);cv.addEventListener('touchend',end);
  document.getElementById('clr').addEventListener('click',court);
  document.getElementById('dl').addEventListener('click',function(){var a=document.createElement('a');a.download='schema_seduta.png';a.href=cv.toDataURL('image/png');a.click();});
})();
</script>
"""

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0b1220 0%, #101b33 100%); }
    .stSidebar { background-color: #0c1526 !important; }
    h1, h2, h3 { color: #ffb703 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button {
        border-radius: 8px; font-weight: 600; border: none;
        background: linear-gradient(90deg, #ff9f1c, #ffbf69); color: #1a1000;
    }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(255,159,28,0.4); }
    .block-seduta {
        background: #16223d; border-radius: 10px; padding: 14px 16px;
        margin-bottom: 10px; border-left: 4px solid #ff9f1c;
    }
    .ex-card {
        background: #14213d; border-radius: 10px; padding: 12px 14px;
        margin-bottom: 8px; border: 1px solid #26334f;
    }
    div[data-testid="stMetricValue"] { font-size: 1.7rem !important; font-weight: 700 !important; }
    .player-card {
        position: relative;
        background: linear-gradient(135deg, #14213d 0%, #1b2c52 100%);
        border-radius: 14px; padding: 14px 16px; margin-bottom: 12px;
        border: 1px solid rgba(255,191,105,0.35);
        box-shadow: 0 0 14px rgba(255,159,28,0.25), inset 0 0 12px rgba(255,159,28,0.05);
        transition: all .2s ease;
    }
    .player-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 24px rgba(255,159,28,0.55), inset 0 0 18px rgba(255,159,28,0.08);
    }
    .player-card .pc-num {
        font-size: 1.5rem; font-weight: 800; color: #ffb703;
        text-shadow: 0 0 10px rgba(255,183,3,0.85);
    }
    .player-card .pc-name { font-size: 1.12rem; font-weight: 700; color: #eaf1ff; }
    .player-card .pc-meta { color: #9fb3d1; font-size: .9em; }
    .player-card .pc-badge {
        display:inline-block; padding: 2px 10px; border-radius: 999px;
        font-size: .8em; font-weight: 700; margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LIBRERIA ESERCIZI DEFAULT
# ============================================================
ESERCIZI_DEFAULT = [
    # --- RISCALDAMENTO / FISICO ---
    {"Nome": "Corsa e mobilit\u00e0 articolare", "Fondamentale": "Fisico", "Obiettivo": "Condizione fisica", "Fase": "Riscaldamento", "Min_Giocatrici": 1, "Durata_min": 10, "Livello": "Base", "Descrizione": "Corsa leggera, skip, calciata, aperture anche e spalle. Attivazione generale.", "Varianti": "Aggiungere andature laterali e spostamenti a specchio a coppie."},
    {"Nome": "Attivazione a coppie con palla", "Fondamentale": "Fisico", "Obiettivo": "Tecnica generale", "Fase": "Riscaldamento", "Min_Giocatrici": 2, "Durata_min": 8, "Livello": "Base", "Descrizione": "Palleggio e bagher a coppie a distanza crescente, lavoro su appoggi e trasferimento del peso.", "Varianti": "Un tocco in palleggio + un tocco in bagher alternati."},
    {"Nome": "Core stability circuit", "Fondamentale": "Fisico", "Obiettivo": "Condizione fisica", "Fase": "Centrale", "Min_Giocatrici": 1, "Durata_min": 12, "Livello": "Medio", "Descrizione": "Plank frontale/laterale, ponte, russian twist, superman. 3 giri.", "Varianti": "Aggiungere instabilit\u00e0 (fitball) o carico leggero."},
    {"Nome": "Pliometria salti al muro", "Fondamentale": "Fisico", "Obiettivo": "Condizione fisica", "Fase": "Centrale", "Min_Giocatrici": 1, "Durata_min": 10, "Livello": "Medio", "Descrizione": "Serie di salti verticali con rincorsa da muro/attacco, focus su tecnica di stacco e atterraggio.", "Varianti": "Salti su box, salti ripetuti reattivi."},

    # --- BATTUTA ---
    {"Nome": "Battuta a bersaglio", "Fondamentale": "Battuta", "Obiettivo": "Battuta", "Fase": "Centrale", "Min_Giocatrici": 4, "Durata_min": 15, "Livello": "Base", "Descrizione": "Zone bersaglio a terra (1, 5, 6). Ogni giocatrice serve 10 palloni cercando le zone. Si conta il punteggio.", "Varianti": "Aumentare il rischio: bersagli pi\u00f9 piccoli o zone di conflitto."},
    {"Nome": "Battuta salto float", "Fondamentale": "Battuta", "Obiettivo": "Battuta", "Fase": "Centrale", "Min_Giocatrici": 3, "Durata_min": 12, "Livello": "Medio", "Descrizione": "Tecnica di battuta in salto flottante: lancio, timing, colpo pieno. Serie da 8-10.", "Varianti": "Battuta in salto spin per le pi\u00f9 avanzate."},
    {"Nome": "Battuta sotto pressione (7 di fila)", "Fondamentale": "Battuta", "Obiettivo": "Fase break (cambio palla)", "Fase": "Situazionale", "Min_Giocatrici": 6, "Durata_min": 12, "Livello": "Medio", "Descrizione": "La squadra deve fare 7 battute buone consecutive. Ogni errore riparte da zero. Gestione tensione.", "Varianti": "Alzare/abbassare il target in base al livello."},

    # --- RICEZIONE ---
    {"Nome": "Ricezione a due (P1-P5)", "Fondamentale": "Ricezione", "Obiettivo": "Ricezione", "Fase": "Centrale", "Min_Giocatrici": 5, "Durata_min": 15, "Livello": "Base", "Descrizione": "Due ricevitrici, battute dall'altro campo verso il palleggiatore in zona 2-3. Focus su appoggi e bersaglio alzata.", "Varianti": "Introdurre chiamata e comunicazione tra le ricevitrici."},
    {"Nome": "Ricezione a tre + attacco", "Fondamentale": "Ricezione", "Obiettivo": "Fase side-out", "Fase": "Situazionale", "Min_Giocatrici": 8, "Durata_min": 20, "Livello": "Medio", "Descrizione": "Ricezione a 3, palleggiatore alza, attacco completo. Valuta la qualit\u00e0 del cambio palla dopo servizio.", "Varianti": "Battute mirate sulle zone di conflitto tra ricevitrici."},
    {"Nome": "Ricezione con valutazione (# / + / -)", "Fondamentale": "Ricezione", "Obiettivo": "Ricezione", "Fase": "Centrale", "Min_Giocatrici": 4, "Durata_min": 12, "Livello": "Medio", "Descrizione": "Ogni ricezione viene valutata a voce (perfetta/buona/scarsa). Obiettivo: % di positivit\u00e0 sopra soglia.", "Varianti": "Registrare i dati e confrontarli tra sedute."},

    # --- PALLEGGIO / ALZATA ---
    {"Nome": "Alzata di precisione ai bersagli", "Fondamentale": "Palleggio", "Obiettivo": "Tecnica generale", "Fase": "Centrale", "Min_Giocatrici": 3, "Durata_min": 12, "Livello": "Base", "Descrizione": "Palleggiatrici alzano a bersagli fissi in zona 4, 2 e primo tempo. Precisione e altezza costanti.", "Varianti": "Alzata dopo spostamento o da posizione defilata."},
    {"Nome": "Palleggiatore in situazione (ricezione random)", "Fondamentale": "Palleggio", "Obiettivo": "Fase side-out", "Fase": "Situazionale", "Min_Giocatrici": 6, "Durata_min": 15, "Livello": "Medio", "Descrizione": "Ricezione volutamente imperfetta: la palleggiatrice sceglie la miglior soluzione d'alzata. Sviluppa lettura.", "Varianti": "Introdurre muro avversario per forzare scelte."},

    # --- ATTACCO ---
    {"Nome": "Attacco da zona 4 con alzata", "Fondamentale": "Attacco", "Obiettivo": "Attacco", "Fase": "Centrale", "Min_Giocatrici": 5, "Durata_min": 18, "Livello": "Base", "Descrizione": "Serie di attacchi da banda con alzata reale. Focus su rincorsa, timing e colpo. 10-12 palloni a testa.", "Varianti": "Bersagli a terra (parallela/diagonale), colpo in lungolinea."},
    {"Nome": "Primo tempo centrali", "Fondamentale": "Attacco", "Obiettivo": "Attacco", "Fase": "Centrale", "Min_Giocatrici": 3, "Durata_min": 12, "Livello": "Medio", "Descrizione": "Sincronia palleggiatrice-centrale sul primo tempo. Tempi di stacco e colpo.", "Varianti": "Aggiungere il muro avversario passivo poi attivo."},
    {"Nome": "Attacco contro muro-difesa", "Fondamentale": "Attacco", "Obiettivo": "Muro-Difesa", "Fase": "Situazionale", "Min_Giocatrici": 8, "Durata_min": 20, "Livello": "Avanzato", "Descrizione": "Attacco reale contro muro a uno/due + difesa schierata. Sviluppa scelte di colpo e mani-out.", "Varianti": "Punteggio a chi vince lo scambio."},

    # --- MURO ---
    {"Nome": "Tecnica di muro individuale", "Fondamentale": "Muro", "Obiettivo": "Muro-Difesa", "Fase": "Centrale", "Min_Giocatrici": 2, "Durata_min": 12, "Livello": "Base", "Descrizione": "Spostamento, stacco e penetrazione delle mani oltre rete. Palloni lanciati dall'alto (sgabello).", "Varianti": "Muro dopo spostamento laterale (accostamento centrale)."},
    {"Nome": "Muro a due sincronizzato", "Fondamentale": "Muro", "Obiettivo": "Muro-Difesa", "Fase": "Centrale", "Min_Giocatrici": 4, "Durata_min": 14, "Livello": "Medio", "Descrizione": "Centrale + banda murano insieme. Chiusura del muro e lettura dell'alzata.", "Varianti": "Aggiungere l'attaccante reale che varia la zona."},

    # --- DIFESA ---
    {"Nome": "Difesa su attacco pesante", "Fondamentale": "Difesa", "Obiettivo": "Muro-Difesa", "Fase": "Centrale", "Min_Giocatrici": 4, "Durata_min": 15, "Livello": "Medio", "Descrizione": "Difesa di palloni attaccati con potenza. Posizione bassa, spostamenti, tuffo e rullata.", "Varianti": "Alternare pallonetti e attacchi forti (lettura)."},
    {"Nome": "Difesa e ricostruzione (free-ball)", "Fondamentale": "Difesa", "Obiettivo": "Fase break (cambio palla)", "Fase": "Situazionale", "Min_Giocatrici": 8, "Durata_min": 18, "Livello": "Medio", "Descrizione": "Dalla difesa si costruisce il contrattacco. Transizione difesa-attacco completa.", "Varianti": "Punteggio: 1 pt difesa recuperata, 2 pt contrattacco vincente."},

    # --- GIOCO / SITUAZIONALE ---
    {"Nome": "Wash drill 6vs6 (cambio palla)", "Fondamentale": "Difesa", "Obiettivo": "Fase break (cambio palla)", "Fase": "Situazionale", "Min_Giocatrici": 12, "Durata_min": 20, "Livello": "Avanzato", "Descrizione": "Scambio iniziato dal servizio + free ball. La squadra deve vincere entrambi per fare punto. Alta densit\u00e0.", "Varianti": "Ridurre a 6vs6 con jolly se le presenti sono meno."},
    {"Nome": "Partita a tema (obiettivo del giorno)", "Fondamentale": "Attacco", "Obiettivo": "Tecnica generale", "Fase": "Situazionale", "Min_Giocatrici": 10, "Durata_min": 20, "Livello": "Medio", "Descrizione": "Set a 15 con bonus punti sull'obiettivo tecnico della seduta (es. ace, muro, primo tempo).", "Varianti": "Cambiare la regola bonus a met\u00e0 set."},
    {"Nome": "6vs6 rotazioni fisse", "Fondamentale": "Palleggio", "Obiettivo": "Fase side-out", "Fase": "Situazionale", "Min_Giocatrici": 12, "Durata_min": 22, "Livello": "Avanzato", "Descrizione": "Si gioca insistendo su una rotazione critica per volta, per automatizzare cambio palla.", "Varianti": "Focus sulle rotazioni in cui la squadra soffre di pi\u00f9."},

    # --- DEFATICAMENTO ---
    {"Nome": "Stretching e defaticamento", "Fondamentale": "Fisico", "Obiettivo": "Condizione fisica", "Fase": "Defaticamento", "Min_Giocatrici": 1, "Durata_min": 8, "Livello": "Base", "Descrizione": "Allungamento globale, respirazione, mobilit\u00e0 dolce. Recupero e prevenzione.", "Varianti": "Foam roller su schiena e gambe."},
    {"Nome": "Gioco ludico di chiusura", "Fondamentale": "Fisico", "Obiettivo": "Tecnica generale", "Fase": "Defaticamento", "Min_Giocatrici": 6, "Durata_min": 8, "Livello": "Base", "Descrizione": "Gioco leggero (palla avvelenata / bagher a squadre) per chiudere in positivit\u00e0.", "Varianti": "A eliminazione o a punti."},
]

# ============================================================
# STATO / PERSISTENZA
# ============================================================
def save_state():
    data = {
        "rosa": st.session_state.rosa,
        "esercizi": st.session_state.esercizi.to_dict("records"),
        "sedute": st.session_state.sedute,
        "scouting": st.session_state.get("scouting", []),
        "piani": st.session_state.get("piani", []),
    }
    tmp = tempfile.NamedTemporaryFile(delete=False, dir=".")
    try:
        with open(tmp.name, "wb") as f:
            pickle.dump(data, f)
        shutil.move(tmp.name, SAVE_FILE)
    except Exception:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
        raise


def load_state():
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "rb") as f:
            data = pickle.load(f)
        st.session_state.rosa = data.get("rosa", [])
        es = data.get("esercizi", [])
        st.session_state.esercizi = pd.DataFrame(es) if es else pd.DataFrame(ESERCIZI_DEFAULT)
        st.session_state.sedute = data.get("sedute", [])
        st.session_state.scouting = data.get("scouting", [])
        st.session_state.piani = data.get("piani", [])
        return True
    except Exception:
        return False


if "initialized" not in st.session_state:
    st.session_state.rosa = []
    st.session_state.esercizi = pd.DataFrame(ESERCIZI_DEFAULT)
    st.session_state.sedute = []
    st.session_state.scouting = []
    st.session_state.piani = []
    load_state()
    st.session_state.initialized = True


# ============================================================
# HELPER
# ============================================================
def giocatrici_disponibili():
    return [g for g in st.session_state.rosa if g.get("Stato", "Disponibile") == "Disponibile"]


def conta_ruoli(lista):
    c = {r: 0 for r in RUOLI}
    for g in lista:
        r = g.get("Ruolo")
        if r in c:
            c[r] += 1
    return c


def _durata_fasi(durata_tot, intensita):
    """Ripartisce i minuti totali tra le fasi in base all'intensita."""
    if intensita == "Scarico":
        quote = {"Riscaldamento": 0.20, "Centrale": 0.35, "Situazionale": 0.25, "Defaticamento": 0.20}
    elif intensita == "Pre-partita":
        quote = {"Riscaldamento": 0.25, "Centrale": 0.25, "Situazionale": 0.40, "Defaticamento": 0.10}
    elif intensita == "Carico":
        quote = {"Riscaldamento": 0.15, "Centrale": 0.45, "Situazionale": 0.30, "Defaticamento": 0.10}
    else:  # Medio
        quote = {"Riscaldamento": 0.18, "Centrale": 0.42, "Situazionale": 0.30, "Defaticamento": 0.10}
    return {fase: max(5, round(durata_tot * q)) for fase, q in quote.items()}


def genera_seduta(obiettivo, durata_tot, intensita, n_presenti, seed=None):
    """Genera una seduta strutturata scegliendo esercizi coerenti dalla libreria."""
    rng = random.Random(seed)
    df = st.session_state.esercizi.copy()
    df = df[df["Min_Giocatrici"] <= max(n_presenti, 1)]

    budget = _durata_fasi(durata_tot, intensita)
    ordine_fasi = ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"]
    seduta = []

    for fase in ordine_fasi:
        minuti_fase = budget[fase]
        pool = df[df["Fase"] == fase]
        # Nella parte centrale/situazionale privilegia l'obiettivo del giorno
        if fase in ("Centrale", "Situazionale") and obiettivo not in ("Tecnica generale",):
            mirati = pool[pool["Obiettivo"] == obiettivo]
            altri = pool[pool["Obiettivo"] != obiettivo]
            pool = pd.concat([mirati, altri])
        candidati = pool.to_dict("records")
        rng.shuffle(candidati) if fase in ("Riscaldamento", "Defaticamento") else None
        # Se abbiamo privilegiato l'obiettivo manteniamo l'ordine (mirati prima)
        usati = 0
        for ex in candidati:
            if usati >= minuti_fase and seduta and seduta[-1]["Fase"] == fase:
                break
            seduta.append(ex)
            usati += int(ex["Durata_min"])
            if usati >= minuti_fase:
                break
        # garantisci almeno un esercizio per fase se il pool non e' vuoto
    return seduta, budget


def genera_programma_lt(nome, start, settimane, per_sett, foc_fis, foc_tec, foc_tat):
    """Crea un programma pluri-settimanale (mesocicli) con progressione fisica, tecnica e tattica."""
    blocchi = [
        ("Fase 1 \u00b7 Costruzione", "Base generale: volume alto, tecnica pulita, condizionamento generale.", 0.30,
         "Forza generale + mobilit\u00e0", "Fondamentali di base ({tec})", "Concetti base ({tat})"),
        ("Fase 2 \u00b7 Sviluppo", "Aumento dell'intensit\u00e0: tecnica sotto carico e primi automatismi.", 0.30,
         "Forza-potenza ({fis})", "{tec} sotto pressione", "{tat} a reparti / a coppie"),
        ("Fase 3 \u00b7 Specifica-Tattica", "Lavoro situazionale: sistemi di gioco e intensit\u00e0 gara.", 0.25,
         "Potenza / reattivit\u00e0 ({fis})", "{tec} in situazione di gioco", "{tat} in 6vs6 / sistemi"),
        ("Fase 4 \u00b7 Picco-Mantenimento", "Scarico modulato, rifinitura e gestione della condizione verso le gare.", 0.15,
         "Mantenimento + prevenzione", "Rifinitura {tec}", "Automatismi gara ({tat})"),
    ]
    fasi = []
    assegnate = 0
    for k, (titolo, desc, quota, fis_t, tec_t, tat_t) in enumerate(blocchi):
        if k < len(blocchi) - 1:
            n = max(1, round(settimane * quota))
        else:
            n = max(1, settimane - assegnate)
        w_from = assegnate + 1
        w_to = min(settimane, assegnate + n)
        if w_from > settimane:
            break
        fasi.append({
            "Fase": titolo,
            "Settimane": f"{w_from}-{w_to}",
            "\U0001F4AA Fisico": fis_t.format(fis=foc_fis),
            "\U0001F3D0 Tecnico": tec_t.format(tec=foc_tec),
            "\U0001F9E0 Tattico": tat_t.format(tat=foc_tat),
            "Obiettivo": desc,
        })
        assegnate = w_to
        if assegnate >= settimane:
            break
    return {
        "nome": nome.strip() or "Programma",
        "inizio": start.isoformat(),
        "settimane": int(settimane),
        "per_settimana": int(per_sett),
        "focus_fisico": foc_fis,
        "focus_tecnico": foc_tec,
        "focus_tattico": foc_tat,
        "fasi": fasi,
    }

# ============================================================
# ESERCIZI DA INTERNET
# ============================================================
# Parole chiave per costruire ricerche mirate
KEYWORDS_OBJ = {
    "Ricezione": "serve receive passing",
    "Battuta": "serving",
    "Attacco": "hitting spiking attack",
    "Muro-Difesa": "blocking defense dig",
    "Fase break (cambio palla)": "transition wash drill",
    "Fase side-out": "side out serve receive",
    "Condizione fisica": "conditioning agility",
    "Tecnica generale": "fundamentals technique",
}
# Siti di riferimento per drills di pallavolo (ricerca Google mirata)
SITI_DRILLS = [
    ("The Art of Coaching Volleyball", "theartofcoachingvolleyball.com"),
    ("Volleyball Advisors", "volleyballadvisors.com"),
    ("BetterAtVolleyball", "betteratvolleyball.com"),
    ("Volleyball Toolbox", "volleyballtoolbox.net"),
]


def link_ricerca(fondamentale, obiettivo, livello):
    """Costruisce link di ricerca (YouTube, Google, siti di drills)."""
    kw = KEYWORDS_OBJ.get(obiettivo, "")
    base = f"volleyball {kw} drills {fondamentale} {livello}".strip()
    q = urllib.parse.quote_plus(base + " esercizi pallavolo")
    qen = urllib.parse.quote_plus(base)
    links = {
        "\U0001F534 YouTube (video drills)": f"https://www.youtube.com/results?search_query={qen}",
        "\U0001F50E Google": f"https://www.google.com/search?q={q}",
    }
    for nome, dominio in SITI_DRILLS:
        links[f"\U0001F310 {nome}"] = f"https://www.google.com/search?q={qen}+site:{dominio}"
    return links


def _fetch_url(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (VolleyCoach)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(300000)
    return raw.decode("utf-8", errors="ignore")


def _is_youtube(url):
    u = url.lower()
    return "youtube.com/watch" in u or "youtu.be/" in u or "youtube.com/shorts" in u


def importa_da_link(url):
    """Estrae titolo/descrizione da un link (YouTube via oEmbed, altrimenti HTML).
    Ritorna dict {titolo, descrizione, autore, fonte} o solleva eccezione."""
    url = url.strip()
    if _is_youtube(url):
        api = "https://www.youtube.com/oembed?" + urllib.parse.urlencode({"url": url, "format": "json"})
        data = json.loads(_fetch_url(api))
        return {
            "titolo": data.get("title", ""),
            "descrizione": f"Video di {data.get('author_name','')}. Guarda il drill al link e adattalo.",
            "autore": data.get("author_name", ""),
            "fonte": url,
        }
    htmltxt = _fetch_url(url)
    titolo = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", htmltxt, re.I | re.S)
    if m:
        titolo = _html.unescape(m.group(1)).strip()
    desc = ""
    m = re.search(
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\'](.*?)["\']',
        htmltxt, re.I | re.S,
    )
    if m:
        desc = _html.unescape(m.group(1)).strip()
    return {"titolo": titolo, "descrizione": desc, "autore": "", "fonte": url}


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🏐 VolleyCoach")
    st.caption("Gestione squadra · Serie D femminile")
    st.markdown("---")
    disp = len(giocatrici_disponibili())
    st.metric("Giocatrici in rosa", len(st.session_state.rosa))
    st.metric("Disponibili", disp)
    st.metric("Sedute programmate", len(st.session_state.sedute))
    st.markdown("---")
    if st.button("💾 Salva dati", use_container_width=True):
        save_state()
        st.success("Salvato!")
    st.caption("I dati vengono salvati anche automaticamente a ogni modifica.")

# ============================================================
# MENU
# ============================================================
menu = st.radio(
    "",
    ["🏠 Dashboard", "👥 Rosa", "📋 Programma Allenamenti", "📈 Crescita & Scouting", "📚 Libreria Esercizi", "🌐 Esercizi Online", "🗓️ Calendario"],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("---")

# ============================================================
# DASHBOARD
# ============================================================
if menu == "🏠 Dashboard":
    st.header("🏠 Dashboard")
    if not st.session_state.rosa:
        st.info("Inizia aggiungendo le tue giocatrici nella sezione **Rosa**.")
    c1, c2, c3, c4 = st.columns(4)
    disp = giocatrici_disponibili()
    c1.metric("Giocatrici", len(st.session_state.rosa))
    c2.metric("Disponibili", len(disp))
    c3.metric("Indisponibili", len(st.session_state.rosa) - len(disp))
    c4.metric("Esercizi in libreria", len(st.session_state.esercizi))

    st.markdown("### Composizione rosa per ruolo")
    conteggio = conta_ruoli(st.session_state.rosa)
    cols = st.columns(len(RUOLI))
    for i, (r, nome) in enumerate(RUOLI.items()):
        cols[i].metric(nome, conteggio[r])

    if st.session_state.sedute:
        st.markdown("### Prossime sedute")
        prossime = sorted(st.session_state.sedute, key=lambda s: s["data"])
        oggi = date.today().isoformat()
        future = [s for s in prossime if s["data"] >= oggi][:5]
        if future:
            for s in future:
                st.markdown(
                    f"<div class='block-seduta'><b>{s['data']}</b> — 🎯 {s['obiettivo']} "
                    f"· {s['intensita']} · {s['durata']} min</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Nessuna seduta futura programmata.")

# ============================================================
# ROSA
# ============================================================
if menu == "👥 Rosa":
    st.header("👥 Rosa Giocatrici")

    with st.expander("➕ Aggiungi giocatrice", expanded=not st.session_state.rosa):
        with st.form("add_giocatrice", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                nome = st.text_input("Nome e cognome")
                numero = st.number_input("Numero maglia", min_value=0, max_value=99, step=1)
            with c2:
                ruolo = st.selectbox("Ruolo", list(RUOLI.keys()), format_func=lambda r: RUOLI[r])
                altezza = st.number_input("Altezza (cm)", min_value=140, max_value=210, value=170, step=1)
            with c3:
                stato = st.selectbox("Stato", ["Disponibile", "Infortunata", "In recupero", "Indisponibile"])
                note = st.text_input("Note")
            if st.form_submit_button("Aggiungi", use_container_width=True):
                if nome.strip():
                    st.session_state.rosa.append({
                        "Nome": nome.strip(), "Numero": int(numero), "Ruolo": ruolo,
                        "Altezza": int(altezza), "Stato": stato, "Note": note.strip(),
                    })
                    save_state()
                    st.success(f"Aggiunta {nome}!")
                    st.rerun()
                else:
                    st.warning("Inserisci almeno il nome.")

    if st.session_state.rosa:
        st.markdown("### Elenco")
        filtro = st.multiselect("Filtra per ruolo", list(RUOLI.keys()),
                                format_func=lambda r: RUOLI[r])
        for i, g in enumerate(st.session_state.rosa):
            if filtro and g["Ruolo"] not in filtro:
                continue
            emoji = {"Disponibile": "🟢", "Infortunata": "🔴", "In recupero": "🟡", "Indisponibile": "⚪"}.get(g.get("Stato"), "⚪")
            stato = g.get("Stato", "Disponibile")
            colore = {"Disponibile": "#2ecc71", "Infortunata": "#ff5c5c", "In recupero": "#ffcf5c", "Indisponibile": "#8aa0bd"}.get(stato, "#8aa0bd")
            nome_e = _html.escape(str(g.get("Nome", "")))
            note_e = _html.escape(str(g.get("Note", "") or "—"))
            cc1, cc2 = st.columns([5, 1])
            cc1.markdown(
                f"<div class='player-card' style='box-shadow:0 0 18px {colore}66, inset 0 0 14px {colore}22; border-color:{colore}88;'>"
                f"<span class='pc-num'>#{g['Numero']}</span> &nbsp;<span class='pc-name'>{nome_e}</span><br>"
                f"<span class='pc-meta'>{RUOLI[g['Ruolo']]} · {g['Altezza']} cm</span><br>"
                f"<span class='pc-badge' style='background:{colore}22; color:{colore}; border:1px solid {colore}88;'>{emoji} {stato}</span>"
                f"<br><span class='pc-meta'>📝 {note_e}</span></div>",
                unsafe_allow_html=True,
            )
            with cc2:
                nuovo_stato = st.selectbox("stato", ["Disponibile", "Infortunata", "In recupero", "Indisponibile"],
                                           index=["Disponibile", "Infortunata", "In recupero", "Indisponibile"].index(g.get("Stato", "Disponibile")),
                                           key=f"st_{i}", label_visibility="collapsed")
                if nuovo_stato != g.get("Stato"):
                    st.session_state.rosa[i]["Stato"] = nuovo_stato
                    save_state()
                    st.rerun()
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.rosa.pop(i)
                    save_state()
                    st.rerun()
    else:
        st.info("Nessuna giocatrice inserita.")

# ============================================================
# PROGRAMMA ALLENAMENTI (generatore)
# ============================================================
if menu == "📋 Programma Allenamenti":
    st.header("📋 Programma Allenamenti")
    st.caption("Imposta l'obiettivo della seduta: il generatore compone riscaldamento, parte tecnica, situazionale e defaticamento con esercizi coerenti dalla libreria.")

    disp = giocatrici_disponibili()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        data_seduta = st.date_input("Data", value=date.today())
    with c2:
        obiettivo = st.selectbox("Obiettivo della seduta", OBIETTIVI)
    with c3:
        intensita = st.selectbox("Intensit\u00e0", INTENSITA, index=1)
    with c4:
        durata = st.slider("Durata (min)", 60, 150, 90, step=15)

    n_presenti = st.number_input("Giocatrici presenti", min_value=1, max_value=30,
                                 value=max(len(disp), 1))
    if len(disp) and n_presenti > len(disp):
        st.caption(f"ℹ️ In rosa risultano {len(disp)} disponibili.")

    cga, cgb = st.columns(2)
    with cga:
        genera = st.button("⚡ Genera seduta", type="primary", use_container_width=True)
    with cgb:
        rigenera = st.button("🔄 Proponi variante", use_container_width=True)

    if genera or rigenera:
        seed = random.randint(0, 999999) if rigenera else 42
        seduta, budget = genera_seduta(obiettivo, durata, intensita, int(n_presenti), seed=seed)
        st.session_state._ultima_seduta = {
            "data": data_seduta.isoformat(), "obiettivo": obiettivo,
            "intensita": intensita, "durata": int(durata),
            "presenti": int(n_presenti),
            "esercizi": seduta,
            "disegni": [],
        }

    ult = st.session_state.get("_ultima_seduta")
    if ult:
        st.markdown("---")
        st.subheader(f"🎯 Seduta — {ult['obiettivo']} ({ult['intensita']})")
        tot = sum(int(e["Durata_min"]) for e in ult["esercizi"])
        st.caption(f"📅 {ult['data']} · durata stimata **{tot} min** · {ult['presenti']} presenti")

        fase_corrente = None
        icone = {"Riscaldamento": "🔥", "Centrale": "🏐", "Situazionale": "🆚", "Defaticamento": "🧘"}
        for e in ult["esercizi"]:
            if e["Fase"] != fase_corrente:
                fase_corrente = e["Fase"]
                st.markdown(f"#### {icone.get(fase_corrente,'')} {fase_corrente}")
            st.markdown(
                f"<div class='block-seduta'><b>{e['Nome']}</b> "
                f"<span style='color:#ffbf69'>· {e['Durata_min']} min · {e['Fondamentale']} · {e['Livello']}</span><br>"
                f"<span style='color:#c9d6ea'>{e['Descrizione']}</span><br>"
                f"<span style='color:#7f93b0;font-size:0.9em'>🔁 Variante: {e['Varianti']}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("#### 🎨 Disegni e schemi della seduta")
        with st.expander("✏️ Apri la lavagna tattica (disegna e scarica)"):
            components.html(TACTIC_BOARD_HTML, height=520)
            st.caption("Disegna lo schema sul campo, premi **Scarica PNG**, poi caricalo qui sotto per allegarlo alla seduta.")
        up = st.file_uploader("Allega un disegno/schema (PNG o JPG)", type=["png", "jpg", "jpeg"], key="up_disegno")
        if up is not None and st.button("➕ Allega disegno alla seduta"):
            b64 = base64.b64encode(up.getvalue()).decode()
            ult.setdefault("disegni", []).append({"nome": up.name, "b64": b64})
            st.session_state._ultima_seduta = ult
            st.success("Disegno allegato alla seduta!")
            st.rerun()
        for di, d in enumerate(ult.get("disegni", [])):
            st.image(base64.b64decode(d["b64"]), caption=d.get("nome", ""), use_container_width=True)
            if st.button(f"🗑️ Rimuovi disegno", key=f"deldis_{di}"):
                ult["disegni"].pop(di)
                st.session_state._ultima_seduta = ult
                st.rerun()

        if st.button("📅 Salva questa seduta nel calendario", type="primary"):
            st.session_state.sedute.append(ult)
            save_state()
            st.success("Seduta salvata nel calendario!")

# ============================================================
# LIBRERIA ESERCIZI
# ============================================================
if menu == "📚 Libreria Esercizi":
    st.header("📚 Libreria Esercizi")
    df = st.session_state.esercizi

    with st.expander("➕ Aggiungi esercizio"):
        with st.form("add_ex", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                e_nome = st.text_input("Nome esercizio")
                e_fond = st.selectbox("Fondamentale", FONDAMENTALI)
            with c2:
                e_obj = st.selectbox("Obiettivo", OBIETTIVI)
                e_fase = st.selectbox("Fase", ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"])
            with c3:
                e_min = st.number_input("Min. giocatrici", 1, 24, 4)
                e_dur = st.number_input("Durata (min)", 3, 40, 12)
                e_liv = st.selectbox("Livello", ["Base", "Medio", "Avanzato"])
            e_desc = st.text_area("Descrizione")
            e_var = st.text_input("Varianti / progressioni")
            if st.form_submit_button("Aggiungi esercizio", use_container_width=True):
                if e_nome.strip():
                    nuovo = {"Nome": e_nome.strip(), "Fondamentale": e_fond, "Obiettivo": e_obj,
                             "Fase": e_fase, "Min_Giocatrici": int(e_min), "Durata_min": int(e_dur),
                             "Livello": e_liv, "Descrizione": e_desc.strip(), "Varianti": e_var.strip()}
                    st.session_state.esercizi = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
                    save_state()
                    st.success("Esercizio aggiunto!")
                    st.rerun()
                else:
                    st.warning("Serve almeno il nome dell'esercizio.")

    c1, c2, c3 = st.columns(3)
    f_fond = c1.multiselect("Fondamentale", FONDAMENTALI)
    f_obj = c2.multiselect("Obiettivo", OBIETTIVI)
    f_fase = c3.multiselect("Fase", ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"])

    vista = df.copy()
    if f_fond:
        vista = vista[vista["Fondamentale"].isin(f_fond)]
    if f_obj:
        vista = vista[vista["Obiettivo"].isin(f_obj)]
    if f_fase:
        vista = vista[vista["Fase"].isin(f_fase)]

    st.caption(f"{len(vista)} esercizi")
    for idx, e in vista.iterrows():
        with st.container():
            cc1, cc2 = st.columns([9, 1])
            fonte = e.get("Fonte", "") if hasattr(e, "get") else ""
            fonte_html = ""
            if isinstance(fonte, str) and fonte.strip():
                fonte_html = (f"<br><a href='{_html.escape(fonte)}' target='_blank' "
                              f"style='color:#ffbf69;font-size:0.85em'>🔗 Fonte online</a>")
            cc1.markdown(
                f"<div class='ex-card'><b>{e['Nome']}</b> "
                f"<span style='color:#ffbf69'>· {e['Fondamentale']} · {e['Fase']} · {e['Durata_min']}min · min {e['Min_Giocatrici']} gig. · {e['Livello']}</span><br>"
                f"<span style='color:#c9d6ea'>{e['Descrizione']}</span><br>"
                f"<span style='color:#7f93b0;font-size:0.9em'>🔁 {e['Varianti']}</span>{fonte_html}</div>",
                unsafe_allow_html=True,
            )
            if cc2.button("🗑️", key=f"delex_{idx}"):
                st.session_state.esercizi = df.drop(idx).reset_index(drop=True)
                save_state()
                st.rerun()

# ============================================================
# ESERCIZI ONLINE
# ============================================================
if menu == "🌐 Esercizi Online":
    st.header("🌐 Esercizi da Internet")
    st.caption("Trova ispirazione online e importa nuovi esercizi nella tua libreria. Serve una connessione a internet.")

    tab_cerca, tab_importa = st.tabs(["🔎 Cerca ispirazione", "⬇️ Importa da link"])

    # ---- TAB 1: link di ricerca ----
    with tab_cerca:
        c1, c2, c3 = st.columns(3)
        f_fond = c1.selectbox("Fondamentale", FONDAMENTALI, key="onl_fond")
        f_obj = c2.selectbox("Obiettivo", OBIETTIVI, key="onl_obj")
        f_liv = c3.selectbox("Livello", ["Base", "Medio", "Avanzato"], key="onl_liv")
        st.markdown("#### Apri le ricerche pronte")
        st.caption("I link si aprono in una nuova scheda del browser.")
        for etichetta, url in link_ricerca(f_fond, f_obj, f_liv).items():
            st.markdown(f"- [{etichetta}]({url})")
        st.info("💡 Trovato un buon drill? Copia il link e passa alla scheda **Importa da link** per aggiungerlo alla libreria.")

    # ---- TAB 2: import da URL ----
    with tab_importa:
        url = st.text_input("Incolla il link (video YouTube o pagina web)", key="onl_url")
        if st.button("🔍 Analizza link", use_container_width=True):
            if url.strip():
                try:
                    with st.spinner("Recupero informazioni dal link..."):
                        st.session_state._draft_online = importa_da_link(url)
                    st.success("Informazioni recuperate! Completa i campi e salva.")
                except Exception as e:
                    st.session_state._draft_online = {"titolo": "", "descrizione": "", "autore": "", "fonte": url.strip()}
                    st.warning(f"Non sono riuscito a leggere il contenuto ({e}). Puoi comunque compilare a mano: il link è gi\u00e0 salvato come fonte.")
            else:
                st.warning("Incolla prima un link.")

        draft = st.session_state.get("_draft_online")
        if draft:
            st.markdown("---")
            st.markdown("#### 📝 Nuovo esercizio dal link")
            with st.form("form_online", clear_on_submit=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    o_nome = st.text_input("Nome esercizio", value=draft.get("titolo", ""))
                    o_fond = st.selectbox("Fondamentale", FONDAMENTALI, key="of_fond")
                with c2:
                    o_obj = st.selectbox("Obiettivo", OBIETTIVI, key="of_obj")
                    o_fase = st.selectbox("Fase", ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"], index=1, key="of_fase")
                with c3:
                    o_min = st.number_input("Min. giocatrici", 1, 24, 4, key="of_min")
                    o_dur = st.number_input("Durata (min)", 3, 40, 12, key="of_dur")
                    o_liv = st.selectbox("Livello", ["Base", "Medio", "Avanzato"], index=1, key="of_liv")
                o_desc = st.text_area("Descrizione", value=draft.get("descrizione", ""))
                o_var = st.text_input("Varianti / progressioni")
                o_fonte = st.text_input("Fonte (link)", value=draft.get("fonte", ""))
                if st.form_submit_button("➕ Aggiungi alla libreria", use_container_width=True):
                    if o_nome.strip():
                        nuovo = {"Nome": o_nome.strip(), "Fondamentale": o_fond, "Obiettivo": o_obj,
                                 "Fase": o_fase, "Min_Giocatrici": int(o_min), "Durata_min": int(o_dur),
                                 "Livello": o_liv, "Descrizione": o_desc.strip(), "Varianti": o_var.strip(),
                                 "Fonte": o_fonte.strip()}
                        st.session_state.esercizi = pd.concat([st.session_state.esercizi, pd.DataFrame([nuovo])], ignore_index=True)
                        save_state()
                        st.session_state._draft_online = None
                        st.success(f"'{o_nome}' aggiunto alla libreria!")
                        st.rerun()
                    else:
                        st.warning("Serve almeno il nome dell'esercizio.")

# ============================================================
# CALENDARIO
# ============================================================
if menu == "🗓️ Calendario":
    st.header("🗓️ Calendario Sedute")
    if not st.session_state.sedute:
        st.info("Nessuna seduta salvata. Generane una nella sezione **Programma Allenamenti**.")
    else:
        sedute = sorted(st.session_state.sedute, key=lambda s: s["data"])
        # riepilogo carichi settimana
        st.markdown("### Sedute programmate")
        for i, s in enumerate(sedute):
            tot = sum(int(e["Durata_min"]) for e in s["esercizi"])
            with st.expander(f"📅 {s['data']} — {s['obiettivo']} · {s['intensita']} · {tot} min"):
                fase_corrente = None
                for e in s["esercizi"]:
                    if e["Fase"] != fase_corrente:
                        fase_corrente = e["Fase"]
                        st.markdown(f"**{fase_corrente}**")
                    st.markdown(f"- {e['Nome']} ({e['Durata_min']} min) — _{e['Descrizione']}_")
                for d in s.get("disegni", []):
                    st.image(base64.b64decode(d["b64"]), caption=d.get("nome", ""), use_container_width=True)
                if st.button("🗑️ Elimina seduta", key=f"delsed_{i}"):
                    st.session_state.sedute.remove(s)
                    save_state()
                    st.rerun()

        st.markdown("---")
        st.markdown("### Distribuzione carichi")
        dfc = pd.DataFrame([{"Data": s["data"], "Intensit\u00e0": s["intensita"], "Obiettivo": s["obiettivo"]} for s in sedute])
        st.dataframe(dfc, use_container_width=True, hide_index=True)
        pesi = {"Scarico": 1, "Pre-partita": 2, "Medio": 2, "Carico": 3}
        dfc["Carico"] = dfc["Intensit\u00e0"].map(pesi)
        st.bar_chart(dfc.set_index("Data")["Carico"])
        st.caption("Consiglio: evita due sedute a carico alto consecutive e programma uno scarico prima della gara.")

# ============================================================
# CRESCITA & SCOUTING
# ============================================================
if menu == "📈 Crescita & Scouting":
    st.header("📈 Crescita & Scouting")
    st.caption("Individua dove migliorare, costruisci il programma fisico-tecnico-tattico a lungo termine e raccogli lo scouting sulle avversarie.")
    tab_migl, tab_prog, tab_scout = st.tabs([
        "🎯 Dove posso migliorare",
        "🗓️ Programma a lungo termine",
        "🔍 Scouting",
    ])
    with tab_migl:
        st.caption("Valuta ogni fondamentale da 1 a 5: l'app individua le aree pi\u00f9 deboli e suggerisce esercizi mirati dalla libreria.")
        if not st.session_state.rosa:
            st.info("Aggiungi prima le giocatrici nella sezione **Rosa**.")
        else:
            nomi = [f"#{g['Numero']} {g['Nome']} \u00b7 {RUOLI.get(g['Ruolo'], g['Ruolo'])}" for g in st.session_state.rosa]
            idx = st.selectbox("Giocatrice", range(len(nomi)), format_func=lambda i: nomi[i])
            g = st.session_state.rosa[idx]
            val = g.get("Valutazioni", {})
            with st.form(f"val_form_{idx}"):
                st.markdown("#### Valutazione fondamentali (1 = da migliorare \u00b7 5 = punto di forza)")
                nuove = {}
                cols = st.columns(len(FONDAMENTALI))
                for j, f in enumerate(FONDAMENTALI):
                    nuove[f] = cols[j].slider(f, 1, 5, int(val.get(f, 3)), key=f"val_{idx}_{f}")
                note_m = st.text_area("Note sullo sviluppo della giocatrice", value=g.get("NoteSviluppo", ""))
                if st.form_submit_button("💾 Salva valutazione", use_container_width=True):
                    st.session_state.rosa[idx]["Valutazioni"] = nuove
                    st.session_state.rosa[idx]["NoteSviluppo"] = note_m.strip()
                    save_state()
                    st.success("Valutazione salvata!")
                    st.rerun()
            if val:
                ordinate = sorted(val.items(), key=lambda kv: kv[1])
                deboli = [f for f, v in ordinate if v <= 2][:3] or [ordinate[0][0]]
                st.markdown("#### 🔻 Aree su cui lavorare")
                st.markdown(" \u00b7 ".join(f"**{d}** ({val[d]}/5)" for d in deboli))
                df = st.session_state.esercizi
                sugg = df[df["Fondamentale"].isin(deboli)]
                st.markdown("#### 🏐 Esercizi consigliati per migliorare")
                if sugg.empty:
                    st.caption("Nessun esercizio in libreria per queste aree. Aggiungine dalla sezione Libreria o Esercizi Online.")
                else:
                    for _, e in sugg.head(8).iterrows():
                        st.markdown(
                            f"<div class='ex-card'><b>{e['Nome']}</b> "
                            f"<span style='color:#ffbf69'>\u00b7 {e['Fondamentale']} \u00b7 {e['Durata_min']}min \u00b7 {e['Livello']}</span><br>"
                            f"<span style='color:#c9d6ea'>{e['Descrizione']}</span></div>",
                            unsafe_allow_html=True,
                        )
            else:
                st.info("Compila e salva la valutazione per vedere le aree di miglioramento e gli esercizi consigliati.")
            st.markdown("---")
            st.markdown("### 📊 Panoramica squadra")
            valutate = [gg for gg in st.session_state.rosa if gg.get("Valutazioni")]
            if valutate:
                medie = {}
                for f in FONDAMENTALI:
                    vals = [gg["Valutazioni"].get(f) for gg in valutate if gg["Valutazioni"].get(f)]
                    if vals:
                        medie[f] = round(sum(vals) / len(vals), 1)
                if medie:
                    st.bar_chart(pd.DataFrame({"Media (1-5)": medie}))
                    deboli_team = sorted(medie.items(), key=lambda kv: kv[1])[:2]
                    st.caption("Aree pi\u00f9 deboli della squadra: " + " \u00b7 ".join(f"{f} ({v}/5)" for f, v in deboli_team))
                st.caption(f"Giocatrici valutate: {len(valutate)}/{len(st.session_state.rosa)}")
            else:
                st.caption("Nessuna valutazione registrata ancora.")
    with tab_prog:
        st.caption("Costruisci un programma pluri-settimanale con focus fisico, tecnico e tattico. Ogni fase (mesociclo) evidenzia le priorit\u00e0 del periodo.")
        with st.form("form_prog"):
            c1, c2, c3 = st.columns(3)
            with c1:
                p_nome = st.text_input("Nome del programma", value="Programma stagionale")
                p_start = st.date_input("Data inizio", value=date.today(), key="prog_start")
            with c2:
                p_sett = st.number_input("Durata (settimane)", 4, 40, 12)
                p_persett = st.number_input("Sedute a settimana", 1, 6, 3)
            with c3:
                foc_fis = st.selectbox("Focus fisico", AREE_SVILUPPO["Fisico"])
                foc_tec = st.selectbox("Focus tecnico", AREE_SVILUPPO["Tecnico"])
                foc_tat = st.selectbox("Focus tattico", AREE_SVILUPPO["Tattico"])
            if st.form_submit_button("⚡ Genera programma a lungo termine", type="primary", use_container_width=True):
                piano = genera_programma_lt(p_nome, p_start, int(p_sett), int(p_persett), foc_fis, foc_tec, foc_tat)
                st.session_state.piani.append(piano)
                save_state()
                st.success("Programma generato e salvato!")
                st.rerun()
        if st.session_state.piani:
            st.markdown("---")
            st.markdown("### 📚 Programmi salvati")
            for pi in range(len(st.session_state.piani) - 1, -1, -1):
                piano = st.session_state.piani[pi]
                with st.expander(f"🗓️ {piano['nome']} \u2014 dal {piano['inizio']} \u00b7 {piano['settimane']} sett. \u00b7 {piano['per_settimana']}/sett."):
                    st.markdown(f"**Focus:** 💪 {piano['focus_fisico']} \u00b7 🏐 {piano['focus_tecnico']} \u00b7 🧠 {piano['focus_tattico']}")
                    st.dataframe(pd.DataFrame(piano["fasi"]), use_container_width=True, hide_index=True)
                    if st.button("🗑️ Elimina programma", key=f"delpiano_{pi}"):
                        st.session_state.piani.pop(pi)
                        save_state()
                        st.rerun()
        else:
            st.info("Nessun programma ancora. Compila i campi qui sopra e genera il tuo piano a lungo termine.")
    with tab_scout:
        st.caption("Raccogli informazioni sulle squadre avversarie: sistema di gioco, giocatrici pericolose, punti di forza e debolezze.")
        with st.expander("➕ Nuovo report scouting", expanded=not st.session_state.scouting):
            with st.form("form_scout", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    s_avv = st.text_input("Squadra avversaria")
                    s_data = st.date_input("Data osservazione", value=date.today(), key="scout_data")
                    s_sistema = st.text_input("Sistema di gioco (es. 5-1, 4-2)")
                    s_peric = st.text_input("Giocatrici pericolose (numeri / nomi / ruoli)")
                with c2:
                    s_forza = st.text_area("Punti di forza")
                    s_deboli = st.text_area("Punti deboli / come attaccarle")
                s_note = st.text_area("Note tattiche (battuta, ricezione, muro-difesa...)")
                if st.form_submit_button("💾 Salva report", use_container_width=True):
                    if s_avv.strip():
                        st.session_state.scouting.append({
                            "avversario": s_avv.strip(),
                            "data": s_data.isoformat(),
                            "sistema": s_sistema.strip(),
                            "pericolose": s_peric.strip(),
                            "forza": s_forza.strip(),
                            "deboli": s_deboli.strip(),
                            "note": s_note.strip(),
                        })
                        save_state()
                        st.success("Report scouting salvato!")
                        st.rerun()
                    else:
                        st.warning("Inserisci almeno il nome della squadra avversaria.")
        if st.session_state.scouting:
            st.markdown("### 🗂️ Report salvati")
            for sc in sorted(st.session_state.scouting, key=lambda x: x["data"], reverse=True):
                titolo = f"🔍 {sc['avversario']} \u2014 {sc['data']} \u00b7 sistema {sc['sistema'] or 'n/d'}"
                with st.expander(titolo):
                    st.markdown(f"**⚠️ Giocatrici pericolose:** {sc['pericolose'] or '\u2014'}")
                    st.markdown(f"**💪 Punti di forza:** {sc['forza'] or '\u2014'}")
                    st.markdown(f"**🎯 Punti deboli / come attaccarle:** {sc['deboli'] or '\u2014'}")
                    st.markdown(f"**📝 Note tattiche:** {sc['note'] or '\u2014'}")
                    if st.button("🗑️ Elimina report", key=f"delscout_{sc['avversario']}_{sc['data']}"):
                        st.session_state.scouting.remove(sc)
                        save_state()
                        st.rerun()
        else:
            st.info("Nessun report scouting ancora registrato.")
