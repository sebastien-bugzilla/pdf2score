# -*- coding:Utf-8 -*-
#!/usr/bin/env python

import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
from xml.etree import ElementTree

from portees.pdf2score_portees import *
from mesures.pdf2score_mesures import *
from notes.pdf2score_notes import *


#-------------------------------------------------
#----------------- portees -----------------------
#-------------------------------------------------
nom_image='mendelssohn'
img = cv2.imread(nom_image + ".jpg")
height, width = img.shape[:2]
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,50,150,apertureSize = 3)
minLineLength = 120   #100
maxLineGap = 16        #10
lines = cv2.HoughLinesP(edges,1,np.pi/180,200,minLineLength,maxLineGap)
pdf2score_portees(nom_image, lines, height, width)


#-------------------------------------------------
#----------------- mesures -----------------------
#-------------------------------------------------

#img_rgb = cv2.imread('saintsaens.jpg')
#img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
threshold = 0.60
input_array = []
for i_temp in range(8):
    template = cv2.imread('./motifs/0_barre' + str(i_temp + 1) + '.png',0)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > threshold)
    input_array.append(loc)
width_template, height_template = template.shape[::-1]
width_partition, height_partition = gray.shape[::-1]
resMesures = pdf2score_mesures(nom_image, input_array, width_partition, width_template, height_template)


#-------------------------------------------------
#------------------ notes ------------------------
#-------------------------------------------------

threshold = 0.60
tabRes = []
template1 = cv2.imread('./motifs/elm_lily_note23_1.png',0)
res1 = cv2.matchTemplate(gray, template1, cv2.TM_CCOEFF_NORMED)
loc1 = np.where(res1 > threshold)

template2 = cv2.imread('./motifs/elm_lily_note23_2.png',0)
res2 = cv2.matchTemplate(gray, template2, cv2.TM_CCOEFF_NORMED)
loc2 = np.where(res2 > threshold)

template3 = cv2.imread('./motifs/elm_lily_note23_3.png',0)
res3 = cv2.matchTemplate(gray, template3, cv2.TM_CCOEFF_NORMED)
loc3 = np.where(res3 > threshold)


width_template1, height_template1 = template1.shape[::-1]
width_template2, height_template2 = template2.shape[::-1]
width_template3, height_template3 = template3.shape[::-1]
size_template= []
size_template.append(width_template1)
size_template.append(height_template1)
size_template.append(width_template2)
size_template.append(height_template2)
size_template.append(width_template3)
size_template.append(height_template3)
result = pdf2score_notes(nom_image, loc1, loc2, loc3, size_template)


