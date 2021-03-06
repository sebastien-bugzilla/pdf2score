# -*- coding:Utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
from operator import itemgetter, attrgetter, methodcaller
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree


class Point:
    def __init__(self, x, y, nb_detection):
        self.x = x
        self.y = y
        self.x_min = x
        self.x_max = x
        self.y_min = y
        self.y_max = y
        self.nb_detection = nb_detection
        self.sum_x = float(x)
        self.sum_y = float(y)
        self.status = ""
    
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
        self.nb_detection = self.nb_detection + 1
        self.sum_x = self.sum_x + float(x_new)
        self.sum_y = self.sum_y + float(y_new)
        self.x = round(self.sum_x / self.nb_detection,2)
        self.y = round(self.sum_y / self.nb_detection,2)
        self.x_min = min(self.x_min, x_new)
        self.x_max = max(self.x_max, x_new)
        self.y_min = min(self.y_min, y_new)
        self.y_max = max(self.y_max, y_new)
    
    def get_x(self):
        return (self.x_min, self.x_max)
    
    def get_y(self):
        return (self.y_min, self.y_max)
    
    def affiche(self):
        print(self.x_min, self.x_max, self.y_min,self.y_max, self.nb_detection)
    
    def setStatus(self, status):
        self.status = status
    
    def ifOverlap(self, point):
        overlap = 0
        if (self.x_min <= point.x_max and self.x_min >= point.x_min):
            if (self.y_min <= point.y_max and self.y_min >= point.y_min):
                overlap = 1
            if (self.y_max <= point.y_max and self.y_max >= point.y_min):
                overlap = 1
        if (self.x_max <= point.x_max and self.x_max >= point.x_min):
            if (self.y_min <= point.y_max and self.y_min >= point.y_min):
                overlap = 1
            if (self.y_max <= point.y_max and self.y_max >= point.y_min):
                overlap = 1
        return overlap
    
    def fusion(self, point):
        self.x_min = min(self.x_min, point.x_min)
        self.x_max = max(self.x_max, point.x_max)
        self.y_min = min(self.y_min, point.y_min)
        self.y_max = max(self.y_max, point.y_max)
        self.sum_x = self.sum_x + point.sum_x
        self.sum_y = self.sum_y + point.sum_y
        self.nb_detection = self.nb_detection + point.nb_detection
        self.x = round(self.sum_x / self.nb_detection,2)
        self.y = round(self.sum_y / self.nb_detection,2)

