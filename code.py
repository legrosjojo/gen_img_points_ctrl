import cv2 as cv
import numpy as np
import sys

def openShowImg(img_path):
    '''
    This function open and show an img
    Args:
        img_path: path to an image

    Returns:
        An opened image

    Exemples:
        >>>openShowImg("mire_315a.png")
    '''
    #img_path = "mire_315a.png"
    if img_path is None:
        sys.exit("err::Could not read the image.")
    
    img_orig = cv.imread(cv.samples.findFile(img_path))
    
    cv.imshow("Display window", img_orig)
    key = cv.waitKey(0)
    return img_orig

def saveImg(img):
    cv.imwrite("img_modif.png", img)
    return

def rotationImg(img, rotDeg, resizeBool,color=(255,255,255)):#sens antihoraire
    #img size
    nrows, ncols = img.shape[:2]
    if resizeBool :
        # Compute the translation and the new image size
        transformation_matrix = cv.getRotationMatrix2D((0,0), -rotDeg, 1)
        orig_corners = np.array([[0, 0], [ncols, 0], [ncols, nrows], [0, nrows]]).T
        new_corners = np.int32(np.dot(transformation_matrix[:, :2], orig_corners))
        x, y, ncols, nrows = cv.boundingRect(new_corners.T.reshape(1, 4, 2))
        transformation_matrix[:, 2] = [-x, -y]
    else :
        # Compute the translation and keep the original image size
        transformation_matrix = cv.getRotationMatrix2D((ncols // 2, nrows//2), -rotDeg, 1)

    #Compute the rotation part of the affine transformation
    rotatedImg = cv.warpAffine(img, transformation_matrix, (ncols, nrows), borderValue=color) #(B,G,R)
    return rotatedImg

def scaleImg(img, s):#s>1=zoom & s<1=dezoom
    nrows, ncols = img.shape[:2]
    cx, cy= ncols // 2, nrows // 2
    transformation_matrix = np.array([
        [s, 0, cx * (1 - s)],
        [0, s, cy * (1 - s)]
    ], 
    dtype=np.float32)
    #
    scaledImg = cv.warpAffine(img, transformation_matrix, (ncols, nrows), flags=cv.INTER_AREA, borderValue=(255,255,255))
    return scaledImg

def rotation3D(img, rot3D, axe='x'):
    nrows, ncols = img.shape[:2]
    rot3D_rad = np.radians(rot3D) #pour sin&cos

    src_pts = np.float32([[0, 0], 
                          [ncols, 0], 
                          [ncols, nrows], 
                          [0, nrows]])

    if axe == 'x':  #axe x
        offset = int(nrows * 0.3 * np.sin(rot3D_rad)) 
        dst_pts = np.float32([[0, offset],  # ht-gauche
                              [ncols, - offset],  # ht-droit
                              [ncols, nrows + offset],  # bas-droit
                              [0, nrows - offset]  # bas-gauche
        ])
    else:#axe y
        offset = int(ncols * 0.3 * np.sin(rot3D_rad))
        dst_pts = np.float32([[offset, 0],  # ht-gauche
                              [ncols - offset, 0],  # ht-droit
                              [ncols + offset, nrows],  # bas-droit
                              [-offset, nrows]  # bas-gauche
        ])
  
    transformation_matrix = cv.getPerspectiveTransform(src_pts, dst_pts)
    rot3DImg = cv.warpPerspective(img, transformation_matrix, (ncols, nrows), borderValue=(255, 255, 255)) # regarder borderMode
    return rot3DImg

def maskColor(img, colorMask):  #BGR vert:[38, 179, 38] rouge:[0, 0, 255] noir:[0,0,0]
    mask= np.all(img==colorMask,axis=-1)
    img_colorMask = np.full_like(img,255)
    img_colorMask[mask] = colorMask
    return  img_colorMask



img_orig = openShowImg("mire_315a.png")
mask = [[38, 179, 38],[0, 0, 255],[0,0,0]]
img = maskColor(img_orig,mask[1])
cv.imshow("maskColor1", img )
cv.imwrite("img/mask.png", img)

#erreur FindContours supports only CV_8UC1 images when mode != CV_RETR_FLOODFILL
img = cv.cvtColor(img, code=cv.COLOR_BGR2GRAY) #convertion image vers format CV_8UC1, içi en niveau de gris 
ret, thresh = cv.threshold(img, 127, 255, 0)  #stack overflow, le threshold de filter les valeurs extremes
#recup les contours (tous les points)
contours, hierarchy = cv.findContours(image=thresh,
                                      mode=cv.RETR_TREE, 
                                      method=cv.CHAIN_APPROX_SIMPLE,
                                      offset=(0,0))#RETR_LIST,
#dessine et donne le milieu de chaque contours 
for c in contours:
        if cv.contourArea(c) <= 50 :
            continue    
        x,y,w,h = cv.boundingRect(c)
        cv.rectangle(img_orig, (x, y), (x + w, y + h), (255, 0,255), 2)
        center = (x,y)
        print (center)

#cv.imshow("maskColor2", maskColor(img_orig,mask[1]) )
#cv.imshow("maskColor3", maskColor(img_orig,mask[2]) )
modifImg = rotationImg(img_orig, 20, False)
modifImg = rotation3D(modifImg, 15)
cv.imshow("rotation3D", modifImg)

key = cv.waitKey(0)
if key == ord('s'):
    saveImg(modifImg)
cv.destroyAllWindows()

#pour chaque fonction, j'envoie une image, je fabrique une matrice de transformation, je l'applique à mon image, je retourne mon image... pour tester transfo par transfo

#at the end -> je déclare une matrice de transformation MatT
#MatT= fctScale(...) @ fctRotate(...) @ fctRotate3D(...)
#warpAffine(img_orig, MatT, img.scape[:2], flag=INTER_..., borderValue=...) 

#faire doxypypy
#faire script test
