import streamlit as st
import random
import time

st.set_page_config(page_title="10'er-venner", layout="centered")

# ---------- KONSTANTER ----------
GRID_COLS = 5
GRID_ROWS = 2
TOTAL_CELLS = GRID_COLS * GRID_ROWS
TARGET_SUM = 10

BLUE_COLOR = "#005BBB"   # mørk blå
RED_COLOR = "#C62828"    # mørk rød
BOX_COLOR = "#C62828"    # talbokse samme farve som rød

RIGHT_MESSAGES = ["RIGTIGT!", "FLOT!", "GODT GÅET!", "SUPER!", "SEJT!"]
WRONG_MESSAGES = ["Øv, prøv igen", "Tæt på, prøv igen", "Prøv en gang til", "Du kan godt!", "Næsten!"]

# Knapper: label og værdi (sidste tal i udtrykket)
NUMBER_BUTTONS = [
    ("1+9", 9),
    ("2+8", 8),
    ("3+7", 7),
    ("4+6", 6),
    ("5+5", 5),
    ("6+4", 4),
    ("7+3", 3),
    ("8+2", 2),
    ("9+1", 1),
]

# Faser:
# idle        = før spillet er startet
# clear       = tom tavle mellem runder (1 sekund)
# question    = blå cirkler vises, ingen røde
# wrong_show  = blå + røde vises, blink gult, derefter falder røde ned
# wrong_clear = kun blå tilbage, nyt forsøg
# right       = blå + røde vises, rigtigt svar, ny runde efter 2 sek


# ---------- INIT SESSION STATE ----------
if "n_blue" not in st.session_state:
    st.session_state.n_blue = None
if "phase" not in st.session_state:
    st.session_state.phase = "idle"
if "last_guess" not in st.session_state:
    st.session_state.last_guess = None
if "message" not in st.session_state:
    st.session_state.message = ""
if "blink_cells" not in st.session_state:
    st.session_state.blink_cells = []


def handle_guess(guess_value: int):
    """Håndter klik på en knap (sidste tal i udtrykket)."""
    if st.session_state.phase not in ["question", "wrong_clear"]:
        return

    n_blue = st.session_state.n_blue
    if n_blue is None:
        return

    correct_red = TARGET_SUM - n_blue
    st.session_state.last_guess = guess_value

    if guess_value == correct_red:
        # Rigtigt svar
        st.session_state.phase = "right"
        st.session_state.message = random.choice(RIGHT_MESSAGES)
        st.session_state.blink_cells = []
    else:
        # Forkert svar
        st.session_state.phase = "wrong_show"
        st.session_state.message = random.choice(WRONG_MESSAGES)

        blink = []
        if guess_value < correct_red:
            # for få røde -> tomme celler skal blinke
            start = n_blue + guess_value
            end = n_blue + correct_red
            blink = list(range(start, min(end, TOTAL_CELLS)))
        elif guess_value > correct_red:
            # for mange røde -> ekstra røde celler skal blinke
            start = n_blue + correct_red
            end = n_blue + guess_value
            blink = list(range(start, min(end, TOTAL_CELLS)))
        st.session_state.blink_cells = blink


def render_grid():
    phase = st.session_state.phase
    n_blue = st.session_state.n_blue
    last_guess = st.session_state.last_guess if st.session_state.last_guess is not None else 0

    # CLEAR-fase: tom tavle (ingen cirkler)
    if phase == "clear":
        html_cells = []
        for idx in range(TOTAL_CELLS):
            html_cells.append('<div class="cell"></div>')

        rows_html = []
        for r in range(GRID_ROWS):
            row_cells = html_cells[r * GRID_COLS:(r + 1) * GRID_COLS]
            rows_html.append(f'<div class="row">{"".join(row_cells)}</div>')

        grid_html = f"""
        <div class="grid">
            {''.join(rows_html)}
        </div>
        """
        st.markdown(grid_html, unsafe_allow_html=True)
        return

    # Andre faser: vi kan have blå og evt. røde
    if n_blue is None:
        n_blue = 0

    # Hvor mange røde skal vises?
    if phase in ["wrong_show", "right"]:
        n_red = last_guess
    else:
        n_red = 0  # question, wrong_clear, idle

    html_cells = []
    for idx in range(TOTAL_CELLS):
        classes = ["cell"]

        # Blå cirkler først
        if idx < n_blue:
            classes.append("blue")

        # Røde cirkler efter blå
        red_start = n_blue
        red_end = n_blue + n_red
        if red_start <= idx < red_end:
            # I wrong_show skal de komme op (riseIn)
            # I right også op
            # I wrong_clear skal de være væk (n_red=0), så vi ender ikke her
            if phase in ["wrong_show", "right"]:
                classes.append("red_up")

        # Blinkende celler ved forkert svar
        if idx in st.session_state.blink_cells and phase == "wrong_show":
            classes.append("blink")

        cell_div = f'<div class="{" ".join(classes)}"></div>'
        html_cells.append(cell_div)

    # Lav rækker
    rows_html = []
    for r in range(GRID_ROWS):
        row_cells = html_cells[r * GRID_COLS:(r + 1) * GRID_COLS]
        rows_html.append(f'<div class="row">{"".join(row_cells)}</div>')

    grid_html = f"""
    <div class="grid">
        {''.join(rows_html)}
    </div>
    """
    st.markdown(grid_html, unsafe_allow_html=True)