class Cloud:
    def __init__(self):
        self.point_array = []
        self.point_number = 0
    
    def addPoint(self, Point):
        self.point_array.append(Point)
        self.point_number = self.point_number + 1
    
    def checkPointOverlap(self):
        for i in range(self.point_number):
            for j in range(self.point_number):
                if i <> j:
                    temp = self.point_array[i].ifOverlap(self.point_array[j])
                    if temp == 1:
                        if self.point_array[i].nb_detection > self.point_array[j].nb_detection:
                            self.point_array[i].fusion(self.point_array[j])
                            self.point_array[j].setStatus("NOK")
                        else:
                            self.point_array[j].fusion(self.point_array[i])
                            self.point_array[i].setStatus("NOK")
    
    def classifyPoint(self):
        nb_pt_ok = 0
        for i_pt in range(self.point_number):
            if self.point_array[i_pt].status <> "NOK":
                if self.point_array[i_pt].nb_detection >= 5:
                    self.point_array[i_pt].setStatus("OK")
                    nb_pt_ok = nb_pt_ok + 1
                else:
                    self.point_array[i_pt].setStatus("NOK")
        self.valid_point = nb_pt_ok
    
    def imprimeXml(self):
        # creation d'une structure xml
        cloud_xml = Element('cloud')
        nb_point_found = SubElement(cloud_xml, 'nb_point_found')
        nb_point_found.text = str(self.valid_point)
        nb_point_valid = 0
        for i_pt in range(self.point_number):
            if self.point_array[i_pt].status == "OK":
                nb_point_valid = nb_point_valid + 1
                point = SubElement(cloud_xml, 'point')
                rank = SubElement(point, 'rank')
                rank.text = str(nb_point_valid)
                x_min = SubElement(point, 'x_min')
                x_min.text = str(self.point_array[i_pt].x_min)
                x_max = SubElement(point, 'x_max')
                x_max.text = str(self.point_array[i_pt].x_max)
                y_min = SubElement(point, 'y_min')
                y_min.text = str(self.point_array[i_pt].y_min)
                y_max = SubElement(point, 'y_max')
                y_max.text = str(self.point_array[i_pt].y_max)
                x = SubElement(point, 'x')
                x.text = str(self.point_array[i_pt].x)
                y = SubElement(point, 'y')
                y.text = str(self.point_array[i_pt].y)
                status = SubElement(point, 'status')
                status.text = str(self.point_array[i_pt].status)
                nb_detection = SubElement(point, 'nb_detection')
                nb_detection.text = str(self.point_array[i_pt].nb_detection)
        self.xml = cloud_xml


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def pdf2score_notes(nom_fichier, loc1, loc2, loc3, size_template):
    tabRes = []
    for i_pt in range(len(loc1[0])):
        detection=[loc1[1][i_pt] + size_template[1]/2, loc1[0][i_pt] + size_template[0]/2-2]
        tabRes.append(detection)
    for i_pt in range(len(loc2[0])):
        detection=[loc2[1][i_pt] + size_template[3]/2, loc2[0][i_pt] + size_template[2]/2-2]
        tabRes.append(detection)
    for i_pt in range(len(loc3[0])):
        detection=[loc3[1][i_pt] + size_template[5]/2, loc3[0][i_pt] + size_template[4]/2-2]
        tabRes.append(detection)
    tabResOrdre = sorted(tabRes, key=itemgetter(1,0))
    nb_res = len(tabResOrdre)
    cloud_result = Cloud()
    nb_point=0
    historique=50
    for i_pt in range(nb_res):
        x_new = tabResOrdre[i_pt][0]
        y_new = tabResOrdre[i_pt][1]
        si_existant = 0
        if i_pt == 0:
            si_existant = 0
            nb_last_point = 0
        else:
            nb_last_point = min(historique, nb_point)
            for i_point in range(nb_last_point):
                if cloud_result.point_array[nb_point - nb_last_point + i_point].testPoint(x_new, y_new) == 1:
                    cloud_result.point_array[nb_point - nb_last_point + i_point].ajoutPoint(x_new, y_new)
                    si_existant = 1
        if si_existant == 0:
            onePoint = Point(x_new, y_new, 1)
            cloud_result.addPoint(onePoint)
            nb_point = nb_point + 1
        x_old = x_new
        y_old = y_new
    cloud_result.checkPointOverlap()
    cloud_result.classifyPoint()
    cloud_result.imprimeXml()
    fichier_xml = open(nom_fichier + '_notes.xml', 'w')
    fichier_xml.write(prettify(cloud_result.xml))
    fichier_xml.close()
    return cloud_result


if __name__ == "__main__":
    nom_image = 'beethoven'
    img_rgb = cv2.imread(nom_image + '.jpg')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    threshold = 0.60
    tabRes = []
    template1 = cv2.imread('elm_lily_note23_1.png',0)
    res1 = cv2.matchTemplate(img_gray, template1, cv2.TM_CCOEFF_NORMED)
    loc1 = np.where(res1 > threshold)
    
    template2 = cv2.imread('elm_lily_note23_2.png',0)
    res2 = cv2.matchTemplate(img_gray, template2, cv2.TM_CCOEFF_NORMED)
    loc2 = np.where(res2 > threshold)
    
    template3 = cv2.imread('elm_lily_note23_3.png',0)
    res3 = cv2.matchTemplate(img_gray, template3, cv2.TM_CCOEFF_NORMED)
    loc3 = np.where(res3 > threshold)
    
    width_template1, height_template1 = template1.shape[::-1]
    width_template2, height_template2 = template2.shape[::-1]
    width_template3, height_template3 = template3.shape[::-1]
    size_template= []
    size_template.append(width_template1)
    size_template.append(height_template1)
    size_template.append(width_template2)
    size_template.append(height_template2)
    size_template.append(width_template3)
    size_template.append(height_template3)
    result = pdf2score_notes(nom_image, loc1, loc2, loc3, size_template)
    for i in range(result.point_number):
        if result.point_array[i].status == "OK":
            x_min = result.point_array[i].x_min
            x_max = result.point_array[i].x_max
            y_min = result.point_array[i].y_min
            y_max = result.point_array[i].y_max
            cv2.rectangle(img_rgb, (x_min, y_min), (x_max, y_max), (0,0,255), 1)
    cv2.imwrite('res_' + str(nom_image) + '_nuage3.png',img_rgb)
