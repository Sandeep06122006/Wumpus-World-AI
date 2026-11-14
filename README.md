# Wumpus World AI Agent Using Knowledge-Based Reasoning and Search Algorithms

## 1. Introduction
The **Wumpus World** is a classic benchmark problem in Artificial Intelligence originally introduced by Gregory Yob in 1973 and popularized by Stuart Russell and Peter Norvig in *Artificial Intelligence: A Modern Approach*. It represents an environment where an agent explores an unknown 4×4 grid cave filled with hazards such as bottomless pits and the fearsome Wumpus beast, with the goal of retrieving hidden gold and safely exiting.

This project implements an intelligent, autonomous agent that makes sound deductions using Propositional Logic and navigates safely using state-of-the-art Search Algorithms.

---

## 2. Problem Statement
In the Wumpus World:
- The environment is partially observable, deterministic, sequential, static, and discrete.
- Moving blindly into a pit or into the cell containing the living Wumpus causes instant death.
- The agent must use local sensor percepts (`Breeze`, `Stench`, `Glitter`, `Bump`, `Scream`) to infer hidden hazards, deduce safe cells, locate the gold, and plot safe navigation paths without ever making a fatal move.

---

## 3. Project Objectives
1. Implement a faithful, customizable 4×4 Wumpus World environment.
2. Develop a Propositional Logic Knowledge Base with `TELL` and `ASK` interfaces and CNF representations.
3. Build an Inference Engine featuring:
   - **Forward Chaining** (Horn / definite rule deductions)
   - **Propositional Resolution** (refutation proof)
   - **DPLL Algorithm** (Davis-Putnam-Logemann-Loveland SAT solver)
4. Implement classic search algorithms (**Breadth-First Search** and **A\* with Manhattan Distance**) constrained strictly to verified safe cells.
5. Provide both a **Console Interface** with step-by-step ASCII visual traces and a modern, interactive **Streamlit Web Dashboard**.

---

## 4. Technologies Used
- **Programming Language:** Python 3.10+
- **Standard Libraries:** `collections` (`deque`), `heapq`, `random`, `time`, `sys`
- **Web UI Framework:** `streamlit`

---

## 5. Folder Structure
```
WumpusWorld_AI_Project/
│
├── main.py               # Console simulation runner and ASCII grid renderer
├── world.py              # Wumpus World environment, percepts, and state updates
├── knowledge_base.py     # Propositional KB (facts, CNF clauses, TELL/ASK, history)
├── inference_engine.py   # Forward Chaining, Resolution, and DPLL SAT checking
├── search.py             # BFS and A* pathfinding using Manhattan distance
├── agent.py              # Intelligent agent brain integrating reasoning & search
├── visualization.py      # Interactive Streamlit Web UI dashboard
├── requirements.txt      # Minimal project dependencies (Streamlit)
└── README.md             # Project documentation and manual
```

---

## 6. Explanation of AI Algorithms

### A. Forward Chaining
- **Concept:** Data-driven deduction starting from known facts and iteratively applying inference rules until no new facts can be added.
- **In this Project:**
  - If a cell has no breeze, all adjacent neighbors are deduced `NOT_PIT`.
  - If a cell has no stench, all adjacent neighbors are deduced `NOT_WUMPUS`.
  - If a cell is proven `NOT_PIT` and `NOT_WUMPUS`, it is marked `SAFE`.
  - If a breeze cell has only one remaining candidate neighbor, that neighbor must be a `PIT`.
  - If a stench cell has only one remaining candidate neighbor, that neighbor must be the `WUMPUS`.

### B. Propositional Logic Resolution
- **Concept:** Refutation-based theorem proving. To prove that $KB \models \alpha$, we add the negated query $\neg \alpha$ to $KB$ and systematically resolve pairs of complementary literals $(L \lor C_1)$ and $(\neg L \lor C_2)$ to derive new resolvents until the empty clause (contradiction) is produced.
- **In this Project:** Used to rigorously prove safety and hazard assertions in CNF.

