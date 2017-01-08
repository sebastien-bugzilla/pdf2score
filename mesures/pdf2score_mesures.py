# -*- coding:Utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree

class Mesure_OCV:
    def __init__(self, x_barre, y_min, nbrePoints, height):
        self.x_barre = x_barre
        self.nbrePoints = nbrePoints
        self.y_min = y_min
        self.y_max = y_min + height
        self.x_somme = x_barre
        self.x_moy = x_barre / nbrePoints
    
    def get_x(self):
        return self.x_barre
    
    def distance(self, x):
        return abs(self.x_barre - x)
    
    def ajoutPoint(self, x, y, h):
        self.nbrePoints= self.nbrePoints + 1
        if self.y_max < y + h:
            self.y_max = y + h
        self.x_somme = self.x_somme + x
        self.x_moy = self.x_somme / self.nbrePoints
    
    def centreBarre(self):
        self.y_centre = round(float((self.y_min + self.y_max) / 2),2)
    
    def ecartCentre(self, y_group):
        self.ecart_centre = round(float(abs(y_group - self.y_centre)),2)
    
    def pourcentDetection(self, nbreDetection):
        self.pourcent_detection = round(float(self.nbrePoints) / nbreDetection * 100,2)
    
    def classement(self, methode, nbreMesure):
        if methode == "pourcent":
            limite = round(float(100./(nbreMesure+2)))
            if self.pourcent_detection > limite:
                self.status = "OK"
            else:
                self.status = "NOK"
            if abs(self.pourcent_detection - limite) < 0.5:
                self.status = "TBC"
        elif methode == "centrage":
            if self.ecart_centre < 5:
                self.status = "OK"
            elif 5 < self.ecart_centre < 10:
                self.status = "TBC"
            else:
                self.status = "NOK"
    
    def affiche(self, rang):
        enTete = ["Pos. X","nbrePoint","y_centre","ecart centre","pourcent","status"]
        data = [self.x_moy, self.nbrePoints, self.y_centre, self.ecart_centre, self.pourcent_detection , self.status]
        temp = []
        for i in range(len(data)):
            temp.append(str(data[i]))
        if rang == 0:
            print(formatLog(enTete, 15, "|"))
        print(formatLog(temp, 15, "|"))
        return data

