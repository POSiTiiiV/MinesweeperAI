import sys
import argparse
from minesweeper.game import MinesweeperGame
from minesweeper.ai.solver import MinesweeperSolver


def main():
    parser = argparse.ArgumentParser(description='Run Minesweeper game')
    parser.add_argument('--mode', choices=['human', 'ai'], 
                       default='human', help='Game mode')
    parser.add_argument('--mobile', action='store_true', 
                       help='Run in mobile mode')
    
    args = parser.parse_args()
    
    # Add mobile flag to sys.argv for the game to detect
    if args.mobile:
        sys.argv.append('--mobile')
    
    # Create and run the game
    game = MinesweeperGame()
    
    if args.mode == 'human':
        print("Starting game in human mode. Good luck!")
        game.run()
    elif args.mode == 'ai':
        print("Starting game with AI solver...")
        # Start the game without running the full game loop
        game.setup()
        
        # Create solver with game API
        solver = MinesweeperSolver(game.api)
        solver.start()

if __name__ == "__main__":
    main()