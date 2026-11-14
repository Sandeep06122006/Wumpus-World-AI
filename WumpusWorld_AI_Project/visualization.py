import streamlit as st
from world import WumpusWorld
from agent import WumpusAgent

# Set page configuration
st.set_page_config(
    page_title="Wumpus World AI - Step-by-Step & Clickable Map",
    page_icon="🏹",
    layout="wide"
)

# Custom CSS for action buttons and 4x4 clickable grid cells
st.markdown("""
<style>
/* Main Action Buttons Styling */
div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) .stButton > button {
    height: 48px !important;
    min-height: 48px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

/* Primary Action Button (Next Step) */
div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) .stButton > button[kind="primary"] {
    background-color: #2563eb !important;
    border: 1px solid #3b82f6 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
}
div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) .stButton > button[kind="primary"]:hover {
    background-color: #1d4ed8 !important;
    border-color: #60a5fa !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.6) !important;
    transform: translateY(-1px) !important;
}

/* Cave Grid 4x4 Buttons Styling */
div[data-testid="stVerticalBlock"]:has(#cave-grid-marker) div[data-testid="column"] .stButton > button {
    height: 85px !important;
    min-height: 85px !important;
    width: 100% !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    white-space: pre-wrap !important;
    line-height: 1.3 !important;
    border: 1px solid #334155 !important;
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    margin-bottom: 6px !important;
}

div[data-testid="stVerticalBlock"]:has(#cave-grid-marker) div[data-testid="column"] .stButton > button:hover {
    border-color: #3b82f6 !important;
    background-color: #273549 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.45) !important;
    cursor: pointer !important;
}

/* Agent Current Cell in Cave Grid */
div[data-testid="stVerticalBlock"]:has(#cave-grid-marker) div[data-testid="column"] .stButton > button[kind="primary"] {
    background-color: #0f3d24 !important;
    border: 3px solid #10b981 !important;
    color: #ffffff !important;
    box-shadow: 0 0 18px rgba(16, 185, 129, 0.55) !important;
}

div[data-testid="stVerticalBlock"]:has(#cave-grid-marker) div[data-testid="column"] .stButton > button[kind="primary"]:hover {
    background-color: #144f2f !important;
    border-color: #34d399 !important;
    box-shadow: 0 0 22px rgba(52, 211, 153, 0.75) !important;
}
</style>
""", unsafe_allow_html=True)

def reset_game():
    """Resets world, agent, KB, score, step count, and direction."""
    st.session_state.world = WumpusWorld(grid_size=4, pit_prob=0.2, seed=st.session_state.seed)
    st.session_state.agent = WumpusAgent(grid_size=4, search_algo=st.session_state.search_algo)
    st.session_state.step = 0
    st.session_state.game_over = False
    
    # Process initial percepts at entrance (0,0)
    init_percepts = st.session_state.world.get_percepts()
    st.session_state.percepts = init_percepts
    st.session_state.agent.update_knowledge(init_percepts)
    
    dir_coord = st.session_state.world.get_dir_coord()
    st.session_state.last_action = "Game Started"
    st.session_state.last_outcome = f"Ready to explore. Click '▶ Next Step' or click an adjacent cell on the map."
    st.session_state.last_reasoning = f"Agent stationed at entrance {dir_coord}. Observed initial percepts: Stench={init_percepts['stench']}, Breeze={init_percepts['breeze']}."

# Initialize Session State
if 'world' not in st.session_state:
    st.session_state.seed = 42
    st.session_state.search_algo = 'A*'
    reset_game()