def render_number_buttons():
    st.markdown("<div class='numbers-title'>Vælg 10'er-vennen:</div>", unsafe_allow_html=True)
    cols = st.columns(9)
    for i, (label, value) in enumerate(NUMBER_BUTTONS):
        with cols[i]:
            if st.button(label, key=f"num_{label}", use_container_width=True):
                handle_guess(value)
                st.rerun()


# ---------- CSS ----------
st.markdown(
    f"""
    <style>
    .grid {{
        display: inline-block;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
    .row {{
        display: flex;
        flex-direction: row;
        justify-content: center;
    }}
    .cell {{
        width: 120px;
        height: 120px;
        margin: 6px;
        background-color: white;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 0 0 2px #e0e0e0;
    }}
    .cell::before {{
        content: "";
        position: absolute;
        width: 80%;
        height: 80%;
        border-radius: 50%;
        top: 10%;
        left: 10%;
        opacity: 0;
        transform: translateY(0);
    }}
    .cell.blue::before {{
        background-color: {BLUE_COLOR};
        animation: dropIn 0.8s ease-out forwards;
    }}
    .cell.red_up::before {{
        background-color: {RED_COLOR};
        animation: riseIn 0.8s ease-out forwards;
    }}
    @keyframes dropIn {{
        0% {{ transform: translateY(-150%); opacity: 0; }}
        100% {{ transform: translateY(0); opacity: 1; }}
    }}
    @keyframes riseIn {{
        0% {{ transform: translateY(150%); opacity: 0; }}
        100% {{ transform: translateY(0); opacity: 1; }}
    }}
    .blink {{
        animation: blinkBg 0.5s ease-in-out 6;
    }}
    @keyframes blinkBg {{
        0%, 100% {{ background-color: white; }}
        50% {{ background-color: #FFEB3B; }}
    }}
    .numbers-title {{
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-align: center;
    }}
    .stButton > button {{
        background-color: {BOX_COLOR};
        color: white;
        border-radius: 12px;
        border: none;
        font-size: 1.2rem;
        padding: 10px 0;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }}
    .stButton > button:hover {{
        background-color: #a32020;
    }}
    .message-right {{
        font-size: 2rem;
        font-weight: 800;
        color: #2e7d32;
        text-align: center;
        margin-top: 10px;
    }}
    .message-wrong {{
        font-size: 1.6rem;
        font-weight: 700;
        color: #c62828;
        text-align: center;
        margin-top: 10px;
    }}
    .start-button > button {{
        font-size: 1.4rem !important;
        padding: 10px 24px !important;
        border-radius: 20px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- UI ----------
st.title("10'er-venner")

st.write("Klik på **Start**, se hvor mange blå cirkler der kommer, og vælg så 10'er-vennen nedenunder.")

col_start, _ = st.columns([1, 3])
with col_start:
    if st.button("Start", key="start_btn", use_container_width=True):
        # Start ny runde: først tom tavle (clear)
        st.session_state.phase = "clear"
        st.session_state.n_blue = None
        st.session_state.last_guess = None
        st.session_state.message = ""
        st.session_state.blink_cells = []
        st.rerun()

phase = st.session_state.phase

# CLEAR-fase: vis tom tavle, vent 1 sekund, start ny runde
if phase == "clear":
    render_grid()
    time.sleep(1)
    st.session_state.n_blue = random.randint(1, 9)
    st.session_state.last_guess = None
    st.session_state.blink_cells = []
    st.session_state.message = ""
    st.session_state.phase = "question"
    st.rerun()

# Vis grid i alle andre aktive faser
if phase in ["question", "wrong_show", "wrong_clear", "right"]:
    render_grid()

# Knapper kun når man skal svare
if phase in ["question", "wrong_clear"]:
    render_number_buttons()

# Håndter beskeder og fase-skift
if phase == "right":
    st.markdown(f"<div class='message-right'>{st.session_state.message}</div>", unsafe_allow_html=True)
    time.sleep(2)
    # Efter rigtigt svar: tom tavle og ny runde
    st.session_state.phase = "clear"
    st.session_state.n_blue = None
    st.session_state.last_guess = None
    st.session_state.blink_cells = []
    st.session_state.message = ""
    st.rerun()

elif phase == "wrong_show":
    st.markdown(f"<div class='message-wrong'>{st.session_state.message}</div>", unsafe_allow_html=True)
    # Vis blink + røde et øjeblik, derefter fjern røde (kun blå tilbage)
    time.sleep(1.5)
    st.session_state.phase = "wrong_clear"
    # I wrong_clear viser vi kun blå (n_red=0 i render_grid)
    st.rerun()

elif phase == "wrong_clear":
    st.markdown(f"<div class='message-wrong'>{st.session_state.message}</div>", unsafe_allow_html=True)
