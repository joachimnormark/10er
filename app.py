import streamlit as st
import random
import time

st.set_page_config(page_title="10'er-venner", layout="centered")

# ---------- KONSTANTER ----------
GRID_COLS = 5
GRID_ROWS = 2
TOTAL_CELLS = GRID_COLS * GRID_ROWS
TARGET_SUM = 10

BLUE_COLOR = "#005BBB"
RED_COLOR = "#C62828"
BOX_COLOR = "#C62828"

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
# idle        = før spillet starter
# clear       = tom tavle mellem runder
# question    = blå vises
# wrong_show  = blå + røde vises + blink
# wrong_clear = kun blå tilbage, nyt forsøg
# right       = rigtigt svar, røde vises, ny runde efter pause


# ---------- INIT ----------
if "n_blue" not in st.session_state:
    st.session_state.n_blue = None
if "phase" not in st.session_state:
    st.session_state.phase = "idle"
if "last_guess" not in st.session_state:
    st.session_state.last_guess = None
if "blink_cells" not in st.session_state:
    st.session_state.blink_cells = []
if "message" not in st.session_state:
    st.session_state.message = ""


# ---------- LOGIK ----------
def handle_guess(guess_value: int):
    """Håndter klik på knap."""
    if st.session_state.phase not in ["question", "wrong_clear"]:
        return

    n_blue = st.session_state.n_blue
    correct_red = TARGET_SUM - n_blue
    st.session_state.last_guess = guess_value

    # Beregn røde positioner (bagfra)
    red_positions = list(range(TOTAL_CELLS - 1, TOTAL_CELLS - guess_value - 1, -1))

    # Blink-logik
    blink = []

    for idx in red_positions:
        if idx < 0 or idx >= TOTAL_CELLS:
            continue

        # A) Rød oveni blå → blink
        if idx < n_blue:
            blink.append(idx)

        # B) Hvis guess < correct_red → mangler røde i nogle felter
        # (men kun hvis feltet findes)
        if guess_value < correct_red:
            needed_positions = list(range(TOTAL_CELLS - 1, TOTAL_CELLS - correct_red - 1, -1))
            if idx not in red_positions and idx in needed_positions:
                blink.append(idx)

    # Fjern dubletter
    st.session_state.blink_cells = sorted(set(blink))

    # Rigtigt eller forkert?
    if guess_value == correct_red:
        st.session_state.phase = "right"
        st.session_state.message = random.choice(RIGHT_MESSAGES)
    else:
        st.session_state.phase = "wrong_show"
        st.session_state.message = random.choice(WRONG_MESSAGES)


def render_grid():
    phase = st.session_state.phase
    n_blue = st.session_state.n_blue
    guess = st.session_state.last_guess

    # CLEAR fase → tom tavle
    if phase == "clear":
        html = "".join(
            "<div class='row'>" +
            "".join("<div class='cell'></div>" for _ in range(GRID_COLS)) +
            "</div>"
            for _ in range(GRID_ROWS)
        )
        st.markdown(f"<div class='grid'>{html}</div>", unsafe_allow_html=True)
        return

    # Beregn røde positioner
    red_positions = []
    if phase in ["wrong_show", "right"]:
        red_positions = list(range(TOTAL_CELLS - 1, TOTAL_CELLS - guess - 1, -1))

    html_cells = []
    for idx in range(TOTAL_CELLS):
        classes = ["cell"]

        # Blå
        if n_blue is not None and idx < n_blue:
            classes.append("blue")

        # Rød
        if idx in red_positions:
            if phase in ["wrong_show", "right"]:
                classes.append("red_up")

        # Blink
        if idx in st.session_state.blink_cells and phase == "wrong_show":
            classes.append("blink")

        html_cells.append(f"<div class='{' '.join(classes)}'></div>")

    # Rækker
    rows = []
    for r in range(GRID_ROWS):
        row = html_cells[r * GRID_COLS:(r + 1) * GRID_COLS]
        rows.append("<div class='row'>" + "".join(row) + "</div>")

    st.markdown(f"<div class='grid'>{''.join(rows)}</div>", unsafe_allow_html=True)


def render_number_buttons():
    st.markdown("<div class='numbers-title'>Vælg 10'er-vennen:</div>", unsafe_allow_html=True)
    cols = st.columns(9)
    for i, (label, value) in enumerate(NUMBER_BUTTONS):
        with cols[i]:
            if st.button(label, key=f"btn_{label}", use_container_width=True):
                handle_guess(value)
                st.rerun()


# ---------- CSS ----------
st.markdown(f"""
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
}}
</style>
""", unsafe_allow_html=True)


# ---------- UI ----------
st.title("10'er-venner")

if st.button("Start", use_container_width=True):
    st.session_state.phase = "clear"
    st.session_state.n_blue = None
    st.session_state.last_guess = None
    st.session_state.blink_cells = []
    st.session_state.message = ""
    st.rerun()

phase = st.session_state.phase

# CLEAR → tom tavle → vent → ny runde
if phase == "clear":
    render_grid()
    time.sleep(1)
    st.session_state.n_blue = random.randint(1, 9)
    st.session_state.phase = "question"
    st.rerun()

# Tegn grid
if phase in ["question", "wrong_show", "wrong_clear", "right"]:
    render_grid()

# Knapper
if phase in ["question", "wrong_clear"]:
    render_number_buttons()

# Wrong-show → blink → røde falder ned
if phase == "wrong_show":
    st.markdown(f"<div class='message-wrong'>{st.session_state.message}</div>", unsafe_allow_html=True)
    time.sleep(1.5)
    st.session_state.phase = "wrong_clear"
    st.rerun()

# Right → pause → tom tavle → ny runde
if phase == "right":
    st.markdown(f"<div class='message-right'>{st.session_state.message}</div>", unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.phase = "clear"
    st.session_state.n_blue = None
    st.session_state.last_guess = None
    st.session_state.blink_cells = []
    st.session_state.message = ""
    st.rerun()
