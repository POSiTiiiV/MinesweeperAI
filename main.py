import sys
import argparse
from minesweeper.game import MinesweeperGame
from minesweeper.ai.solver import MinesweeperSolver


def parse_arguments():
    """Parse command line arguments for game mode selection."""
    parser = argparse.ArgumentParser(description="Minesweeper Game with AI")
    parser.add_argument('--mode', type=str, choices=['human', 'ai', 'random'],
                        default='human', help='Game mode: human, ai, or random')
    return parser.parse_args()


def main():
    """Main entry point for the game."""
    args = parse_arguments()
    
    # Initialize the game
    game = MinesweeperGame()
    
    # Choose mode based on argument
    if args.mode == 'human':
        print("Starting game in human mode. Good luck!")
        game.run()
    else:
        # Start the game without running the full game loop
        game.setup()
        
        # Create solver with game API
        solver = MinesweeperSolver(game.api)
        
        if args.mode == 'ai':
            print("Starting game with AI solver...")
            # Use the intelligent solver
            solver.start()
        elif args.mode == 'random':
            print("Starting game with random solver...")
            # Use the random clicking solver
            solver.click_random_tiles_to_vicotry()


if __name__ == "__main__":
    main()