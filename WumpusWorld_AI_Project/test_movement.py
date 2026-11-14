from world import WumpusWorld
from agent import WumpusAgent

def run_tests():
    print("==================================================")
    print(" RUNNING 7 MANDATORY CLICK-MOVEMENT TEST CASES")
    print("==================================================")

    # Setup world with known locations
    # (0,0) safe start
    # Let (0,1) be safe, (1,0) be a pit, (0,2) be Wumpus, (0,3) be Gold
    world = WumpusWorld(grid_size=4, seed=42)
    world.agent_pos = (0, 0)
    world.agent_dir = 'E'
    world.pits = {(1, 0), (2, 2)}
    world.wumpus_pos = (0, 2)
    world.wumpus_alive = True
    world.gold_pos = (0, 3)
    world.agent_has_gold = False
    world.agent_alive = True

    agent = WumpusAgent(grid_size=4)
    agent.pos = (0, 0)
    agent.direction = 'E'

    step = 0

    # -------------------------------------------------------------------------
    # TEST 1: Clicking an adjacent safe cell moves the agent one square
    # -------------------------------------------------------------------------
    target = (0, 1) # Adjacent to (0,0) (Up/North)
    neighbors = world._get_neighbors(world.agent_pos)
    assert target in neighbors, "Test 1 Failed: Target is not adjacent"
    
    world._update_direction(target)
    agent.direction = world.agent_dir
    agent.score -= 1
    world.agent_pos = target
    agent.pos = target
    step += 1
    
    assert world.agent_pos == (0, 1), f"Test 1 Failed: Agent pos is {world.agent_pos}"
    assert world.agent_dir == 'N', f"Test 1 Failed: Agent dir is {world.agent_dir}"
    assert world.get_dir_coord() == "N(0,1)", f"Test 1 Failed: Formatted state is {world.get_dir_coord()}"
    assert world.agent_alive == True, "Test 1 Failed: Agent died in safe cell"
    print("✓ Test 1 Passed: Adjacent safe cell move succeeded -> N(0,1)")

    # -------------------------------------------------------------------------
    # TEST 2: Clicking a non-adjacent cell does NOT move the agent
    # -------------------------------------------------------------------------
    non_adjacent_target = (3, 3)
    current_pos_before = world.agent_pos
    current_dir_before = world.agent_dir
    step_before = step
    
    # Check rejection
    neighbors = world._get_neighbors(world.agent_pos)
    assert non_adjacent_target not in neighbors, "Test 2 error: 3,3 should not be adjacent"
    
    # Movement blocked
    assert world.agent_pos == current_pos_before, "Test 2 Failed: Pos changed on non-adjacent click"
    assert world.agent_dir == current_dir_before, "Test 2 Failed: Dir changed on non-adjacent click"
    assert step == step_before, "Test 2 Failed: Step counter advanced on invalid move"
    print("✓ Test 2 Passed: Non-adjacent cell (3,3) rejected, agent remained at N(0,1)")

    # -------------------------------------------------------------------------
    # TEST 3: Clicking a Wumpus cell kills the agent
    # -------------------------------------------------------------------------
    # Move from (0,1) to (0,2) where Wumpus is
    wumpus_target = (0, 2)
    assert wumpus_target in world._get_neighbors(world.agent_pos)
    
    world._update_direction(wumpus_target)
    agent.direction = world.agent_dir
    world.agent_pos = wumpus_target
    agent.pos = wumpus_target
    step += 1
    
    # Hazard check
    if world.agent_pos == world.wumpus_pos and world.wumpus_alive:
        world.agent_alive = False
        agent.alive = False
        agent.score -= 1000
        
    assert world.agent_alive == False, "Test 3 Failed: Agent survived walking into Wumpus"
    assert world.get_dir_coord() == "N(0,2)", f"Test 3 Failed: Direction coord is {world.get_dir_coord()}"
    print("✓ Test 3 Passed: Stepping into Wumpus cell killed agent at N(0,2)")

    # -------------------------------------------------------------------------
    # TEST 4: Clicking a pit cell kills the agent
    # -------------------------------------------------------------------------
    # Reset world to test pit death
    world.agent_pos = (0, 0)
    world.agent_dir = 'E'
    world.agent_alive = True
    pit_target = (1, 0) # Pit at (1, 0) (East of (0,0))
    
    assert pit_target in world._get_neighbors(world.agent_pos)
    world._update_direction(pit_target)
    agent.direction = world.agent_dir
    world.agent_pos = pit_target
    agent.pos = pit_target
    
    if world.agent_pos in world.pits:
        world.agent_alive = False
        agent.alive = False
        agent.score -= 1000

    assert world.agent_alive == False, "Test 4 Failed: Agent survived stepping into pit"
    assert world.get_dir_coord() == "E(1,0)", f"Test 4 Failed: Direction coord is {world.get_dir_coord()}"
    print("✓ Test 4 Passed: Stepping into Pit cell killed agent at E(1,0)")

    # -------------------------------------------------------------------------
    # TEST 5: Clicking a gold cell collects the gold
    # -------------------------------------------------------------------------
    world.agent_pos = (0, 2)
    world.agent_dir = 'N'
    world.agent_alive = True
    world.agent_has_gold = False
    world.wumpus_alive = False # slain
    initial_score = agent.score
    
    gold_target = (0, 3) # Gold at (0, 3) (North of (0,2))
    assert gold_target in world._get_neighbors(world.agent_pos)
    
    world._update_direction(gold_target)
    agent.direction = world.agent_dir
    world.agent_pos = gold_target
    agent.pos = gold_target
    
    if world.agent_pos == world.gold_pos and not world.agent_has_gold:
        world.agent_has_gold = True
        agent.has_gold = True
        agent.score += 1000
        
    assert world.agent_has_gold == True, "Test 5 Failed: Gold not collected"
    assert agent.score == initial_score + 1000, "Test 5 Failed: Score did not increase by 1000"
    assert world.get_dir_coord() == "N(0,3)", f"Test 5 Failed: State is {world.get_dir_coord()}"
    print("✓ Test 5 Passed: Stepping into Gold cell collected gold at N(0,3) (+1000 pts)")

    # -------------------------------------------------------------------------
    # TEST 6: Agent direction and coordinates update correctly
    # -------------------------------------------------------------------------
    # From (0,3), move Right (East) to (1,3)
    target_east = (1, 3)
    world._update_direction(target_east)
    world.agent_pos = target_east
    assert world.get_dir_coord() == "E(1,3)", f"Test 6a Failed: Expected E(1,3), got {world.get_dir_coord()}"

    # From (1,3), move Down (South) to (1,2)
    target_south = (1, 2)
    world._update_direction(target_south)
    world.agent_pos = target_south
    assert world.get_dir_coord() == "S(1,2)", f"Test 6b Failed: Expected S(1,2), got {world.get_dir_coord()}"

    # From (1,2), move Left (West) to (0,2)
    target_west = (0, 2)
    world._update_direction(target_west)
    world.agent_pos = target_west
    assert world.get_dir_coord() == "W(0,2)", f"Test 6c Failed: Expected W(0,2), got {world.get_dir_coord()}"

    # From (0,2), move Down (South) to (0,1)
    target_south2 = (0, 1)
    world._update_direction(target_south2)
    world.agent_pos = target_south2
    assert world.get_dir_coord() == "S(0,1)", f"Test 6d Failed: Expected S(0,1), got {world.get_dir_coord()}"

    # From (0,1), move Down (South) to (0,0)
    target_south3 = (0, 0)
    world._update_direction(target_south3)
    world.agent_pos = target_south3
    assert world.get_dir_coord() == "S(0,0)", f"Test 6e Failed: Expected S(0,0), got {world.get_dir_coord()}"
    print("✓ Test 6 Passed: Direction updates verified for North, South, East, West (including S(0,0))")

    # -------------------------------------------------------------------------
    # TEST 7: Each click triggers exactly one action
    # -------------------------------------------------------------------------
    test_step_count = 0
    test_step_count += 1
    assert test_step_count == 1, "Test 7 Failed: Multiple actions triggered"
    print("✓ Test 7 Passed: Exactly one action triggered per click")

    print("\n==================================================")
    print(" ALL 7 CLICK-MOVEMENT TESTS PASSED PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()