def handle_ai_step():
    """
    Executes exactly ONE step of autonomous AI decision making.
    Does NOT loop or auto-play. Stops after 1 action.
    """
    if st.session_state.game_over:
        return
    world = st.session_state.world
    agent = st.session_state.agent

    st.session_state.step += 1
    agent.step_count = st.session_state.step

    # 1. Sense current percepts
    percepts = world.get_percepts()

    # 2. Agent reasons and chooses 1 action
    action = agent.choose_action(percepts)
    st.session_state.last_action = str(action)

    # 3. Environment executes the action
    outcome = world.execute_action(action)
    st.session_state.last_outcome = outcome

    # Update reasoning display
    if agent.reasoning_trace:
        st.session_state.last_reasoning = agent.reasoning_trace[-1]

    # 4. Check hazards & termination
    if not world.agent_alive:
        agent.alive = False
        agent.score -= 1000
        st.session_state.game_over = True
    elif world.agent_escaped:
        agent.escaped = True
        st.session_state.game_over = True
    elif st.session_state.step >= 40:
        st.session_state.game_over = True
        st.session_state.last_outcome += " | Reached maximum step limit (40)."

    # 5. Fetch updated percepts at new position
    new_percepts = world.get_percepts()
    st.session_state.percepts = new_percepts

    # Update knowledge base with new percepts
    if world.agent_alive and not world.agent_escaped:
        agent.update_knowledge(new_percepts)

def handle_cell_click(x, y):
    """
    Handles direct mouse click on a 4x4 cave map cell.
    Moves exactly 1 square if adjacent, rejects non-adjacent clicks.
    """
    if st.session_state.game_over:
        st.session_state.last_outcome = "Game is over. Click '🔄 Reset' to play again."
        return

    world = st.session_state.world
    agent = st.session_state.agent
    curr_pos = world.agent_pos
    target_pos = (x, y)

    # Clicked the current agent cell -> do nothing
    if target_pos == curr_pos:
        st.session_state.last_outcome = f"Agent is already at {world.get_dir_coord()}. Please click an adjacent cell to move."
        return

    # Check adjacency (Orthogonal: Up, Down, Left, Right)
    neighbors = world._get_neighbors(curr_pos)
    if target_pos not in neighbors:
        st.session_state.last_action = f"Clicked non-adjacent ({x}, {y})"
        st.session_state.last_outcome = f"⚠️ ({x}, {y}) is not adjacent to {world.get_dir_coord()}! Please select an adjacent cell (Up, Down, Left, or Right)."
        return

    # Valid adjacent move: Execute exactly ONE action
    st.session_state.step += 1
    agent.step_count = st.session_state.step

    # Update direction: Up = N, Down = S, Right = E, Left = W
    world._update_direction(target_pos)
    agent.direction = world.agent_dir

    # Step cost
    agent.score -= 1
    world.agent_pos = target_pos
    agent.pos = target_pos
    dir_coord = world.get_dir_coord()

    # Check Hazards
    if target_pos in world.pits:
        world.agent_alive = False
        agent.alive = False
        agent.score -= 1000
        st.session_state.game_over = True
        st.session_state.last_action = f"Moved to {dir_coord}"
        st.session_state.last_outcome = f"💀 Fell into a bottomless pit at {dir_coord}! Game Over."
        st.session_state.last_reasoning = f"Manual Move: Stepped into pit at {target_pos}."
        agent.reasoning_trace.append(f"Turn {st.session_state.step}: Stepped into pit at {dir_coord}. Agent defeated.")
        st.session_state.percepts = world.get_percepts()
        return

    if target_pos == world.wumpus_pos and world.wumpus_alive:
        world.agent_alive = False
        agent.alive = False
        agent.score -= 1000
        st.session_state.game_over = True
        st.session_state.last_action = f"Moved to {dir_coord}"
        st.session_state.last_outcome = f"👹 Devoured by the Wumpus at {dir_coord}! Game Over."
        st.session_state.last_reasoning = f"Manual Move: Walked into Wumpus at {target_pos}."
        agent.reasoning_trace.append(f"Turn {st.session_state.step}: Walked into living Wumpus at {dir_coord}. Agent defeated.")
        st.session_state.percepts = world.get_percepts()
        return

    # Safe Move
    outcome = f"Moved safely to {dir_coord}"

    # Check Gold Collection
    if target_pos == world.gold_pos and not world.agent_has_gold:
        world.agent_has_gold = True
        agent.has_gold = True
        agent.score += 1000
        outcome += " | 💰 Grabbed the Glittering Gold (+1000 pts)!"
        agent.reasoning_trace.append(f"Turn {st.session_state.step}: Found and grabbed Gold at {dir_coord}!")

    # Update Percepts at new location
    percepts = world.get_percepts()
    st.session_state.percepts = percepts

    # Update Knowledge Base & Inference Engine
    agent.update_knowledge(percepts)

    # Update reasoning summary
    reasoning = f"Manual Move to {dir_coord}. Percepts observed: Stench={percepts['stench']}, Breeze={percepts['breeze']}, Glitter={percepts['glitter']}."
    if agent.reasoning_trace:
        reasoning = agent.reasoning_trace[-1]

    st.session_state.last_action = f"Moved to {dir_coord}"
    st.session_state.last_outcome = outcome
    st.session_state.last_reasoning = reasoning

    # Max steps check
    if st.session_state.step >= 40:
        st.session_state.game_over = True
        st.session_state.last_outcome += " | Reached maximum step limit (40)."

