# Tetris Game

A classic Tetris game built with Python and Pygame, enhanced with modern features.

## Features

-   Classic Tetris gameplay with scoring, levels, and progressive difficulty
-   **Progressive Speed:** Speed increases both with time and level for maximum challenge
-   **Game Timer:** Track your session duration in real-time
-   Start Menu, Pause, and Game Over screens
-   **Hold Piece:** Press `C` to hold a piece for later use.
-   **High Score:** Your high score is saved automatically.
-   **Sound Effects & Music:** Engaging audio feedback.
-   All 7 Tetrominoes with unique colors
-   Next piece preview
-   Clean and modular code structure

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Make sure you have Python 3.10+ installed.
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Optional) Add Sounds:**
    Place your sound files (`.wav` or `.ogg`) in the `assets/sounds/` directory. The game will look for:
    - `clear.wav`
    - `drop.wav`
    - `game_over.wav`
    - `rotate.wav`
    - `music.ogg` (for background music)

## How to Play

Run the game with the following command:
```bash
python main.py
```

### Controls

-   **Left/Right Arrow:** Move piece
-   **Down Arrow:** Soft drop
-   **Up Arrow:** Rotate piece
-   **Spacebar:** Hard drop
-   **C:** Hold piece
-   **P / ESC:** Pause game
-   **Enter:** Select in menus
-   **M:** Return to menu from Game Over screen
-   **Q:** Quit from menu

Enjoy the game! 