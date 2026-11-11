class InferenceEngine:
    """
    Inference Engine implementing three core AI logic algorithms:
    1. Forward Chaining (Rule-based deduction)
    2. Propositional Logic Resolution (Refutation proof)
    3. DPLL Algorithm (Davis-Putnam-Logemann-Loveland for SAT checking)
    
    Tracks the total number of logical operations performed.
    """
    def __init__(self):
        self.operations_count = 0

    def reset_counter(self):
        """Resets the inference operations counter."""
        self.operations_count = 0

    # =========================================================================
    # 1. FORWARD CHAINING
    # =========================================================================
    def forward_chaining(self, kb):
        """
        Applies forward chaining over definite logical rules:
        - Rule 1: No breeze at (x,y) -> all neighbors are NOT_PIT.
        - Rule 2: No stench at (x,y) -> all neighbors are NOT_WUMPUS.
        - Rule 3: If a cell is both NOT_PIT and NOT_WUMPUS -> deduce SAFE.
        - Rule 4: If a breeze cell has only ONE neighbor that could be a pit -> that neighbor IS a PIT.
        - Rule 5: If a stench cell has only ONE neighbor that could be Wumpus -> that neighbor IS WUMPUS.
        - Rule 6: If Wumpus position is confirmed, all other cells are NOT_WUMPUS.
        """
        deductions_made = True
        
        while deductions_made:
            deductions_made = False
            self.operations_count += 1
            
            # Rule 1: Propagate No-Breeze
            for pos in list(kb.no_breeze_cells):
                for neighbor in kb._get_neighbors(pos):
                    if neighbor not in kb.known_not_pits:
                        kb.tell('NOT_PIT', neighbor)
                        deductions_made = True
                        self.operations_count += 1
                        
            # Rule 2: Propagate No-Stench
            for pos in list(kb.no_stench_cells):
                for neighbor in kb._get_neighbors(pos):
                    if neighbor not in kb.known_not_wumpus:
                        kb.tell('NOT_WUMPUS', neighbor)
                        deductions_made = True
                        self.operations_count += 1

            # Rule 3: Combine NOT_PIT and NOT_WUMPUS into SAFE
            for x in range(kb.grid_size):
                for y in range(kb.grid_size):
                    cell = (x, y)
                    if cell in kb.known_not_pits and cell in kb.known_not_wumpus:
                        if cell not in kb.known_safe:
                            kb.tell('SAFE', cell)
                            deductions_made = True
                            self.operations_count += 1

            # Rule 4: Eliminate impossible pit locations around a breeze
            for pos in list(kb.breeze_cells):
                neighbors = kb._get_neighbors(pos)
                # Candidates are neighbors that are not proven NOT_PIT
                candidates = [n for n in neighbors if n not in kb.known_not_pits]
                if len(candidates) == 1:
                    pit_cell = candidates[0]
                    if pit_cell not in kb.known_pits:
                        kb.tell('PIT', pit_cell)
                        deductions_made = True
                        self.operations_count += 1

            # Rule 5: Eliminate impossible Wumpus locations around a stench
            for pos in list(kb.stench_cells):
                neighbors = kb._get_neighbors(pos)
                candidates = [n for n in neighbors if n not in kb.known_not_wumpus]
                if len(candidates) == 1:
                    wumpus_cell = candidates[0]
                    if wumpus_cell not in kb.known_wumpus:
                        kb.tell('WUMPUS', wumpus_cell)
                        deductions_made = True
                        self.operations_count += 1

            # Rule 6: If Wumpus is found, all other cells are NOT_WUMPUS
            if kb.known_wumpus:
                wumpus_cell = next(iter(kb.known_wumpus))
                for x in range(kb.grid_size):
                    for y in range(kb.grid_size):
                        cell = (x, y)
                        if cell != wumpus_cell and cell not in kb.known_not_wumpus:
                            kb.tell('NOT_WUMPUS', cell)
                            deductions_made = True
                            self.operations_count += 1

    # =========================================================================
    # 2. PROPOSITIONAL LOGIC RESOLUTION
    # =========================================================================
    def _negate_literal(self, literal):
        """Helper to negate a literal string (e.g., 'P_0_1' -> '~P_0_1', '~P_0_1' -> 'P_0_1')."""
        if literal.startswith('~'):
            return literal[1:]
        return '~' + literal

    def resolution(self, kb_clauses, query_literal):
        """
        Resolution algorithm: Tests whether KB entails query_literal.
        Proof by refutation: Adds negated query to KB and resolves pairs of clauses.
        Returns True if a contradiction (empty clause) is derived, else False.
        """
        negated_query = self._negate_literal(query_literal)
        
        # Convert clauses to frozensets of literals
        clauses = set(frozenset(c) for c in kb_clauses)
        clauses.add(frozenset([negated_query]))
        
        new_clauses = set()
        
        while True:
            clause_list = list(clauses)
            n = len(clause_list)
            
            for i in range(n):
                for j in range(i + 1, n):
                    c1 = clause_list[i]
                    c2 = clause_list[j]
                    self.operations_count += 1
                    
                    # Look for complementary literals
                    for lit in c1:
                        neg_lit = self._negate_literal(lit)
                        if neg_lit in c2:
                            # Resolve c1 and c2
                            resolvent = (c1 - {lit}) | (c2 - {neg_lit})
                            
                            # Contradiction reached: empty clause
                            if len(resolvent) == 0:
                                return True
                                
                            new_clauses.add(frozenset(resolvent))
            
            # If no new clauses were derived, refutation failed
            if new_clauses.issubset(clauses):
                return False
                
            clauses.update(new_clauses)

    # =========================================================================
    # 3. DPLL (Davis-Putnam-Logemann-Loveland) ALGORITHM
    # =========================================================================
    def _evaluate_clause(self, clause, model):
        """
        Evaluates a clause under the given boolean assignment model.
        Returns True, False, or None (if undetermined).
        """
        has_undetermined = False
        for lit in clause:
            negated = lit.startswith('~')
            var = lit[1:] if negated else lit
            
            if var in model:
                val = model[var]
                lit_val = not val if negated else val
                if lit_val is True:
                    return True
            else:
                has_undetermined = True
                
        if has_undetermined:
            return None
        return False

    def dpll(self, clauses, symbols, model=None):
        """
        DPLL Algorithm for checking satisfiability of CNF clauses:
        - Unit clause propagation
        - Backtracking search over symbols
        """
        if model is None:
            model = {}
            
        self.operations_count += 1
        
        # Check all clauses under current model
        all_true = True
        for clause in clauses:
            eval_res = self._evaluate_clause(clause, model)
            if eval_res is False:
                return False # A clause is violated
            if eval_res is not True:
                all_true = False
                
        if all_true:
            return True # All clauses satisfied

        # Unit Clause Heuristic: Find a clause with exactly 1 unassigned literal
        for clause in clauses:
            unassigned = []
            satisfied = False
            for lit in clause:
                negated = lit.startswith('~')
                var = lit[1:] if negated else lit
                if var in model:
                    if (not model[var] if negated else model[var]) is True:
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
                    
            if not satisfied and len(unassigned) == 1:
                unit_lit = unassigned[0]
                neg = unit_lit.startswith('~')
                var = unit_lit[1:] if neg else unit_lit
                new_model = dict(model)
                new_model[var] = False if neg else True
                rem_symbols = [s for s in symbols if s != var]
                return self.dpll(clauses, rem_symbols, new_model)

        # Branching: Pick first unassigned symbol and try True, then False
        if not symbols:
            return False
            
        p = symbols[0]
        rest = symbols[1:]
        
        # Branch 1: Try p = True
        model_true = dict(model)
        model_true[p] = True
        if self.dpll(clauses, rest, model_true):
            return True
            
        # Branch 2: Try p = False
        model_false = dict(model)
        model_false[p] = False
        return self.dpll(clauses, rest, model_false)

    def entails_dpll(self, kb_clauses, query_literal):
        """
        Checks if KB entails query_literal using DPLL.
        KB |= query iff (KB AND ~query) is UNSATISFIABLE.
        """
        negated_query = self._negate_literal(query_literal)
        test_clauses = [set(c) for c in kb_clauses] + [{negated_query}]
        
        # Extract unique symbols from clauses
        symbols = set()
        for clause in test_clauses:
            for lit in clause:
                var = lit[1:] if lit.startswith('~') else lit
                symbols.add(var)
                
        # If unsatisfiable, then entailment holds
        is_sat = self.dpll(test_clauses, sorted(list(symbols)), {})
        return not is_sat

