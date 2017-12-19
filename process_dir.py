#! /usr/bin/env python
# -*- coding: utf-8 -*-

from kakaduPy.kakaduPy import compressToJP2
from jpylyzer import jpylyzer
from hsSRU.hsSRU import getPPN
import urllib
import errno
import sys
import os
import re
import codecs
from time import sleep

# example invocation:
# ./process_dir.py ~/small-sample/ \
#                  /opt3/handschriften/jp2/by-ppn \
#                  http://imageviewer-iiif.kbresearch.nl/iiif-service \
#                 'http://kbresearch.nl/resolver-proxy/resolve.php?urn=manuscript:%s:iiif-manifest'
batch_dir = sys.argv[1]
out_dir = sys.argv[2]
tiffs = os.listdir(batch_dir)
iiif_service_location = sys.argv[3] #http://imageviewer-iiif.kbresearch.nl/iiif-service
resolver_pattern = sys.argv[4]

def readFile(fn):
    with open(fn, 'r') as myfile:
        return myfile.read().replace('\n', '')

manifest_template = readFile('manifest.json.tmpl')
canvas_template = readFile('canvas.json.tmpl')

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
    ppn, title = getPPN(tiff)
    ppns.add(ppn)
    mkdir_p(os.path.join(out_dir, ppn))
    print >> sys.stderr, "Compressing: " + tiff
    print >> sys.stderr, "-- ppn: " + ppn
    print >> sys.stderr, "-- title: " + title
    compressToJP2(os.path.join(batch_dir, tiff), os.path.join(out_dir, ppn) + "/" + os.path.splitext(tiff)[0] + ".jp2", ["-r", "5", "-t", "1024,1024", "-n", "6"], False)
    with codecs.open(os.path.join(out_dir, ppn) + "/title.txt", "w", "utf-8") as metadata_file:
        metadata_file.write(title)

print >> sys.stderr, "---generate manifests"

for ppn in ppns:
    jp2s = [x for x in sorted(os.listdir(os.path.join(out_dir, ppn))) if x.endswith(".jp2")]
    canvases = []
    for jp2 in jp2s:
        result = jpylyzer.checkOneFile(os.path.join(out_dir, ppn) + "/" + jp2)
        height = result.findtext('./properties/jp2HeaderBox/imageHeaderBox/height')
        width = result.findtext('./properties/jp2HeaderBox/imageHeaderBox/width')
        canvases.append(canvas_template
            .replace("%%IIIF-SERVICE-LOCATION%%", iiif_service_location)
            .replace("%%LABEL%%", re.sub('^.*_', '', jp2.replace(".jp2", "")))
            .replace("%%IDENTIFIER%%", ('file://' + os.path.join(out_dir, ppn) + "/" + jp2).replace("/", "%2F").replace(":", "%3A"))
            .replace("%%HEIGHT%%", height)
            .replace("%%WIDTH%%", width))
    with open(os.path.join(out_dir, ppn) + "/manifest.json", "w") as manifest_file:
        manifest_file.write(manifest_template
            .replace("%%TITLE%%", readFile(os.path.join(out_dir, ppn) + "/title.txt"))
            .replace("%%MANIFEST_URL%%", resolver_pattern.replace("%s", ppn))
            .replace("%%PPN%%", ppn)
            .replace("%%CANVASES%%", ",".join(canvases)))
