# -*- coding:Utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree
from scipy.interpolate import interp1d

class Portees_OCV:
    
    def __init__(self, position, valeur, score, x_beg, x_end):
        self.positions = position
        self.valeurs = valeur
        self.score = score
        self.score_moy = 0
        self.nbre_portee = 0
        self.ecart = []
        self.x_beg = x_beg
        self.x_end = x_end
    
    def ajoutPortee(self, maxPosition, maxValeur, ecart):
        self.positions.append(maxPosition)
        self.valeurs.append(maxValeur)
        self.score = self.score + maxValeur
        self.nbre_portee = self.nbre_portee + 1
        self.ecart.append(ecart)
    
    def calculScore(self):
        if self.nbre_portee == 0:
            self.score_moy = 0
        else:
            self.score_moy = self.score / self.nbre_portee
    
    def setDeviationGauche(self, dev_gauche):
        self.deviation_gauche = dev_gauche
    
    def setDeviationDroite(self, dev_droite):
        self.deviation_droite = dev_droite
    
    def setDeviationCentre(self, dev_centre):
        self.deviation_centre = dev_centre
    
    def setEcartDecim(self, ecart):
        self.ecart_decim = []
        for i in range(self.nbre_portee):
            self.ecart_decim.append(ecart)
    
    def imprimeXml(self):
        # creation d'une structure xml
        all_staves = Element('all_staves')
        nombre_portees = SubElement(all_staves, 'nombre_portees')
        nombre_portees.text = str(self.nbre_portee)
        x_beg = SubElement(all_staves, 'x_beg')
        x_beg.text = str(self.x_beg)
        x_end = SubElement(all_staves, 'x_end')
        x_end.text = str(self.x_end)
        for staves in range(self.nbre_portee):
            staff = SubElement(all_staves, 'staff')
            rank = SubElement(staff, 'rank')
            rank.text = str(staves + 1)
            key = SubElement(staff, 'key')
            key.text = ' '
            voice = SubElement(staff, 'voice')
            voice.text = ' '
            position = SubElement(staff, 'position')
            position.text = str(self.positions[staves])
            gap = SubElement(staff, 'gap')
            gap.text = str(self.ecart[staves])
            gap_decim = SubElement(staff,'gap_decim')
            gap_decim.text = str(self.ecart_decim[staves])
            left_deviation = SubElement(staff, 'left_deviation')
            left_deviation.text = str(self.deviation_gauche[staves])
            right_deviation = SubElement(staff, 'right_deviation')
            right_deviation.text = str(self.deviation_droite[staves])
            centre_deviation = SubElement(staff, 'centre_deviation')
            centre_deviation.text = str(self.deviation_centre[staves])
        self.xml = all_staves

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def lectureTableauLigne(lines, nbColonne, height, width):
    ligneH=[[0] * nbColonne for _ in range(height)]
    x_beg = 3000
    x_end = 0
    for x1, y1, x2, y2 in lines[0]:
        if abs(y1-y2)<=1: #la ligne est horizontale
            if x1 < x_beg:
                x_beg = x1
            if x2 > x_end:
                x_end = x2
            position = int(((x1+x2)/2.)/float(width) * nbColonne)
            longueur = abs(x1-x2)
            ligneH[y1-1][position] = ligneH[y1-1][position] + longueur
    return ligneH, x_beg, x_end

def vecteurRateau(ecart):
    Vecteur=[]
    for j in range(4):
        for i in range(3):
            Vecteur.append(1)
        for i in range(ecart-3):
            Vecteur.append(0)
    for i in range(3):
        Vecteur.append(1)
    return Vecteur

def tailleVecteurRateau(ecart):
    taille = 4*ecart+3
    return taille

def produitScalaire(V1, V2):
    prod = 0
    for i in range(len(V1)):
        prod = prod + V1[i]*V2[i]
    return prod

