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
    
    def setXbeg(self, x_beg):
        self.x_beg = x_beg
    
    def setXend(self, x_end):
        self.x_end = x_end
    
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
    
    def findNoteName(self):
        dictionnaire = ['si', 'do', 'ré', 'mi', 'fa', 'sol', 'la']
        y_staff = self.position
        dev_left = self.deviation_gauche
        dev_right = self.deviation_droite
        dev_center = self.deviation_centre
        x_beg = self.x_beg
        x_end = self.x_end
        x_mil = (x_beg + x_end) / 2
        gap = self.gap
        for i in range(self.nb_notes):
            y_note = self.notes[i].y
            x_note = self.notes[i].x
            if x_note < x_mil:
                y_dev = float(dev_left + (dev_center - dev_left) * (x_note - x_beg) / (x_mil - x_beg))
            else:
                y_dev = float(dev_center + (dev_right - dev_center) * (x_note - x_mil) / (x_end - x_mil))
            offset = int(round((y_staff + y_dev - y_note)/(gap / 2.)))
            octave = 0
            if offset > 0:
                correction = -7
            else:
                correction = 7
            while abs(offset)>6:
                offset = offset + correction
                octave = octave + 1
            self.notes[i].setName(dictionnaire[offset])
            self.notes[i].setOctave(octave)
    
    def ordonneNotes(self):
        note_array = []
        for i in range(self.nb_notes):
            note_array.append([self.notes[i].x, self.notes[i]])
        note_array_sorted = sorted(note_array, key=itemgetter(0))
        self.notes = []
        for i in range(len(note_array_sorted)):
            self.notes.append(note_array_sorted[i][1])
    
class Systeme:
    
    def __init__(self, portee, nbre_portee):
        self.nbre_portee = nbre_portee
        self.tabPortees = portee
    
    def ajoutePortee(self, portee):
        self.tabPortees.append(portee)
        self.nbre_portee = self.nbre_portee + 1
    

class Note:
    
    def __init__(self, x, y, nbre_detection):
        self.x = x
        self.y = y
        self.nbre_detection = nbre_detection
    
    def setName(self, name):
        self.name = name
    
    def setOctave(self, octave):
        self.octave = octave
#-------------------------------------------------
#----------------- portees -----------------------
#-------------------------------------------------
nom_image='bach2'

xml_portee = ElementTree.parse(nom_image + "_portees.xml")
root_portee = xml_portee.getroot()

tab_portee = []
x_beg = int(root_portee.find('x_beg').text)
x_end = int(root_portee.find('x_end').text)
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
    myStaff.setXbeg(x_beg)
    myStaff.setXend(x_end)
    tab_portee.append(myStaff)


#-------------------------------------------------
#----------------- mesures -----------------------
#-------------------------------------------------

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

xml_note = ElementTree.parse(nom_image + "_notes.xml")
root_note = xml_note.getroot()
for note in root_note.iter('point'):
    x = int(note.find('x').text)
    y = int(note.find('y').text)
    nb_det = int(note.find('nb_detection').text)
    #each note is attributed to the nearest staff
    distance = 1000
    for i in range(len(tab_portee)):
        temp = tab_portee[i].distance(y)
        if temp < distance:
            distance = temp
            nearest_staff = i
    tab_portee[nearest_staff].addNotes(Note(x, y, nb_det))

print("-------------------------")
for i in range(len(tab_portee)):
    tab_portee[i].findNoteName()
    tab_portee[i].ordonneNotes()

img = cv2.imread(nom_image + ".jpg")
for i in range(len(tab_portee)):
    y_portee=tab_portee[i].position
    for j in range(tab_portee[i].nb_notes):
        #print i, len(tab_portee), j, tab_portee[i].nb_notes, len(tab_portee[i].notes)
        print tab_portee[i].notes[j].x, tab_portee[i].notes[j].y, tab_portee[i].notes[j].name
#        print("    y_portee= " + str(y_portee) + "- y=" +str(tab_portee[i].notes[j].y))
        x_note = tab_portee[i].notes[j].x
        y_note = tab_portee[i].notes[j].y
        cv2.line(img,(x_note+5,y_note+10),(x_note-5,y_note-10),(0,255,0),2)
cv2.imwrite(nom_image + "_check_note.jpg",img)