### C. DPLL Algorithm (Davis-Putnam-Logemann-Loveland)
- **Concept:** A highly efficient recursive backtracking algorithm for solving Boolean Satisfiability (SAT).
- **In this Project:** It tests whether $KB \land \neg \alpha$ is unsatisfiable. Features:
  1. Early termination if all clauses are satisfied.
  2. Immediate backtracking if any clause is falsified.
  3. Unit Clause propagation heuristic to fast-track single literal clauses.
  4. Branching on unassigned propositional symbols.

### D. Breadth-First Search (BFS)
- **Concept:** Uninformed search exploring nodes layer-by-layer using a FIFO queue.
- **In this Project:** Finds the shortest step path between the agent's current position and target safe coordinates, navigating strictly through safe squares.

### E. A\* Search
- **Concept:** Informed best-first search guided by the evaluation function $f(n) = g(n) + h(n)$, where $g(n)$ is the path cost and $h(n)$ is an admissible heuristic.
- **Heuristic:** Manhattan distance $h((x_1, y_1), (x_2, y_2)) = |x_1 - x_2| + |y_1 - y_2|$.
- **In this Project:** Quickly navigates to the nearest unvisited safe cell or back to the entrance $(0,0)$ while avoiding all hazards.

---

## 7. Installation Instructions

1. Ensure Python 3.10 or later is installed.
2. Open a terminal / command prompt and navigate to the project directory:
   ```bash
   cd WumpusWorld_AI_Project
   ```
3. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 8. How to Run the Project

### A. Running the Standalone Interactive Web App (Recommended)
You can directly open `index.html` in any web browser without needing any background Python servers:
- **Double click** [index.html](file:///c:/Users/sande/OneDrive/Desktop/Wumpus-World-AI/index.html) or run `run_web.bat`.
- Features real-time animated 4×4 cave grid, audio effects, live sensor percepts HUD, Knowledge Base inspector, DPLL SAT solver & Forward Chaining telemetry, A*/BFS path visualizer, and manual play mode.

### B. Running the Streamlit Web Application
To launch the interactive graphical Streamlit dashboard:
```bash
python -m streamlit run visualization.py
```
Or use the launcher:
```bash
run_web.bat
```
Then visit `http://localhost:8501` in your browser.

### C. Running the Console Version
To run the automated console simulation with real-time ASCII grid traces:
```bash
python main.py
```

---

## 9. Sample Output (Console Version)
```
============================================================
   WUMPUS WORLD AI AGENT (KNOWLEDGE-BASED & SEARCH)
============================================================
Configuration: Seed=42 | Search Algorithm=A* | Max Steps=35

Initial World Generated:
- Gold Location: (3, 1)
- Wumpus Location: (0, 2)
- Pit Locations: [(2, 3), (1, 1), (1, 2), (2, 2)]

--- STEP 1 ---
Agent Percepts at (0, 0): [Stench: False] [Breeze: False] [Glitter: False]
Agent Reasoning: Action: Heading to safe unvisited cell (0, 1). Path via A*: [(0, 0), (0, 1)]. Stepping to (0, 1).
Selected Action: ('MOVE_TO', (0, 1))
World Response : Moved to (0, 1)

--- STEP 5 ---
Agent Percepts at (0, 0): [Stench: False] [Breeze: False] [Glitter: False]
Agent Reasoning: Action: Wumpus spotted at (0, 2)! Shooting arrow from (0, 0) (-10 score).
Selected Action: ('SHOOT', (0, 2))
World Response : Arrow shot! You heard a terrifying scream: Wumpus is dead!

============================================================
                     SIMULATION FINISHED
============================================================
Final Outcome      : SURVIVED: Agent safely retreated to (0,0) without gold.
Total Steps Taken  : 6
Final Score        : -14
Gold Collected     : False
Wumpus Eliminated  : True
Inference Operations: 86 logical deductions
Total Safe Cells Known: [(0, 0), (0, 1), (1, 0)]
============================================================
```

---

## 10. Conclusion
This project demonstrates how combining knowledge representation, logical deduction (Forward Chaining, Resolution, DPLL), and heuristic search (BFS, A\*) enables an AI agent to operate prudently in partially observable, hazardous environments. The agent never takes unjustified risks, reliably kills or avoids monsters, extracts gold when accessible, and exits safely.

