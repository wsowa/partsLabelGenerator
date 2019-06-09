#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fpdf import FPDF
import os
import sys
import csv
import pyqrcode
import time

# batch qr generator:  https://qrexplore.com/generate/
COLS=5
ROWS=12

PAGE_MARGN_TOP = 21.3
PAGE_MARGN_LEFT = 10

LABEL_H=21.3
LABEL_W=38
LABEL_MARGIN=2

TITLE_FONT = 'df'
TITLE_FONT_SIZE = 8
TITLE_FONT_HEIGHT = 2

DESC_FONT = 'df'
DESC_FONT_SIZE = 6
DESC_FONT_HEIGHT = 2.2

IMAGE_SIZE=LABEL_H-2*LABEL_MARGIN-TITLE_FONT_HEIGHT
IMAGE_PADDING=1


def main():
    descriptions = readInput()
    qrFiles = generateQrs(descriptions.keys())
    generatePdf(descriptions, qrFiles)
    removeQrs(qrFiles.values())
    
def readInput():
    if (len(sys.argv) < 2):
        print "Usage: " + sys.argv[0] + " <parts desc> [previous parts desc]"
        sys.exit(1)
    csvNew = readCsv(sys.argv[1])
    if (len(sys.argv) > 2):
        csvOld = readCsv(sys.argv[2])
        csvDiff = {key: csvNew[key] for key in csvNew if key not in csvOld.keys()}
        return csvDiff
    else:
        return csvNew

def readCsv(path):
    f = open(path, 'rb')
    reader = csv.reader(f)
    reader.next()
    entries = map(lambda row: (row[0], row[1]) ,reader)
    f.close()
    return dict(entries)
    
def generateQrs(titles):
    qrFiles = {}
    i = 0
    prefix="QR-"+str(int(time.time()))
    for t in titles:
        fileName = str.format("{}-{:05d}.png", prefix, i)
        pyqrcode.create(t, error='L').png(fileName, scale=5, quiet_zone=2)
        qrFiles[t]=fileName
        i+=1
    return qrFiles

def removeQrs(qrFiles):
    for f in qrFiles: os.remove(f)

def generatePdf(descriptions, qrFiles):  
    pdf = FPDF()
    pdf.add_font(TITLE_FONT,'','/usr/share/fonts/truetype/freefont/FreeSans.ttf', True)
    pdf.add_page()

    ix=0
    iy=0
    for item in sorted(descriptions.keys()):
        print item, descriptions[item]
        
        pdf.set_xy(ix*LABEL_W+LABEL_MARGIN+PAGE_MARGN_LEFT, iy*LABEL_H+LABEL_MARGIN+PAGE_MARGN_TOP)
        pdf.set_font(TITLE_FONT, '', TITLE_FONT_SIZE)
        pdf.cell(LABEL_W-LABEL_MARGIN*2, 0, item, 0, 0, 'C')

        pdf.image(qrFiles[item], ix*LABEL_W+LABEL_MARGIN+PAGE_MARGN_LEFT, iy*LABEL_H+LABEL_MARGIN+TITLE_FONT_HEIGHT+PAGE_MARGN_TOP, IMAGE_SIZE, IMAGE_SIZE)
        
        pdf.set_xy(ix*LABEL_W+LABEL_MARGIN+IMAGE_SIZE+PAGE_MARGN_LEFT, iy*LABEL_H+LABEL_MARGIN+TITLE_FONT_HEIGHT+PAGE_MARGN_TOP+IMAGE_PADDING)
        pdf.set_font(DESC_FONT, '', DESC_FONT_SIZE)
        pdf.multi_cell(LABEL_W-IMAGE_SIZE-LABEL_MARGIN, DESC_FONT_HEIGHT, descriptions[item], 0, 'L')

        ix=ix+1
        if ix == COLS:
            ix = 0
            iy=iy+1

        if iy == ROWS:
            iy = 0
            pdf.add_page()

    pdf.output('labels.pdf', 'F')

if __name__ == "__main__":
    main()
    