def produitConvolution(V1, ecartLigne, nbColonne, height):
    V3 = [[0] * nbColonne for _ in range(len(V1))]
    V2 = vecteurRateau(ecartLigne)
    for i_dim in range(nbColonne):
        for i_lig in range(2*ecartLigne+1):
            V3[i_lig][i_dim] = 0
            V3[height-1-i_lig][i_dim] = 0
    for i_dim in range(nbColonne):
        for i_lig in range(height-1-len(V2)):
            extractV1 = []
            for i_vect in range(len(V2)):
                extractV1.append(V1[i_lig+i_vect][i_dim])
            V3[2*ecartLigne + 1 + i_lig][i_dim] = produitScalaire(extractV1, V2)
    return V3

def calculMaxLocaux(V1, ecartLigne, nbColonne, height):
    V2 = [[0] * nbColonne for _ in range(len(V1))]
    for i_dim in range(nbColonne):
        for i_lig in range(2*ecartLigne+1):
            V2[i_lig][i_dim] = 0
            V2[height-1-i_lig][i_dim] = 0
    plage = tailleVecteurRateau(ecartLigne)
    for i_dim in range(nbColonne):
        for i_lig in range(height-1-plage):
            valeurMax = 0
            for i_vect in range(plage):
                valeurMax = max(valeurMax,V1[i_lig+i_vect][i_dim])
            V2[2*ecartLigne + 1 + i_lig][i_dim] = valeurMax
    return V2

def attributMaxLocaux(V1, ecartLigne, nbColonne):
    if nbColonne == 1:
        maxPosition = []
        maxValeur = []
        maxLargeur = []
    else:
        maxPosition = [[] for _ in range(nbColonne)]
        maxValeur = [[] for _ in range(nbColonne)]
        maxLargeur = [[] for _ in range(nbColonne)]
    for i_dim in range(nbColonne):
        valeurConsecutive = 1
        valeurPrecedente = 0
        valeurMax = 0
        for i_lig in range(len(V1)):
            if V1[i_lig][i_dim] != 0:
                if V1[i_lig][i_dim] == valeurPrecedente:
                    valeurConsecutive = valeurConsecutive + 1
                    valeurMax = V1[i_lig][i_dim]
                    valeurPrecedente = V1[i_lig][i_dim]
                else:
                    if valeurConsecutive > tailleVecteurRateau(ecartLigne)-ecartLigne \
                        and valeurConsecutive < tailleVecteurRateau(ecartLigne)+ecartLigne:
                        if nbColonne ==1:
                            maxPosition.append(i_lig-2*ecartLigne-1)
                            maxValeur.append(valeurMax)
                            maxLargeur.append(valeurConsecutive)
                        else:
                            maxPosition[i_dim].append(i_lig-2*ecartLigne-1)
                            maxValeur[i_dim].append(valeurMax)
                            maxLargeur[i_dim].append(valeurConsecutive)
                    valeurConsecutive = 1
                    valeurPrecedente = V1[i_lig][i_dim]
    return maxPosition, maxValeur, maxLargeur

def calculEcart(maxValeur, res_best):
    x = [0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.]
    f = interp1d(x, maxValeur, kind='cubic')
    val_max = 0.
    x_max=0.
    for i in range(200):
        t = float(i/100.)
        if f(res_best -1 + t)>val_max:
            x_max = t
            val_max = f(t)
    return res_best - 1 + x_max

