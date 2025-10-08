

# Simple Snake Game 🐍

A minimalist snake game written in Python using `asyncio`.

---

## Author

* **userAnonymous**
* GitHub: [ramimK0bir](https://github.com/ramimk0bir)

---

## Installation

Install the game easily using pip:

```bash
pip install python-snake-game
```

---

## Usage



You can import and run the game from Python code:

```python
import python_snake_game as snake_game

snake_game.play()

```

---

## Parameters of `play` function

| Parameter              | Type            | Default | Description                                                   |
| -----------------------| --------------- | ------- | --------------------------------------------------------------|
| `speed`                | int             | 2       | Controls the game speed (higher = faster)(1-10).              |
| `snake_food_emoji`     | str             | "🍎"    | Emoji to represent the food on the grid.                      |
| `grid_size`            | tuple (int,int) | (15,12) | Size of the game grid as (width, height).                     |
| `background_emoji`     | str             | "🟫"    | Emoji or character to represent the grid blocks.              |
| `invisible_wall`       | bool            | False   | Allow snake to pass through walls and appear on the other side. |
|And many more you can explore after using this |


---

## Controls

* **Arrow keys** to move the snake:

  * Up arrow: Move up
  * Down arrow: Move down
  * Left arrow: Move left
  * Right arrow: Move right
* **Space bar** to pause or resume the game.

---

## How to Play

* The snake moves continuously on the grid.
* Eat the food (represented by the food emoji) to grow longer and increase your score.
* Avoid hitting the walls or the snake's own body.
* The game ends if you collide with yourself or the grid edges.
* Your current score is displayed above the grid.

---

## Notes

* The game uses ANSI escape codes for terminal control (clear screen, colors).
* Works best on terminals supporting Unicode and ANSI colors.
* Keyboard input requires the `pynput` package (automatically handled if installed via pip).
* If running the game script directly, make sure `pynput` is installed: `pip install pynput`.

---



## Troubleshooting

* If the game does not respond to key presses, ensure your terminal supports `pynput` keyboard listening.
* On Windows, you may need to run the terminal with administrator privileges for keyboard capture.
* If `pynput` is not installed, install it via `pip install pynput`.

---

## License

This project is open source. Feel free to contribute or modify!

