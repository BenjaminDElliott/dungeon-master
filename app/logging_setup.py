"""Logging configuration for the Dungeon Master app."""

import logging
import sys


def setup_logging(level: str = "DEBUG") -> None:
    """Configure root logger with structured output to stderr.

    In production, this is where you would wire up a JSON formatter
    and send to a log aggregator.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.addHandler(handler)
