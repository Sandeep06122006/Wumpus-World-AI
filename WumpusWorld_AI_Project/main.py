import sys
import time
from world import WumpusWorld
from agent import WumpusAgent

def print_grid(world, agent, reveal_all=False):
    """
    Renders the 4x4 Wumpus World in clean ASCII text.
    (0,0) is at the bottom-left corner.
    """
    grid_size = world.grid_size
    print("\n" + "=" * 33)
    
    for y in range(grid_size - 1, -1, -1):
        row_str = f"Row {y} |"
        for x in range(grid_size):
            cell = (x, y)
            symbols = []
            
            # Agent representation
            if cell == world.agent_pos:
                symbols.append(world.agent_dir) # N, S, E, W
                
            # Hazards and Items (Revealed if visited or if reveal_all is True)
            if reveal_all or cell in agent.kb.visited:
                if cell in world.pits:
                    symbols.append("P")
                if cell == world.wumpus_pos:
                    symbols.append("W" if world.wumpus_alive else "w")
                if cell == world.gold_pos and not world.agent_has_gold:
                    symbols.append("G")
            elif cell in agent.kb.known_safe:
                symbols.append("S") # Deduced Safe
            else:
                symbols.append("?") # Unexplored
                
            cell_repr = "".join(symbols).center(6)
            row_str += f"[{cell_repr}]"
        print(row_str)
        
    print("      " + " ".join([f" Col {x}  " for x in range(grid_size)]))
    print("=" * 33)
    print("Legend: A=Agent | P=Pit | W=Wumpus | w=Dead Wumpus | G=Gold | S=Safe | ?=Unknown\n")

def run_simulation(seed=42, search_algo='A*', max_steps=40, delay=0.5):
    """Runs a full console simulation of the Wumpus World AI project."""
    print("=" * 60)
    print("   WUMPUS WORLD AI AGENT (KNOWLEDGE-BASED & SEARCH)")
    print("=" * 60)
    print(f"Configuration: Seed={seed} | Search Algorithm={search_algo} | Max Steps={max_steps}\n")

    # Initialize World and Agent
    world = WumpusWorld(grid_size=4, pit_prob=0.2, seed=seed)
    agent = WumpusAgent(grid_size=4, search_algo=search_algo)

    print("Initial World Generated:")
    print(f"- Gold Location: {world.gold_pos}")
    print(f"- Wumpus Location: {world.wumpus_pos}")
    print(f"- Pit Locations: {list(world.pits)}")
    print_grid(world, agent, reveal_all=False)

    step = 0
    while step < max_steps and world.agent_alive and not world.agent_escaped:
        step += 1
        print(f"\n--- STEP {step} ---")
        
        # 1. Agent receives current percepts
        percepts = world.get_percepts()
        print(f"Agent State   : {world.get_dir_coord()} [Direction: {world.agent_dir}]")
        print(f"Agent Percepts at {world.get_dir_coord()}:")
        print(f"  [Stench: {percepts['stench']}] [Breeze: {percepts['breeze']}] [Glitter: {percepts['glitter']}]")

        # 2. Agent reasons and decides action
        action = agent.choose_action(percepts)
        
        # Show the most recent reasoning explanation from agent
        if agent.reasoning_trace:
            latest_thought = agent.reasoning_trace[-1]
            print(f"Agent Reasoning: {latest_thought}")

        print(f"Selected Action: {action}")

        # 3. Environment executes action
        action_outcome = world.execute_action(action)
        print(f"World Response : {action_outcome}")

        # Display updated world grid
        print_grid(world, agent, reveal_all=False)

        if delay > 0:
            time.sleep(delay)

    # 4. Final Game Evaluation
    print("\n" + "=" * 60)
    print("                     SIMULATION FINISHED")
    print("=" * 60)
    
    if world.agent_escaped and world.agent_has_gold:
        result_status = "VICTORY! The agent retrieved the gold and escaped safely."
    elif world.agent_escaped and not world.agent_has_gold:
        result_status = "SURVIVED: Agent safely retreated to (0,0) without gold."
    elif not world.agent_alive:
        result_status = "DEFEAT: The agent died in the dungeon."
    else:
        result_status = "TIMEOUT: Agent reached maximum allowed steps."

    print(f"Final Outcome      : {result_status}")
    print(f"Total Steps Taken  : {step}")
    print(f"Final Score        : {agent.score}")
    print(f"Gold Collected     : {world.agent_has_gold}")
    print(f"Wumpus Eliminated  : {not world.wumpus_alive}")
    print(f"Inference Operations: {agent.inference.operations_count} logical deductions")
    print(f"Total Safe Cells Known: {sorted(list(agent.kb.known_safe))}")
    print("=" * 60)

    # Print final revealed cave layout
    print("\nFinal Revealed Dungeon Map:")
    print_grid(world, agent, reveal_all=True)

if __name__ == '__main__':
    # Default execution: run A* search simulation
    run_simulation(seed=42, search_algo='A*', max_steps=35, delay=0.1)

