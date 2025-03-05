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

virtual_focal=70

##################################################################################################
#                                          FONCTION                                              #
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
    virtual_focal_dist = ncols / (2 * np.tan(np.radians(virtual_focal / 2))) # distance focal virtuelle
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

def rotationXYZ_bis(rx=0, ry=0, rz=0):
    radX, radY, radZ = np.radians(rx), np.radians(ry), np.radians(rz)
    cosX, cosY, cosZ = np.cos(radX), np.cos(radY), np.cos(radZ)
    sinX, sinY, sinZ = np.sin(radX), np.sin(radY), np.sin(radZ)
    return np.array([
        [cosZ*cosY, (cosZ*sinY*sinX)-(sinZ*cosX), (cosZ*sinY*cosX)+(sinZ*sinX), 0],
        [sinZ*cosY, (sinZ*sinY*sinX)+(cosZ*cosX), (sinZ*sinY*cosX)-(cosZ*sinX), 0],
        [-sinY, cosY*sinX, cosY*cosX, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective 


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

angle = 45

def translationXY(tx=None, ty=None, tz=None):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, np.sin(angle)*(nrows//2)*2], 
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
#                                            MAIN                                                #
##################################################################################################

#H =  translationXY(ncols//2, nrows//2) @ rotationXYZ('x', 45) @ translationXY(-ncols//2, -nrows//2)
r=rotationXYZ_bis(rz=angle)
transfo = translationXY(0,0) @ r
H =  _3Dto2D() @ transfo @ _2Dto3D() 
rotatedImg = cv.warpPerspective(mire_orig, H, (ncols, nrows), None, borderValue=(255,255,255))
cv.imshow("Modif", rotatedImg)

cv.waitKey(0)
