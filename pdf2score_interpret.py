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
    
    def __init__(self, rank, position, gap, gap_decim):
        self.rank = rank
        self.position = position
        self.gap = gap
        self.gap_decim = gap_decim
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
    
    def setKey(self, key):
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
    
    def findNoteName(self, gap, y_staff, dev_l, dev_c, dev_r, key):
        dictionnaire = keyToDictionnary(key)
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
            self.notes[i].setName(dictionnaire[offset_int])
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

def keyToDictionnary(key):
    if key == 'c3':
        dictionnary = ['do','ré','mi','fa','sol','la','si']
    elif key == 'f4':
        dictionnary = ['ré','mi','fa','sol','la','si','do']
    elif key == 'c2':
        dictionnary = ['mi','fa','sol','la','si','do','ré']
    elif key == 'f3':
        dictionnary = ['fa','sol','la','si','do','ré','mi']
    elif key == 'c1':
        dictionnary = ['sol','la','si','do','ré','mi','fa']
    elif key == 'c4':
        dictionnary = ['la','si','do','ré','mi','fa','sol']
    elif key == 'g1':
        dictionnary = ['si','do','ré','mi','fa','sol','la']
    else:
        dictionnary = ['si','do','ré','mi','fa','sol','la']
    return dictionnary

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
    gap_decim = float(staff.find('gap_decim').text)
    position = int(staff.find('position').text)
    left_dev = int(staff.find('left_deviation').text)
    right_dev = int(staff.find('right_deviation').text)
    central_dev = int(staff.find('centre_deviation').text)
    key = str(staff.find('key').text)
    myStaff = Portee(rank, position, gap, gap_decim)
    myStaff.setDeviationGauche(left_dev)
    myStaff.setDeviationDroite(right_dev)
    myStaff.setDeviationCentre(central_dev)
    myStaff.setXbeg(x_beg)
    myStaff.setXend(x_end)
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

# each note is attributed to the nearest staff
xml_note = ElementTree.parse(nom_image + "_notes.xml")
root_note = xml_note.getroot()
for note in root_note.iter('point'):
    x = float(note.find('x').text)
    y = float(note.find('y').text)
    nb_det = int(note.find('nb_detection').text)
    distance = 1000
    for i in range(len(tab_portee)):
        temp = tab_portee[i].distance(y)
        if temp < distance:
            distance = temp
            nearest_staff = i
    tab_portee[nearest_staff].addNotes(Note(x, y, nb_det))

#

# détermination des nom de notes
for i in range(len(tab_portee)):
    tab_portee[i].ordonneNotes()
    optim = tab_portee[i].getBestScore()
    gap = optim[1]
    y_staff = optim[2]
    dev_l = optim[3]
    dev_c = optim[4]
    dev_r = optim[5]
    print(optim)
    key = tab_portee[i].key
    tab_portee[i].findNoteName(gap, y_staff, dev_l, dev_c, dev_r, key)

img = cv2.imread(nom_image + ".jpg")
for i in range(len(tab_portee)):
    y_portee=tab_portee[i].position
    dev_g = tab_portee[i].deviation_gauche
    dev_c = tab_portee[i].deviation_centre
    dev_d = tab_portee[i].deviation_droite
    gap = tab_portee[i].gap_decim
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
        #print i, len(tab_portee), j, tab_portee[i].nb_notes, len(tab_portee[i].notes)
        print tab_portee[i].notes[j].x, tab_portee[i].notes[j].y, tab_portee[i].notes[j].name
#        print("    y_portee= " + str(y_portee) + "- y=" +str(tab_portee[i].notes[j].y))
        x_note = int(tab_portee[i].notes[j].x)
        y_note = int(tab_portee[i].notes[j].y)
        cv2.line(img,(x_note+4,y_note+4),(x_note-4,y_note-4),(0,255,0),1)
        cv2.line(img,(x_note-4,y_note+4),(x_note+4,y_note-4),(0,255,0),1)
    print('')
cv2.imwrite(nom_image + "_check_note.jpg",img)
