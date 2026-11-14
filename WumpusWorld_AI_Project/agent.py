from knowledge_base import KnowledgeBase
from inference_engine import InferenceEngine
from search import bfs, a_star, manhattan_distance

class WumpusAgent:
    """
    Intelligent Knowledge-Based Agent for the Wumpus World.
    Uses:
    - Knowledge Base to store observed percepts and facts
    - Inference Engine (Forward Chaining, Resolution, DPLL) to deduce safe cells
    - Search Algorithms (BFS / A*) to plan safe travel paths
    """
    def __init__(self, grid_size=4, search_algo='A*'):
        self.grid_size = grid_size
        self.search_algo = search_algo # 'A*' or 'BFS'
        
        # Knowledge Base and Inference Engine
        self.kb = KnowledgeBase(grid_size=grid_size)
        self.inference = InferenceEngine()
        
        # Agent status
        self.pos = (0, 0)
        self.direction = 'E' # Direction: N = North, S = South, E = East, W = West
        self.has_gold = False
        self.has_arrow = True
        self.alive = True
        self.escaped = False
        
        # Performance metrics
        self.score = 0
        self.step_count = 0
        self.reasoning_trace = []
        
        # Mark start cell as visited
        self.kb.tell('VISITED', self.pos)

    def get_dir_coord(self):
        """Returns the agent direction and coordinates in format: S(0,0), N(1,2), etc."""
        return f"{self.direction}({self.pos[0]},{self.pos[1]})"

    def _update_direction(self, target_pos):
        """Updates agent direction based on target position."""
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        if dx > 0:
            self.direction = 'E'
        elif dx < 0:
            self.direction = 'W'
        elif dy > 0:
            self.direction = 'N'
        elif dy < 0:
            self.direction = 'S'

    def _find_path(self, start, goal):
        """Finds safe path using the configured search algorithm (A* or BFS)."""
        if self.search_algo == 'BFS':
            return bfs(start, goal, self.kb.known_safe, self.grid_size)
        else:
            return a_star(start, goal, self.kb.known_safe, self.grid_size)

    def update_knowledge(self, percepts):
        """
        Updates the Knowledge Base with new percepts and applies logical reasoning.
        """
        # Record visited
        self.kb.tell('VISITED', self.pos)
        
        # Update breeze
        self.kb.tell('BREEZE', self.pos, percepts['breeze'])
        
        # Update stench
        self.kb.tell('STENCH', self.pos, percepts['stench'])
        
        # If scream heard, Wumpus is dead, all cells become safe from Wumpus
        if percepts['scream']:
            self.reasoning_trace.append("Deduction: Scream heard! The Wumpus is dead. Wumpus danger eliminated.")
            for x in range(self.grid_size):
                for y in range(self.grid_size):
                    self.kb.tell('NOT_WUMPUS', (x, y))

        # 1. Run Forward Chaining to deduce new safe/hazard cells
        old_safe_count = len(self.kb.known_safe)
        self.inference.forward_chaining(self.kb)
        new_safe_count = len(self.kb.known_safe)
        
        if new_safe_count > old_safe_count:
            new_safe = self.kb.known_safe - self.kb.visited
            self.reasoning_trace.append(f"Forward Chaining: Inferred new safe cell(s): {list(new_safe)}")

        # 2. Check unconfirmed neighbors using Resolution / DPLL if applicable
        for neighbor in self.kb._get_neighbors(self.pos):
            if neighbor not in self.kb.known_safe and neighbor not in self.kb.known_pits:
                # Query DPLL whether this cell has a pit
                pit_literal = f"P_{neighbor[0]}_{neighbor[1]}"
                if self.inference.entails_dpll(self.kb.cnf_clauses, pit_literal):
                    self.kb.tell('PIT', neighbor)
                    self.reasoning_trace.append(f"DPLL Logic: Proved that {neighbor} is a PIT.")

    def choose_action(self, percepts):
        """
        Main decision-making function:
        1. Process percepts and deduce safe locations.
        2. Grab gold if glitter is seen.
        3. If gold collected, navigate back to (0,0) and climb out.
        4. Shoot arrow if Wumpus position is pinpointed and in sight.
        5. Explore nearest safe unvisited cell.
        6. Safely retreat to start if no more safe moves are possible.
        """
        self.step_count += 1
        
        # Step 1: Update Knowledge Base with percepts
        self.update_knowledge(percepts)
        
        trace_entry = f"Turn {self.step_count} at {self.get_dir_coord()} | Percepts: {percepts}"
        self.reasoning_trace.append(trace_entry)

        # Step 2: Grab Gold if at glitter cell
        if percepts['glitter'] and not self.has_gold:
            self.has_gold = True
            self.score += 1000
            self.reasoning_trace.append(f"Action: GLITTER detected at {self.get_dir_coord()}! Executing GRAB to take the gold (+1000 score).")
            return 'GRAB'

        # Step 3: If carrying gold, return to (0,0) and climb out
        if self.has_gold:
            if self.pos == (0, 0):
                self.escaped = True
                self.reasoning_trace.append(f"Action: Safely returned to exit {self.get_dir_coord()} with gold! Executing CLIMB out of the cave.")
                return 'CLIMB'
            
            # Plan route back to exit
            path = self._find_path(self.pos, (0, 0))
            if path and len(path) > 1:
                next_step = path[1]
                self._update_direction(next_step)
                self.pos = next_step
                self.score -= 1
                self.reasoning_trace.append(f"Action: Escaping with gold. Path found using {self.search_algo}: {path}. Moving to {self.get_dir_coord()}.")
                return ('MOVE_TO', next_step)

        # Step 4: If Wumpus location is known and we have an arrow, shoot it
        if self.kb.known_wumpus and self.has_arrow:
            wumpus_pos = next(iter(self.kb.known_wumpus))
            # Shoot if aligned horizontally or vertically
            if self.pos[0] == wumpus_pos[0] or self.pos[1] == wumpus_pos[1]:
                self._update_direction(wumpus_pos)
                self.has_arrow = False
                self.score -= 10
                self.reasoning_trace.append(f"Action: Wumpus spotted at {wumpus_pos}! Shooting arrow facing {self.direction} from {self.get_dir_coord()} (-10 score).")
                return ('SHOOT', wumpus_pos)

        # Step 5: Explore safe unvisited cells
        unvisited_safe = [cell for cell in self.kb.known_safe if cell not in self.kb.visited]
        
        if unvisited_safe:
            # Sort candidate cells by Manhattan distance from current pos
            unvisited_safe.sort(key=lambda c: manhattan_distance(self.pos, c))
            
            for candidate in unvisited_safe:
                path = self._find_path(self.pos, candidate)
                if path and len(path) > 1:
                    next_step = path[1]
                    self._update_direction(next_step)
                    self.pos = next_step
                    self.score -= 1
                    self.reasoning_trace.append(f"Action: Heading to safe unvisited cell {candidate}. Path via {self.search_algo}: {path}. Stepping to {self.get_dir_coord()}.")
                    return ('MOVE_TO', next_step)

        # Step 6: No safe unvisited cells accessible - safely retreat to (0,0)
        if self.pos != (0, 0):
            path = self._find_path(self.pos, (0, 0))
            if path and len(path) > 1:
                next_step = path[1]
                self._update_direction(next_step)
                self.pos = next_step
                self.score -= 1
                self.reasoning_trace.append(f"Action: No further safe unexplored cells. Retreating to (0,0). Stepping to {self.get_dir_coord()}.")
                return ('MOVE_TO', next_step)
        else:
            # Already at (0,0) with no safe moves left
            self.escaped = True
            self.reasoning_trace.append(f"Action: At {self.get_dir_coord()} with no further safe paths. CLIMBING out to survive.")
            return 'CLIMB'

        return 'CLIMB'

