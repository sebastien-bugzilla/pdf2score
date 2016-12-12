# -*- coding:Utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller

#class Portee:
#    
#    def __init__(self, ecart, position, valeur, largeur):
#        self.ecart = ecart
#        self.position = position
#        self.valeur = valeur
#        self.largeur = largeur
#        self.deviation_gauche = 0
#        self.deviation_droite = 0
#        self.deviation_centre = 0
#    
#    def setDevGauche(self, valeur):
#        self.deviation_gauche = valeur
#    
#    def setDevDroite(self, valeur):
#        self.deviation_droite = valeur
#    
#    def setDevCentre(self, valeur):
#        self.deviation_centre = valeur

class SetPortees:
    
    def __init__(self, position, valeur, score):
        self.positions = position
        self.valeurs = valeur
        self.score = score
        self.score_moy = 0
        self.nbre_portee = 0
    
    def ajoutPortee(self, maxPosition, maxValeur):
        self.positions.append(maxPosition)
        self.valeurs.append(maxValeur)
        self.score = self.score + maxValeur
        self.nbre_portee = self.nbre_portee + 1
    
    def calculScore(self):
        if self.nbre_portee == 0:
            self.score_moy = 0
        else:
            self.score_moy = self.score / self.nbre_portee


def lectureTableauLigne(lines, nbColonne, height, width):
    ligneH=[[0] * nbColonne for _ in range(height)]
    for x1, y1, x2, y2 in lines[0]:
        if abs(y1-y2)<=1: #la ligne est horizontale
            position = int(((x1+x2)/2.)/float(width) * nbColonne)
            longueur = abs(x1-x2)
            ligneH[y1-1][position] = ligneH[y1-1][position] + longueur
    return ligneH

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

def pdf2score_portees(lines, height, width):
    tableauLigne = lectureTableauLigne(lines, 1, height, width)
    #critereDetection = []
    resultats = []
    for i_test in range(12):
        resultats.append(SetPortees([],[],0))
        ecart = i_test + 4
        prodConv = produitConvolution(tableauLigne, ecart,1, height)
        maxProdConv = calculMaxLocaux(prodConv,ecart,1, height)
        rechercheMax = attributMaxLocaux(maxProdConv,ecart,1)
        maxPosition = rechercheMax[0]
        maxValeur = rechercheMax[1]
        maxLargeur = rechercheMax[2]
        tableauPortees=[]
        for i_max in range(len(maxPosition)):
            #portee=Portee(ecart, maxPosition[i_max], maxValeur[i_max], maxLargeur[i_max])
            resultats[i_test].ajoutPortee(maxPosition[i_max],maxValeur[i_max])
        print("Résultat avec un écart de : " + str(ecart) + " pixels")
        print(maxPosition, maxValeur, maxLargeur)
        resultats[i_test].calculScore()
    # détermination du meilleur résultat (celui dont le score est le plus élevé)
    res_max = 0
    res_best = 0
    for i_res in range(12):
        if res_max < resultats[i_res].score_moy:
            res_max = resultats[i_res].score_moy
            res_best = i_res
    print("---------------------------")
    print("Meilleur écart identifiée : " + str(res_best + 4) + " pixels")
    print("Nombre de ligne détectées : " + str(resultats[res_best].nbre_portee))
    print("---------------------------")
    print("recherche d'éventuelle déviation des portées")
    
    ecart = 4 + res_best
    tableauLigne2 = lectureTableauLigne(lines, 3, height, width)
    prodConv2 = produitConvolution(tableauLigne2, ecart,3, height)
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
    print("déviation à gauche :  " + str(deviation[0]))
    print("déviation au centre : " + str(deviation[1]))
    print("déviation à droite :  " + str(deviation[2]))
#    for i_portee in range(resultats[res_best].nbre_portee):
#        resultats[res_best].portees[i_portee].setDevGauche(deviation[0][i_portee])
#        resultats[res_best].portees[i_portee].setDevDroite(deviation[2][i_portee])
#        resultats[res_best].portees[i_portee].setDevCentre(deviation[1][i_portee])
    return ecart, resultats[res_best], deviation

if __name__ == "__main__":
    nom_image='mendelssohn'
    img = cv2.imread(nom_image + ".jpg")
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    minLineLength = 120   #100
    maxLineGap = 16        #10
    lines = cv2.HoughLinesP(edges,1,np.pi/180,200,minLineLength,maxLineGap)
    porteesDetectees = pdf2score_portees(lines, height, width)
    ecart = porteesDetectees[0]
    for i_portee in range(porteesDetectees[1].nbre_portee):
        #ecart = porteesDetectees.portees[i_portee].ecart
        position = porteesDetectees[1].positions[i_portee]
        dev_gche = porteesDetectees[2][0][i_portee]
        dev_drte = porteesDetectees[2][2][i_portee]
        dev_ctre = porteesDetectees[2][1][i_portee]
        for i_ligne in range(5):
            y_deb = position - ecart*(i_ligne-2) + dev_gche
            y_mil = position - ecart*(i_ligne-2) + dev_drte
            y_fin = position - ecart*(i_ligne-2) + dev_ctre
            cv2.line(img,(1,y_deb),(int(width/2),y_mil),(255,0,0),1)
            cv2.line(img,(int(width/2),y_mil),(width,y_fin),(255,0,0),1)
    cv2.imwrite(nom_image + "_lignev5.jpg",img)