def pdf2score_portees(nom_image, lines, height, width):
    tableauLigne = lectureTableauLigne(lines, 1, height, width)
    #critereDetection = []
    x_beg = tableauLigne[1]
    x_end = tableauLigne[2]
    resultats = []
    for i_test in range(12):
        resultats.append(Portees_OCV([],[],0, x_beg, x_end))
        ecart = i_test + 4
        prodConv = produitConvolution(tableauLigne[0], ecart,1, height)
        maxProdConv = calculMaxLocaux(prodConv,ecart,1, height)
        rechercheMax = attributMaxLocaux(maxProdConv,ecart,1)
        maxPosition = rechercheMax[0]
        maxValeur = rechercheMax[1]
        maxLargeur = rechercheMax[2]
        tableauPortees=[]
        for i_max in range(len(maxPosition)):
            resultats[i_test].ajoutPortee(maxPosition[i_max],maxValeur[i_max],ecart)
        resultats[i_test].calculScore()
    # détermination du meilleur résultat (celui dont le score est le plus élevé)
    res_max = 0
    res_best = 0
    tab_score_moy = []
    for i_res in range(12):
        tab_score_moy.append(resultats[i_res].score_moy)
        if res_max < resultats[i_res].score_moy:
            res_max = resultats[i_res].score_moy
            res_best = i_res
    ecart = 4 + res_best
    ecart_decim = 4. + float(calculEcart(tab_score_moy, res_best))
    resultats[res_best].setEcartDecim(ecart_decim)
    
    tableauLigne2 = lectureTableauLigne(lines, 3, height, width)
    prodConv2 = produitConvolution(tableauLigne2[0], ecart,3, height)
    maxProdConv2 = calculMaxLocaux(prodConv2,ecart,3, height)
    rechercheMax2 = attributMaxLocaux(maxProdConv2,ecart,3)
    maxPosition2 = rechercheMax2[0]
    maxValeur2 = rechercheMax2[1]
    maxLargeur2 = rechercheMax2[2]
    deviation = [[0] * resultats[res_best].nbre_portee for _ in range(3)]
    # déterminer quel element de 2 est le plus proche de 1
    for i_col in range(3):
        for i_lig1 in range(resultats[res_best].nbre_portee):
            dev_mini = 1000
            for i_lig2 in range(len(maxPosition2[i_col])):
                dist = abs(maxPosition2[i_col][i_lig2] - resultats[res_best].positions[i_lig1])
                if dev_mini > dist:
                    dev_mini = dist
                    dev_mini_algebrique = maxPosition2[i_col][i_lig2] - resultats[res_best].positions[i_lig1]
            if dev_mini > 5 * ecart:
                deviation[i_col][i_lig1] = 0
            else:
                deviation[i_col][i_lig1] = dev_mini_algebrique
    resultats[res_best].setDeviationGauche(deviation[0])
    resultats[res_best].setDeviationCentre(deviation[1])
    resultats[res_best].setDeviationDroite(deviation[2])
    
    resultats[res_best].imprimeXml()
    fichier_xml = open(nom_image + "_portees.xml", "w")
    fichier_xml.write(prettify(resultats[res_best].xml))
    return resultats[res_best]

if __name__ == "__main__":
    nom_image='bach2'
    img = cv2.imread(nom_image + ".jpg")
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    minLineLength = 120   #100
    maxLineGap = 16        #10
    lines = cv2.HoughLinesP(edges,1,np.pi/180,200,minLineLength,maxLineGap)
    porteesDetectees = pdf2score_portees(nom_image, lines, height, width)
    ecart = porteesDetectees.ecart[0]
    for i_portee in range(porteesDetectees.nbre_portee):
        #ecart = porteesDetectees.portees[i_portee].ecart
        position = porteesDetectees.positions[i_portee]
        dev_gche = porteesDetectees.deviation_gauche[i_portee]
        dev_drte = porteesDetectees.deviation_droite[i_portee]
        dev_ctre = porteesDetectees.deviation_centre[i_portee]
        for i_ligne in range(5):
            y_deb = position - ecart*(i_ligne-2) + dev_gche
            y_mil = position - ecart*(i_ligne-2) + dev_ctre
            y_fin = position - ecart*(i_ligne-2) + dev_drte
            cv2.line(img,(1,y_deb),(int(width/2),y_mil),(255,0,0),1)
            cv2.line(img,(int(width/2),y_mil),(width,y_fin),(255,0,0),1)
    cv2.imwrite(nom_image + "_lignev5.jpg",img)