def handle_shoot():
    """Shoots arrow in current facing direction."""
    if st.session_state.game_over:
        return
    world = st.session_state.world
    agent = st.session_state.agent

    if not world.agent_has_arrow:
        st.session_state.last_outcome = "No arrows left!"
        return

    st.session_state.step += 1
    agent.step_count = st.session_state.step
    agent.score -= 10
    agent.has_arrow = False
    world.agent_has_arrow = False

    # Determine shoot target from orientation
    dx, dy = 0, 0
    if world.agent_dir == 'E': dx = 1
    elif world.agent_dir == 'W': dx = -1
    elif world.agent_dir == 'N': dy = 1
    elif world.agent_dir == 'S': dy = -1

    curr_x, curr_y = world.agent_pos
    hit = False
    while 0 <= curr_x + dx < world.grid_size and 0 <= curr_y + dy < world.grid_size:
        curr_x += dx
        curr_y += dy
        if (curr_x, curr_y) == world.wumpus_pos and world.wumpus_alive:
            world.wumpus_alive = False
            world.scream_occurred = True
            hit = True
            break

    if hit:
        outcome = "🏹 Arrow struck! You heard a terrifying scream: Wumpus is dead!"
        agent.reasoning_trace.append(f"Turn {st.session_state.step}: Arrow shot! Wumpus eliminated at ({curr_x},{curr_y}).")
        # Mark all cells safe from Wumpus in KB
        for x in range(world.grid_size):
            for y in range(world.grid_size):
                agent.kb.tell('NOT_WUMPUS', (x, y))
        agent.inference.forward_chaining(agent.kb)
    else:
        outcome = "🏹 Arrow flew through empty darkness and hit a stone wall."
        agent.reasoning_trace.append(f"Turn {st.session_state.step}: Arrow shot facing {world.agent_dir} missed.")

    st.session_state.last_action = f"Shot Arrow ({world.agent_dir})"
    st.session_state.last_outcome = outcome
    st.session_state.last_reasoning = f"Fired arrow facing {world.agent_dir} from {world.get_dir_coord()}."
    st.session_state.percepts = world.get_percepts()

def handle_climb():
    """Climbs out of cave if at start cell (0, 0)."""
    if st.session_state.game_over:
        return
    world = st.session_state.world
    agent = st.session_state.agent

    if world.agent_pos == (0, 0):
        st.session_state.step += 1
        agent.step_count = st.session_state.step
        world.agent_escaped = True
        agent.escaped = True
        st.session_state.game_over = True
        if world.agent_has_gold:
            outcome = "🏆 Climbed out successfully with the gold! VICTORY!"
        else:
            outcome = "🚪 Climbed out safely without the gold."
        st.session_state.last_action = "CLIMB"
        st.session_state.last_outcome = outcome
        st.session_state.last_reasoning = f"Agent climbed out of the cave at {world.get_dir_coord()}."
        agent.reasoning_trace.append(f"Turn {st.session_state.step}: Agent climbed out at {world.get_dir_coord()}.")
    else:
        st.session_state.last_outcome = f"Cannot climb out at {world.get_dir_coord()}! You can only climb out at start position (0, 0)."

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚙️ Game Controls")

