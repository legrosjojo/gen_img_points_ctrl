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

def rotationImg(img, rotDeg, resizeBool,color):#sens antihoraire
    #img size
    nrows, ncols = img.shape[:2]
    if resizeBool :
        # Compute the translation and the new image size
        transformation_matrix = cv.getRotationMatrix2D((0,0), rotDeg, 1)
        original_corners = np.array([[0, 0], [ncols, 0], [ncols, nrows], [0, nrows]]).T
        new_corners = np.int32(np.dot(transformation_matrix[:, :2], original_corners))
        x, y, ncols, nrows = cv.boundingRect(new_corners.T.reshape(1, 4, 2))
        transformation_matrix[:, 2] = [-x, -y]
    else :
        # Compute the translation and keep the original image size
        transformation_matrix = cv.getRotationMatrix2D((ncols // 2, nrows//2), rotDeg, 1)

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




img_orig = openShowImg("mire_315a.png")

modifImg = rotationImg(img_orig, 45, True, (255,255,255))
modifImg= scaleImg(modifImg, 0.5)

cv.imshow("Modif", modifImg)
key = cv.waitKey(0)
if key == ord('s'):
    saveImg(modifImg)

