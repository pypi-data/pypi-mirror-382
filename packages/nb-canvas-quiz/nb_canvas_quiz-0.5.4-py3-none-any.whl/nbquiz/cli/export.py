"""
Export a test bank to canvas.
"""

import logging

from nbquiz.canvas.export import CanvasExport
from nbquiz.testbank import bank

logging.basicConfig(level=logging.INFO)


def add_args(parser):
    parser.add_argument(
        "testyaml", help="A YAML file containing a description of a test."
    )


def main(args):
    bank.load()
    logging.info(f"Loading test file: {args.testyaml}")
    c = CanvasExport()
    c.load_file(args.testyaml)
    c.write()