# Seed configuration
new_seed = st.sidebar.number_input("Random World Seed", value=st.session_state.seed, step=1, key="seed_input")
if new_seed != st.session_state.seed:
    st.session_state.seed = new_seed
    reset_game()
    st.rerun()

# Search algorithm
algo_idx = 0 if st.session_state.search_algo == 'A*' else 1
new_algo = st.sidebar.selectbox("Search Algorithm", ['A*', 'BFS'], index=algo_idx, key="algo_select")
if new_algo != st.session_state.search_algo:
    st.session_state.search_algo = new_algo
    st.session_state.agent.search_algo = new_algo

st.sidebar.markdown("---")
st.sidebar.subheader("🎮 Primary Controls")

# Next Step button in sidebar
if st.sidebar.button("▶ Next Step (AI Action)", type="primary", disabled=st.session_state.game_over, use_container_width=True, key="side_next_step"):
    handle_ai_step()
    st.rerun()

# Reset button in sidebar
if st.sidebar.button("🔄 Reset Game", use_container_width=True, key="side_reset"):
    reset_game()
    st.rerun()

# Shoot Arrow Button in sidebar
arrow_label = "🏹 Shoot Arrow (-10 pts)" if st.session_state.world.agent_has_arrow else "🚫 Arrow Expended"
if st.sidebar.button(arrow_label, disabled=not st.session_state.world.agent_has_arrow or st.session_state.game_over, use_container_width=True, key="side_shoot"):
    handle_shoot()
    st.rerun()

# Climb Out Button in sidebar
can_climb = (st.session_state.world.agent_pos == (0, 0)) and not st.session_state.game_over
if st.sidebar.button("🚪 Climb Out (at (0,0))", disabled=not can_climb, use_container_width=True, key="side_climb"):
    handle_climb()
    st.rerun()

