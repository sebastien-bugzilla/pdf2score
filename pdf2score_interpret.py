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
    
    def setClef(self, clef):
        self.clef = clef
    
    def setKey(self, clef):
        self.key = key
    
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
    
    def getDevforX(self, x, dev_left, dev_center, dev_right):
        x_beg = self.x_beg
        x_end = self.x_end
        x_mil = (x_beg + x_end) / 2
        if x < x_mil:
            y = float(dev_left + (dev_center - dev_left) * (x - x_beg) / (x_mil - x_beg))
        else:
            y = float(dev_center + (dev_right - dev_center) * (x - x_mil) / (x_end - x_mil))
        return y
    
    def getError(self, y_portee, gap, dev_l, dev_c, dev_r):
        score = 0.
        for j in range(self.nb_notes):
            y_note = float(self.notes[j].y)
            x_note = float(self.notes[j].x)
            y_dev = self.getDevforX(x_note, dev_l, dev_c, dev_r)
            offset = float((y_portee + y_dev - y_note)/(gap/2.))
            offset_int = int(round(offset))
            if offset_int > 0:
                correction = -7
            else:
                correction = 7
            while abs(offset_int)>6:
                offset = offset + correction
                offset_int = offset_int + correction
            increment = abs(offset-offset_int)
            score = score + increment
        return score
    
    def getBestScore(self):
        score = 100.
        for i_gap in range(5):
            gap = float(self.gap)+(i_gap-2)/4.
            for i_staff  in range(5):
                y_staff = float(self.position) + (i_staff-2)/4.
                dev_l = float(self.deviation_gauche)
                dev_c = float(self.deviation_centre)
                dev_r = float(self.deviation_droite)
                new_score = self.getError(y_staff, gap, dev_l, dev_c, dev_r)
                if new_score < score:
                    res_gap = gap
                    res_y_staff = y_staff
                    res_dev_l = dev_l
                    res_dev_c = dev_c
                    res_dev_r = dev_r
                    score = new_score
        return score, res_gap, res_y_staff, res_dev_l, res_dev_c, res_dev_r
    
    def findNoteName(self, gap, y_staff, dev_l, dev_c, dev_r, clef, key):
        scale = getScale(clef, key)
        x_beg = self.x_beg
        x_end = self.x_end
        x_mil = (x_beg + x_end) / 2
        for i in range(self.nb_notes):
            y_note = float(self.notes[i].y)
            x_note = float(self.notes[i].x)
            y_dev = self.getDevforX(x_note, dev_l, dev_c, dev_r)
            offset = float((y_staff + y_dev - y_note)/(gap / 2.))
            offset_int = int(round(offset))
            octave = 0
            if offset_int > 0:
                correction = -7
            else:
                correction = 7
            while abs(offset_int)>6:
                offset_int = offset_int + correction
                offset = offset + correction
                octave = octave + 1
            self.notes[i].setName(scale[offset_int])
            self.notes[i].setOctave(octave)
    
    def ordonneNotes(self):
        note_array = []
        for i in range(self.nb_notes):
            note_array.append([self.notes[i].x, self.notes[i]])
        note_array_sorted = sorted(note_array, key=itemgetter(0))
        self.notes = []
        for i in range(len(note_array_sorted)):
            self.notes.append(note_array_sorted[i][1])
    
    def detectChord(self):
        x_old = 1
        y_old = self.position
        gap = self.gap
        for i in range(self.nb_notes):
            dx = float(self.notes[i].x - x_old)
            if dx < 1.:
                self.notes[i].setChord()
                self.notes[i-1].setChord()
    
    def detectFalseNotes(self):
        i = 1
        while i < self.nb_notes-1:
            dx = self.notes[i].x - self.notes[i-1].x
            if (dx < 9 and dx > 1):
                y1 = self.notes[i-1].y
                y2 = self.notes[i].y
                y3 = self.notes[i+1].y
                n1 = self.notes[i-1].nbre_detection
                n2 = self.notes[i].nbre_detection
                n3 = self.notes[i+1].nbre_detection
                y_moy = (y1*n1+y2*n2+y3*n3)/(n1+n2+n3)
                d1 = abs(y1 - y_moy)
                d2 = abs(y2 - y_moy)
                d3 = abs(y3 - y_moy)
                if d1 == max(d1,d2,d3):
                    self.notes[i-1].setStatusFalse()
                if d2 == max(d1,d2,d3):
                    self.notes[i].setStatusFalse()
                if d3 == max(d1,d2,d3):
                    self.notes[i+1].setStatusFalse()
                i = i + 2
            else:
                i = i + 1

class Systeme:
    
    def __init__(self, portee, nbre_portee):
        self.nbre_portee = nbre_portee
        self.tabPortees = portee
    
    def ajoutePortee(self, portee):
        self.tabPortees.append(portee)
        self.nbre_portee = self.nbre_portee + 1
    

class Note:
    
    def __init__(self, x, y, nbre_detection, mesure):
        self.x = x
        self.y = y
        self.nbre_detection = nbre_detection
        self.chord = "no"
        self.status = "true"
        self.mesure = mesure
    
    def setName(self, name):
        self.name = name
    
    def setOctave(self, octave):
        self.octave = octave
    
    def setStatusFalse(self):
        self.status = "false"
    
    def setChord(self):
        self.chord="yes"
    
    def setMesure(self, mesure):
        self.mesure = mesure

