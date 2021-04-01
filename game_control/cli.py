"""Console script for game_control."""
import argparse
import signal
import sys
from pathlib import Path
from pydoc import locate


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def grab(args, kwargs):
    import cv2

    from game_control.limiter import Limiter

    game_class = locate(args.game_class)

    game = game_class(**kwargs)
    print("Started grabbing!")
    limiter = Limiter(fps=args.fps)
    while True:
        limiter.start()
        frame = game.grab_frame()
        if frame:
            output_filename = f"{frame.timestamp:%Y%m%d_%H%M%S_%f}.png"
            output_filepath = args.output_dir / output_filename
            print(output_filepath)
            cv2.imwrite(str(output_filepath), frame.img)
        limiter.stop_and_delay()


def other(args, kwargs):
    print("Other command")


def main():
    """Console script for game_control."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

    # GRAB
    parser_grab = subparsers.add_parser(
        "grab",
        help="Grab frames of a Game.",
        description="Remaining unknown arguments are passed to Game constructor. \
            Add e.g. ldplayer_executable_filepath=path_to_dnplayer.exe to pass an executable.",
    )
    parser_grab.add_argument("fps", type=float, help="Framerate to grab frames with.")
    parser_grab.add_argument(
        "output_dir", type=Path, help="Directory to write grabbed frames to."
    )
    parser_grab.add_argument(
        "game_class",
        type=str,
        help="Full game class to grab frames of (e.g. package.module.GameClass)",
    )
    parser_grab.set_defaults(func=grab)

    # OTHER
    parser_other = subparsers.add_parser("other")
    parser_other.set_defaults(func=other)

    args, remaining_args_list = parser.parse_known_args()
    remaining_args = {kv.split("=")[0]: kv.split("=")[1] for kv in remaining_args_list}
    args.func(args, remaining_args)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
