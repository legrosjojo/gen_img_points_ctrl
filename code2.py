import cv2 as cv # type: ignore
import numpy as np
import sys


##################################################################################################
#                                           DEFINE                                               #
##################################################################################################
inter_contours = 10
limit_area = 25
mask = [ ([38, 179, 38], [38, 179, 38]), ([0, 0, 255], [201, 201, 255]), ([0,0,0], [170,170,170])]
centerTab=[]

path_mire_orig = "mire_315a.png" #chemin de la mire orignel
if path_mire_orig is None:
        sys.exit("err::Could not read the image.")    
mire_orig = cv.imread(cv.samples.findFile(path_mire_orig)) #mire originel
cv.imshow("Mire", mire_orig)

nrows, ncols = mire_orig.shape[:2]
virtual_focal= 75 # |warning :: valeur par defaut est 75 en mode dev|
virtual_focal_dist = ncols / (2 * np.tan(np.radians(virtual_focal / 2))) # distance focal virtuelle

#translation
t_x=0
t_y=0
t_z=0
#rotation
r_x=0
r_y=15
r_z=0
#si r_x et r_y déterminer l'odre 'xy' ou 'yx'
bool_rxy=None #PAS TOUCHE PTIT CON
sens_rxy=None
#scale |warning :: valeur par defaut est 1|
sc_x=1
sc_y=1
sc_z=1

#important pour la translation z obligatoire en cas de rotation X et/ou Y 
if (not r_x==0)and(not r_y==0):
    bool_rxy=True
    if sens_rxy not in ['xy','yx']:
        sys.exit("err::sens_rxy")
else:
    bool_rxy=False 





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

def rotationXYZ_bis(rx=1, ry=1, rz=0):
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

angle = 15

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
    print(np.sin(np.radians(0))*(ncols/2)*2)
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, virtual_focal_dist], 
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






##################################################################################################
#                                            MAIN                                                #
##################################################################################################

#H =  translationXY(ncols//2, nrows//2) @ rotationXYZ('x', 45) @ translationXY(-ncols//2, -nrows//2)
transfo= tz_rxy() @ translationXYZ(t_x,t_y,t_z) @  rotationXYZ_bis(r_x,r_y,r_z)
print(transfo)
H =  _3Dto2D() @ transfo @ _2Dto3D() 
print(H)
modImg = cv.warpPerspective(mire_orig, H, (ncols, nrows), None, borderValue=(255,255,255))
cv.imshow("Modif", modImg)

cv.waitKey(0)
