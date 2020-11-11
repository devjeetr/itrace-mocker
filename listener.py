import socket
import time
from argparse import ArgumentParser

from humanfriendly import format_timespan

from shared import ns_to_seconds


def receive(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect(("127.0.0.1", port))
        n_entries = 0

        start_time = None
        end_time = None

        # ignore START_SESSION MESSAGE
        s.recv(1024)
        while True:
            data = s.recv(1024)
            if not start_time:
                start_time = time.time_ns()

            if data:
                n_entries += 1
            else:
                end_time = time.time_ns()
                break

    # end session token
    n_entries -= 1
    dt = ns_to_seconds(end_time - start_time)

    throughput = n_entries / ns_to_seconds(end_time - start_time)
    print(f"Received {n_entries} entries in {format_timespan(dt)}")
    print(f"Throughput: {round(throughput)}Hz")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--port", type=int, help="Port to use for socket", default="8008"
    )

    args = parser.parse_args()

    receive(args.port)

