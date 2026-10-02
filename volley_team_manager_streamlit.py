import streamlit as st
import pandas as pd
import json
import os
import io
import base64
import pickle
import tempfile
import shutil
import random
import urllib.request
import urllib.parse
import re
import html as _html
from datetime import datetime, date, timedelta

# Librerie opzionali (il programma funziona anche senza)
try:
    from PIL import Image, ImageDraw
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False

try:
    from streamlit_drawable_canvas import st_canvas
    _HAS_CANVAS = True
except Exception:
    _HAS_CANVAS = False

# ============================================================
# CONFIGURAZIONE
# ============================================================
st.set_page_config(
    page_title="VolleyCoach Manager",
    page_icon="\U0001F3D0",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAVE_FILE = "volleycoach_state.pkl"
BAK_FILE = "volleycoach_state.pkl.bak"

# Tema grafico predefinito (colori della squadra, personalizzabili dall'app)
TEMA_DEFAULT = {
    "nome_squadra": "VolleyCoach",
    "sottotitolo": "Gestione squadra \u00b7 Serie D femminile",
    "colore1": "#ff9f1c",   # colore principale
    "colore2": "#ffbf69",   # colore secondario / chiaro
    "logo": "",             # logo squadra in base64 (opzionale)
}

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
FASI = ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"]

# Giorni della settimana (0 = lunedi)
GIORNI_IT = ["Luned\u00ec", "Marted\u00ec", "Mercoled\u00ec", "Gioved\u00ec", "Venerd\u00ec", "Sabato", "Domenica"]

# Settimana tipo di DEFAULT (chiavi stringa per compatibilit\u00e0 JSON)
#  Luned\u00ec: prevenzione, fisico e tecnica individuale
#  Marted\u00ec: attacco e difesa
#  Gioved\u00ec: battuta e ricezione
SCHEMA_DEFAULT = {
    "0": {"nome": "Prevenzione, Fisico e Tecnica individuale",
          "obiettivi": ["Condizione fisica", "Tecnica generale"], "prevenzione": True},
    "1": {"nome": "Attacco e Difesa",
          "obiettivi": ["Attacco", "Muro-Difesa"], "prevenzione": False},
    "3": {"nome": "Battuta e Ricezione",
          "obiettivi": ["Battuta", "Ricezione"], "prevenzione": False},
}

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    :root {
        --vc-bg1:#0a1120; --vc-bg2:#0f1c38; --vc-card:#141f3a; --vc-card2:#16223d;
        --vc-border:#26334f; --vc-accent:#ff9f1c; --vc-accent2:#ffbf69;
        --vc-text:#e8eefc; --vc-muted:#9fb3d1;
    }
    .stApp {
        background:
            radial-gradient(1200px 600px at 15% -10%, rgba(255,159,28,0.10), transparent 60%),
            radial-gradient(1000px 500px at 110% 0%, rgba(45,110,255,0.12), transparent 55%),
            linear-gradient(180deg, var(--vc-bg1) 0%, var(--vc-bg2) 100%);
        color: var(--vc-text);
    }
    .block-container { padding-top: 3.2rem; }
    header[data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#0b1526 0%, #0a1120 100%) !important;
        border-right: 1px solid var(--vc-border);
    }
    h1, h2, h3 {
        color: var(--vc-accent) !important;
        font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
        letter-spacing: .3px;
    }
    h2 { border-bottom: 2px solid rgba(255,159,28,0.25); padding-bottom: .35rem; }
    .stButton>button {
        border-radius: 10px; font-weight: 700; border: none;
        background: linear-gradient(90deg, var(--vc-accent), var(--vc-accent2)); color: #1a1000;
        transition: all .18s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(255,159,28,0.45); }
    .stButton>button:active { transform: translateY(0); }
    div[role="radiogroup"] { flex-wrap: wrap; row-gap:.45rem; }
    div[role="radiogroup"][aria-label=""] { gap:.4rem; }
    div[data-testid="stHorizontalBlock"] { align-items: stretch; }
    div[role="radiogroup"] label {
        background: var(--vc-card); border:1px solid var(--vc-border);
        border-radius: 999px; padding: .35rem .9rem; margin: 0 .15rem;
        transition: all .15s ease;
    }
    div[role="radiogroup"] label:hover { border-color: var(--vc-accent); }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, var(--vc-card) 0%, var(--vc-card2) 100%);
        border: 1px solid var(--vc-border); border-radius: 14px;
        padding: 14px 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; color: var(--vc-accent) !important; }
    div[data-testid="stMetricLabel"] { color: var(--vc-muted) !important; }
    .block-seduta {
        background: linear-gradient(90deg, var(--vc-card2), rgba(22,34,61,0.6));
        border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
        border-left: 4px solid var(--vc-accent);
        box-shadow: 0 3px 10px rgba(0,0,0,0.2); transition: transform .15s ease;
    }
    .block-seduta:hover { transform: translateX(3px); }
    .ex-card {
        background: var(--vc-card); border-radius: 12px; padding: 14px 16px;
        margin-bottom: 10px; border: 1px solid var(--vc-border);
        box-shadow: 0 3px 10px rgba(0,0,0,0.18); transition: all .15s ease;
    }
    .ex-card:hover { border-color: var(--vc-accent); box-shadow: 0 6px 18px rgba(0,0,0,0.3); }
    .ex-disegno { max-width:100%; border-radius:10px; border:1px solid var(--vc-border); margin-top:8px; background:#fff; }
    .flip-card { background:transparent; perspective:1200px; height:200px; margin-bottom:6px; }
    .flip-inner {
        position:relative; width:100%; height:100%;
        transition: transform .65s cubic-bezier(.4,.2,.2,1);
        transform-style: preserve-3d;
    }
    .flip-card:hover .flip-inner { transform: rotateY(180deg); }
    .flip-front, .flip-back {
        position:absolute; width:100%; height:100%;
        -webkit-backface-visibility:hidden; backface-visibility:hidden;
        border-radius:18px; padding:16px 18px; box-sizing:border-box; overflow:hidden;
        display:flex; flex-direction:column;
    }
    .flip-front { background: linear-gradient(150deg, #16234180 0%, #101b33f0 100%); }
    .flip-back {
        transform: rotateY(180deg);
        background: linear-gradient(150deg, #101b33f0 0%, #16223dcc 100%);
    }
    .flip-name { font-size:1.15rem; font-weight:800; color:#ffffff; line-height:1.2; }
    .flip-role { font-weight:700; font-size:.95rem; margin-top:2px; }
    .flip-meta { color:#9fb3d1; font-size:.82rem; margin-top:4px; }
    .flip-hint { color:#6f83a0; font-size:.72rem; margin-top:auto; }
    .flip-back-title { font-weight:800; font-size:.95rem; margin-bottom:6px; }
    .flip-back-body { color:#dfe8f7; font-size:.82rem; line-height:1.35; overflow-y:auto; }
    .flip-empty { color:#7f93b0; font-size:.82rem; font-style:italic; }
    .vc-badge {
        display:inline-block; padding:.15rem .6rem; border-radius:999px;
        font-size:.72rem; font-weight:700; letter-spacing:.3px; margin-right:.3rem;
    }
    .badge-base { background:rgba(46,204,113,0.18); color:#5be59a; border:1px solid rgba(46,204,113,0.4); }
    .badge-medio { background:rgba(255,159,28,0.18); color:#ffbf69; border:1px solid rgba(255,159,28,0.4); }
    .badge-avanzato { background:rgba(231,76,60,0.18); color:#ff8f80; border:1px solid rgba(231,76,60,0.4); }
    .role-chip { display:inline-block; padding:.2rem .6rem; border-radius:999px; font-size:.78rem; font-weight:700; margin:.15rem; }
    .vc-hero {
        background: linear-gradient(120deg, rgba(255,159,28,0.16), rgba(45,110,255,0.14));
        border: 1px solid var(--vc-border); border-radius: 18px;
        padding: 20px 26px; margin-bottom: 16px;
        box-shadow: 0 6px 22px rgba(0,0,0,0.28);
    }
    .vc-hero h1 { margin:0; font-size:1.9rem; }
    .vc-hero p { margin:.3rem 0 0; color: var(--vc-muted); font-size:.95rem; }
    button[data-baseweb="tab"] { font-weight:600; }
    div[data-testid="stExpander"] {
        border:1px solid var(--vc-border); border-radius:12px; background:rgba(20,31,58,0.5);
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea, div[data-baseweb="select"]>div {
        border-radius: 10px !important;
    }
    hr { border-color: var(--vc-border); }
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-thumb { background: #2a3a5c; border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--vc-accent); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LIBRERIA ESERCIZI DEFAULT (ampliata)
# ============================================================
def _ex(nome, fond, obj, fase, mn, dur, liv, desc, var):
    return {"Nome": nome, "Fondamentale": fond, "Obiettivo": obj, "Fase": fase,
            "Min_Giocatrici": mn, "Durata_min": dur, "Livello": liv,
            "Descrizione": desc, "Varianti": var, "Disegno": ""}

ESERCIZI_DEFAULT = [
    # --- RISCALDAMENTO / FISICO ---
    _ex("Corsa e mobilit\u00e0 articolare", "Fisico", "Condizione fisica", "Riscaldamento", 1, 10, "Base", "Corsa leggera, skip, calciata, aperture anche e spalle. Attivazione generale.", "Aggiungere andature laterali e spostamenti a specchio a coppie."),
    _ex("Attivazione a coppie con palla", "Fisico", "Tecnica generale", "Riscaldamento", 2, 8, "Base", "Palleggio e bagher a coppie a distanza crescente, lavoro su appoggi e trasferimento del peso.", "Un tocco in palleggio + un tocco in bagher alternati."),
    _ex("Mobilit\u00e0 spalle con elastico", "Fisico", "Condizione fisica", "Riscaldamento", 1, 7, "Base", "Circonduzioni, extrarotazioni ed intrarotazioni con elastico per preparare la spalla al carico di battuta e attacco.", "Aggiungere lavoro di cuffia dei rotatori a corpo libero."),
    _ex("Scaletta agilit\u00e0 (speed ladder)", "Fisico", "Condizione fisica", "Riscaldamento", 1, 8, "Base", "Serie di appoggi rapidi dentro la scaletta: dentro-dentro, laterali, in e out. Frequenza dei piedi.", "Terminare ogni passaggio con uno spostamento difensivo."),
    _ex("Staffette a squadre", "Fisico", "Condizione fisica", "Riscaldamento", 6, 8, "Base", "Staffette con spostamenti, capovolte e tocchi di palla. Attivazione divertente e competitiva.", "Inserire un gesto tecnico (palleggio) a met\u00e0 percorso."),
    _ex("Core stability circuit", "Fisico", "Condizione fisica", "Centrale", 1, 12, "Medio", "Plank frontale/laterale, ponte, russian twist, superman. 3 giri.", "Aggiungere instabilit\u00e0 (fitball) o carico leggero."),
    _ex("Pliometria salti al muro", "Fisico", "Condizione fisica", "Centrale", 1, 10, "Medio", "Serie di salti verticali con rincorsa da muro/attacco, focus su tecnica di stacco e atterraggio.", "Salti su box, salti ripetuti reattivi."),
    _ex("Forza arti inferiori (circuito)", "Fisico", "Condizione fisica", "Centrale", 1, 15, "Medio", "Squat, affondi, hip thrust e calf a corpo libero o con sovraccarico leggero. 3 serie.", "Aumentare il carico o passare a monopodalico."),
    _ex("Stretching e defaticamento", "Fisico", "Condizione fisica", "Defaticamento", 1, 8, "Base", "Allungamento globale, respirazione, mobilit\u00e0 dolce. Recupero e prevenzione.", "Foam roller su schiena e gambe."),
    _ex("Gioco ludico di chiusura", "Fisico", "Tecnica generale", "Defaticamento", 6, 8, "Base", "Gioco leggero (palla avvelenata / bagher a squadre) per chiudere in positivit\u00e0.", "A eliminazione o a punti."),

    # --- BATTUTA ---
    _ex("Battuta a bersaglio", "Battuta", "Battuta", "Centrale", 4, 15, "Base", "Zone bersaglio a terra (1, 5, 6). Ogni giocatrice serve 10 palloni cercando le zone. Si conta il punteggio.", "Aumentare il rischio: bersagli pi\u00f9 piccoli o zone di conflitto."),
    _ex("Battuta salto float", "Battuta", "Battuta", "Centrale", 3, 12, "Medio", "Tecnica di battuta in salto flottante: lancio, timing, colpo pieno. Serie da 8-10.", "Battuta in salto spin per le pi\u00f9 avanzate."),
    _ex("Battuta sotto pressione (7 di fila)", "Battuta", "Fase break (cambio palla)", "Situazionale", 6, 12, "Medio", "La squadra deve fare 7 battute buone consecutive. Ogni errore riparte da zero. Gestione tensione.", "Alzare/abbassare il target in base al livello."),
    _ex("Battuta tecnica dal basso/alto", "Battuta", "Battuta", "Riscaldamento", 2, 10, "Base", "Ripasso tecnico del gesto di battuta: posizione, lancio e colpo. Per le giovani o come riattivazione.", "Progredire dalla battuta dal basso a quella in appoggio."),
    _ex("Battuta e corsa in difesa", "Battuta", "Fase break (cambio palla)", "Situazionale", 4, 12, "Medio", "Dopo la battuta la giocatrice entra subito in campo pronta a difendere. Collega servizio e transizione difensiva.", "L'allenatore attacca subito un pallone sulla battitrice."),
    _ex("Battuta mirata per rotazione", "Battuta", "Fase side-out", "Situazionale", 6, 12, "Avanzato", "Servire nella zona debole della ricezione avversaria in base alla rotazione. Lettura e precisione.", "Assegnare punti bonus se si colpisce la zona chiamata."),

    # --- RICEZIONE ---
    _ex("Ricezione a due (P1-P5)", "Ricezione", "Ricezione", "Centrale", 5, 15, "Base", "Due ricevitrici, battute dall'altro campo verso il palleggiatore in zona 2-3. Focus su appoggi e bersaglio alzata.", "Introdurre chiamata e comunicazione tra le ricevitrici."),
    _ex("Ricezione a tre + attacco", "Ricezione", "Fase side-out", "Situazionale", 8, 20, "Medio", "Ricezione a 3, palleggiatore alza, attacco completo. Valuta la qualit\u00e0 del cambio palla dopo servizio.", "Battute mirate sulle zone di conflitto tra ricevitrici."),
    _ex("Ricezione con valutazione (# / + / -)", "Ricezione", "Ricezione", "Centrale", 4, 12, "Medio", "Ogni ricezione viene valutata a voce (perfetta/buona/scarsa). Obiettivo: % di positivit\u00e0 sopra soglia.", "Registrare i dati e confrontarli tra sedute."),
    _ex("Ricezione in movimento", "Ricezione", "Ricezione", "Centrale", 3, 12, "Base", "La ricevitrice parte da fuori posizione e si sposta sul pallone. Lavoro su spostamenti e stop prima del tocco.", "Battute alternate corte e lunghe."),
    _ex("Ricezione libero + bagher laterale", "Ricezione", "Ricezione", "Centrale", 2, 12, "Medio", "Lavoro specifico libero/seconda linea su bagher laterale e appoggio su palloni tesi.", "Aggiungere il tuffo su palla corta."),
    _ex("Ricezione a muro di pressione (raffica)", "Ricezione", "Ricezione", "Situazionale", 4, 12, "Avanzato", "Battute continue e ravvicinate: la ricevitrice deve riordinarsi rapidamente tra un pallone e l'altro.", "Alternare battitori con traiettorie diverse."),

    # --- PALLEGGIO / ALZATA ---
    _ex("Alzata di precisione ai bersagli", "Palleggio", "Tecnica generale", "Centrale", 3, 12, "Base", "Palleggiatrici alzano a bersagli fissi in zona 4, 2 e primo tempo. Precisione e altezza costanti.", "Alzata dopo spostamento o da posizione defilata."),
    _ex("Palleggiatore in situazione (ricezione random)", "Palleggio", "Fase side-out", "Situazionale", 6, 15, "Medio", "Ricezione volutamente imperfetta: la palleggiatrice sceglie la miglior soluzione d'alzata. Sviluppa lettura.", "Introdurre muro avversario per forzare scelte."),
    _ex("Palleggio di controllo a coppie", "Palleggio", "Tecnica generale", "Riscaldamento", 2, 8, "Base", "Palleggio frontale, dietro, in sospensione a coppie. Mani, polsi e postura.", "Alternare palleggio alto e teso."),
    _ex("Alzata in salto e secondo tocco", "Palleggio", "Fase side-out", "Centrale", 3, 12, "Avanzato", "La palleggiatrice alza in sospensione per velocizzare il gioco; lavoro anche sul secondo tocco d'attacco.", "Chiamate di combinazioni (primo tempo + fast)."),
    _ex("Spostamento del palleggiatore (3 metri)", "Palleggio", "Tecnica generale", "Centrale", 3, 10, "Medio", "La palleggiatrice entra da zona 1 verso la zona 2-3 e alza. Timing di entrata e appoggi.", "Partire da posizioni diverse di difesa."),

    # --- ATTACCO ---
    _ex("Attacco da zona 4 con alzata", "Attacco", "Attacco", "Centrale", 5, 18, "Base", "Serie di attacchi da banda con alzata reale. Focus su rincorsa, timing e colpo. 10-12 palloni a testa.", "Bersagli a terra (parallela/diagonale), colpo in lungolinea."),
    _ex("Primo tempo centrali", "Attacco", "Attacco", "Centrale", 3, 12, "Medio", "Sincronia palleggiatrice-centrale sul primo tempo. Tempi di stacco e colpo.", "Aggiungere il muro avversario passivo poi attivo."),
    _ex("Attacco contro muro-difesa", "Attacco", "Muro-Difesa", "Situazionale", 8, 20, "Avanzato", "Attacco reale contro muro a uno/due + difesa schierata. Sviluppa scelte di colpo e mani-out.", "Punteggio a chi vince lo scambio."),
    _ex("Attacco da zona 2 (opposto)", "Attacco", "Attacco", "Centrale", 5, 15, "Medio", "Attacco da posto 2 con rincorsa corretta. Diagonale stretta e lungolinea.", "Inserire muro avversario a lettura."),
    _ex("Attacco di seconda linea (pipe)", "Attacco", "Attacco", "Situazionale", 6, 15, "Avanzato", "Attacco da zona 6 (pipe) con alzata tesa. Rincorsa dall'interno del campo.", "Combinare pipe + primo tempo per il muro."),
    _ex("Fast e combinazioni d'attacco", "Attacco", "Fase side-out", "Situazionale", 6, 18, "Avanzato", "Combinazioni palleggiatrice-attaccanti (primo tempo + spostamento banda). Lettura del muro.", "Chiamate variabili a sorpresa."),
    _ex("Pallonetto e colpi piazzati", "Attacco", "Attacco", "Centrale", 3, 10, "Base", "Lavoro sui colpi di finezza: pallonetto, smorzata, colpo spinto nei buchi della difesa.", "Chiamare la zona del campo da colpire."),

    # --- MURO ---
    _ex("Tecnica di muro individuale", "Muro", "Muro-Difesa", "Centrale", 2, 12, "Base", "Spostamento, stacco e penetrazione delle mani oltre rete. Palloni lanciati dall'alto (sgabello).", "Muro dopo spostamento laterale (accostamento centrale)."),
    _ex("Muro a due sincronizzato", "Muro", "Muro-Difesa", "Centrale", 4, 14, "Medio", "Centrale + banda murano insieme. Chiusura del muro e lettura dell'alzata.", "Aggiungere l'attaccante reale che varia la zona."),
    _ex("Spostamenti di muro al centro", "Muro", "Muro-Difesa", "Centrale", 2, 10, "Medio", "Accostamento della centrale verso banda con passo o incrocio e stacco in equilibrio.", "Cronometrare il tempo di accostamento."),
    _ex("Muro-difesa coordinati", "Muro", "Muro-Difesa", "Situazionale", 6, 16, "Avanzato", "Il muro copre la diagonale, la difesa si posiziona di conseguenza. Lavoro di reparto.", "Variare l'attacco tra lungolinea e diagonale."),

    # --- DIFESA ---
    _ex("Difesa su attacco pesante", "Difesa", "Muro-Difesa", "Centrale", 4, 15, "Medio", "Difesa di palloni attaccati con potenza. Posizione bassa, spostamenti, tuffo e rullata.", "Alternare pallonetti e attacchi forti (lettura)."),
    _ex("Difesa e ricostruzione (free-ball)", "Difesa", "Fase break (cambio palla)", "Situazionale", 8, 18, "Medio", "Dalla difesa si costruisce il contrattacco. Transizione difesa-attacco completa.", "Punteggio: 1 pt difesa recuperata, 2 pt contrattacco vincente."),
    _ex("Difesa e rullate (tecnica a terra)", "Difesa", "Muro-Difesa", "Centrale", 2, 12, "Base", "Tecnica di caduta: tuffo frontale, rullata laterale, recupero in piedi rapido.", "Partire da spostamento ampio."),
    _ex("Difesa a specchio e copertura", "Difesa", "Muro-Difesa", "Situazionale", 6, 14, "Medio", "La seconda linea legge il muro e si posiziona; copertura dell'attaccante dopo il colpo.", "Introdurre pallonetti dietro il muro."),

    # --- GIOCO / SITUAZIONALE / TRANSIZIONE ---
    _ex("Transizione difesa-attacco (1 contro 1)", "Difesa", "Fase break (cambio palla)", "Situazionale", 4, 12, "Medio", "Fase di transizione: dopo aver difeso ci si stacca e si attacca il contrattacco. Catena difesa-alzata-attacco.", "L'allenatore immette palloni veloci per forzare la transizione."),
    _ex("Transizione muro-attacco", "Attacco", "Fase break (cambio palla)", "Situazionale", 6, 14, "Avanzato", "L'attaccante mura, atterra e si stacca immediatamente per attaccare la transizione. Esplosivit\u00e0 e tempi.", "Collegare con la difesa di seconda linea."),
    _ex("Transizione completa 6vs0", "Palleggio", "Fase break (cambio palla)", "Situazionale", 6, 16, "Medio", "La squadra esegue la catena completa (ricezione/difesa, alzata, attacco, copertura, transizione) senza avversari.", "Aggiungere obiettivi di tempo tra le fasi."),
    _ex("Wash drill 6vs6 (cambio palla)", "Difesa", "Fase break (cambio palla)", "Situazionale", 12, 20, "Avanzato", "Scambio iniziato dal servizio + free ball. La squadra deve vincere entrambi per fare punto. Alta densit\u00e0.", "Ridurre a 6vs6 con jolly se le presenti sono meno."),
    _ex("Partita a tema (obiettivo del giorno)", "Attacco", "Tecnica generale", "Situazionale", 10, 20, "Medio", "Set a 15 con bonus punti sull'obiettivo tecnico della seduta (es. ace, muro, primo tempo).", "Cambiare la regola bonus a met\u00e0 set."),
    _ex("6vs6 rotazioni fisse", "Palleggio", "Fase side-out", "Situazionale", 12, 22, "Avanzato", "Si gioca insistendo su una rotazione critica per volta, per automatizzare cambio palla.", "Focus sulle rotazioni in cui la squadra soffre di pi\u00f9."),
    _ex("Gioco 4vs4 campo ridotto", "Difesa", "Tecnica generale", "Situazionale", 8, 18, "Medio", "Gioco con pochi giocatori su campo ridotto: tanti tocchi, lettura e copertura. Ideale con poche presenti.", "Aggiungere regola dei tre tocchi obbligatori."),
    _ex("Scrimmage con punteggio a obiettivi", "Attacco", "Fase side-out", "Situazionale", 10, 20, "Medio", "Partita in cui alcuni fondamentali valgono doppio. Si allena l'obiettivo mantenendo la competitivit\u00e0.", "Modificare gli obiettivi a rotazioni alterne."),
]

# ============================================================
# STATO / PERSISTENZA (salvataggio atomico + backup .bak)
# ============================================================
def _state_dict():
    return {
        "rosa": st.session_state.rosa,
        "esercizi": st.session_state.esercizi.to_dict("records"),
        "sedute": st.session_state.sedute,
        "macrocicli": st.session_state.get("macrocicli", []),
        "microcicli": st.session_state.get("microcicli", []),
        "schema_settimanale": st.session_state.get("schema_settimanale", dict(SCHEMA_DEFAULT)),
        "tema_squadra": st.session_state.get("tema_squadra", dict(TEMA_DEFAULT)),
        "gare": st.session_state.get("gare", []),
        "versione": 4,
    }


def save_state():
    """Salvataggio atomico: scrive su file temporaneo e poi sposta.
    Mantiene una copia .bak dell'ultimo stato valido per sicurezza."""
    data = _state_dict()
    # backup del file esistente prima di sovrascrivere
    try:
        if os.path.exists(SAVE_FILE):
            shutil.copy2(SAVE_FILE, BAK_FILE)
    except Exception:
        pass
    tmp = tempfile.NamedTemporaryFile(delete=False, dir=".")
    try:
        with open(tmp.name, "wb") as f:
            pickle.dump(data, f)
        shutil.move(tmp.name, SAVE_FILE)
    except Exception:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
        raise


def _apply_data(data):
    st.session_state.rosa = data.get("rosa", [])
    es = data.get("esercizi", [])
    df = pd.DataFrame(es) if es else pd.DataFrame(ESERCIZI_DEFAULT)
    # migrazione: assicura la colonna Disegno
    if "Disegno" not in df.columns:
        df["Disegno"] = ""
    df["Disegno"] = df["Disegno"].fillna("")
    st.session_state.esercizi = df
    st.session_state.sedute = data.get("sedute", [])
    st.session_state.macrocicli = data.get("macrocicli", [])
    st.session_state.microcicli = data.get("microcicli", [])
    sch = data.get("schema_settimanale")
    st.session_state.schema_settimanale = sch if isinstance(sch, dict) and sch else dict(SCHEMA_DEFAULT)
    tem = data.get("tema_squadra")
    if isinstance(tem, dict) and tem:
        _t = dict(TEMA_DEFAULT)
        _t.update(tem)
        st.session_state.tema_squadra = _t
    else:
        st.session_state.tema_squadra = dict(TEMA_DEFAULT)
    st.session_state.gare = data.get("gare", [])


def load_state():
    """Carica lo stato dal file principale; se corrotto prova il backup .bak."""
    for path in (SAVE_FILE, BAK_FILE):
        if not os.path.exists(path):
            continue
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            _apply_data(data)
            return True
        except Exception:
            continue
    return False


def export_json_bytes():
    """Serializza tutto lo stato in JSON (per download/backup esterno)."""
    data = _state_dict()
    data["esportato_il"] = datetime.now().isoformat(timespec="seconds")
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def import_json_bytes(raw):
    """Ricarica lo stato da un file JSON esportato in precedenza."""
    data = json.loads(raw.decode("utf-8"))
    _apply_data(data)
    save_state()


if "initialized" not in st.session_state:
    st.session_state.rosa = []
    st.session_state.esercizi = pd.DataFrame(ESERCIZI_DEFAULT)
    st.session_state.sedute = []
    st.session_state.macrocicli = []
    st.session_state.microcicli = []
    st.session_state.schema_settimanale = dict(SCHEMA_DEFAULT)
    st.session_state.tema_squadra = dict(TEMA_DEFAULT)
    st.session_state.gare = []
    load_state()
    # assicura comunque la colonna Disegno
    if "Disegno" not in st.session_state.esercizi.columns:
        st.session_state.esercizi["Disegno"] = ""
    # assicura le liste dei cicli (compatibilit\u00e0 con backup vecchi)
    if "macrocicli" not in st.session_state:
        st.session_state.macrocicli = []
    if "microcicli" not in st.session_state:
        st.session_state.microcicli = []
    if "schema_settimanale" not in st.session_state:
        st.session_state.schema_settimanale = dict(SCHEMA_DEFAULT)
    if "tema_squadra" not in st.session_state:
        st.session_state.tema_squadra = dict(TEMA_DEFAULT)
    if "gare" not in st.session_state:
        st.session_state.gare = []
    st.session_state.initialized = True

# Guardie di sicurezza: assicurano che le chiavi esistano SEMPRE,
# anche quando la sessione proviene da una versione precedente dell'app
# (su Streamlit Cloud lo stato della sessione pu\u00f2 sopravvivere al deploy).
if "rosa" not in st.session_state:
    st.session_state.rosa = []
if "sedute" not in st.session_state:
    st.session_state.sedute = []
if "esercizi" not in st.session_state:
    st.session_state.esercizi = pd.DataFrame(ESERCIZI_DEFAULT)
if "macrocicli" not in st.session_state:
    st.session_state.macrocicli = []
if "microcicli" not in st.session_state:
    st.session_state.microcicli = []
if "schema_settimanale" not in st.session_state:
    st.session_state.schema_settimanale = dict(SCHEMA_DEFAULT)
if "tema_squadra" not in st.session_state:
    st.session_state.tema_squadra = dict(TEMA_DEFAULT)
if "gare" not in st.session_state:
    st.session_state.gare = []

# Applica il TEMA della squadra: sovrascrive i colori accento del CSS base
# con i colori scelti dall'utente (coerenti in badge, pulsanti, header, grafici).
_tema = st.session_state.get("tema_squadra", TEMA_DEFAULT)
_c1 = _tema.get("colore1") or TEMA_DEFAULT["colore1"]
_c2 = _tema.get("colore2") or TEMA_DEFAULT["colore2"]
st.markdown(
    "<style>"
    ":root{--vc-accent:" + _c1 + ";--vc-accent2:" + _c2 + ";}"
    ".stApp{background:"
    "radial-gradient(1200px 600px at 15% -10%," + _c1 + "1a,transparent 60%),"
    "radial-gradient(1000px 500px at 110% 0%," + _c2 + "1f,transparent 55%),"
    "linear-gradient(180deg,var(--vc-bg1) 0%,var(--vc-bg2) 100%);}"
    "h2{border-bottom-color:" + _c1 + "40 !important;}"
    ".stButton>button:hover{box-shadow:0 6px 18px " + _c1 + "73 !important;}"
    ".vc-hero{background:linear-gradient(120deg," + _c1 + "29," + _c2 + "24) !important;"
    "border-left:5px solid " + _c1 + " !important;}"
    ".vc-logo{height:46px;width:auto;border-radius:10px;vertical-align:middle;margin-right:10px;}"
    "</style>",
    unsafe_allow_html=True,
)


# ============================================================
# HELPER
# ============================================================
def giocatrici_disponibili():
    return [g for g in st.session_state.rosa if g.get("Stato", "Disponibile") == "Disponibile"]


def badge_livello(liv):
    cls = {"Base": "badge-base", "Medio": "badge-medio", "Avanzato": "badge-avanzato"}.get(liv, "badge-medio")
    return f"<span class='vc-badge {cls}'>{_html.escape(str(liv))}</span>"


COLORI_RUOLO = {"P": "#ffb703", "S": "#4cc9f0", "C": "#b5179e", "O": "#f72585", "L": "#52b788"}


def colore_ruolo(r):
    return COLORI_RUOLO.get(r, "#ff9f1c")


def conta_ruoli(lista):
    c = {r: 0 for r in RUOLI}
    for g in lista:
        r = g.get("Ruolo")
        if r in c:
            c[r] += 1
    return c


def chip_ruoli(lista):
    """Restituisce chip HTML colorate con il conteggio per ruolo."""
    c = conta_ruoli(lista)
    out = []
    for r, nome in RUOLI.items():
        col = colore_ruolo(r)
        out.append(
            f"<span class='role-chip' style='background:{col}22;color:{col};border:1px solid {col}66'>"
            f"{r} \u00b7 {nome}: <b>{c[r]}</b></span>"
        )
    return " ".join(out)


# ---- DISEGNI ----
def disegno_html(b64, classe="ex-disegno"):
    if isinstance(b64, str) and b64.strip():
        return f"<img class='{classe}' src='data:image/png;base64,{b64}'/>"
    return ""


def court_background(w=640, h=360):
    """Crea un'immagine PIL con un campo da pallavolo visto dall'alto come sfondo."""
    if not _HAS_PIL:
        return None
    img = Image.new("RGB", (w, h), (247, 230, 200))
    d = ImageDraw.Draw(img)
    m = 30
    x0, y0, x1, y1 = m, m, w - m, h - m
    d.rectangle([x0, y0, x1, y1], outline=(60, 60, 60), width=3)
    midx = (x0 + x1) // 2
    d.line([midx, y0, midx, y1], fill=(0, 0, 0), width=4)  # rete
    # linee dei 3 metri
    att = (x1 - x0) / 3.0
    d.line([x0 + 2 * att, y0, x0 + 2 * att, y1], fill=(120, 120, 120), width=1)
    d.line([x1 - 2 * att, y0, x1 - 2 * att, y1], fill=(120, 120, 120), width=1)
    return img


def canvas_to_base64(image_data):
    """Converte l'output RGBA del canvas in PNG base64 (richiede PIL)."""
    if image_data is None or not _HAS_PIL:
        return ""
    try:
        arr = image_data.astype("uint8")
        # scarta disegni vuoti (canale alpha tutto a zero)
        if arr.shape[-1] == 4 and int(arr[:, :, 3].sum()) == 0:
            return ""
        img = Image.fromarray(arr, "RGBA").convert("RGBA")
        bg = court_background(img.width, img.height)
        if bg is not None:
            base = bg.convert("RGBA")
            base.alpha_composite(img)
            img = base
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return ""


def file_to_base64_png(uploaded):
    """Converte un'immagine caricata in PNG base64."""
    try:
        raw = uploaded.read()
        if _HAS_PIL:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("ascii")
        # senza PIL salva comunque il contenuto grezzo (funziona per PNG)
        return base64.b64encode(raw).decode("ascii")
    except Exception:
        return ""


def stat_presenze_atleta():
    """Ritorna una lista di dict con nome, presenze, totali e percentuale per ogni atleta."""
    sedute = [s for s in st.session_state.sedute if s.get("presenti_nomi") is not None]
    tot = len(sedute)
    righe = []
    for g in st.session_state.rosa:
        nome = g["Nome"]
        pres = sum(1 for s in sedute if nome in (s.get("presenti_nomi") or []))
        perc = round(100 * pres / tot) if tot else 0
        righe.append({"Atleta": nome, "Presenze": pres, "Sedute": tot, "%": perc})
    return righe, tot


def campo_visuale_html(presenti):
    """Disegna uno schema semplice del campo con il numero di atlete per ruolo presenti."""
    c = conta_ruoli(presenti)
    def _cella(label, r):
        col = colore_ruolo(r)
        return ("<div style='flex:1;margin:4px;padding:10px 6px;border-radius:10px;text-align:center;"
                "background:" + col + "22;border:1px solid " + col + "66;color:#e8eefc;'>"
                "<div style='font-size:.75rem;opacity:.8'>" + label + "</div>"
                "<div style='font-size:1.4rem;font-weight:800;color:" + col + "'>" + str(c[r]) + "</div></div>")
    rete = "<div style='height:6px;background:linear-gradient(90deg,#fff,#bbb);border-radius:3px;margin:6px 2px'></div>"
    riga_avanti = "<div style='display:flex'>" + _cella("Z4 Banda", "S") + _cella("Z3 Centrale", "C") + _cella("Z2 Opposto", "O") + "</div>"
    riga_dietro = "<div style='display:flex'>" + _cella("Z5", "S") + _cella("Libero", "L") + _cella("Z1 Palleggio", "P") + "</div>"
    return ("<div style='max-width:420px;padding:12px;border-radius:14px;"
            "background:rgba(20,31,58,0.5);border:1px solid var(--vc-border)'>"
            + rete + riga_avanti + riga_dietro + "</div>")


def seduta_html_stampabile(s):
    """Genera un documento HTML autosufficiente e stampabile per una seduta."""
    tema = st.session_state.get("tema_squadra", TEMA_DEFAULT)
    c1 = tema.get("colore1", "#ff9f1c")
    squadra = _html.escape(tema.get("nome_squadra", "VolleyCoach"))
    tot = sum(int(e["Durata_min"]) for e in s["esercizi"])
    righe = []
    fase_corr = None
    for e in s["esercizi"]:
        if e["Fase"] != fase_corr:
            fase_corr = e["Fase"]
            righe.append("<h3 style='color:" + c1 + ";margin:14px 0 4px'>" + _html.escape(str(fase_corr)) + "</h3>")
        righe.append("<div class='ex'><b>" + _html.escape(str(e["Nome"])) + "</b> "
                     "<span class='min'>(" + str(e["Durata_min"]) + " min)</span><br>"
                     "<span class='desc'>" + _html.escape(str(e.get("Descrizione", ""))) + "</span></div>")
    pres = ", ".join(s.get("presenti_nomi") or []) or "\u2014"
    ass = ", ".join(s.get("assenti_nomi") or []) or "\u2014"
    note = _html.escape(s.get("note", "") or "")
    note_html = ("<div class='note'><b>Note:</b> " + note + "</div>") if note else ""
    doc = (
        "<!DOCTYPE html><html lang='it'><head><meta charset='utf-8'>"
        "<title>Seduta " + s["data"] + "</title><style>"
        "body{font-family:Segoe UI,Arial,sans-serif;max-width:800px;margin:24px auto;padding:0 18px;color:#1a2233}"
        "h1{color:" + c1 + ";margin:0 0 2px}.sub{color:#666;margin:0 0 14px}"
        ".meta{background:" + c1 + "18;border-left:5px solid " + c1 + ";padding:10px 14px;border-radius:8px;margin-bottom:12px}"
        ".ex{padding:6px 0;border-bottom:1px solid #eee}.min{color:" + c1 + ";font-weight:700}"
        ".desc{color:#555;font-size:.92rem}.note{margin-top:16px;padding:10px 14px;background:#fff8e6;border-radius:8px}"
        "@media print{body{margin:0}}</style></head><body>"
        "<h1>" + squadra + "</h1><p class='sub'>Scheda di allenamento</p>"
        "<div class='meta'><b>Data:</b> " + s["data"] + " &nbsp;\u00b7&nbsp; <b>Obiettivo:</b> " + _html.escape(str(s["obiettivo"])) +
        " &nbsp;\u00b7&nbsp; <b>Intensit\u00e0:</b> " + _html.escape(str(s["intensita"])) +
        " &nbsp;\u00b7&nbsp; <b>Durata:</b> " + str(tot) + " min<br>"
        "<b>Presenti:</b> " + _html.escape(pres) + "<br><b>Assenti:</b> " + _html.escape(ass) + "</div>"
        + "".join(righe) + note_html +
        "<p style='margin-top:24px;color:#999;font-size:.8rem'>Generato con VolleyCoach Manager</p>"
        "</body></html>"
    )
    return doc.encode("utf-8")


def editor_disegno(key_prefix, valore_corrente=""):
    """Blocco riutilizzabile per aggiungere/aggiornare il disegno di un esercizio.
    Ritorna la stringa base64 scelta (o quella corrente se non si disegna nulla)."""
    nuovo = valore_corrente
    if valore_corrente:
        st.markdown(disegno_html(valore_corrente), unsafe_allow_html=True)
    tabs = st.tabs(["\u270F\uFE0F Disegna sul campo", "\U0001F5BC\uFE0F Carica immagine"])
    with tabs[0]:
        if _HAS_CANVAS and _HAS_PIL:
            cc1, cc2, cc3 = st.columns(3)
            colore = cc1.color_picker("Colore", "#e63946", key=f"{key_prefix}_col")
            spessore = cc2.slider("Spessore", 1, 10, 3, key=f"{key_prefix}_sp")
            modo = cc3.selectbox("Strumento", ["freedraw", "line", "rect", "circle", "transform"],
                                 key=f"{key_prefix}_mode")
            bg = court_background()
            res = st_canvas(
                fill_color="rgba(255,255,255,0.0)",
                stroke_width=spessore,
                stroke_color=colore,
                background_image=bg,
                height=360, width=640,
                drawing_mode=modo,
                key=f"{key_prefix}_canvas",
            )
            if res is not None and res.image_data is not None:
                b64 = canvas_to_base64(res.image_data)
                if b64:
                    nuovo = b64
        else:
            st.info("Per disegnare direttamente nell'app installa il modulo del canvas. "
                    "In alternativa usa la scheda 'Carica immagine' qui a fianco.")
            st.code("pip install streamlit-drawable-canvas pillow", language="bash")
    with tabs[1]:
        up = st.file_uploader("Carica uno schema (PNG/JPG)", type=["png", "jpg", "jpeg"],
                              key=f"{key_prefix}_up")
        if up is not None:
            b64 = file_to_base64_png(up)
            if b64:
                nuovo = b64
                st.markdown(disegno_html(nuovo), unsafe_allow_html=True)
    if valore_corrente and st.checkbox("\U0001F5D1\uFE0F Rimuovi disegno", key=f"{key_prefix}_del"):
        nuovo = ""
    return nuovo


def _durata_fasi(durata_tot, intensita):
    if intensita == "Scarico":
        quote = {"Riscaldamento": 0.20, "Centrale": 0.35, "Situazionale": 0.25, "Defaticamento": 0.20}
    elif intensita == "Pre-partita":
        quote = {"Riscaldamento": 0.25, "Centrale": 0.25, "Situazionale": 0.40, "Defaticamento": 0.10}
    elif intensita == "Carico":
        quote = {"Riscaldamento": 0.15, "Centrale": 0.45, "Situazionale": 0.30, "Defaticamento": 0.10}
    else:
        quote = {"Riscaldamento": 0.18, "Centrale": 0.42, "Situazionale": 0.30, "Defaticamento": 0.10}
    return {fase: max(5, round(durata_tot * q)) for fase, q in quote.items()}


def genera_seduta(obiettivo, durata_tot, intensita, n_presenti, seed=None):
    rng = random.Random(seed)
    df = st.session_state.esercizi.copy()
    df = df[df["Min_Giocatrici"] <= max(n_presenti, 1)]
    budget = _durata_fasi(durata_tot, intensita)
    ordine_fasi = ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"]
    seduta = []
    for fase in ordine_fasi:
        minuti_fase = budget[fase]
        pool = df[df["Fase"] == fase]
        if fase in ("Centrale", "Situazionale") and obiettivo not in ("Tecnica generale",):
            mirati = pool[pool["Obiettivo"] == obiettivo]
            altri = pool[pool["Obiettivo"] != obiettivo]
            pool = pd.concat([mirati, altri])
        candidati = pool.to_dict("records")
        if fase in ("Riscaldamento", "Defaticamento"):
            rng.shuffle(candidati)
        usati = 0
        for ex in candidati:
            if usati >= minuti_fase and seduta and seduta[-1]["Fase"] == fase:
                break
            seduta.append(ex)
            usati += int(ex["Durata_min"])
            if usati >= minuti_fase:
                break
    return seduta, budget


def _quote_macro(fase_macro):
    """Restituisce i moltiplicatori delle fasi in base alla fase del macrociclo.
    Modula l'enfasi dell'allenamento lungo la periodizzazione:
      - Preparazione generale: tanto fisico/riscaldamento, poco situazionale
      - Preparazione specifica: equilibrio, pi\u00f9 centrale tecnico
      - Pre-competitivo: molto situazionale/gioco, meno fisico
      - Competitivo (mantenimento): situazionale alto, carichi contenuti
      - Transizione (scarico): volumi bassi, prevalenza riscaldamento/defaticamento
    """
    fm = (fase_macro or "").lower()
    if "generale" in fm or "prepar" in fm and "spec" not in fm:
        return {"Riscaldamento": 1.25, "Centrale": 1.15, "Situazionale": 0.70, "Defaticamento": 1.10}
    if "specific" in fm:
        return {"Riscaldamento": 1.00, "Centrale": 1.20, "Situazionale": 1.00, "Defaticamento": 1.00}
    if "pre-comp" in fm or "pre comp" in fm or "precomp" in fm or "pre-camp" in fm or "pre camp" in fm or "precamp" in fm:
        return {"Riscaldamento": 0.90, "Centrale": 0.90, "Situazionale": 1.35, "Defaticamento": 0.95}
    if "comp" in fm or "manteni" in fm or "gara" in fm:
        return {"Riscaldamento": 0.90, "Centrale": 0.85, "Situazionale": 1.40, "Defaticamento": 1.00}
    if "transiz" in fm or "scarico" in fm or "recup" in fm:
        return {"Riscaldamento": 1.30, "Centrale": 0.80, "Situazionale": 0.70, "Defaticamento": 1.40}
    return {"Riscaldamento": 1.0, "Centrale": 1.0, "Situazionale": 1.0, "Defaticamento": 1.0}


def genera_seduta_multi(obiettivi_list, durata_tot, intensita, n_presenti,
                        fase_macro=None, prevenzione=False, seed=None):
    """Genera una seduta con PIU' obiettivi tecnici (settimana tipo) e tiene
    conto della fase del macrociclo tramite _quote_macro.
    - obiettivi_list: lista di obiettivi (es. ["Attacco", "Muro-Difesa"])
    - fase_macro: nome della fase del macrociclo collegato (modula le fasi)
    - prevenzione: se True privilegia esercizi di condizione fisica nel riscaldamento
    """
    rng = random.Random(seed)
    df = st.session_state.esercizi.copy()
    df = df[df["Min_Giocatrici"] <= max(n_presenti, 1)]
    base = _durata_fasi(durata_tot, intensita)
    mult = _quote_macro(fase_macro)
    # applica i moltiplicatori del macrociclo e ri-normalizza sul tempo totale
    pesata = {f: base[f] * mult.get(f, 1.0) for f in base}
    somma = sum(pesata.values()) or 1
    budget = {f: max(5, round(durata_tot * (pesata[f] / somma))) for f in pesata}

    obiettivi_list = [o for o in (obiettivi_list or []) if o] or ["Tecnica generale"]
    ordine_fasi = ["Riscaldamento", "Centrale", "Situazionale", "Defaticamento"]
    seduta = []
    gia_usati = set()
    for fase in ordine_fasi:
        minuti_fase = budget[fase]
        pool = df[df["Fase"] == fase]
        if fase == "Riscaldamento" and prevenzione:
            prev = pool[pool["Obiettivo"] == "Condizione fisica"]
            altri = pool[pool["Obiettivo"] != "Condizione fisica"]
            pool = pd.concat([prev, altri])
        elif fase in ("Centrale", "Situazionale"):
            mirati = pool[pool["Obiettivo"].isin(obiettivi_list)]
            altri = pool[~pool["Obiettivo"].isin(obiettivi_list)]
            cand_m = mirati.to_dict("records")
            rng.shuffle(cand_m)
            pool = pd.concat([pd.DataFrame(cand_m) if cand_m else mirati, altri])
        candidati = pool.to_dict("records")
        if fase in ("Riscaldamento", "Defaticamento"):
            rng.shuffle(candidati)
        usati = 0
        for ex in candidati:
            key = ex.get("Nome", id(ex))
            if key in gia_usati:
                continue
            if usati >= minuti_fase and any(s["Fase"] == fase for s in seduta):
                break
            seduta.append(ex)
            gia_usati.add(key)
            usati += int(ex["Durata_min"])
            if usati >= minuti_fase:
                break
    return seduta, budget

# ============================================================
# ESERCIZI DA INTERNET
# ============================================================
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
SITI_DRILLS = [
    ("The Art of Coaching Volleyball", "theartofcoachingvolleyball.com"),
    ("Volleyball Advisors", "volleyballadvisors.com"),
    ("BetterAtVolleyball", "betteratvolleyball.com"),
    ("Volleyball Toolbox", "volleyballtoolbox.net"),
]


def link_ricerca(fondamentale, obiettivo, livello):
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
    _t = st.session_state.get("tema_squadra", TEMA_DEFAULT)
    if _t.get("logo"):
        st.markdown(
            "<div style='text-align:center'><img src='data:image/png;base64," + _t["logo"] + "' class='vc-logo' style='height:72px'></div>",
            unsafe_allow_html=True,
        )
    st.title("\U0001F3D0 " + (_t.get("nome_squadra") or "VolleyCoach"))
    st.caption(_t.get("sottotitolo") or "Gestione squadra")
    st.markdown("---")
    disp = len(giocatrici_disponibili())
    st.metric("Giocatrici in rosa", len(st.session_state.rosa))
    st.metric("Disponibili", disp)
    st.metric("Sedute programmate", len(st.session_state.sedute))
    st.markdown("---")
    if st.button("\U0001F4BE Salva dati", use_container_width=True):
        save_state()
        st.success("Salvato!")
    st.caption("I dati vengono salvati anche automaticamente a ogni modifica.")

    st.markdown("### \U0001F4E6 Backup & Ripristino")
    st.caption("Scarica un file di backup e conservalo: potrai ricaricarlo in qualsiasi momento se perdi i dati.")
    st.download_button(
        "\u2B07\uFE0F Scarica backup (.json)",
        data=export_json_bytes(),
        file_name=f"volleycoach_backup_{date.today().isoformat()}.json",
        mime="application/json",
        use_container_width=True,
    )
    up_backup = st.file_uploader("\u2B06\uFE0F Ricarica backup (.json)", type=["json"], key="restore_json")
    if up_backup is not None:
        if st.button("\U0001F504 Ripristina da questo file", use_container_width=True):
            try:
                import_json_bytes(up_backup.read())
                st.success("Dati ripristinati dal backup!")
                st.rerun()
            except Exception as e:
                st.error(f"File non valido: {e}")

    st.markdown("---")
    st.markdown("### \U0001F3A8 Tema squadra")
    st.caption("Personalizza nome, sottotitolo, colori e logo: l'app si veste con i colori della tua squadra.")
    with st.expander("Personalizza il tema", expanded=False):
        _tt = st.session_state.get("tema_squadra", TEMA_DEFAULT)
        _nome_sq = st.text_input("Nome squadra", value=_tt.get("nome_squadra", ""), key="tema_nome")
        _sotto = st.text_input("Sottotitolo", value=_tt.get("sottotitolo", ""), key="tema_sotto")
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            _col1 = st.color_picker("Colore principale", value=_tt.get("colore1", "#ff9f1c"), key="tema_col1")
        with tcol2:
            _col2 = st.color_picker("Colore secondario", value=_tt.get("colore2", "#ffbf69"), key="tema_col2")
        st.caption("\U0001F3A8 Preset rapidi:")
        pr1, pr2, pr3, pr4 = st.columns(4)
        _presets = {
            "Arancio": ("#ff9f1c", "#ffbf69"),
            "Blu": ("#2d6eff", "#6ea8ff"),
            "Rosso": ("#e63946", "#ff7b86"),
            "Verde": ("#2a9d8f", "#64d6c6"),
        }
        _preset_scelto = None
        if pr1.button("Arancio", key="pr_ar", use_container_width=True):
            _preset_scelto = "Arancio"
        if pr2.button("Blu", key="pr_bl", use_container_width=True):
            _preset_scelto = "Blu"
        if pr3.button("Rosso", key="pr_ro", use_container_width=True):
            _preset_scelto = "Rosso"
        if pr4.button("Verde", key="pr_ve", use_container_width=True):
            _preset_scelto = "Verde"
        if _preset_scelto:
            c1p, c2p = _presets[_preset_scelto]
            nuovo_tema = dict(_tt)
            nuovo_tema["colore1"] = c1p
            nuovo_tema["colore2"] = c2p
            st.session_state.tema_squadra = nuovo_tema
            save_state()
            st.rerun()
        _logo_up = st.file_uploader("Logo squadra (PNG/JPG)", type=["png", "jpg", "jpeg"], key="tema_logo_up")
        if _tt.get("logo"):
            if st.checkbox("\U0001F5D1\uFE0F Rimuovi logo attuale", key="tema_logo_del"):
                nuovo_tema = dict(_tt)
                nuovo_tema["logo"] = ""
                st.session_state.tema_squadra = nuovo_tema
                save_state()
                st.rerun()
        if st.button("\U0001F4BE Salva tema", use_container_width=True, key="tema_save"):
            nuovo_tema = dict(_tt)
            nuovo_tema["nome_squadra"] = _nome_sq.strip() or "VolleyCoach"
            nuovo_tema["sottotitolo"] = _sotto.strip()
            nuovo_tema["colore1"] = _col1
            nuovo_tema["colore2"] = _col2
            if _logo_up is not None:
                _b64 = file_to_base64_png(_logo_up)
                if _b64:
                    nuovo_tema["logo"] = _b64
            st.session_state.tema_squadra = nuovo_tema
            save_state()
            st.success("Tema salvato!")
            st.rerun()
        if st.button("\u21A9\uFE0F Ripristina tema di default", use_container_width=True, key="tema_reset"):
            st.session_state.tema_squadra = dict(TEMA_DEFAULT)
            save_state()
            st.rerun()

# ============================================================
# MENU
# ============================================================
menu = st.radio(
    "",
    ["\U0001F3E0 Dashboard", "\U0001F465 Rosa", "\U0001F9E9 Periodizzazione", "\U0001F4CB Programma Allenamenti",
     "\U0001F4DA Libreria Esercizi", "\U0001F310 Esercizi Online", "\U0001F5D3\uFE0F Calendario", "\U0001F3C6 Gare", "\U0001F4CA Presenze"],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("---")

# ============================================================
# DASHBOARD
# ============================================================
if menu == "\U0001F3E0 Dashboard":
    _th = st.session_state.get("tema_squadra", TEMA_DEFAULT)
    _logo_html = ("<img src='data:image/png;base64," + _th["logo"] + "' class='vc-logo'>" if _th.get("logo") else "\U0001F3D0 ")
    _nome_h = _html.escape(_th.get("nome_squadra") or "VolleyCoach Manager")
    _sotto_h = _html.escape(_th.get("sottotitolo") or "Il tuo pannello di controllo per la squadra")
    st.markdown(
        "<div class='vc-hero'><h1>" + _logo_html + _nome_h + "</h1>"
        "<p>" + _sotto_h + "</p></div>",
        unsafe_allow_html=True,
    )
    if not st.session_state.rosa:
        st.info("Inizia aggiungendo le tue giocatrici nella sezione **Rosa**.")
    c1, c2, c3, c4 = st.columns(4)
    disp = giocatrici_disponibili()
    _th2 = st.session_state.get("tema_squadra", TEMA_DEFAULT)
    _cc = _th2.get("colore1", "#ff9f1c")
    _righe_pres, _tot_sed = stat_presenze_atleta()
    _pres_media = round(sum(r["%"] for r in _righe_pres) / len(_righe_pres)) if _righe_pres else 0

    def _vcard(col, icona, valore, etichetta):
        col.markdown(
            "<div style='background:var(--vc-card);border:1px solid var(--vc-border);border-radius:14px;"
            "padding:14px 16px;border-left:5px solid " + _cc + "'>"
            "<div style='font-size:1.6rem'>" + icona + "</div>"
            "<div style='font-size:1.8rem;font-weight:800;color:" + _cc + "'>" + str(valore) + "</div>"
            "<div style='color:var(--vc-muted);font-size:.85rem'>" + etichetta + "</div></div>",
            unsafe_allow_html=True,
        )
    _vcard(c1, "\U0001F465", len(st.session_state.rosa), "Giocatrici in rosa")
    _vcard(c2, "\U0001F7E2", len(disp), "Disponibili")
    _vcard(c3, "\U0001F4CA", str(_pres_media) + "%", "Presenza media")
    _vcard(c4, "\U0001F4C5", len(st.session_state.sedute), "Sedute programmate")

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
                    f"<div class='block-seduta'><b>{s['data']}</b> \u2014 \U0001F3AF {s['obiettivo']} "
                    f"\u00b7 {s['intensita']} \u00b7 {s['durata']} min</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Nessuna seduta futura programmata.")

    # ---- Prossima gara (countdown) ----
    if st.session_state.get("gare"):
        _oggi = date.today()
        _future_g = sorted(
            [g for g in st.session_state.gare if g.get("data", "") >= _oggi.isoformat()],
            key=lambda x: x["data"],
        )
        if _future_g:
            _g = _future_g[0]
            try:
                _gg = (date.fromisoformat(_g["data"]) - _oggi).days
            except Exception:
                _gg = None
            _quando = "oggi!" if _gg == 0 else ("domani" if _gg == 1 else ("tra " + str(_gg) + " giorni") if _gg else "")
            st.markdown(
                "<div class='block-seduta'>\U0001F3C6 <b>Prossima gara:</b> " + _html.escape(str(_g.get("avversario", ""))) +
                " \u00b7 " + _g.get("data", "") + (" \u00b7 <b>" + _quando + "</b>" if _quando else "") + "</div>",
                unsafe_allow_html=True,
            )

    # ---- Obiettivi stagionali: quante sedute per fondamentale ----
    if st.session_state.sedute:
        st.markdown("### \U0001F3AF Lavoro stagionale per obiettivo")
        st.caption("Quante sedute hai dedicato finora a ciascun obiettivo (in base alle sedute salvate).")
        _conteggi = {o: 0 for o in OBIETTIVI}
        for _s in st.session_state.sedute:
            for _o in str(_s.get("obiettivo", "")).split(" + "):
                _o = _o.strip()
                if _o in _conteggi:
                    _conteggi[_o] += 1
        _max = max(_conteggi.values()) or 1
        for _o, _n in _conteggi.items():
            if _n == 0:
                continue
            _perc = int(100 * _n / _max)
            st.markdown(
                "<div style='margin:4px 0'><span style='display:inline-block;width:200px'>" + _html.escape(_o) + "</span>"
                "<span style='display:inline-block;width:55%;background:var(--vc-card2);border-radius:6px;vertical-align:middle'>"
                "<span style='display:inline-block;height:14px;border-radius:6px;width:" + str(max(_perc, 4)) + "%;"
                "background:linear-gradient(90deg,var(--vc-accent),var(--vc-accent2))'></span></span>"
                "<b style='margin-left:8px'>" + str(_n) + "</b></div>",
                unsafe_allow_html=True,
            )

# ============================================================
# ROSA
# ============================================================
if menu == "\U0001F465 Rosa":
    st.header("\U0001F465 Rosa Giocatrici")

    with st.expander("\u2795 Aggiungi giocatrice", expanded=not st.session_state.rosa):
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
        st.caption("Passa il mouse su una card per girarla e vedere gli obiettivi. Usa \u201cCompila / modifica scheda\u201d per aggiornarli.")
        filtro = st.multiselect("Filtra per ruolo", list(RUOLI.keys()),
                                format_func=lambda r: RUOLI[r])
        cerca = st.text_input("\U0001F50E Cerca atleta", placeholder="Scrivi un nome o un numero...")
        _q = cerca.strip().lower()
        visibili = [(i, g) for i, g in enumerate(st.session_state.rosa)
                    if not (filtro and g["Ruolo"] not in filtro)
                    and (not _q or _q in str(g.get("Nome", "")).lower() or _q in str(g.get("Numero", "")).lower())]
        N_COL = 3
        for riga_start in range(0, len(visibili), N_COL):
            cols = st.columns(N_COL)
            for col, (i, g) in zip(cols, visibili[riga_start:riga_start + N_COL]):
                with col:
                    emoji = {"Disponibile": "\U0001F7E2", "Infortunata": "\U0001F534", "In recupero": "\U0001F7E1", "Indisponibile": "\u26AA"}.get(g.get("Stato"), "\u26AA")
                    col_r = colore_ruolo(g["Ruolo"])
                    nome = _html.escape(str(g["Nome"]))
                    ruolo_nome = _html.escape(RUOLI[g["Ruolo"]])
                    ob_princ = str(g.get("Obiettivo_principale", "")).strip()
                    obiettivi = str(g.get("Obiettivi", "")).strip()
                    parti = []
                    if ob_princ:
                        parti.append(f"<b>\U0001F3AF {_html.escape(ob_princ)}</b>")
                    if obiettivi:
                        parti.append(_html.escape(obiettivi).replace("\n", "<br>"))
                    if parti:
                        back_body = f"<div class='flip-back-body'>{'<br>'.join(parti)}</div>"
                    else:
                        back_body = "<div class='flip-empty'>Nessun obiettivo inserito.<br>Aprilo qui sotto e compilalo.</div>"
                    _foto = str(g.get("Foto", "")).strip()
                    if _foto:
                        _foto_html = ("<img src='data:image/png;base64," + _foto + "' style='width:72px;height:72px;"
                                      "border-radius:50%;object-fit:cover;border:2px solid " + col_r + "'>")
                    else:
                        _foto_html = "<div style='font-size:1.5rem'>" + emoji + "</div>"
                    st.markdown(
                        f"<div class='flip-card'><div class='flip-inner'>"
                        f"<div class='flip-front' style=\"border:1px solid {col_r}; box-shadow:0 0 18px {col_r}55, inset 0 0 24px {col_r}18;\">"
                        f"{_foto_html}"
                        f"<div class='flip-name'>#{_html.escape(str(g['Numero']))} {nome}</div>"
                        f"<div class='flip-role' style='color:{col_r}'>{ruolo_nome}</div>"
                        f"<div class='flip-meta'>{_html.escape(str(g['Altezza']))} cm \u00b7 {emoji} {_html.escape(str(g.get('Stato','')))}</div>"
                        f"<div class='flip-hint'>\u21bb passa il mouse per la scheda</div>"
                        f"</div>"
                        f"<div class='flip-back' style=\"border:1px solid {col_r}; box-shadow:0 0 18px {col_r}55, inset 0 0 24px {col_r}18;\">"
                        f"<div class='flip-back-title' style='color:{col_r}'>\U0001F4CB Obiettivi \u2014 {nome}</div>"
                        f"{back_body}"
                        f"</div></div></div>",
                        unsafe_allow_html=True,
                    )
                    with st.expander("\u270F\uFE0F Compila / modifica scheda"):
                        with st.form(f"scheda_{i}"):
                            st.markdown("**\U0001F464 Dati giocatrice**")
                            dc1, dc2 = st.columns(2)
                            with dc1:
                                nome_in = st.text_input("Nome e cognome", value=g.get("Nome", ""))
                                numero_in = st.number_input("Numero maglia", min_value=0, max_value=99, step=1,
                                                            value=int(g.get("Numero", 0)))
                            with dc2:
                                ruolo_in = st.selectbox("Ruolo", list(RUOLI.keys()),
                                                        index=list(RUOLI.keys()).index(g.get("Ruolo", "P")) if g.get("Ruolo") in RUOLI else 0,
                                                        format_func=lambda r: RUOLI[r])
                                altezza_in = st.number_input("Altezza (cm)", min_value=140, max_value=210, step=1,
                                                             value=int(g.get("Altezza", 170)))
                            note_in = st.text_input("Note", value=g.get("Note", ""))
                            nuovo_stato = st.selectbox(
                                "Stato", ["Disponibile", "Infortunata", "In recupero", "Indisponibile"],
                                index=["Disponibile", "Infortunata", "In recupero", "Indisponibile"].index(g.get("Stato", "Disponibile")),
                            )
                            st.markdown("**\U0001F3AF Obiettivi tecnici**")
                            ob_princ_in = st.text_input(
                                "Obiettivo tecnico principale",
                                value=g.get("Obiettivo_principale", ""),
                                placeholder="es. Migliorare la ricezione in zona 5",
                            )
                            obiettivi_in = st.text_area(
                                "\U0001F4CC Obiettivi individuali",
                                value=g.get("Obiettivi", ""),
                                placeholder="Uno per riga",
                                height=100,
                            )
                            forza = st.text_area("\U0001F4AA Punti di forza", value=g.get("Punti_forza", ""), height=70)
                            migliorare = st.text_area("\U0001F527 Aree da migliorare", value=g.get("Da_migliorare", ""), height=70)
                            lavoro = st.text_area("\U0001F3CB\uFE0F Lavoro individuale assegnato", value=g.get("Lavoro_individuale", ""), height=70)
                            st.markdown("**\U0001F4F7 Foto**")
                            foto_up = st.file_uploader("Carica/aggiorna foto", type=["png", "jpg", "jpeg"], key=f"foto_{i}")
                            rimuovi_foto = False
                            if g.get("Foto"):
                                rimuovi_foto = st.checkbox("\U0001F5D1\uFE0F Rimuovi foto", key=f"delfoto_{i}")
                            fc1, fc2 = st.columns(2)
                            salva = fc1.form_submit_button("\U0001F4BE Salva", use_container_width=True, type="primary")
                            elimina = fc2.form_submit_button("\U0001F5D1\uFE0F Elimina", use_container_width=True)
                            if salva:
                                if not nome_in.strip():
                                    st.warning("Il nome non pu\u00f2 essere vuoto.")
                                else:
                                    st.session_state.rosa[i]["Nome"] = nome_in.strip()
                                    st.session_state.rosa[i]["Numero"] = int(numero_in)
                                    st.session_state.rosa[i]["Ruolo"] = ruolo_in
                                    st.session_state.rosa[i]["Altezza"] = int(altezza_in)
                                    st.session_state.rosa[i]["Note"] = note_in.strip()
                                    st.session_state.rosa[i]["Stato"] = nuovo_stato
                                    st.session_state.rosa[i]["Obiettivo_principale"] = ob_princ_in.strip()
                                    st.session_state.rosa[i]["Obiettivi"] = obiettivi_in.strip()
                                    st.session_state.rosa[i]["Punti_forza"] = forza.strip()
                                    st.session_state.rosa[i]["Da_migliorare"] = migliorare.strip()
                                    st.session_state.rosa[i]["Lavoro_individuale"] = lavoro.strip()
                                    if rimuovi_foto:
                                        st.session_state.rosa[i]["Foto"] = ""
                                    elif foto_up is not None:
                                        _fb = file_to_base64_png(foto_up)
                                        if _fb:
                                            st.session_state.rosa[i]["Foto"] = _fb
                                    save_state()
                                    st.success("Giocatrice aggiornata!")
                                    st.rerun()
                            if elimina:
                                st.session_state.rosa.pop(i)
                                save_state()
                                st.rerun()
    else:
        st.info("Nessuna giocatrice inserita.")

# ============================================================
# PROGRAMMA ALLENAMENTI (generatore)
# ============================================================
if menu == "\U0001F4CB Programma Allenamenti":
    st.header("\U0001F4CB Programma Allenamenti")
    st.caption("Imposta l'obiettivo della seduta: il generatore compone riscaldamento, parte tecnica, situazionale e defaticamento con esercizi coerenti dalla libreria.")

    # ---- Presenze: chi c'e' e chi e' assente ----
    st.markdown("### \U0001F9CD\u200D\u2640\uFE0F Partecipanti alla seduta")
    presenti = []
    assenti = []
    if st.session_state.rosa:
        rosa = st.session_state.rosa
        nomi = [f"#{g.get('Numero','')} {g['Nome']} ({g['Ruolo']})" for g in rosa]
        idx_by_label = {nomi[i]: i for i in range(len(rosa))}
        default_presenti = [nomi[i] for i, g in enumerate(rosa)
                            if g.get("Stato", "Disponibile") == "Disponibile"]
        sel = st.multiselect(
            "Seleziona le presenti di oggi",
            nomi, default=default_presenti,
            help="Chi non selezioni risulter\u00e0 assente. Di default sono gi\u00e0 selezionate le disponibili.",
        )
        presenti = [rosa[idx_by_label[s]] for s in sel]
        assenti = [g for i, g in enumerate(rosa) if nomi[i] not in sel]

        cpa, cpb = st.columns(2)
        with cpa:
            st.markdown(f"**\u2705 Presenti: {len(presenti)}**")
            st.markdown(chip_ruoli(presenti), unsafe_allow_html=True)
        with cpb:
            if assenti:
                st.markdown(f"**\u274C Assenti: {len(assenti)}**")
                st.markdown(
                    ", ".join(f"{_html.escape(g['Nome'])} ({g.get('Stato','')})" for g in assenti),
                    unsafe_allow_html=False,
                )
            else:
                st.markdown("**\u274C Assenti: 0**")
        # avvisi su ruoli mancanti
        comp = conta_ruoli(presenti)
        avvisi = []
        if comp["P"] == 0:
            avvisi.append("nessuna **palleggiatrice**")
        if comp["L"] == 0:
            avvisi.append("nessun **libero**")
        if comp["C"] == 0:
            avvisi.append("nessuna **centrale**")
        if avvisi:
            st.warning("Attenzione, oggi hai " + ", ".join(avvisi) + ": adatta gli esercizi di conseguenza.")
        # schema visuale del campo con i ruoli presenti
        if presenti:
            st.markdown("**\U0001F3D0 Disposizione in campo (ruoli presenti)**")
            st.markdown(campo_visuale_html(presenti), unsafe_allow_html=True)
    else:
        st.info("Aggiungi le giocatrici nella sezione **Rosa** per gestire le presenze. Puoi comunque generare una seduta indicando il numero di presenti qui sotto.")

    st.markdown("---")

    # ---- Collega la seduta a un microciclo (periodizzazione) ----
    micro_sel = None
    micro_list = st.session_state.get("microcicli", [])
    if micro_list:
        opzioni = ["(nessun microciclo)"] + [
            f"{m.get('macrociclo','')} \u00b7 {m.get('nome','')} ({m.get('obiettivo','')})" for m in micro_list
        ]
        scelta = st.selectbox("\U0001F9E9 Collega a un microciclo", opzioni,
                              help="Scegli la settimana di allenamento: obiettivo e intensit\u00e0 vengono precompilati.")
        if scelta != "(nessun microciclo)":
            micro_sel = micro_list[opzioni.index(scelta) - 1]

    obj_default = micro_sel.get("obiettivo") if micro_sel and micro_sel.get("obiettivo") in OBIETTIVI else None
    int_default = micro_sel.get("intensita") if micro_sel and micro_sel.get("intensita") in INTENSITA else None

    # fase del macrociclo collegato (per modulare le fasi della seduta)
    fase_macro = None
    if micro_sel:
        _nome_macro = micro_sel.get("macrociclo")
        for _m in st.session_state.get("macrocicli", []):
            if _m.get("nome") == _nome_macro:
                fase_macro = _m.get("fase")
                break

    # ---- Data e FOCUS del giorno (settimana tipo) ----
    cdt1, cdt2 = st.columns([1, 2])
    with cdt1:
        data_seduta = st.date_input("Data", value=date.today())
    wd = data_seduta.weekday()
    schema = st.session_state.get("schema_settimanale", dict(SCHEMA_DEFAULT))
    giorno_cfg = schema.get(str(wd))
    with cdt2:
        if giorno_cfg:
            st.success("\U0001F4C5 **" + GIORNI_IT[wd] + "** \u2014 focus del giorno: **" + giorno_cfg.get('nome', '') + "**")
        else:
            st.info("\U0001F4C5 **" + GIORNI_IT[wd] + "** \u2014 nessun focus predefinito (seduta libera).")

    obj_precompilati = []
    if giorno_cfg:
        obj_precompilati = [o for o in giorno_cfg.get("obiettivi", []) if o in OBIETTIVI]
    if not obj_precompilati and obj_default:
        obj_precompilati = [obj_default]
    if not obj_precompilati:
        obj_precompilati = [OBIETTIVI[0]]
    prev_precompilata = bool(giorno_cfg.get("prevenzione")) if giorno_cfg else False

    c1, c2, c3 = st.columns(3)
    with c1:
        obiettivi = st.multiselect("Obiettivi della seduta", OBIETTIVI, default=obj_precompilati,
                                   help="Precompilati in base al focus del giorno e al microciclo. Puoi modificarli.")
    with c2:
        intensita = st.selectbox("Intensit\u00e0", INTENSITA,
                                 index=INTENSITA.index(int_default) if int_default else 1)
    with c3:
        durata = st.slider("Durata (min)", 60, 150, 90, step=15)

    prevenzione = st.checkbox("\U0001FA79 Includi prevenzione/fisico nel riscaldamento",
                              value=prev_precompilata)
    if fase_macro:
        st.caption("\U0001F9E9 Fase macrociclo: **" + str(fase_macro) + "** \u2014 fasi della seduta modulate di conseguenza.")

    default_n = len(presenti) if presenti else max(len(giocatrici_disponibili()), 1)
    n_presenti = st.number_input("Numero di giocatrici presenti", min_value=1, max_value=30,
                                 value=max(default_n, 1))

    cga, cgb = st.columns(2)
    with cga:
        genera = st.button("\u26A1 Genera seduta", type="primary", use_container_width=True)
    with cgb:
        rigenera = st.button("\U0001F504 Proponi variante", use_container_width=True)

    if genera or rigenera:
        seed = random.randint(0, 999999) if rigenera else 42
        obj_eff = obiettivi or [OBIETTIVI[0]]
        seduta, budget = genera_seduta_multi(obj_eff, durata, intensita, int(n_presenti),
                                             fase_macro=fase_macro, prevenzione=prevenzione, seed=seed)
        st.session_state._ultima_seduta = {
            "data": data_seduta.isoformat(), "obiettivo": " + ".join(obj_eff),
            "intensita": intensita, "durata": int(durata),
            "presenti": int(n_presenti),
            "presenti_nomi": [g["Nome"] for g in presenti],
            "assenti_nomi": [g["Nome"] for g in assenti],
            "composizione": conta_ruoli(presenti) if presenti else {},
            "microciclo": (f"{micro_sel.get('macrociclo','')} \u00b7 {micro_sel.get('nome','')}" if micro_sel else ""),
            "fase_macro": fase_macro or "",
            "esercizi": seduta,
        }

    ult = st.session_state.get("_ultima_seduta")
    if ult:
        st.markdown("---")
        st.subheader(f"\U0001F3AF Seduta \u2014 {ult['obiettivo']} ({ult['intensita']})")
        tot = sum(int(e["Durata_min"]) for e in ult["esercizi"])
        st.caption(f"\U0001F4C5 {ult['data']} \u00b7 durata stimata **{tot} min** \u00b7 {ult['presenti']} presenti")
        if ult.get("microciclo"):
            st.caption("\U0001F9E9 Microciclo: " + ult["microciclo"])
        if ult.get("fase_macro"):
            st.caption("\U0001F4C8 Fase macrociclo: " + ult["fase_macro"])
        if ult.get("presenti_nomi"):
            st.markdown(chip_ruoli([g for g in st.session_state.rosa if g["Nome"] in ult["presenti_nomi"]]), unsafe_allow_html=True)
            st.caption("\u2705 " + ", ".join(ult["presenti_nomi"]))
        if ult.get("assenti_nomi"):
            st.caption("\u274C Assenti: " + ", ".join(ult["assenti_nomi"]))

        st.info("\U0001F4A1 Puoi correggere la seduta: modifica, sostituisci, sposta o elimina ogni singolo esercizio qui sotto.")
        es_list = ult["esercizi"]
        tutti_nomi = list(st.session_state.esercizi["Nome"])
        fase_corrente = None
        icone = {"Riscaldamento": "\U0001F525", "Centrale": "\U0001F3D0", "Situazionale": "\U0001F19A", "Defaticamento": "\U0001F9D8"}
        for i, e in enumerate(es_list):
            if e["Fase"] != fase_corrente:
                fase_corrente = e["Fase"]
                st.markdown(f"#### {icone.get(fase_corrente,'')} {fase_corrente}")
            dis = disegno_html(e.get("Disegno", ""))
            st.markdown(
                f"<div class='block-seduta'><b>{i+1}. {_html.escape(str(e['Nome']))}</b> "
                f"<span style='color:#ffbf69'>\u00b7 {e['Durata_min']} min \u00b7 {e['Fondamentale']}</span> {badge_livello(e['Livello'])}<br>"
                f"<span style='color:#c9d6ea'>{_html.escape(str(e['Descrizione']))}</span><br>"
                f"<span style='color:#7f93b0;font-size:0.9em'>\U0001F501 Variante: {_html.escape(str(e['Varianti']))}</span>{dis}</div>",
                unsafe_allow_html=True,
            )
            with st.expander(f"\u270F\uFE0F Correggi l'esercizio {i+1}"):
                # Sostituzione dalla libreria
                csub1, csub2 = st.columns([3, 1])
                nome_attuale = str(e["Nome"])
                idx_sel = tutti_nomi.index(nome_attuale) if nome_attuale in tutti_nomi else 0
                sostituto = csub1.selectbox("Sostituisci con un esercizio della libreria",
                                            tutti_nomi, index=idx_sel, key=f"sub_sel_{i}")
                if csub2.button("\U0001F501 Sostituisci", key=f"sub_btn_{i}", use_container_width=True):
                    nuovo = st.session_state.esercizi[st.session_state.esercizi["Nome"] == sostituto].iloc[0].to_dict()
                    nuovo["Fase"] = e["Fase"]  # mantieni la fase nella seduta
                    es_list[i] = nuovo
                    st.rerun()
                # Modifica puntuale dei campi
                mc1, mc2, mc3 = st.columns(3)
                en = mc1.text_input("Nome", value=str(e["Nome"]), key=f"ed_nome_{i}")
                edur = mc2.number_input("Durata (min)", 1, 60, int(e["Durata_min"]), key=f"ed_dur_{i}")
                eliv = mc3.selectbox("Livello", ["Base", "Medio", "Avanzato"],
                                     index=["Base", "Medio", "Avanzato"].index(e["Livello"]) if e["Livello"] in ["Base", "Medio", "Avanzato"] else 0,
                                     key=f"ed_liv_{i}")
                edesc = st.text_area("Descrizione", value=str(e["Descrizione"]), key=f"ed_desc_{i}", height=80)
                evar = st.text_input("Variante", value=str(e["Varianti"]), key=f"ed_var_{i}")
                b1, b2, b3, b4 = st.columns(4)
                if b1.button("\U0001F4BE Salva", key=f"ed_save_{i}", use_container_width=True):
                    e["Nome"] = en.strip(); e["Durata_min"] = int(edur); e["Livello"] = eliv
                    e["Descrizione"] = edesc.strip(); e["Varianti"] = evar.strip()
                    st.rerun()
                if b2.button("\u2B06\uFE0F Su", key=f"ed_up_{i}", use_container_width=True, disabled=(i == 0)):
                    es_list[i - 1], es_list[i] = es_list[i], es_list[i - 1]
                    st.rerun()
                if b3.button("\u2B07\uFE0F Gi\u00f9", key=f"ed_down_{i}", use_container_width=True, disabled=(i == len(es_list) - 1)):
                    es_list[i + 1], es_list[i] = es_list[i], es_list[i + 1]
                    st.rerun()
                if b4.button("\U0001F5D1\uFE0F Rimuovi", key=f"ed_del_{i}", use_container_width=True):
                    es_list.pop(i)
                    st.rerun()

        # Aggiungi un esercizio alla seduta
        with st.expander("\u2795 Aggiungi un esercizio alla seduta"):
            aa1, aa2, aa3 = st.columns([2, 2, 1])
            add_fase = aa1.selectbox("Fase", FASI, key="add_seduta_fase")
            add_nome = aa2.selectbox("Esercizio", tutti_nomi, key="add_seduta_nome")
            if aa3.button("\u2795 Aggiungi", key="add_seduta_btn", use_container_width=True):
                nuovo = st.session_state.esercizi[st.session_state.esercizi["Nome"] == add_nome].iloc[0].to_dict()
                nuovo["Fase"] = add_fase
                es_list.append(nuovo)
                # riordina per fase mantenendo l'ordine delle fasi
                ordine = {f: k for k, f in enumerate(FASI)}
                es_list.sort(key=lambda x: ordine.get(x["Fase"], 99))
                st.rerun()

        _nota_seduta = st.text_area("\U0001F4DD Note (facoltative)",
                                    value=ult.get("note", ""),
                                    placeholder="Es. focus del giorno, com'\u00e8 andata, cosa migliorare...",
                                    key="nota_nuova_seduta")
        if st.button("\U0001F4C5 Salva questa seduta nel calendario", type="primary"):
            ult["note"] = _nota_seduta.strip()
            st.session_state.sedute.append(ult)
            save_state()
            st.success("Seduta salvata nel calendario!")

# ============================================================
# LIBRERIA ESERCIZI
# ============================================================
if menu == "\U0001F4DA Libreria Esercizi":
    st.header("\U0001F4DA Libreria Esercizi")
    df = st.session_state.esercizi

    with st.expander("\u2795 Aggiungi un tuo esercizio"):
        st.caption("Inserisci i tuoi esercizi personali e, se vuoi, allega uno schema del campo (disegnalo o carica un'immagine).")
        c1, c2, c3 = st.columns(3)
        with c1:
            e_nome = st.text_input("Nome esercizio", key="add_nome")
            e_fond = st.selectbox("Fondamentale", FONDAMENTALI, key="add_fond")
        with c2:
            e_obj = st.selectbox("Obiettivo", OBIETTIVI, key="add_obj")
            e_fase = st.selectbox("Fase", FASI, key="add_fase")
        with c3:
            e_min = st.number_input("Min. giocatrici", 1, 24, 4, key="add_min")
            e_dur = st.number_input("Durata (min)", 3, 40, 12, key="add_dur")
            e_liv = st.selectbox("Livello", ["Base", "Medio", "Avanzato"], key="add_liv")
        e_desc = st.text_area("Descrizione", key="add_desc")
        e_var = st.text_input("Varianti / progressioni", key="add_var")
        st.markdown("**\U0001F3A8 Schema / disegno (facoltativo)**")
        e_dis = editor_disegno("add_ex_draw", "")
        if st.button("Aggiungi esercizio", use_container_width=True, key="add_ex_btn"):
            if e_nome.strip():
                nuovo = {"Nome": e_nome.strip(), "Fondamentale": e_fond, "Obiettivo": e_obj,
                         "Fase": e_fase, "Min_Giocatrici": int(e_min), "Durata_min": int(e_dur),
                         "Livello": e_liv, "Descrizione": e_desc.strip(), "Varianti": e_var.strip(),
                         "Disegno": e_dis}
                st.session_state.esercizi = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
                save_state()
                st.success("Esercizio aggiunto!")
                st.rerun()
            else:
                st.warning("Serve almeno il nome dell'esercizio.")

    c1, c2, c3 = st.columns(3)
    f_fond = c1.multiselect("Fondamentale", FONDAMENTALI)
    f_obj = c2.multiselect("Obiettivo", OBIETTIVI)
    f_fase = c3.multiselect("Fase", FASI)
    testo = st.text_input("\U0001F50E Cerca per nome o descrizione")

    vista = df.copy()
    if f_fond:
        vista = vista[vista["Fondamentale"].isin(f_fond)]
    if f_obj:
        vista = vista[vista["Obiettivo"].isin(f_obj)]
    if f_fase:
        vista = vista[vista["Fase"].isin(f_fase)]
    if testo.strip():
        t = testo.strip().lower()
        vista = vista[vista.apply(lambda r: t in str(r["Nome"]).lower() or t in str(r["Descrizione"]).lower(), axis=1)]

    st.caption(f"{len(vista)} esercizi")
    for idx, e in vista.iterrows():
        with st.container():
            fonte = e.get("Fonte", "") if hasattr(e, "get") else ""
            fonte_html = ""
            if isinstance(fonte, str) and fonte.strip():
                fonte_html = (f"<br><a href='{_html.escape(fonte)}' target='_blank' "
                              f"style='color:#ffbf69;font-size:0.85em'>\U0001F517 Fonte online</a>")
            dis = disegno_html(e.get("Disegno", ""))
            st.markdown(
                f"<div class='ex-card'><b>{_html.escape(str(e['Nome']))}</b> "
                f"<span style='color:#ffbf69'>\u00b7 {e['Fondamentale']} \u00b7 {e['Fase']} \u00b7 {e['Durata_min']}min \u00b7 min {e['Min_Giocatrici']} gig.</span> {badge_livello(e['Livello'])}<br>"
                f"<span style='color:#c9d6ea'>{_html.escape(str(e['Descrizione']))}</span><br>"
                f"<span style='color:#7f93b0;font-size:0.9em'>\U0001F501 {_html.escape(str(e['Varianti']))}</span>{fonte_html}{dis}</div>",
                unsafe_allow_html=True,
            )
            cc1, cc2 = st.columns([1, 1])
            with cc1.expander("\u270F\uFE0F Modifica"):
                m1, m2, m3 = st.columns(3)
                with m1:
                    m_nome = st.text_input("Nome", value=str(e["Nome"]), key=f"m_nome_{idx}")
                    m_fond = st.selectbox("Fondamentale", FONDAMENTALI,
                                          index=FONDAMENTALI.index(e["Fondamentale"]) if e["Fondamentale"] in FONDAMENTALI else 0,
                                          key=f"m_fond_{idx}")
                with m2:
                    m_obj = st.selectbox("Obiettivo", OBIETTIVI,
                                         index=OBIETTIVI.index(e["Obiettivo"]) if e["Obiettivo"] in OBIETTIVI else 0,
                                         key=f"m_obj_{idx}")
                    m_fase = st.selectbox("Fase", FASI,
                                          index=FASI.index(e["Fase"]) if e["Fase"] in FASI else 0,
                                          key=f"m_fase_{idx}")
                with m3:
                    m_min = st.number_input("Min. gig.", 1, 24, int(e["Min_Giocatrici"]), key=f"m_min_{idx}")
                    m_dur = st.number_input("Durata", 3, 40, int(e["Durata_min"]), key=f"m_dur_{idx}")
                    m_liv = st.selectbox("Livello", ["Base", "Medio", "Avanzato"],
                                         index=["Base", "Medio", "Avanzato"].index(e["Livello"]) if e["Livello"] in ["Base", "Medio", "Avanzato"] else 0,
                                         key=f"m_liv_{idx}")
                m_desc = st.text_area("Descrizione", value=str(e["Descrizione"]), key=f"m_desc_{idx}")
                m_var = st.text_input("Varianti", value=str(e["Varianti"]), key=f"m_var_{idx}")
                st.markdown("**\U0001F3A8 Schema / disegno**")
                m_dis = editor_disegno(f"m_draw_{idx}", str(e.get("Disegno", "") or ""))
                if st.button("\U0001F4BE Salva modifiche", key=f"m_save_{idx}", use_container_width=True):
                    st.session_state.esercizi.loc[idx, "Nome"] = m_nome.strip()
                    st.session_state.esercizi.loc[idx, "Fondamentale"] = m_fond
                    st.session_state.esercizi.loc[idx, "Obiettivo"] = m_obj
                    st.session_state.esercizi.loc[idx, "Fase"] = m_fase
                    st.session_state.esercizi.loc[idx, "Min_Giocatrici"] = int(m_min)
                    st.session_state.esercizi.loc[idx, "Durata_min"] = int(m_dur)
                    st.session_state.esercizi.loc[idx, "Livello"] = m_liv
                    st.session_state.esercizi.loc[idx, "Descrizione"] = m_desc.strip()
                    st.session_state.esercizi.loc[idx, "Varianti"] = m_var.strip()
                    st.session_state.esercizi.loc[idx, "Disegno"] = m_dis
                    save_state()
                    st.success("Esercizio aggiornato!")
                    st.rerun()
            if cc2.button("\U0001F5D1\uFE0F Elimina", key=f"delex_{idx}", use_container_width=True):
                st.session_state.esercizi = df.drop(idx).reset_index(drop=True)
                save_state()
                st.rerun()

# ============================================================
# ESERCIZI ONLINE
# ============================================================
if menu == "\U0001F310 Esercizi Online":
    st.header("\U0001F310 Esercizi da Internet")
    st.caption("Trova ispirazione online e importa nuovi esercizi nella tua libreria. Serve una connessione a internet.")

    tab_cerca, tab_importa = st.tabs(["\U0001F50E Cerca ispirazione", "\u2B07\uFE0F Importa da link"])

    with tab_cerca:
        c1, c2, c3 = st.columns(3)
        f_fond = c1.selectbox("Fondamentale", FONDAMENTALI, key="onl_fond")
        f_obj = c2.selectbox("Obiettivo", OBIETTIVI, key="onl_obj")
        f_liv = c3.selectbox("Livello", ["Base", "Medio", "Avanzato"], key="onl_liv")
        st.markdown("#### Apri le ricerche pronte")
        st.caption("I link si aprono in una nuova scheda del browser.")
        for etichetta, url in link_ricerca(f_fond, f_obj, f_liv).items():
            st.markdown(f"- [{etichetta}]({url})")
        st.info("\U0001F4A1 Trovato un buon drill? Copia il link e passa alla scheda **Importa da link** per aggiungerlo alla libreria.")

    with tab_importa:
        url = st.text_input("Incolla il link (video YouTube o pagina web)", key="onl_url")
        if st.button("\U0001F50D Analizza link", use_container_width=True):
            if url.strip():
                try:
                    with st.spinner("Recupero informazioni dal link..."):
                        st.session_state._draft_online = importa_da_link(url)
                    st.success("Informazioni recuperate! Completa i campi e salva.")
                except Exception as e:
                    st.session_state._draft_online = {"titolo": "", "descrizione": "", "autore": "", "fonte": url.strip()}
                    st.warning(f"Non sono riuscito a leggere il contenuto ({e}). Puoi comunque compilare a mano: il link \u00e8 gi\u00e0 salvato come fonte.")
            else:
                st.warning("Incolla prima un link.")

        draft = st.session_state.get("_draft_online")
        if draft:
            st.markdown("---")
            st.markdown("#### \U0001F4DD Nuovo esercizio dal link")
            c1, c2, c3 = st.columns(3)
            with c1:
                o_nome = st.text_input("Nome esercizio", value=draft.get("titolo", ""), key="of_nome")
                o_fond = st.selectbox("Fondamentale", FONDAMENTALI, key="of_fond")
            with c2:
                o_obj = st.selectbox("Obiettivo", OBIETTIVI, key="of_obj")
                o_fase = st.selectbox("Fase", FASI, index=1, key="of_fase")
            with c3:
                o_min = st.number_input("Min. giocatrici", 1, 24, 4, key="of_min")
                o_dur = st.number_input("Durata (min)", 3, 40, 12, key="of_dur")
                o_liv = st.selectbox("Livello", ["Base", "Medio", "Avanzato"], index=1, key="of_liv")
            o_desc = st.text_area("Descrizione", value=draft.get("descrizione", ""), key="of_desc")
            o_var = st.text_input("Varianti / progressioni", key="of_var")
            o_fonte = st.text_input("Fonte (link)", value=draft.get("fonte", ""), key="of_fonte")
            st.markdown("**\U0001F3A8 Schema / disegno (facoltativo)**")
            o_dis = editor_disegno("online_draw", "")
            if st.button("\u2795 Aggiungi alla libreria", use_container_width=True, key="of_btn"):
                if o_nome.strip():
                    nuovo = {"Nome": o_nome.strip(), "Fondamentale": o_fond, "Obiettivo": o_obj,
                             "Fase": o_fase, "Min_Giocatrici": int(o_min), "Durata_min": int(o_dur),
                             "Livello": o_liv, "Descrizione": o_desc.strip(), "Varianti": o_var.strip(),
                             "Fonte": o_fonte.strip(), "Disegno": o_dis}
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
if menu == "\U0001F5D3\uFE0F Calendario":
    st.header("\U0001F5D3\uFE0F Calendario Sedute")
    if not st.session_state.sedute:
        st.info("Nessuna seduta salvata. Generane una nella sezione **Programma Allenamenti**.")
    else:
        sedute = sorted(st.session_state.sedute, key=lambda s: s["data"])
        st.markdown("### Sedute programmate")
        _col_int = {"Scarico": "\U0001F7E2", "Medio": "\U0001F7E1", "Pre-partita": "\U0001F7E0", "Carico": "\U0001F534"}
        for i, s in enumerate(sedute):
            tot = sum(int(e["Durata_min"]) for e in s["esercizi"])
            _pallino = _col_int.get(s["intensita"], "\u26AA")
            with st.expander(f"{_pallino} {s['data']} \u2014 {s['obiettivo']} \u00b7 {s['intensita']} \u00b7 {tot} min"):
                if s.get("presenti_nomi"):
                    st.caption("\u2705 Presenti: " + ", ".join(s["presenti_nomi"]))
                if s.get("assenti_nomi"):
                    st.caption("\u274C Assenti: " + ", ".join(s["assenti_nomi"]))

                # --- Modifica presenze anche dopo il salvataggio ---
                with st.popover("\u270F\uFE0F Modifica presenze"):
                    if st.session_state.rosa:
                        _nomi_rosa = [g["Nome"] for g in st.session_state.rosa]
                        _pres_corr = [n for n in (s.get("presenti_nomi") or []) if n in _nomi_rosa]
                        _sel_pres = st.multiselect(
                            "Chi era presente", _nomi_rosa, default=_pres_corr,
                            key=f"editpres_{i}",
                            help="Aggiorna le atlete presenti: chi non selezioni risulter\u00e0 assente.")
                        if st.button("\U0001F4BE Salva presenze", key=f"savepres_{i}", use_container_width=True):
                            _assenti_nomi = [n for n in _nomi_rosa if n not in _sel_pres]
                            s["presenti_nomi"] = _sel_pres
                            s["assenti_nomi"] = _assenti_nomi
                            s["presenti"] = len(_sel_pres)
                            _pres_obj = [g for g in st.session_state.rosa if g["Nome"] in _sel_pres]
                            s["composizione"] = conta_ruoli(_pres_obj)
                            save_state()
                            st.success("Presenze aggiornate!")
                            st.rerun()
                    else:
                        st.info("Aggiungi prima le giocatrici nella sezione Rosa.")
                fase_corrente = None
                for e in s["esercizi"]:
                    if e["Fase"] != fase_corrente:
                        fase_corrente = e["Fase"]
                        st.markdown(f"**{fase_corrente}**")
                    st.markdown(f"- {e['Nome']} ({e['Durata_min']} min) \u2014 _{e['Descrizione']}_")
                    d = disegno_html(e.get("Disegno", ""))
                    if d:
                        st.markdown(d, unsafe_allow_html=True)

                # --- Note post-allenamento (editabili) ---
                _nota = st.text_area("\U0001F4DD Note post-allenamento", value=s.get("note", ""),
                                     key=f"notacal_{i}",
                                     placeholder="Com'\u00e8 andata, cosa migliorare la prossima volta...")
                cbn1, cbn2, cbn3 = st.columns(3)
                if cbn1.button("\U0001F4BE Salva note", key=f"savenote_{i}", use_container_width=True):
                    s["note"] = _nota.strip()
                    save_state()
                    st.success("Note salvate!")
                    st.rerun()
                if cbn2.button("\U0001F4CB Duplica seduta", key=f"dup_{i}", use_container_width=True):
                    import copy as _copy
                    _nuova = _copy.deepcopy(s)
                    _nuova["data"] = date.today().isoformat()
                    st.session_state.sedute.append(_nuova)
                    save_state()
                    st.success("Seduta duplicata (con data di oggi)!")
                    st.rerun()
                cbn3.download_button(
                    "\U0001F5A8\uFE0F Scarica/stampa",
                    data=seduta_html_stampabile(s),
                    file_name="seduta_" + s["data"] + ".html",
                    mime="text/html",
                    key=f"print_{i}",
                    use_container_width=True,
                )
                if st.button("\U0001F5D1\uFE0F Elimina seduta", key=f"delsed_{i}"):
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
# PERIODIZZAZIONE (macrocicli e microcicli)
# ============================================================
if menu == "\U0001F9E9 Periodizzazione":
    st.header("\U0001F9E9 Periodizzazione \u2014 Macrocicli & Microcicli")
    st.caption("Programma la stagione a lungo termine: i **macrocicli** sono i grandi blocchi (es. preparazione, competizione), "
               "i **microcicli** sono le singole settimane. Nel Programma Allenamenti puoi collegare ogni seduta al suo microciclo.")

    FASI_MACRO = ["Preparazione generale", "Preparazione specifica", "Pre-campionato",
                  "Competizione", "Transizione / scarico"]

    tab_macro, tab_micro = st.tabs(["\U0001F5FA\uFE0F Macrocicli", "\U0001F4C6 Microcicli"])

    # ---------- SETTIMANA TIPO (schema di default per giorno) ----------
    with st.expander("\U0001F5D3\uFE0F Settimana tipo \u2014 allenamenti di default per giorno", expanded=False):
        st.caption("Imposta il focus ricorrente di ogni giorno: nel **Programma Allenamenti** gli obiettivi "
                   "vengono precompilati in base al giorno scelto. Lascia vuoti gli obiettivi per rendere il giorno 'libero'.")
        _schema = st.session_state.get("schema_settimanale", dict(SCHEMA_DEFAULT))
        _nuovo_schema = {}
        for _d in range(7):
            _cfg = _schema.get(str(_d), {})
            with st.container():
                st.markdown("**" + GIORNI_IT[_d] + "**")
                sc1, sc2, sc3 = st.columns([2, 3, 1])
                with sc1:
                    _nome_g = st.text_input("Nome focus", value=_cfg.get("nome", ""),
                                            key=f"sch_nome_{_d}", label_visibility="collapsed",
                                            placeholder="es. Attacco e Difesa (vuoto = libero)")
                with sc2:
                    _obj_def = [o for o in _cfg.get("obiettivi", []) if o in OBIETTIVI]
                    _obj_g = st.multiselect("Obiettivi", OBIETTIVI, default=_obj_def,
                                            key=f"sch_obj_{_d}", label_visibility="collapsed",
                                            placeholder="Obiettivi del giorno")
                with sc3:
                    _prev_g = st.checkbox("\U0001FA79", value=bool(_cfg.get("prevenzione")),
                                          key=f"sch_prev_{_d}", help="Prevenzione/fisico nel riscaldamento")
                if _nome_g.strip() or _obj_g:
                    _nuovo_schema[str(_d)] = {"nome": _nome_g.strip(), "obiettivi": _obj_g, "prevenzione": _prev_g}
        bsc1, bsc2 = st.columns(2)
        with bsc1:
            if st.button("\U0001F4BE Salva settimana tipo", use_container_width=True, key="sch_save"):
                st.session_state.schema_settimanale = _nuovo_schema
                save_state()
                st.success("Settimana tipo salvata!")
                st.rerun()
        with bsc2:
            if st.button("\u21A9\uFE0F Ripristina default", use_container_width=True, key="sch_reset"):
                st.session_state.schema_settimanale = dict(SCHEMA_DEFAULT)
                save_state()
                st.success("Ripristinata la settimana tipo di default.")
                st.rerun()

    # ---------- MACROCICLI ----------
    with tab_macro:
        with st.expander("\u2795 Nuovo macrociclo", expanded=not st.session_state.macrocicli):
            mc1, mc2 = st.columns(2)
            with mc1:
                ma_nome = st.text_input("Nome", placeholder="es. Blocco Autunno", key="ma_nome")
                ma_fase = st.selectbox("Fase stagionale", FASI_MACRO, key="ma_fase")
                ma_inizio = st.date_input("Data inizio", value=date.today(), key="ma_inizio")
            with mc2:
                ma_fine = st.date_input("Data fine", value=date.today() + timedelta(days=28), key="ma_fine")
                ma_obj = st.text_input("Obiettivo generale", placeholder="es. Costruzione fisica e tecnica", key="ma_obj")
            ma_note = st.text_area("Note", key="ma_note", height=70)
            if st.button("\u2795 Crea macrociclo", use_container_width=True, key="ma_btn"):
                if ma_nome.strip():
                    st.session_state.macrocicli.append({
                        "nome": ma_nome.strip(), "fase": ma_fase,
                        "inizio": ma_inizio.isoformat(), "fine": ma_fine.isoformat(),
                        "obiettivo": ma_obj.strip(), "note": ma_note.strip(),
                    })
                    save_state()
                    st.success("Macrociclo creato!")
                    st.rerun()
                else:
                    st.warning("Inserisci almeno il nome.")

        if st.session_state.macrocicli:
            for i, m in enumerate(sorted(st.session_state.macrocicli, key=lambda x: x.get("inizio", ""))):
                ni = st.session_state.macrocicli.index(m)
                with st.expander(f"\U0001F5FA\uFE0F {m['nome']} \u00b7 {m['fase']} \u00b7 {m.get('inizio','')} \u2192 {m.get('fine','')}"):
                    st.markdown(f"**Obiettivo:** {_html.escape(m.get('obiettivo','') or '\u2014')}")
                    if m.get("note"):
                        st.caption(m["note"])
                    # microcicli collegati
                    collegati = [mi for mi in st.session_state.microcicli if mi.get("macrociclo") == m["nome"]]
                    st.caption(f"\U0001F4C6 Microcicli collegati: {len(collegati)}")
                    if st.button("\U0001F5D1\uFE0F Elimina macrociclo", key=f"ma_del_{ni}"):
                        st.session_state.macrocicli.pop(ni)
                        save_state()
                        st.rerun()
        else:
            st.info("Nessun macrociclo. Creane uno per impostare la stagione.")

    # ---------- MICROCICLI ----------
    with tab_micro:
        nomi_macro = [m["nome"] for m in st.session_state.macrocicli]
        with st.expander("\u2795 Nuovo microciclo (settimana)", expanded=not st.session_state.microcicli):
            if not nomi_macro:
                st.warning("Crea prima un macrociclo nella scheda a fianco.")
            mi1, mi2 = st.columns(2)
            with mi1:
                mi_nome = st.text_input("Nome", placeholder="es. Settimana 1", key="mi_nome")
                mi_macro = st.selectbox("Macrociclo di appartenenza", nomi_macro or ["(crea prima un macrociclo)"], key="mi_macro")
                mi_inizio = st.date_input("Inizio settimana", value=date.today(), key="mi_inizio")
            with mi2:
                mi_obj = st.selectbox("Obiettivo della settimana", OBIETTIVI, key="mi_obj")
                mi_int = st.selectbox("Intensit\u00e0 target", INTENSITA, index=1, key="mi_int")
                mi_nsed = st.number_input("N. sedute previste", 1, 10, 3, key="mi_nsed")
            mi_note = st.text_area("Note / focus settimanale", key="mi_note", height=70)
            if st.button("\u2795 Crea microciclo", use_container_width=True, key="mi_btn"):
                if mi_nome.strip() and nomi_macro:
                    st.session_state.microcicli.append({
                        "nome": mi_nome.strip(), "macrociclo": mi_macro,
                        "inizio": mi_inizio.isoformat(), "obiettivo": mi_obj,
                        "intensita": mi_int, "n_sedute": int(mi_nsed), "note": mi_note.strip(),
                    })
                    save_state()
                    st.success("Microciclo creato!")
                    st.rerun()
                else:
                    st.warning("Serve il nome e almeno un macrociclo.")

        if st.session_state.microcicli:
            for m in sorted(st.session_state.microcicli, key=lambda x: x.get("inizio", "")):
                ni = st.session_state.microcicli.index(m)
                # quante sedute salvate sono gia' collegate a questo microciclo
                etichetta = f"{m.get('macrociclo','')} \u00b7 {m.get('nome','')}"
                svolte = sum(1 for s in st.session_state.sedute if s.get("microciclo") == etichetta)
                with st.expander(f"\U0001F4C6 {m['nome']} \u00b7 {m.get('macrociclo','')} \u00b7 \U0001F3AF {m['obiettivo']} \u00b7 {m['intensita']}"):
                    st.markdown(f"Inizio: **{m.get('inizio','')}** \u00b7 sedute previste: **{m.get('n_sedute',0)}** \u00b7 svolte: **{svolte}**")
                    if m.get("note"):
                        st.caption(m["note"])
                    if st.button("\U0001F5D1\uFE0F Elimina microciclo", key=f"mi_del_{ni}"):
                        st.session_state.microcicli.pop(ni)
                        save_state()
                        st.rerun()
        else:
            st.info("Nessun microciclo. Crea le settimane di lavoro collegate a un macrociclo.")

# ============================================================
# GARE (calendario partite + convocazioni + countdown)
# ============================================================
if menu == "\U0001F3C6 Gare":
    st.header("\U0001F3C6 Calendario Gare")
    st.caption("Programma le partite, scegli le convocate e tieni d'occhio il conto alla rovescia.")

    _oggi_g = date.today()

    # ---- Nuova gara ----
    with st.expander("\u2795 Aggiungi una gara", expanded=not st.session_state.gare):
        with st.form("form_nuova_gara", clear_on_submit=True):
            cg1, cg2 = st.columns(2)
            with cg1:
                g_data = st.date_input("Data", value=_oggi_g, key="g_data_new")
                g_avv = st.text_input("Avversario", key="g_avv_new")
                g_casa = st.radio("Dove", ["Casa", "Trasferta"], horizontal=True, key="g_casa_new")
            with cg2:
                g_ora = st.text_input("Ora (es. 18:30)", value="18:00", key="g_ora_new")
                g_luogo = st.text_input("Luogo / Palestra", key="g_luogo_new")
                g_comp = st.text_input("Competizione (es. Campionato)", key="g_comp_new")
            _nomi_rosa = [x["Nome"] for x in st.session_state.rosa]
            g_conv = st.multiselect("Convocate", _nomi_rosa, key="g_conv_new")
            g_note = st.text_area("Note (strategia, assenze, ecc.)", key="g_note_new")
            if st.form_submit_button("\U0001F4BE Salva gara"):
                if not g_avv.strip():
                    st.warning("Inserisci almeno il nome dell'avversario.")
                else:
                    st.session_state.gare.append({
                        "data": g_data.isoformat(), "ora": g_ora.strip(),
                        "avversario": g_avv.strip(), "casa": g_casa,
                        "luogo": g_luogo.strip(), "competizione": g_comp.strip(),
                        "convocate": g_conv, "note": g_note.strip(), "esito": "",
                    })
                    save_state()
                    st.success("Gara aggiunta!")
                    st.rerun()

    if not st.session_state.gare:
        st.info("Nessuna gara in calendario. Aggiungine una qui sopra.")
    else:
        _gare_ord = sorted(st.session_state.gare, key=lambda x: (x.get("data", ""), x.get("ora", "")))
        _future = [g for g in _gare_ord if g.get("data", "") >= _oggi_g.isoformat()]

        # ---- Countdown prossima gara + promemoria ----
        if _future:
            _p = _future[0]
            try:
                _gg = (date.fromisoformat(_p["data"]) - _oggi_g).days
            except Exception:
                _gg = None
            _quando = "OGGI!" if _gg == 0 else ("DOMANI" if _gg == 1 else ("tra " + str(_gg) + " giorni") if _gg is not None else "")
            st.markdown(
                "<div class='block-seduta'><h3 style='margin:0'>\u23F3 Prossima gara: " + _quando + "</h3>"
                "<b>" + _html.escape(_p.get("avversario", "")) + "</b> \u00b7 " + _p.get("data", "") +
                (" \u00b7 " + _p.get("ora", "") if _p.get("ora") else "") +
                " \u00b7 " + _p.get("casa", "") + (" \u00b7 " + _html.escape(_p.get("luogo", "")) if _p.get("luogo") else "") +
                "<br>\U0001F465 Convocate: " + str(len(_p.get("convocate") or [])) + " atlete</div>",
                unsafe_allow_html=True,
            )
            # Promemoria scaricabile pre-gara
            _conv_txt = "\n".join("- " + n for n in (_p.get("convocate") or [])) or "(nessuna convocata selezionata)"
            _promemoria = (
                "PROMEMORIA GARA\n================\n"
                + "Avversario: " + _p.get("avversario", "") + "\n"
                + "Data: " + _p.get("data", "") + "  Ora: " + _p.get("ora", "") + "\n"
                + "Dove: " + _p.get("casa", "") + "  Luogo: " + _p.get("luogo", "") + "\n"
                + "Competizione: " + _p.get("competizione", "") + "\n\n"
                + "CONVOCATE (" + str(len(_p.get("convocate") or [])) + "):\n" + _conv_txt + "\n\n"
                + "NOTE:\n" + (_p.get("note", "") or "-") + "\n"
            )
            st.download_button("\U0001F4E5 Scarica promemoria pre-gara", data=_promemoria.encode("utf-8"),
                               file_name="promemoria_gara_" + _p.get("data", "") + ".txt", mime="text/plain")

        st.markdown("---")
        st.markdown("### \U0001F4C5 Tutte le gare")
        for _i, _g in enumerate(_gare_ord):
            _passata = _g.get("data", "") < _oggi_g.isoformat()
            _ico = "\u2705" if _passata else "\U0001F539"
            _titolo = (_ico + " " + _g.get("data", "") + " \u00b7 " + _g.get("avversario", "") +
                       " (" + _g.get("casa", "") + ")")
            with st.expander(_titolo):
                with st.form("form_gara_" + str(_i)):
                    e1, e2 = st.columns(2)
                    with e1:
                        try:
                            _dval = date.fromisoformat(_g.get("data", _oggi_g.isoformat()))
                        except Exception:
                            _dval = _oggi_g
                        ed_data = st.date_input("Data", value=_dval, key="ed_data_" + str(_i))
                        ed_avv = st.text_input("Avversario", value=_g.get("avversario", ""), key="ed_avv_" + str(_i))
                        ed_casa = st.radio("Dove", ["Casa", "Trasferta"],
                                           index=0 if _g.get("casa") == "Casa" else 1,
                                           horizontal=True, key="ed_casa_" + str(_i))
                    with e2:
                        ed_ora = st.text_input("Ora", value=_g.get("ora", ""), key="ed_ora_" + str(_i))
                        ed_luogo = st.text_input("Luogo", value=_g.get("luogo", ""), key="ed_luogo_" + str(_i))
                        ed_comp = st.text_input("Competizione", value=_g.get("competizione", ""), key="ed_comp_" + str(_i))
                    _nomi_rosa2 = [x["Nome"] for x in st.session_state.rosa]
                    _conv_val = [n for n in (_g.get("convocate") or []) if n in _nomi_rosa2]
                    ed_conv = st.multiselect("Convocate", _nomi_rosa2, default=_conv_val, key="ed_conv_" + str(_i))
                    ed_esito = st.text_input("Esito (es. 3-1, Vinta)", value=_g.get("esito", ""), key="ed_esito_" + str(_i))
                    ed_note = st.text_area("Note", value=_g.get("note", ""), key="ed_note_" + str(_i))
                    cbt1, cbt2 = st.columns(2)
                    with cbt1:
                        _upd = st.form_submit_button("\U0001F4BE Aggiorna")
                    with cbt2:
                        _del = st.form_submit_button("\U0001F5D1\uFE0F Elimina")
                    if _upd:
                        _g.update({
                            "data": ed_data.isoformat(), "ora": ed_ora.strip(),
                            "avversario": ed_avv.strip(), "casa": ed_casa,
                            "luogo": ed_luogo.strip(), "competizione": ed_comp.strip(),
                            "convocate": ed_conv, "note": ed_note.strip(), "esito": ed_esito.strip(),
                        })
                        save_state()
                        st.success("Gara aggiornata!")
                        st.rerun()
                    if _del:
                        st.session_state.gare = [x for x in st.session_state.gare if x is not _g]
                        save_state()
                        st.warning("Gara eliminata.")
                        st.rerun()

# ============================================================
# PRESENZE (mensili)
# ============================================================
if menu == "\U0001F4CA Presenze":
    st.header("\U0001F4CA Registro Presenze Mensile")
    st.caption("Le presenze vengono registrate dalle sedute salvate nel calendario (presenti/assenti selezionati nel Programma Allenamenti).")

    sedute = [s for s in st.session_state.sedute if s.get("presenti_nomi") is not None]
    if not st.session_state.rosa:
        st.info("Aggiungi prima le giocatrici nella sezione **Rosa**.")
    elif not sedute:
        st.info("Nessuna seduta con presenze registrate. Genera e salva una seduta selezionando le presenti.")
    else:
        mesi = sorted({s["data"][:7] for s in sedute if s.get("data")}, reverse=True)
        def _label_mese(ym):
            try:
                nomi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
                        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
                y, mm = ym.split("-")
                return f"{nomi[int(mm)-1].capitalize()} {y}"
            except Exception:
                return ym
        mese_sel = st.selectbox("Mese", mesi, format_func=_label_mese)

        sedute_mese = [s for s in sedute if s.get("data", "").startswith(mese_sel)]
        n_sedute = len(sedute_mese)
        st.markdown(f"**{n_sedute} sedute** nel mese selezionato.")

        righe = []
        for g in st.session_state.rosa:
            nome = g["Nome"]
            pres = sum(1 for s in sedute_mese if nome in (s.get("presenti_nomi") or []))
            ass = sum(1 for s in sedute_mese if nome in (s.get("assenti_nomi") or []))
            tot = pres + ass
            perc = round(100 * pres / tot) if tot else 0
            righe.append({
                "Giocatrice": nome, "Ruolo": g.get("Ruolo", ""),
                "Presenze": pres, "Assenze": ass, "% Presenza": perc,
            })
        dfp = pd.DataFrame(righe).sort_values("% Presenza", ascending=False)
        st.dataframe(dfp, use_container_width=True, hide_index=True)

        if not dfp.empty:
            st.markdown("### Presenze per giocatrice")
            st.bar_chart(dfp.set_index("Giocatrice")["Presenze"])
            media = round(dfp["% Presenza"].mean())
            cma, cmb, cmc = st.columns(3)
            cma.metric("Sedute nel mese", n_sedute)
            cmb.metric("Presenza media", f"{media}%")
            top = dfp.iloc[0]
            cmc.metric("Pi\u00f9 presente", f"{top['Giocatrice']} ({top['% Presenza']}%)")

        st.markdown("---")
        st.markdown("### Dettaglio sedute del mese")
        for s in sorted(sedute_mese, key=lambda x: x["data"]):
            pres = ", ".join(s.get("presenti_nomi") or []) or "\u2014"
            ass = ", ".join(s.get("assenti_nomi") or []) or "nessuna"
            st.markdown(
                f"<div class='block-seduta'><b>{s['data']}</b> \u00b7 \U0001F3AF {s['obiettivo']} \u00b7 {s['intensita']}<br>"
                f"<span style='color:#5be59a'>\u2705 {_html.escape(pres)}</span><br>"
                f"<span style='color:#ff8f80'>\u274C {_html.escape(ass)}</span></div>",
                unsafe_allow_html=True,
            )

        # Esporta il registro presenze del mese in CSV
        csv = dfp.to_csv(index=False).encode("utf-8")
        st.download_button("\u2B07\uFE0F Scarica il registro del mese (CSV)", data=csv,
                           file_name=f"presenze_{mese_sel}.csv", mime="text/csv")

        # ---- Andamento sull'intera stagione (tutte le sedute) ----
        st.markdown("---")
        st.markdown("### \U0001F4C8 Andamento stagionale (tutte le sedute)")
        _righe_s, _tot_s = stat_presenze_atleta()
        if _righe_s and _tot_s:
            _dfs = pd.DataFrame(_righe_s).sort_values("%", ascending=False)
            st.caption("Percentuale di presenza di ogni atleta su tutte le " + str(_tot_s) + " sedute registrate.")
            st.bar_chart(_dfs.set_index("Atleta")["%"])
            cs1, cs2 = st.columns(2)
            with cs1:
                st.markdown("**\U0001F3C5 Pi\u00f9 presenti**")
                for _r in _dfs.head(3).to_dict("records"):
                    st.markdown("- " + _html.escape(_r["Atleta"]) + f" \u2014 {_r['%']}% ({_r['Presenze']}/{_r['Sedute']})")
            with cs2:
                st.markdown("**\u26A0\uFE0F Da monitorare**")
                for _r in _dfs.tail(3).to_dict("records")[::-1]:
                    st.markdown("- " + _html.escape(_r["Atleta"]) + f" \u2014 {_r['%']}% ({_r['Presenze']}/{_r['Sedute']})")
