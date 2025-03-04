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

##################################################################################################
#                                          FONCTION                                              #
##################################################################################################

#
# ROTATION
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
        modified_H_part = np.eye(3)
        nrows, ncols = mire_orig.shape[:2]
        modified_H_part[0:2] = cv.getRotationMatrix2D((ncols // 2, nrows//2), -degZ, 1)
        return modified_H_part



##################################################################################################
#                                            MAIN                                                #
##################################################################################################
nrows, ncols = mire_orig.shape[:2]

rotatedImg = cv.warpPerspective(mire_orig, H @ rotationZ(45), (ncols, nrows), borderValue=(255, 255, 255))
cv.imshow("contours", rotatedImg)
cv.waitKey(0)
#COM code.py
#pour chaque fonction, j'envoie une image, je fabrique une matrice de transformation, je l'applique à mon image, je retourne mon image... pour tester transfo par transfo

#at the end -> je déclare une matrice de transformation MatT
#MatT= fctScale(...) @ fctRotate(...) @ fctRotate3D(...)
#warpAffine(img_orig, MatT, img.scape[:2], flag=INTER_..., borderValue=...) 

def rotate3D(degrees, axis='x', second_axis=None):
    T = np.eye(3)
    rad = np.radians(degrees)
    
    if axis == 'x':
        T = np.array([[1, 0, 0],
                      [0, np.cos(rad), -np.sin(rad)],
                      [0, np.sin(rad), np.cos(rad)]])
    elif axis == 'y':
        T = np.array([[np.cos(rad), 0, np.sin(rad)],
                      [0, 1, 0],
                      [-np.sin(rad), 0, np.cos(rad)]])
    elif axis == 'z':
        T[:2, :3] = cv.getRotationMatrix2D(center=(0, 0), angle=-degrees, scale=1.0)
    
    if second_axis:
        T2 = rotate3D(degrees, axis=second_axis)
        T = np.dot(T2, T)  # Composition des transformations
    
    return T
