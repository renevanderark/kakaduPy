#! /usr/bin/env python
"""Functions to convert TIFF to JP2"""

import sys
import os
import uuid
import io
import subprocess as sub
import csv


# Path to kdu_compress binary
global kdu_compress
kdu_compress = "/home/johan/kakadu/kdu_compress"

# NOTE: path to kdu_compress must be part of LD_LIBRARY_PATH!
# To add it, use:
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/home/johan/kakadu/

# Path to ExifTool binary (only needed if extractMetadataFlag is set to True)
global exiftool
exiftool = "/usr/bin/exiftool"


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

def extractMetadata(fileIn):
    """Extract metadata to XMP format (written to stdout)"""

    # Add command-line arguments
    args = [exiftool]
    args.append(fileIn)
    args.append("-o")
    args.append("-.xmp")

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


def compressToJP2(fileIn, fileOut, parameters, extractMetadataFlag):
    """Compress image to JP2
    if extractMetadataFlag is True, Exiftool is used to extract metadata from
    fileIn in, which is subsequently written to an XMP sidecar file and then
    embedded in an XML box (as per KB specs). However, by default Kakadu
    already does the metadata extraction natively, but it uses the uuid box!
    """

    # Add command-line arguments
    args = [kdu_compress]
    args.append("-i")
    args.append(fileIn)
    args.append("-o")
    args.append(fileOut)

    for p in parameters:
        args.append(p)

    if extractMetadataFlag:
        # Extract metadata from fileIn to XMP
        resultExiftool = extractMetadata(fileIn)

        # XMP data in stdout
        xmpData = resultExiftool["stdout"]

        # Prepend xmpData with string "xml "
        xmpData = "xml "+ xmpData

        # Write xmpData to temporary file
        xmpFNameTemp = str(uuid.uuid1())
        with io.open(xmpFNameTemp, "w", encoding="utf-8") as fXMP:
            fXMP.write(xmpData)
        fXMP.close()

        args.append("-jp2_box")
        args.append(xmpFNameTemp)
    
    # Command line as string (used for logging purposes only)
    cmdStr = " ".join(args)

    status, out, err = launchSubProcess(args)

    # Main results to dictionary
    dictOut = {}
    dictOut["cmdStr"] = cmdStr
    dictOut["status"] = status
    dictOut["stdout"] = out
    dictOut["stderr"] = err

    if extractMetadataFlag:
        os.remove(xmpFNameTemp)

    return dictOut

def convertDirectory(dirIn, ExtIn, dirOut):
    """Convert all files with extension ExtIn in directory dirIn to JP2 in directory dirOut"""
    pass
    

def main():

    # Input
    imageIn = "/home/johan/handschriften/tiff/KBHSS01000058055/424C1-02-02_0208.tif"
    imageOut = "/home/johan/test/test.jp2"
    extractMetadataFlag = False

    # Parameters for lossy compression of  RGB image at 20:1 ratio
    # TODO: add XMP metadata, codestream comment
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
              "Cmodes=SEGMARK",
              "-com",
              "KB_ACCESS_LOSSY_01/01/2015"]

    resultKakadu = compressToJP2(imageIn, imageOut, params, extractMetadataFlag)


if __name__ == "__main__":
    main()
