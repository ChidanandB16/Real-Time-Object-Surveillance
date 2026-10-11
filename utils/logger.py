import datetime
import os

log_file = None


def initialize_logger():

    global log_file

    os.makedirs("logs", exist_ok=True)

    if log_file is not None and not log_file.closed:
        log_file.close()

    log_file = open(
        "logs/tracking_log.txt",
        "w",
        encoding="utf-8"
    )


def log(message):

    global log_file

    if log_file is None or log_file.closed:
        initialize_logger()

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    line = f"[{timestamp}] {message}"

    print(line)

    log_file.write(line + "\n")

    log_file.flush()


def close_logger():

    global log_file

    if log_file is not None and not log_file.closed:
        log_file.close()