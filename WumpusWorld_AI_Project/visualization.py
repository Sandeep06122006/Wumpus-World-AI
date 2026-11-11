import streamlit as st
import time
from world import WumpusWorld
from agent import WumpusAgent

# Set page configuration
st.set_page_config(
    page_title="Wumpus World AI Agent",
    page_icon="🏹",
    layout="wide"
)

# Initialize Session State
if 'world' not in st.session_state:
    st.session_state.seed = 42
    st.session_state.search_algo = 'A*'
    st.session_state.world = WumpusWorld(grid_size=4, pit_prob=0.2, seed=st.session_state.seed)
    st.session_state.agent = WumpusAgent(grid_size=4, search_algo=st.session_state.search_algo)
    st.session_state.step = 0
    st.session_state.game_over = False
    st.session_state.last_action = "Game Started"
    st.session_state.last_outcome = "Ready to explore"

def reset_game():
    st.session_state.world = WumpusWorld(grid_size=4, pit_prob=0.2, seed=st.session_state.seed)
    st.session_state.agent = WumpusAgent(grid_size=4, search_algo=st.session_state.search_algo)
    st.session_state.step = 0
    st.session_state.game_over = False
    st.session_state.last_action = "Game Reset"
    st.session_state.last_outcome = "Ready to explore"

def step_game():
    if st.session_state.game_over:
        return
        
    world = st.session_state.world
    agent = st.session_state.agent
    
    if not world.agent_alive or world.agent_escaped or st.session_state.step >= 40:
        st.session_state.game_over = True
        return
        
    st.session_state.step += 1
    
    # 1. Get Percepts
    percepts = world.get_percepts()
    
    # 2. Agent Chooses Action
    action = agent.choose_action(percepts)
    st.session_state.last_action = str(action)
    
    # 3. World Executes Action
    outcome = world.execute_action(action)
    st.session_state.last_outcome = outcome
    
    # Check end condition
    if not world.agent_alive or world.agent_escaped or st.session_state.step >= 40:
        st.session_state.game_over = True

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚙️ Game Settings")
st.session_state.seed = st.sidebar.number_input("Random World Seed", value=42, step=1)
st.session_state.search_algo = st.sidebar.selectbox("Search Algorithm", ['A*', 'BFS'])

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("▶ Next Step", use_container_width=True):
        step_game()
with col_btn2:
    if st.button("🔄 Reset", use_container_width=True):
        reset_game()

if st.sidebar.button("⏩ Auto Play", use_container_width=True):
    while not st.session_state.game_over:
        step_game()
        time.sleep(0.05)
    st.rerun()

reveal_map = st.sidebar.checkbox("👁️ Reveal Full Cave (Debug)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Legend")
st.sidebar.markdown("""
- 🤖 **Agent** (Current Location)
- 🟨 **Safe Cell** (Deducted by Logic)
- 🟩 **Visited Cell**
- 💰 **Gold**
- 👹 **Wumpus** (💀 if dead)
- 🕳️ **Pit**
- ❓ **Unexplored**
""")

# --- MAIN SCREEN ---
st.title("🏹 Wumpus World AI Agent")
st.caption("Knowledge-Based Reasoning (Forward Chaining, Resolution, DPLL) + Search Algorithms (BFS, A*)")

world = st.session_state.world
agent = st.session_state.agent
percepts = world.get_percepts()

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Turn", st.session_state.step)
m2.metric("Agent Score", agent.score)
m3.metric("Logical Deductions", agent.inference.operations_count)
status_label = "Exploring"
if world.agent_escaped and world.agent_has_gold:
    status_label = "🏆 VICTORY (Escaped with Gold)"
elif world.agent_escaped:
    status_label = "🚪 RETREATED SAFELY"
elif not world.agent_alive:
    status_label = "💀 DEFEATED"
m4.metric("Status", status_label)

st.markdown("---")

col_grid, col_info = st.columns([3, 2])

# --- GRID VISUALIZATION ---
with col_grid:
    st.subheader("🗺️ Cave Map")
    grid_size = world.grid_size
    
    # Generate HTML Table for the 4x4 grid
    html_grid = "<table style='width:100%; text-align:center; border-collapse: separate; border-spacing: 6px;'>"
    for y in range(grid_size - 1, -1, -1):
        html_grid += "<tr>"
        for x in range(grid_size):
            cell = (x, y)
            is_agent = (cell == world.agent_pos)
            is_visited = (cell in agent.kb.visited)
            is_safe = (cell in agent.kb.known_safe)
            is_pit = (cell in world.pits)
            is_wumpus = (cell == world.wumpus_pos)
            is_gold = (cell == world.gold_pos and not world.agent_has_gold)
            
            # Decide visual styling
            bg_color = "#2b2b2b"
            border = "1px solid #444"
            content = []
            
            if is_agent:
                content.append("🤖")
                border = "3px solid #00d26a"
                
            if is_visited or reveal_map:
                if is_pit:
                    content.append("🕳️")
                    bg_color = "#4a1515"
                if is_wumpus:
                    content.append("👹" if world.wumpus_alive else "💀")
                    bg_color = "#3d1f4a"
                if is_gold:
                    content.append("💰")
                if not is_pit and not is_wumpus and is_visited:
                    bg_color = "#1f3a2b"
            elif is_safe:
                content.append("🟨 Safe")
                bg_color = "#2a3b2a"
            else:
                content.append("❓")

            cell_text = " ".join(content) if content else f"({x},{y})"
            html_grid += f"<td style='height: 80px; background-color: {bg_color}; border: {border}; border-radius: 8px; font-size: 16px; font-weight: bold;'>{cell_text}<br><span style='font-size: 11px; color: #888;'>({x}, {y})</span></td>"
        html_grid += "</tr>"
    html_grid += "</table>"
    
    st.markdown(html_grid, unsafe_allow_html=True)
    st.markdown(f"**Last Action:** `{st.session_state.last_action}` | **Outcome:** `{st.session_state.last_outcome}`")

# --- PERCEPTS & KNOWLEDGE BASE INFO ---
with col_info:
    st.subheader("📡 Current Sensor Percepts")
    p_cols = st.columns(3)
    p_cols[0].info(f"👃 **Stench:** {percepts['stench']}")
    p_cols[1].info(f"💨 **Breeze:** {percepts['breeze']}")
    p_cols[2].info(f"✨ **Glitter:** {percepts['glitter']}")

    st.subheader("🧠 Knowledge Base Summary")
    st.write(f"- **Known Safe Cells:** `{sorted(list(agent.kb.known_safe))}`")
    st.write(f"- **Visited Cells:** `{sorted(list(agent.kb.visited))}`")
    st.write(f"- **Detected Pits:** `{sorted(list(agent.kb.known_pits))}`")
    st.write(f"- **Detected Wumpus:** `{sorted(list(agent.kb.known_wumpus))}`")
    st.write(f"- **Total Active CNF Clauses:** `{len(agent.kb.cnf_clauses)}`")

# --- REASONING TRACE LOG ---
st.markdown("---")
st.subheader("📜 Agent Reasoning Trace & Logical Audit Log")
with st.expander("Click to view complete decision trace", expanded=True):
    if agent.reasoning_trace:
        for log in reversed(agent.reasoning_trace[-10:]):
            st.markdown(f"- {log}")
    else:
        st.write("No actions executed yet.")

