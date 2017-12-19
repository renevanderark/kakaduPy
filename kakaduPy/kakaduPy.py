#! /usr/bin/env python
"""Minimalistic Python wrapper for Kakadu's kdu_ccompres tool
Requires python-xmp-toolkit. Note that python-xmp-toolkit is not available
for Windows, so metadata extraction won't work on Windows!
"""

import sys
import os
import uuid
import io
import glob
import subprocess as sub



# Path to kdu_compress binary
global kdu_compress
kdu_compress = "opj_compress"

# NOTE: path to kdu_compress must be part of LD_LIBRARY_PATH!
# To add it, use:
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/home/johan/kakadu/


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


def compressToJP2(fileIn, fileOut, parameters, extractMetadataFlag):
    """
    Compress image to JP2
    if extractMetadataFlag is True, metadata is extractede from fileIn,
    which is subsequently written to an XMP sidecar file and then
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


def convertDirectory(dirIn, patternIn, dirOut, params, extractMetadataFlag):
    """
    Convert all files with glob pattern patternIn in directory dirIn to JP2 in
    directory dirOut
    """

    dirIn = os.path.normpath(dirIn)
    dirOut = os.path.normpath(dirOut)

    imagesIn = glob.glob(os.path.join(dirIn,patternIn))

    for imageIn in imagesIn:
            # Construct name for output image
            imageInTail = os.path.split(imageIn)[1]
            baseNameIn = os.path.splitext(imageInTail)[0]
            imageNameOut = baseNameIn + ".jp2"
            imageOut = os.path.join(dirOut, imageNameOut)

            # Convert to JP2
            compressToJP2(imageIn, imageOut, params, extractMetadataFlag)


def main():

    # Directory with input images (TIFF)
    dirIn = "/home/rar010/KBHSS01000058055"
    # Glob pattern defines which files are processed
    patternIn = "*.*"

    # Output directory
    dirOut = "/home/rar010/research/jp2-out"

    # True/False flag that activates metadata extraction
    # Leave
    extractMetadataFlag = False

    # Parameters for lossy compression of  RGB image at 20:1 ratio
    params = ["-r", "5", "-t", "1024,1024", "-n", "6"]

    # Convert all files in directory
    convertDirectory(dirIn,
                     patternIn,
                     dirOut,
                     params,
                     extractMetadataFlag)


if __name__ == "__main__":
    main()
