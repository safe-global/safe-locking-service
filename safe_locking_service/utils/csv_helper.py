import csv
from typing import IO, Generator


def parse(
    stream: IO[str], skip_header: bool = True
) -> Generator[list[str], None, None]:
    """
    Reads a CSV stream (file-like object) and yields each row one at a time, optionally skipping the header.
    """
    reader = csv.reader(stream, delimiter=",", quotechar="|")
    # Skips the header
    if skip_header:
        next(reader, None)

    # Read and print each row
    for row in reader:
        yield row
