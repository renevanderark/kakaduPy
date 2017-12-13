#! /usr/bin/env python
"""Functions to convert TIFF to JP2"""

import sys
import os
import subprocess as sub
import csv


# Path to kdu_compress binary
global kdu_compress
kdu_compress = "/home/johan/kakadu/kdu_compress"

# NOTE: path to kdu_compress must be part of LD_LIBRARY_PATH!
# To add it, use:
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/home/johan/kakadu/

# Path to ExifTool binary
global exiftool
exiftool = "/usr/bin/exiftool"


def printWarning(msg):
    """Print warning to stderr"""
    msgString = ("User warning: " + msg + "\n")
    sys.stderr.write(msgString)


def errorExit(msg):
    """Print warning to stderr and exit"""
    msgString = ("Error: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()


def launchSubProcess(args):
    """Launch subprocess and return exit code, stdout and stderr"""
    try:
        # Execute command line; stdout + stderr redirected to objects
        # 'output' and 'errors'.
        # Setting shell=True avoids console window poppong up with pythonw
        p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE, shell=False)
        output, errors = p.communicate()

        # Decode to UTF8
        outputAsString = output.decode('utf-8')
        errorsAsString = errors.decode('utf-8')

        exitStatus = p.returncode

    except Exception:
        # I don't even want to to start thinking how one might end up here ...

        exitStatus = -99
        outputAsString = ""
        errorsAsString = ""

    return(exitStatus, outputAsString, errorsAsString)


def compressToJP2(fileIn, fileOut, parameters):
    """Compress image to JP2"""

    # Add command-line arguments
    args = [kdu_compress]
    args.append("-i")
    args.append(fileIn)
    args.append("-o")
    args.append(fileOut)

    for p in parameters:
        args.append(p)
    
    # Command line as string (used for logging purposes only)
    cmdStr = " ".join(args)

    status, out, err = launchSubProcess(args)

    # Main results to dictionary
    dictOut = {}
    dictOut["cmdStr"] = cmdStr
    dictOut["status"] = status
    dictOut["stdout"] = out
    dictOut["stderr"] = err

    return dictOut
    

def main():

    # Input
    imageIn = "/home/johan/handschriften/tiff/KBHSS01000058055/424C1-02-02_0208.tif"
    imageOut = "/home/johan/test/test.jp2"

    # Parameters for lossy compression of  RGB image at 20:1 ratio 
    params = ["Creversible=no",
              "Clevels=5",
              "Corder=RPCL",
              "Stiles={1024,1024}",
              "Cblk={64,64}",
              "Cprecincts={256,256},{256,256},{128,128}",
              "Clayers=8",
              "-rate",
              "1.2,0.6,0.3,0.15,0.075,0.0375,0.01875,0.009375",
              "Cuse_sop=yes",
              "Cuse_eph=yes",
              "Cmodes=SEGMARK"]

    resultKakadu = compressToJP2(imageIn, imageOut, params)
    print(resultKakadu)


if __name__ == "__main__":
    main()
