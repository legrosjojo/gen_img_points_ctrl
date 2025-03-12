import cv2 as cv # type: ignore
import numpy as np
import sys
import os


##################################################################################################
#                                           DEFINE                                               #
##################################################################################################

path_mire_orig = "mire_315a.png" #chemin de la mire orignel
if path_mire_orig is None:
        sys.exit("err::Could not read the image.")    
mire_orig = cv.imread(cv.samples.findFile(path_mire_orig)) #mire originel
nrows, ncols = mire_orig.shape[:2]

modified_mire = mire_orig

virtual_focal = 75 # |warning :: valeur par defaut est 75 en mode dev|
virtual_focal_dist = ncols / (2 * np.tan(np.radians(virtual_focal / 2))) # distance focal virtuelle

#translation
t_x = 0
t_y = 0
t_z = 0
#rotation
r_x = 15
r_y = 0
r_z = 45
#si r_x et r_y déterminer l'odre 'xy' ou 'yx'
bool_rxy = None #PAS TOUCHE PTIT CON
sens_rxy = None
#scale |warning :: valeur par defaut est 1|
sc_x = 1
sc_y = 1
sc_z = 1

#important pour la translation z obligatoire en cas de rotation X et/ou Y 
if (not r_x==0)and(not r_y==0):
    bool_rxy = True
    if sens_rxy not in ['xy','yx']:
        sys.exit("err::sens_rxy")
else:
    bool_rxy = False 


inter_contours = 10
limit_area = 25

mask = [([38, 179, 38], [38, 179, 38]), ([0, 0, 255], [201, 201, 255]), ([0,0,0], [170,170,170])]
threshold = [100, 76, 30]
center_tab = []

#img, transformation, mask, hsv, grey, threshold, contours 
show_data = [True, True, True, False, False, False, True]
#parametres + "
save_data = [True, True, True, False, False, False, False, True]
if any(save_data):
    if not os.path.exists("data"):
        os.makedirs("data")



##################################################################################################
#                                   FONCTION TRANSFORMATION                                      #
##################################################################################################

#
#   MATRICE DE PROJECTION
#   

def _2Dto3D():
    return np.array([
        [1, 0, -(ncols/2)],
        [0, 1, -(nrows/2)],
        [0, 0, 0],
        [0, 0, 1]
    ], dtype=np.float32)

def _3Dto2D():
    return np.array([
        [virtual_focal_dist, 0, ncols/2, 0],
        [0, virtual_focal_dist, nrows/2, 0],
        [0, 0, 1, 0]
    ], dtype=np.float32)

#
# Les fonctions qui suivent se base sur le reperes suivant:  (le plan image est (x,y))
#
#               z  
#               |  
#               |  
#               |  
#               O----------------- y  
#              /  
#             /  
#            /  
#           x 
#

#
#   ROTATION
#   

#
# Matrices de tranformation pour effectuer une rotation autour des axes X, Y et Z
#
#   X:                            Y:                            Z:
#     [[1,      0,       0, 0]      [[ cos(b), 0, sin(b), 0]      [[cos(c), -sin(c), 0, 0]
#      [0, cos(a), -sin(a), 0]       [      0, 1,      0, 0]       [sin(c),  cos(c), 0, 0]
#      [0, sin(a),  cos(a), 0]       [-sin(b), 0, cos(b), 0]       [     0,       0, 1, 0]
#      [0,      0,       0, 1]]      [      0, 0,      0, 1]]      [     0,       0, 0, 1]]
#
#   XYZ:
#     [[ cos(b)*cos(c), cos(c)*sin(a)*sin(b) - cos(a)*sin(c), cos(a)*cos(c)*sin(b) + sin(a)*sin(c), 0]
#      [ cos(b)*sin(c), cos(a)*cos(c) + sin(a)*sin(b)*sin(c), cos(a)*sin(b)*sin(c) - cos(c)*sin(a), 0]
#      [       -sin(b),                        cos(b)*sin(a),                        cos(a)*cos(b), 0]
#      [             0,                                    0,                                    0, 1]]
#

