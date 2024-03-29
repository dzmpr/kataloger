import asyncio
import sys

from kataloger.cli import cli
from kataloger.exceptions.kataloger_exception import KatalogerException


def main() -> int:
    try:
        return asyncio.run(cli.run())
    except KatalogerException as error:
        print(error.message, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Update search terminated.")
        return 128 + 2  # http://www.tldp.org/LDP/abs/html/exitcodes.html


if __name__ == "__main__":
    sys.exit(main())