def getScale(clef, key):
    n = ['c','d','e','f','g','a','b','c','d','e','f','g','a','b','c']
    sharp = ['f','c','g','d','a','e','b']
    flat = ['b','e','a','d','g','c','f']
    if clef == 'c3':
        offset = 0
    elif clef == 'f4':
        offset = 1
    elif clef == 'c2':
        offset = 2
    elif clef == 'f3':
        offset = 3
    elif clef == 'c1':
        offset = 4
    elif clef == 'c4':
        offset = 5
    elif clef == 'g2':
        offset = 6
    else:
        offset = 6
    if len(key) > 0:
        nb_accidentals = int(key[0])
        suffix = key[1:3]
        if suffix == 'es':
            note_modified = flat[0:nb_accidentals]
        elif suffix == 'is':
            note_modified = sharp[0:nb_accidentals]
        else:
            note_modified = []
        scale = []
        for i in range(7):
            if n[offset + i] in note_modified:
                scale.append(n[offset + i] + suffix)
            else:
                scale.append(n[offset + i])
    else:
        for i in range(7):
            scale.append(n[offset + i])
    return scale
#-------------------------------------------------
#----------------- portees -----------------------
#-------------------------------------------------
nom_image='mendelssohn'

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
    key = str(staff.find('key').text)
    clef = str(staff.find('clef').text)
    myStaff = Portee(rank, position, gap)
    myStaff.setDeviationGauche(left_dev)
    myStaff.setDeviationDroite(right_dev)
    myStaff.setDeviationCentre(central_dev)
    myStaff.setXbeg(x_beg)
    myStaff.setXend(x_end)
    myStaff.setClef(clef)
    myStaff.setKey(key)
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

#-------------------------------------------------
#------------------ notes ------------------------
#-------------------------------------------------

xml_note = ElementTree.parse(nom_image + "_notes.xml")
root_note = xml_note.getroot()
for note in root_note.iter('point'):
    x = float(note.find('x').text)
    y = float(note.find('y').text)
    nb_det = int(note.find('nb_detection').text)
    # each note is attributed to the nearest staff
    distance = 1000
    for i in range(len(tab_portee)):
        temp = tab_portee[i].distance(y)
        if temp < distance:
            distance = temp
            nearest_staff = i
    # find the right bar :
    mesure = 0
    for bar in range(len(tab_portee[nearest_staff].mesures)-1):
        if (x < tab_portee[nearest_staff].mesures[bar+1] and
            x > tab_portee[nearest_staff].mesures[bar]):
            mesure = bar
    tab_portee[nearest_staff].addNotes(Note(x, y, nb_det, mesure))

# détermination des nom de notes
for i in range(len(tab_portee)):
    tab_portee[i].ordonneNotes()
    tab_portee[i].detectChord()
    tab_portee[i].detectFalseNotes()
    optim = tab_portee[i].getBestScore()
    gap = optim[1]
    y_staff = optim[2]
    dev_l = optim[3]
    dev_c = optim[4]
    dev_r = optim[5]
    print(optim)
    key = tab_portee[i].key
    clef = tab_portee[i].clef
    tab_portee[i].findNoteName(gap, y_staff, dev_l, dev_c, dev_r, clef, key)

img = cv2.imread(nom_image + ".jpg")
for i in range(len(tab_portee)):
    y_portee=tab_portee[i].position
    dev_g = tab_portee[i].deviation_gauche
    dev_c = tab_portee[i].deviation_centre
    dev_d = tab_portee[i].deviation_droite
    gap = tab_portee[i].gap
    x_beg = tab_portee[i].x_beg
    x_end = tab_portee[i].x_end
    x_mil = (x_beg + x_end)/2
    # dessin des portées
    for j in range(5):
        temp = int(gap *(j-2))
        cv2.line(img, (x_beg, y_portee + dev_g + temp),(x_mil, y_portee + dev_c + temp),(0,0,255),1)
        cv2.line(img, (x_mil, y_portee + dev_c + temp),(x_end, y_portee + dev_d + temp),(0,0,255),1)
    if i > 0:
        y_inter = int((y_portee + y_portee_old)/2)
        cv2.line(img, (x_beg, y_inter),(x_end, y_inter),(0,0,255),1)
    y_portee_old = y_portee
    # dessin des notes
    for j in range(tab_portee[i].nb_notes):
        if tab_portee[i].notes[j].status == "true":
            print tab_portee[i].notes[j].x, tab_portee[i].notes[j].y, tab_portee[i].notes[j].nbre_detection, tab_portee[i].notes[j].mesure, tab_portee[i].notes[j].name
            x_note = int(tab_portee[i].notes[j].x)
            y_note = int(tab_portee[i].notes[j].y)
            cv2.line(img,(x_note+4,y_note+4),(x_note-4,y_note-4),(0,255,0),2)
            cv2.line(img,(x_note-4,y_note+4),(x_note+4,y_note-4),(0,255,0),2)
        else:
            x_note = int(tab_portee[i].notes[j].x)
            y_note = int(tab_portee[i].notes[j].y)
            cv2.line(img,(x_note+4,y_note+4),(x_note-4,y_note-4),(255,0,0),2)
            cv2.line(img,(x_note-4,y_note+4),(x_note+4,y_note-4),(255,0,0),2)
    print('')
cv2.imwrite(nom_image + "_check_note.jpg",img)
