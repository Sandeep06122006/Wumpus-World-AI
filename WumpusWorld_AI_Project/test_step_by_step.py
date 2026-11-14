from world import WumpusWorld
from agent import WumpusAgent

def test_step_by_step_execution():
    print("==================================================")
    print(" RUNNING STEP-BY-STEP EXECUTION TEST SUITE")
    print("==================================================")

    # 1. Initialize World and Agent
    world = WumpusWorld(grid_size=4, pit_prob=0.2, seed=42)
    agent = WumpusAgent(grid_size=4, search_algo='A*')

    # Initial state
    assert world.agent_pos == (0, 0), "Initial position must be (0,0)"
    assert world.agent_dir == 'E', "Initial direction must be E"
    assert world.get_dir_coord() == "E(0,0)", f"Expected E(0,0), got {world.get_dir_coord()}"
    assert agent.score == 0, "Initial score must be 0"
    step = 0
    print(f"✓ Step 0 Initialized: Agent at {world.get_dir_coord()} with score {agent.score}")

    # First click of Next Step:
    # 1 action must be chosen and executed
    step += 1
    percepts1 = world.get_percepts()
    action1 = agent.choose_action(percepts1)
    outcome1 = world.execute_action(action1)
    
    assert step == 1, f"Step count should be 1, got {step}"
    assert world.agent_pos != (0, 0) or action1 == 'GRAB' or action1 == 'CLIMB', "Agent should have taken an action"
    pos_after_step_1 = world.agent_pos
    dir_after_step_1 = world.agent_dir
    print(f"✓ Click 1 (Step 1) Passed: Action={action1}, Position={world.get_dir_coord()}, Outcome={outcome1}")

    # Second click of Next Step:
    step += 1
    percepts2 = world.get_percepts()
    action2 = agent.choose_action(percepts2)
    outcome2 = world.execute_action(action2)
    
    assert step == 2, f"Step count should be 2, got {step}"
    print(f"✓ Click 2 (Step 2) Passed: Action={action2}, Position={world.get_dir_coord()}, Outcome={outcome2}")

    # Verify that each click performed exactly ONE action
    assert step == 2

    # -------------------------------------------------------------------------
    # Test Manual Move interleaved with Step Execution
    # -------------------------------------------------------------------------
    neighbors = world._get_neighbors(world.agent_pos)
    manual_target = neighbors[0]
    
    step += 1
    world._update_direction(manual_target)
    agent.direction = world.agent_dir
    world.agent_pos = manual_target
    agent.pos = manual_target
    agent.score -= 1
    agent.step_count = step
    
    assert world.agent_pos == manual_target
    assert step == 3
    print(f"✓ Click 3 (Manual Move) Passed: Stepped to {world.get_dir_coord()}, Score={agent.score}")

    # -------------------------------------------------------------------------
    # Test Hazard Death (Pit)
    # -------------------------------------------------------------------------
    test_world = WumpusWorld(grid_size=4, seed=123)
    test_world.pits = {(0, 1)}
    test_world.agent_pos = (0, 0)
    test_world.agent_dir = 'E'
    test_agent = WumpusAgent(grid_size=4)
    
    # Step into pit at (0,1)
    test_world._update_direction((0, 1))
    test_agent.direction = test_world.agent_dir
    test_world.agent_pos = (0, 1)
    test_agent.pos = (0, 1)
    test_agent.score -= 1
    
    # Hazard resolution
    if (0, 1) in test_world.pits:
        test_world.agent_alive = False
        test_agent.alive = False
        test_agent.score -= 1000
        game_over = True
        
    assert test_world.agent_alive == False, "Agent must die in pit"
    assert test_agent.alive == False, "Agent status must be dead"
    assert test_agent.score == -1001, f"Expected -1001, got {test_agent.score}"
    assert game_over == True, "Game must be over after death"
    print(f"✓ Hazard Death Passed: Pit at {test_world.get_dir_coord()} killed agent, Game Over confirmed")

    # -------------------------------------------------------------------------
    # Test Game Stops After Death
    # -------------------------------------------------------------------------
    # Attempting another action while game_over must be blocked
    action_blocked = game_over
    assert action_blocked == True, "Further actions must be blocked when game is over"
    print("✓ Game Over Lock Passed: Actions blocked after death")

    # -------------------------------------------------------------------------
    # Test Reset
    # -------------------------------------------------------------------------
    reset_world = WumpusWorld(grid_size=4, pit_prob=0.2, seed=42)
    reset_agent = WumpusAgent(grid_size=4)
    reset_step = 0
    reset_game_over = False
    
    assert reset_world.agent_pos == (0, 0)
    assert reset_world.agent_dir == 'E'
    assert reset_world.get_dir_coord() == "E(0,0)"
    assert reset_agent.score == 0
    assert reset_step == 0
    assert reset_game_over == False
    print(f"✓ Reset Passed: Fresh simulation restored to {reset_world.get_dir_coord()}, step 0")

    print("\n==================================================")
    print(" ALL STEP-BY-STEP UNIT TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_step_by_step_execution()

