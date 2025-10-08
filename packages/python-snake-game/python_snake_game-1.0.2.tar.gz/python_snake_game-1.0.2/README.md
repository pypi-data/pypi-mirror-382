

# Simple Snake Game 🐍

A minimalist snake game written in Python using `asyncio`.

---

## Author

* **userAnonymous**
* GitHub: [ramimK0bir](https://github.com/ramimk0bir)

---

## Installation 

Install the game easily using `pip`:

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



## 🚀 Command Line Interface – `python -m python_snake_game`

Run the snake game directly from the command line using the module:

```bash
python -m python_snake_game [options]
```

---

### 📥 Available CLI Arguments

| Argument           | Type            | Default | Description                                                             |
| ------------------ | --------------- | ------- | ----------------------------------------------------------------------- |
| `--speed`          | int (1–10)      | `2`     | Controls game speed. Higher = faster. If out of range, defaults to `2`. |
| `--grid_size`      | string (W,H)    | `15,12` | Grid size as `width,height`. Must be two positive integers.             |
| `--invisible_wall` | flag (no value) | `False` | If set, snake wraps around screen edges instead of dying at the wall.   |

---

### 🧪 Examples

```bash
# Run with default settings
python -m python_snake_game

# Custom speed and grid size
python -m python_snake_game --speed 5 --grid_size 20,15

# Enable invisible walls (screen wrapping)
python -m python_snake_game --invisible_wall

# All options together
python -m python_snake_game --speed 8 --grid_size 30,20 --invisible_wall
```


## Controls

* **Arrow keys** to move the snake:

  * Up arrow: Move up(w)
  * Down arrow: Move down(s)
  * Left arrow: Move left(a)
  * Right arrow: Move right(d)
* **Space bar** to pause or resume the game.

---

## How to Play

* The snake moves continuously on the grid.
* Eat the food (represented by the food emoji) to grow longer and increase your score.
* Avoid hitting the walls or the snake's own body.
* The game ends if you collide with yourself or the grid edges.
* Use invisible_wall=True to pass through grid edges.
* Your current score is displayed above the grid.

---

## Notes

* The game uses ANSI escape codes for terminal control (clear screen, colors).
* Works best on terminals supporting Unicode and ANSI colors.

---




## License

This project is open source. Feel free to contribute or modify!

