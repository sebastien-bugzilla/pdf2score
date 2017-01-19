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

class Portee:
    
    def __init__(self, rank, position, gap):
        self.rank = rank
        self.position = position
        self.gap = gap
        self.deviation_gauche = 0
        self.deviation_droite = 0
        self.deviation_centre = 0
        self.mesures = []
        self.notes = []
        self.nb_notes = 0
    
    def setDeviationGauche(self, dev_gauche):
        self.deviation_gauche = dev_gauche
    
    def setDeviationDroite(self, dev_droite):
        self.deviation_droite = dev_droite
    
    def setDeviationCentre(self, dev_centre):
        self.deviation_centre = dev_centre
    
    def addMesure(self, mesure):
        self.mesures.append(mesure)
    
    def defMesure(self, mesure):
        self.mesures = mesure
    
    def defNotes(self, note):
        self.notes = note
    
    def addNotes(self, note):
        self.notes.append(note)
        self.nb_notes = self.nb_notes + 1
    
    def distance(self, y):
        return abs(self.position - y)

class Systeme:
    
    def __init__(self, portee, nbre_portee):
        self.nbre_portee = nbre_portee
        self.tabPortees = portee
    
    def ajoutePortee(self, portee):
        self.tabPortees.append(portee)
        self.nbre_portee = self.nbre_portee + 1

class Note:
    
    def __init__(self, x_min, x_max, y_min, y_max, nbre_detection):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x = (x_min + x_max) / 2
        self.y = (y_min + y_max) / 2
        self.nbre_detection = nbre_detection
    
    def findName(self, y_staff, gap):
        dictionnaire = ['si', 'do', 'ré', 'mi', 'fa', 'sol', 'la']
        offset = (self.x - y_staff)/(gap / 2)
        if abs(offset) > 7:
            self.name = 'unknown'
        else:
            self.name = dictionnaire[offset]
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

xml_portee = ElementTree.parse(nom_image + "_portees.xml")
root_portee = xml_portee.getroot()
tab_portee = []
for staff in root_portee.iter('staff'):
    rank = int(staff.find('rank').text)
    gap = int(staff.find('gap').text)
    position = int(staff.find('position').text)
    left_dev = int(staff.find('left_deviation').text)
    right_dev = int(staff.find('right_deviation').text)
    central_dev = int(staff.find('centre_deviation').text)
    myStaff = Portee(rank, position, gap)
    myStaff.setDeviationGauche(left_dev)
    myStaff.setDeviationDroite(right_dev)
    myStaff.setDeviationCentre(central_dev)
    tab_portee.append(myStaff)


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

xml_mesure = ElementTree.parse(nom_image + "_mesures.xml")
root_mesure = xml_mesure.getroot()
tab_system = []
for system in root_mesure.iter('system'):
    y_min = int(system.find('y_min').text)
    y_max = int(system.find('y_max').text)
    tab_mesure = []
    for bar in system.iter('bar'):
        tab_mesure.append(int(bar.find('x_moy').text))
    mySystem = Systeme([], 0)
    for i_staff in range(len(tab_portee)):
        if (tab_portee[i_staff].position >= y_min and
            tab_portee[i_staff].position <= y_max):
            mySystem.ajoutePortee(tab_portee[i_staff])
    if mySystem.nbre_portee > 0:
        for i in range(mySystem.nbre_portee):
            mySystem.tabPortees[i].defMesure(tab_mesure)
        tab_system.append(mySystem)

for i in range(len(tab_system)):
    for j in range(tab_system[i].nbre_portee):
        print tab_system[i].tabPortees[j].mesures

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

width_template1, height_template1 = template1.shape[::-1]
width_template2, height_template2 = template2.shape[::-1]
size_template= []
size_template.append(width_template1)
size_template.append(height_template1)
size_template.append(width_template2)
size_template.append(height_template2)
result = pdf2score_notes(nom_image, loc1, loc2, size_template)

xml_note = ElementTree.parse(nom_image + "_notes.xml")
root_note = xml_note.getroot()
for note in root_note.iter('point'):
    x_min = int(note.find('x_min').text)
    x_max = int(note.find('x_max').text)
    y_min = int(note.find('y_min').text)
    y_max = int(note.find('y_max').text)
    nb_det = int(note.find('nb_detection').text)
    y_mean = (y_min + y_max) / 2
    #each note is attributed to the nearest staff
    distance = 1000
    for i in range(len(tab_portee)):
        temp = tab_portee[i].distance(y_mean)
        if temp < distance:
            distance = temp
            nearest_staff = i
    tab_portee[nearest_staff].addNotes(Note(x_min, x_max, y_min, y_max, nb_det))

print("-------------------------")
for i in range(len(tab_portee)):
    y_portee = tab_portee[i].position
    gap = tab_portee[i].gap
    for j in range(tab_portee[i].nb_notes):
        tab_portee[i].notes[j].findName(y_portee, gap)
        print tab_portee[i].notes[j].x, tab_portee[i].notes[j].y, tab_portee[i].notes[j].name
