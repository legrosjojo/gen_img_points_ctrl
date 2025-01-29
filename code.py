import cv2 as cv
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

img = openShowImg("mire_315a.png")
key = cv.waitKey(0)
if key == ord('s'):
    saveImg(img)