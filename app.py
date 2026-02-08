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

# ---------- INIT SESSION STATE ----------
if "n_blue" not in st.session_state:
    st.session_state.n_blue = None
if "phase" not in st.session_state:
    st.session_state.phase = "idle"  # idle, question, wrong, right
if "guess" not in st.session_state:
    st.session_state.guess = None
if "message" not in st.session_state:
    st.session_state.message = ""
if "blink_cells" not in st.session_state:
    st.session_state.blink_cells = []


def new_round():
    st.session_state.n_blue = random.randint(1, 9)  # 1-9, ingen 0+10
    st.session_state.phase = "question"
    st.session_state.guess = None
    st.session_state.message = ""
    st.session_state.blink_cells = []


def handle_guess(guess):
    if st.session_state.phase not in ["question", "wrong"]:
        return

    n_blue = st.session_state.n_blue
    correct_red = TARGET_SUM - n_blue
    st.session_state.guess = guess

    if guess == correct_red:
        st.session_state.phase = "right"
        st.session_state.message = random.choice(RIGHT_MESSAGES)
        st.session_state.blink_cells = []
    else:
        st.session_state.phase = "wrong"
        st.session_state.message = random.choice(WRONG_MESSAGES)
        # beregn hvilke celler der skal blinke
        blink = []
        if guess < correct_red:
            # for få røde -> tomme celler skal blinke
            start = n_blue + guess
            end = n_blue + correct_red
            blink = list(range(start, min(end, TOTAL_CELLS)))
        elif guess > correct_red:
            # for mange røde -> ekstra røde celler skal blinke
            start = n_blue + correct_red
            end = n_blue + guess
            blink = list(range(start, min(end, TOTAL_CELLS)))
        st.session_state.blink_cells = blink


def render_grid():
    n_blue = st.session_state.n_blue
    guess = st.session_state.guess if st.session_state.guess is not None else 0
    correct_red = TARGET_SUM - n_blue if n_blue is not None else 0

    if st.session_state.phase in ["question", "wrong", "right"]:
        n_red = guess if st.session_state.phase in ["wrong", "right"] else 0
    else:
        n_red = 0

    html_cells = []
    for idx in range(TOTAL_CELLS):
        content = ""
        classes = ["cell"]

        # blå cirkler først
        if n_blue is not None and idx < n_blue:
            classes.append("blue")
            content = ""
        else:
            # røde cirkler efter blå
            red_start = n_blue if n_blue is not None else 0
            red_end = red_start + n_red
            if n_blue is not None and red_start <= idx < red_end:
                classes.append("red")
                content = ""

        if idx in st.session_state.blink_cells and st.session_state.phase == "wrong":
            classes.append("blink")

        cell_div = f'<div class="{" ".join(classes)}"></div>'
        html_cells.append(cell_div)

    # lav rækker
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
    for i in range(1, 10):
        with cols[i - 1]:
            if st.button(str(i), key=f"num_{i}", use_container_width=True):
                handle_guess(i)
                st.experimental_rerun()


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
        transform: translateY(-150%);
        opacity: 0;
    }}
    .cell.blue::before {{
        background-color: {BLUE_COLOR};
        animation: dropIn 0.8s ease-out forwards;
    }}
    .cell.red::before {{
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
        font-size: 1.4rem;
        padding: 12px 0;
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
        new_round()
        st.experimental_rerun()

if st.session_state.phase in ["question", "wrong", "right"]:
    render_grid()
else:
    st.empty()

if st.session_state.phase in ["question", "wrong"]:
    render_number_buttons()

if st.session_state.phase == "right":
    st.markdown(f"<div class='message-right'>{st.session_state.message}</div>", unsafe_allow_html=True)
    # kort pause og ny runde
    time.sleep(2)
    new_round()
    st.experimental_rerun()
elif st.session_state.phase == "wrong":
    st.markdown(f"<div class='message-wrong'>{st.session_state.message}</div>", unsafe_allow_html=True)
