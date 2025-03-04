import cv2 as cv # type: ignore
import numpy as np
import sys

##################################################################################################
#                                           DEFINE                                               #
##################################################################################################
inter_contours = 10
limit_area = 25

H = np.eye(3) #matrice de transformation H ->np.eye matrice identite

path_mire_orig = "mire_315a.png" #chemin de la mire orignel

if path_mire_orig is None:
        sys.exit("err::Could not read the image.")    
mire_orig = cv.imread(cv.samples.findFile(path_mire_orig)) #mire originel
cv.imshow("Mire", mire_orig)

nrows, ncols = mire_orig.shape[:2]

##################################################################################################
#                                          FONCTION                                              #
##################################################################################################

#
#   ROTATION
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

def rotationZ(degZ=None):
    if degZ:
        radZ = np.radians(degZ) #np.cos et np.sin fonctionnent en radians
        cosZ, sinZ = np.cos(radZ), np.sin(radZ)
        #modified_H_part = np.eye(3)
        modified_H_part = np.array([
            [cosZ, -sinZ, 0],
            [sinZ, cosZ, 0],
            [0, 0, 1]
        ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec l'opérateur @ 
        return modified_H_part

def rotationXY( axis, degXY=None):
    if degXY:
        if axis.lower() in ['x','y']:

            radXY = np.radians(degXY) #np.cos et np.sin fonctionnent en radians
            cosXY, sinXY = np.cos(radXY), np.sin(radXY)
            #modified_H_part = np.eye(3)
            if axis == 'x':  #axe x
                modified_H_part = np.array([
                    [1, 0, 0],
                    [0, cosXY, -sinXY],
                    [0, sinXY, cosXY]
                ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec l'opérateur @ 
            else: #axe y
                modified_H_part = np.array([
                    [cosXY, 0, sinXY],
                    [0, 1, 0],
                    [-sinXY, 0, cosXY]
                ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec l'opérateur @ 
            return modified_H_part

#
#   TRANSLATION
#

def translation(x, y):
    return np.array([
        [1, 0, x],
        [0, 1, y],
        [0, 0, 1]
    ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec l'opérateur @ 


##################################################################################################
#                                            MAIN                                                #
##################################################################################################
nrows, ncols = mire_orig.shape[:2]
#@ rotationXY('X', 15)
T1, T2 = translation(ncols//2, nrows//2), translation(-ncols//2, -nrows//2)
R = rotationZ(45) @ rotationXY('X', 90)
H = T1 @ R @ T2
rotatedImg = cv.warpPerspective(mire_orig, H , (ncols, nrows), borderValue=(255, 255, 255))
cv.imshow("contours", rotatedImg)
cv.waitKey(0)

#COM code.py
#pour chaque fonction, j'envoie une image, je fabrique une matrice de transformation, je l'applique à mon image, je retourne mon image... pour tester transfo par transfo

#at the end -> je déclare une matrice de transformation MatT
#MatT= fctScale(...) @ fctRotate(...) @ fctRotate3D(...)
#warpAffine(img_orig, MatT, img.scape[:2], flag=INTER_..., borderValue=...) 
