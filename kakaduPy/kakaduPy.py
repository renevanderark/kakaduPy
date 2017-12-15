#! /usr/bin/env python
"""Functions to convert TIFF to JP2"""

import sys
import os
import uuid
import io
import glob
import subprocess as sub
from libxmp import XMPFiles, consts


# Path to kdu_compress binary
global kdu_compress
kdu_compress = "/home/johan/kakadu/kdu_compress"

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

        xmpData = str(XMPFiles(file_path=fileIn).get_xmp())
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
            resultKakadu = compressToJP2(imageIn, imageOut, params, extractMetadataFlag)
    

def main():

    # Directory with input images (TIFF)
    dirIn = "/home/johan/handschriften/tiff/KBHSS01000058055"
    # Glob pattern defines which files are processed    
    patternIn = "*.*"

    # Output directory
    dirOut = "/home/johan/test"

    # True/False flag that activates metadata extraction
    extractMetadataFlag = False

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
              "Cmodes=SEGMARK",
              "-com",
              "KB_ACCESS_LOSSY_01/01/2015"]

    # Convert all files in directory    
    convertDirectory(dirIn,
                     patternIn,
                     dirOut,
                     params,
                     extractMetadataFlag)


if __name__ == "__main__":
    main()
