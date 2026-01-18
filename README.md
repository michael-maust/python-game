# Space Invaders Game

A classic Space Invaders game built with Python and Pygame.

## Features

- **Enhanced Graphics:**
  - Detailed player spaceship with animated engine glow
  - Intricate enemy alien designs with animated glowing eyes
  - Particle explosion effects
  - Animated star field background
  - Enhanced bullet graphics with trail effects
  - Improved UI with life indicators

- **Audio Effects:**
  - Shooting sound effects
  - Explosion sound effects
  - Background music (toggle with M key)

- **Gameplay:**
  - Player-controlled spaceship at the bottom of the screen
  - Multiple rows of enemy aliens that move horizontally and downward
  - Shooting mechanics for both player and enemies
  - Collision detection
  - Score system
  - Lives system (3 lives)
  - Game over and win conditions
  - Restart functionality

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

Or if you have pip available:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python3 space_invaders.py
```

Or if you have python available:
```bash
python space_invaders.py
```

2. Controls:
   - **Left Arrow**: Move player left
   - **Right Arrow**: Move player right
   - **Space**: Shoot bullets
   - **R**: Restart game (when game over)
   - **M**: Toggle background music

## Game Rules

- Destroy all enemies to win
- Avoid enemy bullets and don't let enemies reach you
- You have 3 lives
- Each enemy destroyed gives you 10 points

## Game Mechanics

- Enemies move horizontally and move down when they hit the screen edges
- Enemies randomly shoot bullets at the player
- Player can shoot unlimited bullets
- Collision detection handles bullet-enemy and bullet-player interactions

Enjoy the game!