def rotationXYZ(axis, degXYZ=None):
    if degXYZ :
        if axis.lower() in ['x','y','z']:
            radXYZ = np.radians(degXYZ) #np.cos et np.sin fonctionnent en radians
            cosXYZ, sinXYZ = np.cos(radXYZ), np.sin(radXYZ)
            if axis.lower() == 'x':  #axe x
                modified_H_part = np.array([
                    [1, 0, 0, 0],
                    [0, cosXYZ, -sinXYZ, 0],
                    [0, sinXYZ, cosXYZ, 0],
                    [0, 0, 0, 1]
                ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective 
            elif axis.lower() == 'y': #axe y
                modified_H_part = np.array([
                    [cosXYZ, 0, sinXYZ, 0],
                    [0, 1, 0, 0],
                    [-sinXYZ, 0, cosXYZ, 0],
                    [0, 0, 0, 1]
                ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective 
            else: #axe z
                modified_H_part = np.array([
                    [cosXYZ, -sinXYZ, 0, 0],
                    [sinXYZ, cosXYZ, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
                ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective   
            return modified_H_part
    return np.eye(4)

def rotationXYZBis(rx=1, ry=1, rz=0):
    radX, radY, radZ = np.radians(rx), np.radians(ry), np.radians(rz)
    cosX, cosY, cosZ = np.cos(radX), np.cos(radY), np.cos(radZ)
    sinX, sinY, sinZ = np.sin(radX), np.sin(radY), np.sin(radZ)
    return np.array([
        [cosZ*cosY, (cosZ*sinY*sinX)-(sinZ*cosX), (cosZ*sinY*cosX)+(sinZ*sinX), 0],
        [sinZ*cosY, (sinZ*sinY*sinX)+(cosZ*cosX), (sinZ*sinY*cosX)-(cosZ*sinX), 0],
        [-sinY, cosY*sinX, cosY*cosX, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective 

# faire une fonction récursive qui regarde les valeurs r_x, r_y, r_z et sens_rxyz puis fait XYZ, XZY, YXZ, YZX, ZXY ou ZYX en fonction de sens_rxyz

#
#   TRANSLATION
# 

#
# Matrice de transformation pour effectuer une translation le long des axes X, Y et Z
#                                                  
#   [[ 1,  0,  0, tx]      
#    [ 0,  1,  0, ty]       
#    [ 0,  0,  1, tz]       
#    [ 0,  0,  0,  1]]      
#

def translationXYZ(tx=0, ty=0, tz=0):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz], 
        [0, 0, 0, 1]
    ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective 

#VOIR AVEC DOIGNON :doit toujours être applique, la projection en perspective -> 2Dto3D -> 3Dto2D -> warpPerspective n'aime pas quand tout les points ont une coordonnees z=0 ou tres proche de 0, on force donc une translation en z qui correspond juste à un decalage de l'image dans l'espace (donc aucune transformation geometrique) pour devier ce probleme
def tz_rxy():
#    if (r_x==0)and(r_y==0):
#        print('yep')
#        return np.eye(4)
#    else:
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, virtual_focal_dist], #on peut mettre n'importe quel valeur
        [0, 0, 0, 1]
    ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective

#
#   MISE A L'ECHELLE
#

#
# Matrice de transformation pour effectuer une mise à l'echelle sur les axes X, Y et Z
#                                                  
#   [[ scx,   0,   0,   0]      
#    [   0, scy,   0,   0]       
#    [   0,   0, scz,   0]       
#    [   0,   0,   0,   1]]      
#

def scaleXYZ(scx, scy, scz):
    return np.array([
        [scx, 0, 0, 0],
        [0, scy, 0, 0],
        [0, 0, scz, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

#
#   SHEAR (cisaillement) 
#

# a faire ?



##################################################################################################
#                                      FONCTION CONTOURS                                         #
##################################################################################################

def maskMotif(img, inter_motif):  #BGR vert:[38, 179, 38] rouge:[0, 0, 255] noir:[0,0,0]
    mask = cv.inRange(img, np.array(inter_motif[0], dtype=np.uint8), np.array(inter_motif[1], dtype=np.uint8))
    filtered_img = np.full_like(img,255, dtype=np.uint8)
    filtered_img[mask > 0] = inter_motif[0] #if [201, 201, 255] is None else [0, 0, 255]
    return filtered_img

def grayAndThreshold(img, threshold_value, i=None):
    #hsv -> gray -> threshold fonctionne que gray -> threshold non
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    if show_data[3]:
            cv.imshow("hsv"+str(i), hsv_img)
    if save_data[4]:
        cv.imwrite("data/hsv"+str(i)+".png", hsv_img)
    gray_img = cv.cvtColor(hsv_img, code=cv.COLOR_BGR2GRAY) 
    if show_data[4]:
            cv.imshow("gray"+str(i), gray_img)
    if save_data[5]:
        cv.imwrite("data/gray"+str(i)+".png", gray_img)
    _, thresh = cv.threshold(gray_img, threshold_value, 255, 0)  #stack overflow, le threshold de filter les valeurs extremes
    return thresh

def contientDeja(list_center, x, y, inter=inter_contours):
    if len(list_center) > 0 :
        for i in range (0,len(list_center)):
            if (list_center[i][0] >= x-inter)&(list_center[i][0] <= x+inter) :
                if (list_center[i][1] >= y-inter)&(list_center[i][1] <= y+inter):
                    return True
    return False  
def findContours(img, motif=None):
    if motif is None:
        sys.exit("err::findContours motif is None")
    contours, _ = cv.findContours(image=img,
                                  mode=cv.RETR_TREE, 
                                  method=cv.CHAIN_APPROX_SIMPLE,
                                  offset=(0,0))#RETR_LIST,
    for c in contours:
        # if cv.contourArea(c) >= 90000:
            #    print("degage")
            if cv.contourArea(c) <= limit_area :
                continue    
            x,y,w,h = cv.boundingRect(c)
            if ( (x,y)!=(0,0) )&(not contientDeja(center_tab, x, y)):
                                                             #(155+(i*50)) -> du etre changer sinon contour compter comme motif pour mask[2] -> ? n'est pas sensé appliqué le mask sur une image comportnat des contours
                cv.rectangle(modified_mire, (x, y), (x + w, y + h), (171+(motif*42), 0, 0), 2)
                center_tab.append((x,y,motif)) #motif in {"rond", "trait", "cercle"}
                #print ((x,y,motif))
    
def fullContoursProcess(img):
    for i in range(0,len(mask)):
        img_mask = maskMotif(modified_mire, mask[i])
        if show_data[2]:
            cv.imshow("mask"+str(i), img_mask)
        if save_data[3]:
            cv.imwrite("data/mask"+str(i)+".png", img_mask)
        img_thresh = grayAndThreshold(img_mask, threshold[i], i)
        if show_data[5]:
            cv.imshow("thresh"+str(i), img_thresh)
        if save_data[6]:
            cv.imwrite("data/thresh"+str(i)+".png", img_thresh)
        findContours(img_thresh, i)



##################################################################################################
#                                      FONCTION ENCODAGE                                         #
##################################################################################################

def encodeur(img):
    return


##################################################################################################
#                                            MAIN                                                #
##################################################################################################

if show_data[0]:
    cv.imshow("Mire originale", mire_orig)
if save_data[1]:
    cv.imwrite("data/mire.png", mire_orig)

t = tz_rxy() @ translationXYZ(t_x,t_y,t_z) @  rotationXYZBis(r_x,r_y,r_z)
H =  _3Dto2D() @ t @ _2Dto3D() 
modified_mire = cv.warpPerspective(mire_orig, H, (ncols, nrows), None, borderValue=(255,255,255))
if show_data[1]:
    cv.imshow("Mire transformee", modified_mire)
if save_data[2]:
    cv.imwrite("data/trans.png", modified_mire)

fullContoursProcess(modified_mire)
if show_data[6]:
    cv.imshow("Contours", modified_mire)
if save_data[7]:
    cv.imwrite("data/contours.png", modified_mire)

if save_data[0]:
    parameters = {
        "path_mire_orig": path_mire_orig,
        "nrows": nrows,
        "ncols": ncols,
        "virtual_focal": virtual_focal,
        "virtual_focal_dist": virtual_focal_dist,
        "t_x": t_x,
        "t_y": t_y,
        "t_z": t_z,
        "r_x": r_x,
        "r_y": r_y,
        "r_z": r_z,
        "bool_rxy": bool_rxy,
        "sens_rxy": sens_rxy,
        "sc_x": sc_x,
        "sc_y": sc_y,
        "sc_z": sc_z,
        "inter_contours": inter_contours,
        "limit_area": limit_area,
        "mask": mask,
        "threshold": threshold,
        "show_data": show_data,
        "save_data": save_data
    }
    generated_data = {
        "center_tab": center_tab,
        "t": t.tolist() if t is not None else None,
        "H": H.tolist() if H is not None else None,  
    }
    with open("data/data.txt", "w") as file:
        file.write("                -------- PARAMETRES --------\n\n")
        for k, v in parameters.items():
            file.write(f"{k}: {v}\n")
        file.write("\n\n\n                -------- DONNEES GENEREES --------\n\n")
        for k, v in generated_data.items():
            file.write(f"{k}: {v}\n")

cv.waitKey(0)
