import random

class WumpusWorld:
    """
    Represents the 4x4 Wumpus World environment.
    Coordinates are (x, y) where x is the column (0 to 3)
    and y is the row (0 to 3), with (0,0) at the bottom-left corner.
    """
    def __init__(self, grid_size=4, pit_prob=0.2, seed=None):
        self.grid_size = grid_size
        self.pit_prob = pit_prob
        
        if seed is not None:
            random.seed(seed)
            
        # Agent state
        self.agent_pos = (0, 0)
        self.agent_dir = 'E' # Direction: N = North, S = South, E = East, W = West
        self.agent_has_gold = False
        self.agent_has_arrow = True
        self.agent_alive = True
        self.agent_escaped = False
        
        # World elements
        self.wumpus_alive = True
        self.pits = set()
        self.wumpus_pos = None
        self.gold_pos = None
        
        # Percept flags
        self.bump_occurred = False
        self.scream_occurred = False
        
        # Generate the world elements safely
        self._generate_world()
        
    def get_dir_coord(self):
        """Returns the agent direction and coordinates in format: S(0,0), N(1,2), etc."""
        return f"{self.agent_dir}({self.agent_pos[0]},{self.agent_pos[1]})"

    def _update_direction(self, target_pos):
        """Updates agent direction based on target position."""
        dx = target_pos[0] - self.agent_pos[0]
        dy = target_pos[1] - self.agent_pos[1]
        if dx > 0:
            self.agent_dir = 'E'
        elif dx < 0:
            self.agent_dir = 'W'
        elif dy > 0:
            self.agent_dir = 'N'
        elif dy < 0:
            self.agent_dir = 'S'

    def _get_neighbors(self, pos):
        """Returns valid adjacent cells (Up, Down, Left, Right)."""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors

    def _generate_world(self):
        """Places pits, Wumpus, and gold while keeping (0,0) safe."""
        all_cells = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        all_cells.remove((0, 0)) # Start cell is always safe
        
        # Make sure at least one neighbor of (0,0) is free of pits and Wumpus
        start_neighbors = [(0, 1), (1, 0)]
        guaranteed_safe_cell = random.choice(start_neighbors)
        
        # 1. Place Wumpus
        possible_wumpus_cells = [c for c in all_cells if c != guaranteed_safe_cell]
        self.wumpus_pos = random.choice(possible_wumpus_cells)
        
        # 2. Place Pits
        for cell in all_cells:
            if cell != guaranteed_safe_cell and cell != self.wumpus_pos:
                if random.random() < self.pit_prob:
                    self.pits.add(cell)
                    
        # 3. Place Gold (not in a pit, and not at (0,0))
        gold_candidates = [c for c in all_cells if c not in self.pits]
        if not gold_candidates:
            gold_candidates = [guaranteed_safe_cell]
        self.gold_pos = random.choice(gold_candidates)

    def get_percepts(self):
        """
        Returns a dictionary of percepts experienced by the agent at the current cell:
        - Stench: adjacent to living or dead Wumpus
        - Breeze: adjacent to a pit
        - Glitter: gold is in current cell and not yet taken
        - Bump: agent hit a boundary wall in the last move
        - Scream: Wumpus was killed in the last action
        """
        x, y = self.agent_pos
        neighbors = self._get_neighbors(self.agent_pos)
        
        stench = (self.wumpus_pos in neighbors) or (self.agent_pos == self.wumpus_pos)
        breeze = any(neighbor in self.pits for neighbor in neighbors)
        glitter = (self.agent_pos == self.gold_pos) and (not self.agent_has_gold)
        bump = self.bump_occurred
        scream = self.scream_occurred
        
        # Reset one-turn percepts
        self.bump_occurred = False
        self.scream_occurred = False
        
        return {
            'stench': stench,
            'breeze': breeze,
            'glitter': glitter,
            'bump': bump,
            'scream': scream
        }

    def execute_action(self, action):
        """
        Executes an agent action and updates world state.
        Actions can be:
        - 'MOVE_TO', target_pos: move to an adjacent cell
        - 'GRAB': pick up gold
        - 'SHOOT', target_pos: shoot arrow towards an adjacent cell or direction
        - 'CLIMB': climb out of the cave at (0,0)
        """
        if not self.agent_alive or self.agent_escaped:
            return "Game Over"

        action_name = action[0] if isinstance(action, tuple) else action
        
        if action_name == 'MOVE_TO':
            target_pos = action[1]
            if target_pos in self._get_neighbors(self.agent_pos):
                self._update_direction(target_pos)
                self.agent_pos = target_pos
                self.bump_occurred = False
                
                # Check hazards
                if self.agent_pos in self.pits:
                    self.agent_alive = False
                    return f"Fell into a pit at {self.get_dir_coord()}!"
                elif self.agent_pos == self.wumpus_pos and self.wumpus_alive:
                    self.agent_alive = False
                    return f"Eaten by the Wumpus at {self.get_dir_coord()}!"
                return f"Moved to {self.get_dir_coord()}"
            else:
                self.bump_occurred = True
                return "Bumped into a wall!"

        elif action_name == 'GRAB':
            if self.agent_pos == self.gold_pos and not self.agent_has_gold:
                self.agent_has_gold = True
                return f"Grabbed the Gold at {self.get_dir_coord()}!"
            return "No gold here to grab."

        elif action_name == 'SHOOT':
            if not self.agent_has_arrow:
                return "No arrows left!"
            
            self.agent_has_arrow = False
            target_pos = action[1]
            self._update_direction(target_pos)
            
            # Calculate direction vector
            dx = target_pos[0] - self.agent_pos[0]
            dy = target_pos[1] - self.agent_pos[1]
            
            # Normalize step
            step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
            step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
            
            # Arrow travels along the row/column until hitting boundary or Wumpus
            curr_x, curr_y = self.agent_pos
            hit = False
            while 0 <= curr_x + step_x < self.grid_size and 0 <= curr_y + step_y < self.grid_size:
                curr_x += step_x
                curr_y += step_y
                if (curr_x, curr_y) == self.wumpus_pos and self.wumpus_alive:
                    self.wumpus_alive = False
                    self.scream_occurred = True
                    hit = True
                    break
                    
            if hit:
                return "Arrow shot! You heard a terrifying scream: Wumpus is dead!"
            else:
                return "Arrow shot! Flew through empty air and hit a wall."

        elif action_name == 'CLIMB':
            if self.agent_pos == (0, 0):
                self.agent_escaped = True
                if self.agent_has_gold:
                    return "Climbed out successfully with the gold! Victory!"
                return "Climbed out safely, but without the gold."
            return "Can only climb out at start position (0, 0)."

        return "Unknown action."