class Systeme_OCV:
    def __init__(self):
        self.y_min = 5000
        self.y_max = 0
        self.nbreMesure = 0
        self.mesures = []
    
    def ajoutBarre(self, uneMesure):
        self.nbreMesure = self.nbreMesure + 1
        self.mesures.append(uneMesure)
    
    def statusPoint(self, x, y, h):
        distance_mini = 1000
        for i in range(self.nbreMesure):
            distance_courante = self.mesures[i].distance(x)
            if distance_courante < distance_mini:
                distance_mini = distance_courante
                mesureProche = i
        if distance_mini < 7:
            self.mesures[mesureProche].ajoutPoint(x, y, h)
            if self.y_min > y:
                self.y_min = y
            if self.y_max < y + h:
                self.y_max = y + h
        else:
            nouvelleMesure = Mesure_OCV(x, y, 1, h)
            self.ajoutBarre(nouvelleMesure)
    
    def ordonneBarre(self):
        temp = []
        for i_barre in range(self.nbreMesure):
            temp.append([self.mesures[i_barre].get_x(), self.mesures[i_barre]])
        temp.sort()
        temp2 = []
        for i_barre in range(self.nbreMesure):
            temp2.append(temp[i_barre][1])
        self.mesures=temp2
    
    def triResultats(self):
        y_moy = 0
        nb_pt = 0
        for i_barre in range(self.nbreMesure):
            self.mesures[i_barre].centreBarre()
            y_moy = y_moy + self.mesures[i_barre].y_centre * self.mesures[i_barre].nbrePoints
            nb_pt = nb_pt + self.mesures[i_barre].nbrePoints
        self.y_moy_pond = y_moy / nb_pt
        for i_barre in range(self.nbreMesure):
            self.mesures[i_barre].ecartCentre(y_moy / nb_pt)
            self.mesures[i_barre].pourcentDetection(nb_pt)
        if self.y_max - self.y_min > 120:
            for i_barre in range(self.nbreMesure):
                self.mesures[i_barre].classement("centrage", nb_pt)
        else:
            for i_barre in range(self.nbreMesure):
                self.mesures[i_barre].classement("pourcent", self.nbreMesure)
    
    def imprimeXml(self, rank):
        # creation d'une structure xml
        system_xml = Element('system')
        system_rank = SubElement(system_xml, 'rank')
        system_rank.text = str(rank + 1)
        y_min = SubElement(system_xml, 'y_min')
        y_min.text = str(self.y_min)
        y_max = SubElement(system_xml, 'y_max')
        y_max.text = str(self.y_max)
        bar_number_ok = 0
        for bar in range(self.nbreMesure):
            if self.mesures[bar].status != "NOK":
                bar_number_ok = bar_number_ok + 1
        bar_number = SubElement(system_xml, 'bar_number')
        bar_number.text = str(bar_number_ok)
        bar_number_ok = 0
        for bar in range(self.nbreMesure):
            if self.mesures[bar].status != "NOK":
                bar_number_ok = bar_number_ok + 1
                bar_xml = SubElement(system_xml, 'bar')
                bar_rank = SubElement(bar_xml, 'rank')
                bar_rank.text = str(bar_number_ok)
                bar_ymin = SubElement(bar_xml, 'y_min')
                bar_ymin.text = str(self.mesures[bar].y_min)
                bar_ymax = SubElement(bar_xml, 'y_max')
                bar_ymax.text = str(self.mesures[bar].y_max)
                bar_xmoy = SubElement(bar_xml, 'x_moy')
                bar_xmoy.text = str(self.mesures[bar].x_moy)
                bar_status = SubElement(bar_xml, 'status')
                bar_status.text = str(self.mesures[bar].status)
        self.xml = system_xml


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def pdf2score_mesures(nom_fichier, tabRes, width, width_template, height_template):
    # etude en concaténant tous les résultats
    tabResConcat = []
    for i_barre in range(8):
        for i_pt in range(len(tabRes[i_barre][0])):
            if 30 < tabRes[i_barre][1][i_pt] < width - 30:
                unPoint=[tabRes[i_barre][1][i_pt] + width_template / 2, tabRes[i_barre][0][i_pt]]
                tabResConcat.append(unPoint)
    tabResOrdre = sorted(tabResConcat, key=itemgetter(1))
    nb_pt = 0
    nb_syst = 0
    tab_systeme = []
    ecart_y = 0
    y_old = 0
    for i_pt in range(len(tabResOrdre)):
        y_new = tabResOrdre[i_pt][1]
        if nb_pt == 0:
            monSysteme_OCV = Systeme_OCV()
            maMesure = Mesure_OCV(tabResOrdre[i_pt][0], tabResOrdre[i_pt][1], 1, height_template)
            monSysteme_OCV.ajoutBarre(maMesure)
            tab_systeme.append(monSysteme_OCV)
            nb_syst = nb_syst + 1
        else:
            ecart_y = y_new - y_old
            if ecart_y > 10:
                monSysteme_OCV = Systeme_OCV()
                maMesure = Mesure_OCV(tabResOrdre[i_pt][0], tabResOrdre[i_pt][1], 1, height_template)
                monSysteme_OCV.ajoutBarre(maMesure)
                tab_systeme.append(monSysteme_OCV)
                nb_syst = nb_syst + 1
            else:
                tab_systeme[nb_syst-1].statusPoint(tabResOrdre[i_pt][0], tabResOrdre[i_pt][1], height_template)
        nb_pt = nb_pt + 1
        y_old = y_new
    all_system = Element('all_system')
    for i_syst in range(nb_syst):
        system = SubElement(all_system, 'system')
        tab_systeme[i_syst].ordonneBarre()
        tab_systeme[i_syst].triResultats()
        tab_systeme[i_syst].imprimeXml(i_syst)
        system.extend(tab_systeme[i_syst].xml)
    fichier_xml = open(nom_fichier + "_mesures.xml", "w")
    fichier_xml.write(prettify(all_system))
    return tab_systeme

if __name__ == "__main__":
    nom_image = 'saintsaens'
    img_rgb = cv2.imread(nom_image + '.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    threshold = 0.60
    tabRes = []
    for i_temp in range(8):
        template = cv2.imread('0_barre' + str(i_temp + 1) + '.png',0)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res > threshold)
        tabRes.append(loc)
    width_template, height_template = template.shape[::-1]
    width_partition, height_partition = img_gray.shape[::-1]
    pdf2score_mesures(nom_image, tabRes, width_partition, width_template, height_template)

