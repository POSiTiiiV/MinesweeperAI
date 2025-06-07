# MinesweeperAI

A Python implementation of the classic Minesweeper game with an AI solver that uses logical deduction to play automatically.

![Minesweeper Game](minesweeper/assets/face_happy.png)

## Features

- Full Minesweeper game implementation with customizable board size
- Classic Windows-style UI with emoji faces and counters
- Multiple play modes: Human, AI solver, and Random clicker
- AI solver that uses logical deduction and priority-based decision making
- Clean architecture with separation of concerns between game logic and UI

## Requirements

- Python 3.9+
- pygame
- heapdict

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MinesweeperAI.git
cd MinesweeperAI
```

2. Install the required packages:
```bash
pip install pygame heapdict
```

## Usage

Run the game with one of the following modes:

```bash
# Play manually
python main.py --mode human

# Watch the AI solver play
python main.py --mode ai

# Watch random clicking strategy
python main.py --mode random
```

### Game Controls

- **Left Click**: Reveal a tile
- **Right Click**: Flag/unflag a tile
- **Shift + Left Click**: Chord (reveal all non-flagged neighbors of a satisfied numbered tile)
- **Click Emoji Face**: Restart the game

## Project Structure

- `main.py`: Entry point of the application
- `minesweeper/`
  - `game.py`: Main game class and constants
  - `grid.py`: Grid management and bomb placement logic
  - `tile.py`: Tile representation and neighbor connections
  - `api.py`: API for interacting with the game (used by both UI and AI)
  - `ai/`
    - `solver.py`: AI solver implementation
  - `assets/`: Game images and sprites

## How the AI Works

The AI solver uses a priority queue to process tiles based on their potential for making progress:

1. **Priority 0**: Satisfied tiles (where all bombs are flagged)
2. **Priority 1**: Satisfiable tiles (where all hidden neighbors must be bombs)
3. **Priority 2**: Tiles that require more information

The solver continuously:
1. Picks the highest priority tile from the queue
2. Flags bombs when identified with certainty
3. Reveals safe tiles when identified
4. Uses "chording" to efficiently reveal multiple tiles at once
5. Makes a random move when logical deduction is insufficient

## Customization

You can customize the game by modifying constants in `minesweeper/game.py`:

```python
ROWS, COLS = 16, 16    # Grid dimensions
N_BOMBS = 40           # Number of bombs
```

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the classic Windows Minesweeper game
- Built with pygame for rendering