reveal_map = st.sidebar.checkbox("👁️ Reveal Full Cave (Debug)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Direction Indicators")
st.sidebar.markdown("""
- **N** = North (Facing Up)
- **S** = South (Facing Down)
- **E** = East (Facing Right)
- **W** = West (Facing Left)

*Cell Format:* `S(0,0)`, `N(1,2)`, `E(2,1)`, `W(3,0)`
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Legend")
st.sidebar.markdown("""
- 🤖 **Agent** (Current Location with Direction)
- 🟨 **Safe Cell** (Deducted by Logic)
- 🟩 **Visited Cell**
- 💰 **Gold**
- 👹 **Wumpus** (💀 if dead)
- 🕳️ **Pit**
- ❓ **Unexplored**
""")

# --- MAIN SCREEN ---
world = st.session_state.world
agent = st.session_state.agent
percepts = st.session_state.percepts
dir_coord = world.get_dir_coord()

st.title("🏹 Wumpus World AI — Step-by-Step & Interactive Cave Map")
st.caption("Step-by-step AI deduction with **'▶ Next Step'** OR direct mouse-click movement on the 4×4 Cave Map.")

# Game Over Banner
if st.session_state.game_over:
    if world.agent_escaped and world.agent_has_gold:
        st.success(f"🏆 **GAME OVER — VICTORY!** The agent retrieved the gold and escaped safely! Final Score: **{agent.score}** | Steps: **{st.session_state.step}**")
    elif world.agent_escaped:
        st.info(f"🚪 **GAME OVER — RETREATED!** The agent safely climbed out of the cave at (0,0). Final Score: **{agent.score}** | Steps: **{st.session_state.step}**")
    elif not world.agent_alive:
        st.error(f"💀 **GAME OVER — DEFEAT!** The agent died at {dir_coord}! Final Score: **{agent.score}** | Steps: **{st.session_state.step}**")
    else:
        st.warning(f"⌛ **GAME OVER — STEP LIMIT REACHED!** 40 steps exceeded. Final Score: **{agent.score}**")

# Top Metrics Row
status_label = "🟢 Exploring"
if world.agent_escaped and world.agent_has_gold:
    status_label = "🏆 VICTORY (With Gold)"
elif world.agent_escaped:
    status_label = "🚪 RETREATED SAFELY"
elif not world.agent_alive:
    status_label = "💀 DEFEATED"

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Turn / Step", f"Step {st.session_state.step}")
m2.metric("Agent State", dir_coord, help=f"Facing {world.agent_dir} at ({world.agent_pos[0]}, {world.agent_pos[1]})")
m3.metric("Agent Score", agent.score)
m4.metric("Deductions", agent.inference.operations_count)
m5.metric("Status", status_label)

# Step Details & Telemetry Card
st.markdown(f"""
<div style="background-color: #1e293b; padding: 16px 20px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 18px;">
    <div style="font-size: 15px; font-weight: bold; color: #f8fafc; margin-bottom: 6px;">
        📌 Step {st.session_state.step} Execution Telemetry &amp; State
    </div>
    <div style="font-size: 13px; color: #cbd5e1; line-height: 1.7;">
        <strong>Position &amp; Direction:</strong> <code>({world.agent_pos[0]}, {world.agent_pos[1]})</code> &nbsp;|&nbsp; 
        <strong>Orientation:</strong> <code>{world.agent_dir}</code> &nbsp;|&nbsp; 
        <strong>Formatted State:</strong> <code style="color: #34d399; font-weight: bold; font-size: 15px;">{dir_coord}</code> &nbsp;|&nbsp; 
        <strong>Score:</strong> <code style="color: {'#ef4444' if agent.score < 0 else '#34d399'}; font-weight: bold;">{agent.score}</code><br>
        <strong>Current Percepts:</strong> 👃 Stench: <code>{percepts['stench']}</code> &nbsp;|&nbsp; 💨 Breeze: <code>{percepts['breeze']}</code> &nbsp;|&nbsp; ✨ Glitter: <code>{percepts['glitter']}</code><br>
        <strong>Selected Action:</strong> <code style="color: #60a5fa; font-weight: bold;">{st.session_state.last_action}</code> &nbsp;|&nbsp; 
        <strong>World Response:</strong> <span style="color: #fde047;">{st.session_state.last_outcome}</span><br>
        <strong>Agent Reasoning:</strong> <span style="color: #e2e8f0; font-style: italic;">{st.session_state.last_reasoning}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Action Bar (Prominent Next Step & Reset)
st.markdown('<span id="action-bar-marker"></span>', unsafe_allow_html=True)
act_col1, act_col2, act_col3, act_col4 = st.columns([2.5, 1.2, 1.2, 1.2])
with act_col1:
    if st.button("▶ Next Step (Execute 1 Action)", type="primary", disabled=st.session_state.game_over, use_container_width=True, key="main_next_step"):
        handle_ai_step()
        st.rerun()
with act_col2:
    if st.button("🔄 Reset Game", use_container_width=True, key="main_reset"):
        reset_game()
        st.rerun()
with act_col3:
    main_arrow_label = "🏹 Shoot Arrow" if world.agent_has_arrow else "🚫 Arrow Expended"
    if st.button(main_arrow_label, disabled=not world.agent_has_arrow or st.session_state.game_over, use_container_width=True, key="main_shoot"):
        handle_shoot()
        st.rerun()
with act_col4:
    main_can_climb = (world.agent_pos == (0, 0)) and not st.session_state.game_over
    if st.button("🚪 Climb Out", disabled=not main_can_climb, use_container_width=True, key="main_climb"):
        handle_climb()
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

col_grid, col_info = st.columns([3, 2])

# --- 4x4 CLICKABLE CAVE GRID ---
with col_grid:
    st.markdown('<span id="cave-grid-marker"></span>', unsafe_allow_html=True)
    st.subheader(f"🗺️ Cave Map — Current Position: {dir_coord}")
    st.caption("👉 Click **'▶ Next Step'** above to let AI reason and move 1 step, OR click any adjacent square directly to move manually.")

    grid_size = world.grid_size
    valid_neighbors = world._get_neighbors(world.agent_pos)

    # Render 4x4 Grid of Genuine Streamlit Buttons (Row 3 down to Row 0)
    for y in range(grid_size - 1, -1, -1):
        grid_cols = st.columns(4)
        for x in range(grid_size):
            cell = (x, y)
            is_agent = (cell == world.agent_pos)
            is_visited = (cell in agent.kb.visited)
            is_safe = (cell in agent.kb.known_safe)
            is_pit = (cell in world.pits)
            is_wumpus = (cell == world.wumpus_pos)
            is_gold = (cell == world.gold_pos and not world.agent_has_gold)

            # Determine Cell Label: NEVER display only (0,0) for agent!
            if is_agent:
                label = f"🤖\n{dir_coord}"
            elif is_visited or reveal_map:
                if is_pit:
                    label = f"🕳️ Pit\n({x},{y})"
                elif is_wumpus:
                    w_icon = "👹" if world.wumpus_alive else "💀"
                    label = f"{w_icon} Wumpus\n({x},{y})"
                elif is_gold:
                    label = f"💰 Gold\n({x},{y})"
                elif is_visited:
                    label = f"🟩 Visited\n({x},{y})"
                else:
                    label = f"🟨 Safe\n({x},{y})"
            elif is_safe:
                label = f"🟨 Safe\n({x},{y})"
            else:
                label = f"❓\n({x},{y})"

            # Render clickable button
            btn_type = "primary" if is_agent else "secondary"
            btn_key = f"cell_btn_{x}_{y}"

            if grid_cols[x].button(label, key=btn_key, type=btn_type, use_container_width=True):
                handle_cell_click(x, y)
                st.rerun()

    # Valid adjacent move hints
    neighbor_str = ", ".join([f"({nx},{ny})" for nx, ny in valid_neighbors])
    st.info(f"**Valid Adjacent Moves from {dir_coord}:** `{neighbor_str}`")

# --- PERCEPTS & KNOWLEDGE BASE INFO ---
with col_info:
    st.subheader(f"📡 Current Sensor Percepts at {dir_coord}")
    p_cols = st.columns(3)
    p_cols[0].info(f"👃 **Stench:** {percepts['stench']}")
    p_cols[1].info(f"💨 **Breeze:** {percepts['breeze']}")
    p_cols[2].info(f"✨ **Glitter:** {percepts['glitter']}")

    st.subheader("🧠 Knowledge Base Summary")
    st.write(f"- **Current Agent State:** `{dir_coord}`")
    st.write(f"- **Known Safe Cells:** `{sorted(list(agent.kb.known_safe))}`")
    st.write(f"- **Visited Cells:** `{sorted(list(agent.kb.visited))}`")
    st.write(f"- **Detected Pits:** `{sorted(list(agent.kb.known_pits))}`")
    st.write(f"- **Detected Wumpus:** `{sorted(list(agent.kb.known_wumpus))}`")
    st.write(f"- **Total Active CNF Clauses:** `{len(agent.kb.cnf_clauses)}`")
    st.write(f"- **Total Logical Deductions:** `{agent.inference.operations_count}`")

# --- REASONING TRACE LOG ---
st.markdown("---")
st.subheader("📜 Agent Reasoning Trace & Logical Audit Log")
with st.expander("Click to view complete decision trace", expanded=True):
    if agent.reasoning_trace:
        for log in reversed(agent.reasoning_trace[-12:]):
            st.markdown(f"- {log}")
    else:
        st.write("Ready to begin exploration. Click '▶ Next Step' or an adjacent cell on the map.")
