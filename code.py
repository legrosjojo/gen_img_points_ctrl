import cv2 as cv
import sys

img_path = "mire_315a.png"
img_orig = cv.imread(cv.samples.findFile(img_path))

if img_orig is None:
    sys.exit("err::Could not read the image.")

cv.imshow("Display window", img_orig)
key = cv.waitKey(0)
