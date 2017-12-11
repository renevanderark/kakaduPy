#! /usr/bin/env python
"""Functions to convert TIFF to JP2"""

import sys
import os
import csv
from . import config
from . import exiftool
from . import kakadu

# Fix empty scriptName if called from Java/Jython
if len(scriptName) == 0:
    scriptName = 'kakaduPy'

__version__ = '0.1.0'

# Create parser
parser = argparse.ArgumentParser(
    description="Verify file size of ISO image and extract technical information")


def parseCommandLine():
    """Parse command line"""
    # Add arguments
    parser.add_argument('ISOImages',
                        action="store",
                        type=str,
                        help="input ISO image(s) (wildcards allowed)")
    parser.add_argument('--version', '-v',
                        action='version',
                        version=__version__)
    parser.add_argument('--offset', '-o',
                        type=int,
                        help="offset (in sectors) of ISO image on CD (analogous to \
                        -N option in cdinfo)",
                        action='store',
                        dest='sectorOffset',
                        default=0)

    # Parse arguments
    args = parser.parse_args()

    return args


def printWarning(msg):
    """Print warning to stderr"""
    msgString = ("User warning: " + msg + "\n")
    sys.stderr.write(msgString)


def errorExit(msg):
    """Print warning to stderr and exit"""
    msgString = ("Error: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()

def toJP2(imageIn, imageOut, parameters):
    jp2OutInfo = kakadu. 
    



def main():
    # Set encoding of the terminal to UTF-8
    if sys.version.startswith("2"):
        out = codecs.getwriter("UTF-8")(sys.stdout)
        err = codecs.getwriter("UTF-8")(sys.stderr)
    elif sys.version.startswith("3"):
        out = codecs.getwriter("UTF-8")(sys.stdout.buffer)
        err = codecs.getwriter("UTF-8")(sys.stderr.buffer)

    # Get input from command line
    #args = parseCommandLine()

    # Input
    imageIn = "/home/johan/handschriften/tiff/KBHSS01000058055/424C1-02-02_0208.tif"
    imageOut = "/home/johan/test/test.jp2"
    params = []


if __name__ == "__main__":
    main()
