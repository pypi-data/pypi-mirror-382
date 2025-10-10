import asyncio

from analysis_root import main


def main_cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    main_cli()
