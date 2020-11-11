import itertools
import json
import sched
import socket
import time
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from typing import Any, Callable, List, Tuple, Generator, Iterator

import numpy as np
import pandas as pd
from humanfriendly import format_timespan

from shared import seconds_to_ns


def every(
    interval: float, duration: float, timing_fn: Callable[[], float]
) -> Iterator[None]:
    """Lets you run a loop every 'interval' time units, for a total duration
       'duration', all timed using a timing function 'timing_fn'

    Args:
        interval (float): time interval
        duration (float): total duration
        timing_fn (Callable[[], float]): function that returns current time
    """
    start_time = timing_fn()
    last_time = start_time
    yield

    while True:
        current_time = timing_fn()
        if current_time - last_time >= interval:
            yield
            last_time = current_time

        if current_time - start_time > duration:
            break


def generate_mock_data(
    n: float,
    xlim: Tuple[float, float] = [500, 1000],
    ylim: Tuple[float, float] = [400, 700],
) -> List[dict]:
    return pd.DataFrame(
        {"x": np.random.randint(*xlim, size=n), "y": np.random.randint(*ylim, size=n)},
    ).to_dict("records")


def send_end_session(socket: socket.socket):
    socket.sendall(bytes("session_end", "utf-8"))


def send_start_session(socket: socket.socket, a: int, b: int, path: str):
    socket.sendall(bytes(f"session_start,{a},{b},{path}\n", "utf-8",))


def send_gaze_data(socket: socket.socket, t: int, x: any, y: any):
    socket.sendall(bytes(f"gaze,{t},{x},{y}\n", "utf-8"))


def start_mock_server(
    frequency: float,
    duration: float,
    data: List[dict],
    timing_fn: Callable[[], float],
    port: int,
    wait=False,
    delay=1,
    data_path="./",
):
    interval = 1 / frequency

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen()
        print("- Server listening")
        conn, _ = s.accept()
        entries_sent = 0

        print("-- plugin connected  ")

        print(f"--- Starting session ")
        send_start_session(
            conn, int(time.time_ns() / 100), time.time() * 1000, data_path
        )
        print(f"--- Session started. Waiting {delay}s ")
        time.sleep(delay)

        print(f"---- Sending gazes @{frequency}hz ({interval} gazes / second) ")
        # run experiment
        for entry, _ in zip(
            itertools.cycle(data), every(interval, duration, timing_fn)
        ):
            send_gaze_data(conn, int(time.time() * 1000), **entry)
            entries_sent += 1

        print(f"--- Ending session. {entries_sent} entries sent. ")
        # send session end message
        send_end_session(conn)
        print()


def parse_time(time_str: str):
    try:
        return int(time_str)
    except ValueError:
        assert time_str.endswith("m")
        return int(time_str[:-1]) * 60


def get_cmd_args() -> Namespace:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--freq", "-f", help="Data sending frequency, in Hertz", default=60, type=int
    )
    parser.add_argument(
        "--duration",
        help="Duration for which to send the data, in seconds or minutes. Eg: 10 seconds -> 10, 10m -> 10 minutes ",
        default="60",
    )
    parser.add_argument(
        "--mock-session-path",
        help="Path to the mock directory sent to Atom iTrace",
        default="./",
    )

    parser.add_argument(
        "--data",
        help="path to json containing the data to send. If not provided, the script will generate new data. Data format: [{'x': float, 'y': float}]. The script will iterate cyclically over the array.",
    )
    parser.add_argument(
        "--mock-size", help="size of the mock data", default=500, type=int
    )
    parser.add_argument(
        "--save",
        help="If data is not provided, setting --save will save the generated mock data",
        action="store_true",
    )

    parser.add_argument("--port", type=int, help="Port to use for socket", default=8008)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_cmd_args()

    mock_data = None
    should_save = False
    if args.data:
        with open(args.data) as f:
            print(f"Loading mock data from {args.data}")
            mock_data = json.load(f)
            assert isinstance(mock_data, list), "Mock data must be a json"
            assert len(mock_data) > 0, "Mock data must have a length of atleast 1"
            assert (
                "x" in mock_data[0] and "y" in mock_data[0]
            ), "Mock data must be an array of {x, y}"
    else:
        mock_data = generate_mock_data(args.mock_size)
        should_save = True

    start_mock_server(
        frequency=args.freq,
        duration=parse_time(args.duration),
        data=mock_data,
        timing_fn=time.perf_counter,
        port=args.port,
        data_path=args.mock_session_path,
    )

    if should_save:
        with open("mock-data.json", "w") as f:
            json.dump(mock_data, f)
