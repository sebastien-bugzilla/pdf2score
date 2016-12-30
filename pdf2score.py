# -*- coding:Utf-8 -*-
#!/usr/bin/env python

import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller
from portees.pdf2score_portees import *
from mesures.pdf2score_mesures import *

class Portee:
    
    def __init__(self, position, interligne):
        self.position = position
        self.interligne = interligne
        self.deviation_gauche = 0
        self.deviation_droite = 0
        self.deviation_centre = 0
        self.mesures = []
        self.notes = []
    
    def setDeviationGauche(self, dev_gauche):
        self.deviation_gauche = dev_gauche
    
    def setDeviationDroite(self, dev_droite):
        self.deviation_droite = dev_droite
    
    def setDeviationCentre(self, dev_centre):
        self.deviation_centre = dev_centre
    
    def addMesure(self, mesure):
        self.mesures.append(mesure)

class Systeme:
    
    def __init__(self, portee, nbre_portee):
        self.nbre_portee = nbre_portee
        self.tabPortees = portee
    
    def ajoutePortee(self, portee):
        self.tabPortees.append(portee)
        self.nbre_portee = self.nbre_portee + 1

# portees
nom_image='mendelssohn'
img = cv2.imread(nom_image + ".jpg")
height, width = img.shape[:2]
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,50,150,apertureSize = 3)
minLineLength = 120   #100
maxLineGap = 16        #10
lines = cv2.HoughLinesP(edges,1,np.pi/180,200,minLineLength,maxLineGap)
resPortees = pdf2score_portees(lines, height, width)

nbre_portee = resPortees.nbre_portee
tab_portees = []
for portees in range(nbre_portee):
    ecart = resPortees.ecart[portees]
    position = resPortees.positions[portees]
    dev_gauche = resPortees.deviation_gauche[portees]
    dev_centre = resPortees.deviation_centre[portees]
    dev_droite = resPortees.deviation_droite[portees]
    portee = Portee(position, ecart)
    portee.setDeviationGauche(dev_gauche)
    portee.setDeviationCentre(dev_centre)
    portee.setDeviationDroite(dev_droite)
    tab_portees.append(portee)


# mesures
#img_rgb = cv2.imread('saintsaens.jpg')
#img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
threshold = 0.60
tabRes = []
for i_temp in range(8):
    template = cv2.imread('./motifs/0_barre' + str(i_temp + 1) + '.png',0)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > threshold)
    tabRes.append(loc)
width_template, height_template = template.shape[::-1]
width_partition, height_partition = gray.shape[::-1]
resMesures = pdf2score_mesures(tabRes, width_partition, width_template, height_template)

tab_systeme = []
nombre_systeme = len(resMesures)
for i_sys in range(nombre_systeme):
    systeme_courant = Systeme([], 0)
    y_min_sys = resMesures[i_sys].y_min
    y_max_sys = resMesures[i_sys].y_max
    for i in range(nbre_portee):
        y_portee = tab_portees[i].position
        if (y_min_sys < y_portee and y_portee < y_max_sys):
            systeme_courant.ajoutePortee(tab_portees[i])
            for j in range(resMesures[i_sys].nbreMesure):
                tab_portees[i].addMesure(resMesures[i_sys].mesures[j])
    tab_systeme.append(systeme_courant)



#for i_portee in range(porteesDetectees.nbre_portee):
#    ecart = porteesDetectees.portees[i_portee].ecart
#    position = porteesDetectees.portees[i_portee].position
#    dev_gche = porteesDetectees.portees[i_portee].deviation_gauche
#    dev_drte = porteesDetectees.portees[i_portee].deviation_droite
#    dev_ctre = porteesDetectees.portees[i_portee].deviation_centre
#    for i_ligne in range(5):
#        y_deb = position - ecart*(i_ligne-2) + dev_gche
#        y_mil = position - ecart*(i_ligne-2) + dev_drte
#        y_fin = position - ecart*(i_ligne-2) + dev_ctre
#        cv2.line(img,(1,y_deb),(int(width/2),y_mil),(255,0,0),1)
#        cv2.line(img,(int(width/2),y_mil),(width,y_fin),(255,0,0),1)
#cv2.imwrite(nom_image + "_lignev5.jpg",img)
