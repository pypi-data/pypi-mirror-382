import argparse
import python_snake_game as sanke_game
def check_speed(value):
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Speed must be an integer, got '{value}'")
    if 1 <= ivalue <= 10:
        return ivalue
    else:
        # If out of range, return default 2
        print("Warning: speed out of range (1-10), using default 2")
        return 2

def check_grid_size(value):
    try:
        parts = value.split(',')
        if len(parts) != 2:
            raise argparse.ArgumentTypeError("Grid size must be two integers separated by a comma")
        x, y = map(int, parts)
        if x <= 0 or y <= 0:
            raise argparse.ArgumentTypeError("Grid size must be positive integers")
        return (x, y)
    except ValueError:
        raise argparse.ArgumentTypeError("Grid size must be two integers separated by a comma")

def main():
    parser = argparse.ArgumentParser(description="CLI with speed, invisible_wall, and grid_size args")

    parser.add_argument(
        '--speed',
        type=check_speed,
        default=2,
        help='Speed value (int) between 1 and 10, default=2'
    )

    parser.add_argument(
        '--invisible_wall',
        action='store_true',
        help='Boolean flag for invisible wall'
    )

    parser.add_argument(
        '--grid_size',
        type=check_grid_size,
        default=(15,12) ,

        help='Grid size as two positive integers separated by a comma, e.g. 5,10'
    )

    args = parser.parse_args()

    print(f"Speed: {args.speed}")
    print(f"Invisible wall: {args.invisible_wall}")
    print(f"Grid size: {args.grid_size}")
    sanke_game.play(speed=args.speed, invisible_wall=args.invisible_wall, grid_size=args.grid_size)
if __name__ == "__main__":
    main()
