#! /usr/bin/env python

from kakaduPy.kakaduPy import compressToJP2
from jpylyzer import jpylyzer
from hsSRU.hsSRU import getPPN
import errno
import sys
import os
import re

batch_dir = sys.argv[1]
out_dir = sys.argv[2]
tiffs = os.listdir(batch_dir)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

ppns = set([])
for tiff in tiffs:
    ppn = getPPN(tiff)
    ppns.add(ppn)
    mkdir_p(os.path.join(out_dir, ppn))
    print("Compressing: " + tiff)
    compressToJP2(os.path.join(batch_dir, tiff), os.path.join(out_dir, ppn) + "/" + os.path.splitext(tiff)[0] + ".jp2", ["-r", "5", "-t", "1024,1024", "-n", "6"], False)

for ppn in ppns:
    jp2s = os.listdir(os.path.join(out_dir, ppn))
    for jp2 in jp2s:
        result = jpylyzer.checkOneFile(os.path.join(out_dir, ppn) + "/" + jp2)
        height = result.findtext('./properties/jp2HeaderBox/imageHeaderBox/height')
        width = result.findtext('./properties/jp2HeaderBox/imageHeaderBox/width')
