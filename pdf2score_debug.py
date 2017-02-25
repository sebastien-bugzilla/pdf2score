# -*- coding:Utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree
from operator import itemgetter, attrgetter, methodcaller

nom_fichier = 'mendelssohn'
xml_mesures = ElementTree.parse(nom_fichier + '_mesures.xml')
root_mesures = xml_mesures.getroot()
xml_notes = ElementTree.parse(nom_fichier + '_notes2.xml')
root_notes = xml_notes.getroot()
xml_portees = ElementTree.parse(nom_fichier + '_portees.xml')
root_portees = xml_portees.getroot()

position = []
gap = []
dev_l = []
dev_c = []
dev_r = []
x_beg = int(root_portees.find('x_beg').text)
x_end = int(root_portees.find('x_end').text)
nb_portee = 0
for staff in root_portees.findall('./staff'):
    position.append(staff.find('position').text)
    gap.append(staff.find('gap').text)
    dev_l.append(staff.find('left_deviation').text)
    dev_c.append(staff.find('centre_deviation').text)
    dev_r.append(staff.find('right_deviation').text)
    nb_portee = nb_portee + 1

bar_x = []
bar_y_min = []
bar_y_max = []
nb_bar = 0
for bar in root_mesures.findall('./system/bar'):
    bar_x.append(bar.find('x_moy').text)
    bar_y_min.append(bar.find('y_min').text)
    bar_y_max.append(bar.find('y_max').text)
    nb_bar = nb_bar + 1

note_x = []
note_y = []
status = []
nb_note = 0
for note in root_notes.findall('./point'):
    note_x.append(note.find('x').text)
    note_y.append(note.find('y').text)
    status.append(note.find('status').text)
    nb_note = nb_note + 1

img = cv2.imread(nom_fichier + ".jpg")
for i in range(nb_portee):
    y_portee = int(position[i])
    d_g = int(dev_l[i])
    d_c = int(dev_c[i])
    d_d = int(dev_r[i])
    g = int(gap[i])
    x_mil = (x_beg + x_end)/2
    for j in range(5):
        temp = int(g *(j-2))
        cv2.line(img, (x_beg, y_portee + d_g + temp),(x_mil, y_portee + d_c + temp),(255,0,0),1)
        cv2.line(img, (x_mil, y_portee + d_c + temp),(x_end, y_portee + d_d + temp),(255,0,0),1)
    if i > 0:
        y_inter = int((y_portee + y_portee_old)/2)
        cv2.line(img, (x_beg, y_inter),(x_end, y_inter),(0,0,255),1)
    y_portee_old = y_portee

# dessin des notes
for i in range(nb_note):
    x_note = int(float(note_x[i]))
    y_note = int(float(note_y[i]))
    is_ok = status[i]
    if is_ok == "OK":
        cv2.line(img,(x_note+4,y_note+4),(x_note-4,y_note-4),(0,255,0),2)
        cv2.line(img,(x_note-4,y_note+4),(x_note+4,y_note-4),(0,255,0),2)
    else:
        cv2.line(img,(x_note+4,y_note+4),(x_note-4,y_note-4),(0,0,255),2)
        cv2.line(img,(x_note-4,y_note+4),(x_note+4,y_note-4),(0,0,255),2)

for i in range(nb_bar):
    pos_x = int(bar_x[i])
    pos_y_min = int(bar_y_min[i])
    pos_y_max = int(bar_y_max[i])
    cv2.line(img,(pos_x, pos_y_min),(pos_x, pos_y_max),(50,0,50),3)

cv2.imwrite(nom_fichier + "_debug.jpg",img)



