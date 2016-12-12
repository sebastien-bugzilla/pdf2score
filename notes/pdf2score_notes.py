# -*- coding:Utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller

class nuage:
    def __init__(self, x, y, nbrePoints):
        self.x = x
        self.y = y
        self.x_min = x
        self.x_max = x
        self.y_min = y
        self.y_max = y
        self.nbrePoints = nbrePoints
    
    def testPoint(self, x_new, y_new):
        if (self.x_min-2<=x_new and x_new <= self.x_max + 2):
            si_ok_x = 1
        else:
            si_ok_x = 0
        if (self.y_min-2<=y_new and y_new <= self.y_max + 2):
            si_ok_y = 1
        else:
            si_ok_y = 0
        return si_ok_x * si_ok_y
    
    def ajoutPoint(self, x_new, y_new):
        self.nbrePoints = self.nbrePoints + 1
        self.x_min = min(self.x_min, x_new)
        self.x_max = max(self.x_max, x_new)
        self.y_min = min(self.y_min, y_new)
        self.y_max = max(self.y_max, y_new)
    
    def get_x(self):
        return (self.x_min, self.x_max)
    
    def get_y(self):
        return (self.y_min, self.y_max)
    
    def affiche(self):
        print(self.x_min, self.x_max, self.y_min,self.y_max, self.nbrePoints)


def pdf2score_notes(loc1, loc2, size_template):
    tabRes = []
    for i_pt in range(len(loc1[0])):
        point=[loc1[1][i_pt] + size_template[1]/2, loc1[0][i_pt] + size_template[0]/2-2]
        tabRes.append(point)
    for i_pt in range(len(loc2[0])):
        point=[loc2[1][i_pt] + size_template[3]/2, loc2[0][i_pt] + size_template[2]/2-2]
        tabRes.append(point)
    tabResOrdre = sorted(tabRes, key=itemgetter(1,0))
#    for i in range(len(tabResOrdre)):
#        print(tabResOrdre[i][0],tabResOrdre[i][1])
    nb_res = len(tabResOrdre)
    tabNuage = []
    nb_ligne=0
    historique=10
    for i_pt in range(nb_res):
        x_new = tabResOrdre[i_pt][0]
        y_new = tabResOrdre[i_pt][1]
        si_existant = 0
# %%%%%%% début méthode 1
#        for i_nuage in range(len(tabNuage)):
#            if tabNuage[i_nuage].testPoint(x_new, y_new) == 1:
#                si_existant = 1
#                tabNuage[i_nuage].ajoutPoint(x_new, y_new)
#                positionX=tabNuage[i_nuage].get_x()
#                positionY=tabNuage[i_nuage].get_y()
#                print("i_pt = " + str(i_pt) + " / nb_ligne = " + str(nb_ligne) +\
#                    " / " + str(x_new) + ", " + str(y_new) + " ajouté à " +\
#                    str(positionX[0]) + ", " + str(positionX[1]) + " / " +\
#                    str(positionY[0]) + ", " + str(positionY[1]))
#        if si_existant == 0:
#            tabNuage.append(nuage(x_new, y_new, 1))
#            print("i_pt = " + str(i_pt) + " / nb_ligne = " + str(nb_ligne) +\
#                " / " + str(x_new) + ", " + str(y_new) + " créé")
#        x_old = x_new
#        y_old = y_new
#    tabNoteTemp = []
#    for i_nuage in range(len(tabNuage)):
#        if tabNuage[i_nuage].nbrePoints >= 5:
#            tabNoteTemp.append(tabNuage[i_nuage])
#            tabNuage[i_nuage].affiche()
# %%%%%%% fin méthode 1
# %%%%%%% début méthode 2
        if i_pt == 0:
            tabNuage.append([])
            #tabNuage[nb_ligne].append(nuage(x_new, y_new,1))
        else:
            if y_new != y_old:
                #print("----- nouvelle ligne -----")
                nb_ligne = nb_ligne + 1
                tabNuage.append([])
            num_old_line = min(historique, nb_ligne)
            for i_lig in range(num_old_line):
                for i_nuage in range(len(tabNuage[nb_ligne-i_lig])):
                    if tabNuage[nb_ligne-i_lig][i_nuage].testPoint(x_new, y_new) == 1:
                        tabNuage[nb_ligne-i_lig][i_nuage].ajoutPoint(x_new, y_new)
                        si_existant = 1
#                        positionX=tabNuage[nb_ligne-i_lig][i_nuage].get_x()
#                        positionY=tabNuage[nb_ligne-i_lig][i_nuage].get_y()
#                        print("i_pt = " + str(i_pt) + " / nb_ligne = " + str(nb_ligne) +\
#                            " / " + str(x_new) + ", " + str(y_new) + " ajouté à " +\
#                            str(positionX[0]) + ", " + str(positionX[1]) + " / " +\
#                            str(positionY[0]) + ", " + str(positionY[1]))
        if si_existant == 0:
            tabNuage[nb_ligne].append(nuage(x_new, y_new,1))
#            print("i_pt = " + str(i_pt) + " / nb_ligne = " + str(nb_ligne) +\
#                " / " + str(x_new) + ", " + str(y_new) + " créé")
        x_old = x_new
        y_old = y_new
    # verif de ce qu'on a trouvé
#    for i in range(len(tabNuage)):
#        for j in range(len(tabNuage[i])):
#            tabNuage[i][j].affiche()
    tabNoteTemp = []
    for i_lig in range(len(tabNuage)):
        for i_nuage in range(len(tabNuage[i_lig])):
            if tabNuage[i_lig][i_nuage].nbrePoints >= 5:
                tabNoteTemp.append(tabNuage[i_lig][i_nuage])
                tabNuage[i_lig][i_nuage].affiche()
# %%%%%%% fin méthode 2
    return tabNoteTemp


if __name__ == "__main__":
    img_rgb = cv2.imread('bach1.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    threshold = 0.60
    tabRes = []
    template1 = cv2.imread('elm_lily_note23_1.png',0)
    res1 = cv2.matchTemplate(img_gray, template1, cv2.TM_CCOEFF_NORMED)
    loc1 = np.where(res1 > threshold)
    
    template2 = cv2.imread('elm_lily_note23_2.png',0)
    res2 = cv2.matchTemplate(img_gray, template2, cv2.TM_CCOEFF_NORMED)
    loc2 = np.where(res2 > threshold)
    
    width_template1, height_template1 = template1.shape[::-1]
    width_template2, height_template2 = template2.shape[::-1]
    size_template= []
    size_template.append(width_template1)
    size_template.append(height_template1)
    size_template.append(width_template2)
    size_template.append(height_template2)
#    print("--------------------------")
#    print("template 1")
#    print("--------------------------")
#    for i in range(len(loc1[0])):
#        print(loc1[0][i],loc1[1][i])
#    print("--------------------------")
#    print("template 2")
#    print("--------------------------")
#    for i in range(len(loc2[0])):
#        print(loc2[0][i],loc2[1][i])
    #width_partition, height_partition = img_gray.shape[::-1]
    tabNuage = pdf2score_notes(loc1, loc2, size_template)
    for i in range(len(tabNuage)):
        x_min = tabNuage[i].x_min
        x_max = tabNuage[i].x_max
        y_min = tabNuage[i].y_min
        y_max = tabNuage[i].y_max
        cv2.rectangle(img_rgb, (x_min, y_min), (x_max, y_max), (0,0,255), 1)
    cv2.imwrite('res_bach1_nuage.png',img_rgb)
