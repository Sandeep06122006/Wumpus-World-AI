class KnowledgeBase:
    """
    A simple Propositional Logic Knowledge Base for Wumpus World.
    Stores known facts, CNF clauses, and keeps a chronological history.
    """
    def __init__(self, grid_size=4):
        self.grid_size = grid_size
        
        # Categorized sets of known facts
        self.known_safe = {(0, 0)}         # (0, 0) is always safe
        self.visited = set()
        
        self.known_pits = set()
        self.known_not_pits = {(0, 0)}
        
        self.known_wumpus = set()
        self.known_not_wumpus = {(0, 0)}
        
        # Percept history sets
        self.breeze_cells = set()
        self.no_breeze_cells = set()
        self.stench_cells = set()
        self.no_stench_cells = set()
        
        # Logical rules and assertions stored in Conjunctive Normal Form (CNF)
        # Each clause is a frozenset of string literals (e.g., frozenset({"P_1_0", "P_0_1"}))
        self.cnf_clauses = []
        
        # Fact history log for auditing agent decisions
        self.fact_history = []
        
        # Tell the KB that (0, 0) is safe, has no pit, and has no wumpus
        self.tell('SAFE', (0, 0))
        self.tell('NOT_PIT', (0, 0))
        self.tell('NOT_WUMPUS', (0, 0))

    def _get_neighbors(self, pos):
        """Returns adjacent valid cells."""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors

    def tell(self, fact_type, pos, value=True):
        """
        TELL operation: Adds a fact to the knowledge base and generates CNF clauses.
        """
        x, y = pos
        fact_str = f"{fact_type} at ({x}, {y}) = {value}"
        self.fact_history.append(fact_str)
        
        neighbors = self._get_neighbors(pos)

        if fact_type == 'VISITED':
            self.visited.add(pos)
            self.known_safe.add(pos)
            self.known_not_pits.add(pos)
            self.known_not_wumpus.add(pos)

        elif fact_type == 'BREEZE':
            if value:
                self.breeze_cells.add(pos)
                # CNF Rule: Breeze at (x,y) => Pit in at least one neighbor: (P_n1 v P_n2 v ...)
                clause = set(f"P_{nx}_{ny}" for nx, ny in neighbors)
                if clause and clause not in self.cnf_clauses:
                    self.cnf_clauses.append(clause)
            else:
                self.no_breeze_cells.add(pos)
                # CNF Rule: No breeze at (x,y) => ~P_n for every neighbor
                for nx, ny in neighbors:
                    self.known_not_pits.add((nx, ny))
                    neg_clause = {f"~P_{nx}_{ny}"}
                    if neg_clause not in self.cnf_clauses:
                        self.cnf_clauses.append(neg_clause)

        elif fact_type == 'STENCH':
            if value:
                self.stench_cells.add(pos)
                # CNF Rule: Stench at (x,y) => Wumpus in at least one neighbor: (W_n1 v W_n2 v ...)
                clause = set(f"W_{nx}_{ny}" for nx, ny in neighbors)
                if clause and clause not in self.cnf_clauses:
                    self.cnf_clauses.append(clause)
            else:
                self.no_stench_cells.add(pos)
                # CNF Rule: No stench at (x,y) => ~W_n for every neighbor
                for nx, ny in neighbors:
                    self.known_not_wumpus.add((nx, ny))
                    neg_clause = {f"~W_{nx}_{ny}"}
                    if neg_clause not in self.cnf_clauses:
                        self.cnf_clauses.append(neg_clause)

        elif fact_type == 'PIT':
            self.known_pits.add(pos)
            pos_clause = {f"P_{x}_{y}"}
            if pos_clause not in self.cnf_clauses:
                self.cnf_clauses.append(pos_clause)

        elif fact_type == 'NOT_PIT':
            self.known_not_pits.add(pos)
            neg_clause = {f"~P_{x}_{y}"}
            if neg_clause not in self.cnf_clauses:
                self.cnf_clauses.append(neg_clause)

        elif fact_type == 'WUMPUS':
            self.known_wumpus.add(pos)
            pos_clause = {f"W_{x}_{y}"}
            if pos_clause not in self.cnf_clauses:
                self.cnf_clauses.append(pos_clause)

        elif fact_type == 'NOT_WUMPUS':
            self.known_not_wumpus.add(pos)
            neg_clause = {f"~W_{x}_{y}"}
            if neg_clause not in self.cnf_clauses:
                self.cnf_clauses.append(neg_clause)

        elif fact_type == 'SAFE':
            self.known_safe.add(pos)
            self.known_not_pits.add(pos)
            self.known_not_wumpus.add(pos)

    def ask(self, query_type, pos):
        """
        ASK operation: Queries direct knowledge about a cell.
        Returns True, False, or 'UNKNOWN'.
        """
        if query_type == 'IS_SAFE':
            return pos in self.known_safe
        elif query_type == 'IS_PIT':
            if pos in self.known_pits:
                return True
            if pos in self.known_not_pits:
                return False
            return 'UNKNOWN'
        elif query_type == 'IS_WUMPUS':
            if pos in self.known_wumpus:
                return True
            if pos in self.known_not_wumpus:
                return False
            return 'UNKNOWN'
        elif query_type == 'IS_VISITED':
            return pos in self.visited
        return 'UNKNOWN'

    def get_summary(self):
        """Returns a human-readable summary of facts."""
        return {
            'safe_cells': sorted(list(self.known_safe)),
            'visited_cells': sorted(list(self.visited)),
            'known_pits': sorted(list(self.known_pits)),
            'known_wumpus': sorted(list(self.known_wumpus)),
            'total_cnf_clauses': len(self.cnf_clauses),
            'total_facts_logged': len(self.fact_history)
        }

