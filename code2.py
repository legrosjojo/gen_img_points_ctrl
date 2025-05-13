import cv2 as cv # type: ignore
import numpy as np
import sys
import os
import math
import tkinter
import tkinter.messagebox
import cv2 as cv
import numpy as np
import customtkinter


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                                           DEFINE                                              #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## @var path_mire_orig
#  Path to the original target image.
path_mire_orig = "mire_315a.png"
if path_mire_orig is None:
    sys.exit("err::Could not read the image.")

## @var mire_orig
#  Original target image.
mire_orig = cv.imread(cv.samples.findFile(path_mire_orig))
nrows, ncols = mire_orig.shape[:2]

## @var modified_mire
#  Modified version of the original target image.
modified_mire = mire_orig
transformed_mire = mire_orig.copy()
contours_mire=None

## @var virtual_focal
#  Virtual focal length (default: 75 in dev mode).
virtual_focal = 75

## @var virtual_focal_dist
#  Virtual focal distance.
virtual_focal_dist = ncols / (2 * np.tan(np.radians(virtual_focal / 2)))

# Translation
## @var t_x
#  Translation along the X-axis.
t_x = 0

## @var t_y
#  Translation along the Y-axis.
t_y = 0

## @var t_z
#  Translation along the Z-axis.
t_z = 20

# Rotation
## @var r_x
#  Rotation around the X-axis.
r_x = 20

## @var r_y
#  Rotation around the Y-axis.
r_y = 0

## @var r_z
#  Rotation around the Z-axis.
r_z = 46

## @var bool_rxy
#  Determines the rotation order 'xy' or 'yx' when both r_x and r_y are used.
bool_rxy = None  # PAS TOUCHE PTIT CON

## @var sens_rxy
#  Specifies the rotation order ('xy' or 'yx') when both r_x and r_y are used.
sens_rxy = None

# Scale
## @var sc_x
#  Scaling factor along the X-axis (default: 1).
sc_x = 1

## @var sc_y
#  Scaling factor along the Y-axis (default: 1).
sc_y = 1

## @var sc_z
#  Scaling factor along the Z-axis (default: 1).
sc_z = 1

# Important for Z-translation when both X and Y rotations are applied
if (not r_x == 0) and (not r_y == 0):
    bool_rxy = True
    if sens_rxy not in ['xy', 'yx']:
        sys.exit("err::sens_rxy")
else:
    bool_rxy = False

## @var inter_contours
#  Inter-contour spacing.
inter_contours = 10

## @var limit_area
#  Minimum contour area to be considered.
limit_area = 25
limit_extrm_angle = 5.0

## @var mask
#  List of color masks.
mask = [([38, 179, 38], [38, 179, 38]), ([0, 0, 255], [201, 201, 255]), ([0, 0, 0], [170, 170, 170])]

## @var threshold
#  Threshold values for each mask.
threshold = [100, 76, 30]

## @var center_tab
#  List of detected contour centers.
center_tab = []
angle_tab=[]

## @var show_data
#  Flags to show different stages of processing (img, transformation, mask, hsv, grey, threshold, contours, contours min rouge).
show_data = [False, False, False, False, False, False, False, False]

## @var save_data
#  Flags to save different stages of processing (parameters, img, transformation, mask, hsv, grey, threshold, contours, contours min rouge).
save_data = [False, False, False, False, False, False, False, False, False]

# Create 'data' directory if any save option is enabled
if any(save_data):
    if not os.path.exists("data"):
        os.makedirs("data")
## @var max_distance_search_pixel
#  Maximum radius of pixel for pixel searching (default : 50)
max_distance_search_pixel = 50


##################################################################################################
#                                   FONCTION TRANSFORMATION                                      #
##################################################################################################

#
#   MATRICE DE PROJECTION
#   

def _2Dto3D():
    '''
    This function creates a 2D to 3D transformation matrix that centers the image coordinates.

    Args:
        None

    Returns:
        np.ndarray: A 4x4 transformation matrix of type float32.

    Examples:
        >>> matrix = _2Dto3D()
    '''
    return np.array([
        [1, 0, -(ncols/2)],
        [0, 1, -(nrows/2)],
        [0, 0, 0],
        [0, 0, 1]
    ], dtype=np.float32)

def _3Dto2D():
    '''
    This function creates a 3D to 2D projection matrix to simulate a virtual camera.

    Args:
        None

    Returns:
        np.ndarray: A 3x4 projection matrix of type float32.

    Examples:
        >>> projection_matrix = _3Dto2D()
    '''
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
    '''
    This function creates a 4x4 rotation matrix around a specified axis (X, Y, or Z) by a given angle in degrees.

    Args:
        axis (str): The axis of rotation ('x', 'y', or 'z').
        degXYZ (float, optional): The angle of rotation in degrees. Defaults to None.

    Returns:
        np.ndarray: A 4x4 rotation matrix of type float32. If no angle is provided, returns the identity matrix.

    Examples:
        >>> rot_x = rotationXYZ('x', 45)
        >>> rot_y = rotationXYZ('y', 30)
        >>> rot_z = rotationXYZ('z', 90)
        >>> identity = rotationXYZ('x')

    Notes:
        - Uses radians for trigonometric functions.
        - The matrix is compatible with `cv.warpPerspective` due to dtype=np.float32.
    '''
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
    '''
    This function creates a 4x4 rotation matrix combining rotations around the X, Y, and Z axes.

    Args:
        rx (float, optional): Rotation angle around the X-axis in degrees. Defaults to 1.
        ry (float, optional): Rotation angle around the Y-axis in degrees. Defaults to 1.
        rz (float, optional): Rotation angle around the Z-axis in degrees. Defaults to 0.

    Returns:
        np.ndarray: A 4x4 rotation matrix of type float32.

    Examples:
        >>> rot_matrix = rotationXYZBis(45, 30, 60)
        >>> identity = rotationXYZBis(0, 0, 0)

    Notes:
        - Uses radians for trigonometric functions.
        - The matrix is compatible with `cv.warpPerspective` due to dtype=np.float32.
        - Combines the rotations around each axis in a single matrix.
    '''
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
    '''
    This function creates a 4x4 translation matrix to move an object along the X, Y, and Z axes.

    Args:
        tx (float, optional): Translation along the X-axis. Defaults to 0.
        ty (float, optional): Translation along the Y-axis. Defaults to 0.
        tz (float, optional): Translation along the Z-axis. Defaults to 0.

    Returns:
        np.ndarray: A 4x4 translation matrix of type float32.

    Examples:
        >>> translation = translationXYZ(10, 20, 30)
        >>> no_translation = translationXYZ()

    Notes:
        - The matrix is compatible with `cv.warpPerspective` due to dtype=np.float32.
        - Can be combined with rotation matrices for more complex transformations.
    '''
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz], 
        [0, 0, 0, 1]
    ], dtype=np.float32) #np.array avec dtype=np.float32 pour être compatible avec warpPerspective 

#VOIR AVEC DOIGNON :doit toujours être applique, la projection en perspective -> 2Dto3D -> 3Dto2D -> warpPerspective n'aime pas quand tout les points ont une coordonnees z=0 ou tres proche de 0, on force donc une translation en z qui correspond juste à un decalage de l'image dans l'espace (donc aucune transformation geometrique) pour devier ce probleme
def tz_rxy():
    '''
    This function creates a 4x4 translation matrix along the Z-axis, typically used to simulate perspective effects.

    Args:
        None

    Returns:
        np.ndarray: A 4x4 translation matrix of type float32.

    Examples:
        >>> tz_matrix = tz_rxy()

    Notes:
        - Translates along the Z-axis by the value of `virtual_focal_dist`.
        - Compatible with `cv.warpPerspective` due to dtype=np.float32.
        - The parameter `virtual_focal_dist` should be defined globally before calling this function.
    '''
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
    '''
    This function creates a 4x4 scaling matrix to apply scaling transformations along the X, Y, and Z axes.

    Args:
        scx (float): Scaling factor along the X-axis.
        scy (float): Scaling factor along the Y-axis.
        scz (float): Scaling factor along the Z-axis.

    Returns:
        np.ndarray: A 4x4 scaling matrix of type float32.

    Examples:
        >>> scale_matrix = scaleXYZ(2, 2, 2)  # Uniform scaling
        >>> stretch_x = scaleXYZ(1.5, 1, 1)   # Stretch along X-axis

    Notes:
        - Compatible with `cv.warpPerspective` due to dtype=np.float32.
        - Can be combined with translation and rotation matrices for more complex transformations.
    '''
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
    '''
    This function creates a mask to filter specific color ranges in an image and replaces them with a specified color.

    Args:
        img (np.ndarray): Input image (BGR format).
        inter_motif (list of list): List containing two BGR color values representing the lower and upper bounds of the color range to mask.

    Returns:
        np.ndarray: Filtered image where the detected colors are replaced by the lower bound color of `inter_motif`.

    Examples:
        >>> inter_motif = [[38, 179, 38], [0, 0, 255]]  # Green and Red in BGR
        >>> masked_img = maskMotif(input_image, inter_motif)

    Notes:
        - `cv.inRange` is used to create the mask, detecting pixels within the specified BGR range.
        - Pixels in the range are replaced by `inter_motif[0]` in the output image.
        - The result is an image with the same shape and type as the input but with masked areas replaced.
    '''
    mask = cv.inRange(img, np.array(inter_motif[0], dtype=np.uint8), np.array(inter_motif[1], dtype=np.uint8))
    filtered_img = np.full_like(img,255, dtype=np.uint8)
    filtered_img[mask > 0] = inter_motif[0] #if [201, 201, 255] is None else [0, 0, 255]
    return filtered_img

def grayAndThreshold(img, threshold_value, i=None):
    '''
    Converts an image to HSV, then to grayscale, and applies a threshold.

    Args:
        img (np.ndarray): Input image in BGR format.
        threshold_value (int): Threshold value used for binarization (0 to 255).
        i (int, optional): Index used for saving and displaying images, useful in iterative processes.

    Returns:
        np.ndarray: Thresholded binary image.

    Examples:
        >>> thresh_img = grayAndThreshold(input_image, 127)

    Notes:
        - Converts the input BGR image to HSV before converting to grayscale.
        - Displays intermediate HSV and grayscale images if `show_data` is enabled.
        - Saves intermediate images if `save_data` is enabled.
        - Uses `cv.threshold` to filter extreme values in the grayscale image.
    '''
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
    '''
    Checks if a point (x, y) is already present in a list of centers within a given tolerance.

    Args:
        list_center (list of tuples): List of (x, y) coordinates representing centers.
        x (int or float): X-coordinate of the point to check.
        y (int or float): Y-coordinate of the point to check.
        inter (int, optional): Tolerance for considering points as duplicates (default is inter_contours).

    Returns:
        bool: True if the point (x, y) is already in the list within the tolerance, False otherwise.

    Examples:
        >>> centers = [(100, 200), (150, 250)]
        >>> contientDeja(centers, 102, 198, 5)
        True
        >>> contientDeja(centers, 300, 400, 5)
        False

    Notes:
        - Compares each point in `list_center` with (x, y) using a square region of ±`inter` pixels.
        - Returns True as soon as a match is found.
    '''
    if len(list_center) > 0 :
        for i in range (0,len(list_center)):
            if (list_center[i][0] >= x-inter)&(list_center[i][0] <= x+inter) :
                if (list_center[i][1] >= y-inter)&(list_center[i][1] <= y+inter):
                    return True
    return False  

def findContours(img, motif=None):
    """
    Finds contours in a binary image and calculates the center of each contour,
    adding the center coordinates and motif type to the global list `center_tab`.

    Args:
        img (numpy.ndarray): Binary image (usually obtained after thresholding).
        motif (int): Identifier for the type of contour detected (e.g., "rond", "trait", "cercle").
                     Must be provided; otherwise, the function will exit.

    Returns:
        None: The function modifies the global variable `center_tab`.

    Raises:
        SystemExit: If `motif` is None, the program exits with an error message.

    Notes:
        - Uses `cv.findContours` to retrieve the contours.
        - Filters contours by area using the global `limit_area` variable.
        - Calculates the centroid (center) of each contour using `cv.moments`.
        - Checks for duplicate contours using the `contientDeja` function before adding new ones.

    Global Variables:
        - center_tab (list): Stores detected contour centers with their motifs.
        - limit_area (int): Minimum area required for a contour to be considered.
    """
    if motif is None:
        sys.exit("err::findContours motif is None")

    contours, _ = cv.findContours(
        image=img,
        mode=cv.RETR_TREE,
        method=cv.CHAIN_APPROX_SIMPLE,
        offset=(0, 0)
    )  # RETR_LIST,
    for c in contours:
        if cv.contourArea(c) <= limit_area:
            continue

        # Calculer les moments du contour
        M = cv.moments(c)

        # Vérifier si le moment est valide (éviter la division par zéro)
        if M["m00"] != 0:
            # Calculer les coordonnées du centroïde (centre)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            if not contientDeja(center_tab, cX, cY):  # Vérifier si le centre existe déjà
                center_tab.append((cX, cY, motif))  # Ajouter les coordonnées du centre et le motif
        
            #x, y, w, h = cv.boundingRect(c) # À enlever
            #if ((x, y) != (0, 0)) & (not contientDeja(center_tab, x, y)): #À enlever
            #    cv.rectangle(img, (x, y), (x + w, y + h), (171 + (motif * 42), 0, 0), 2) #À enlever
            #    center_tab.append((x, y, motif))  # motif in {"rond", "trait", "cercle"} #À enlever
    
def angleRedPattern(img):
    """
    Analyzes an image to detect red patterns and calculates the average orientation angle of these patterns.

    Args:
        img (numpy.ndarray): Input image to process.

    Returns:
        int: The average orientation angle of the detected red patterns.

    Notes:
        - Applies a mask to the input image using `maskMotif` to isolate red patterns.
        - Converts the masked image to grayscale and applies thresholding with `grayAndThreshold`.
        - Detects contours in the thresholded image using `cv.findContours`.
        - Calculates the minimum area rectangle for each contour and stores its orientation angle.
        - Filters out outlier angles based on quantile analysis.
        - Optionally displays and saves intermediate results based on global `show_data` and `save_data` flags.

    Global Variables:
        - mask (list): List of color ranges used for masking.
        - threshold (list): List of threshold values used for contour detection.
        - angle_tab (list): Stores the orientation angles of detected patterns.
        - show_data (list): Flags controlling which intermediate steps are displayed.
        - save_data (list): Flags controlling which intermediate steps are saved.

    Example:
        >>> img = cv.imread("example.png")
        >>> average_angle = angleRedPattern(img)
        >>> print(f"Average orientation angle of red patterns: {average_angle} degrees")
    """
    filtered_img=maskMotif(img, mask[1])
    contours, _ = cv.findContours(image=grayAndThreshold(filtered_img, threshold[1]),
                                  mode=cv.RETR_TREE, 
                                  method=cv.CHAIN_APPROX_SIMPLE,
                                  offset=(0,0))#RETR_LIST,
    red_pattern_minAreaRect_mire=filtered_img.copy()
    for c in contours:
        temp=cv.minAreaRect(c)
        #print(temp)
        angle_tab.append(temp[-1])
        
        if show_data[7] or save_data[7]:
            box = cv.boxPoints(temp)
            box = np.intp(box)
            cv.drawContours(red_pattern_minAreaRect_mire,[box],0,(0,255,255),2)
    Q_angle_tab=np.quantile(angle_tab, [0.25, 0.5, 0.75])
    Q_angle_tab_mean=np.mean(Q_angle_tab)
    i = len(angle_tab) - 1
    while i >= 0:
        if Q_angle_tab_mean+5 < angle_tab[i] or Q_angle_tab_mean-5 > angle_tab[i]:
            angle_tab.pop(i)
        i -= 1
    angle_tab_mean=np.mean(angle_tab)
    if show_data[7]:
        cv.imshow("minAreaRectRedPattern",red_pattern_minAreaRect_mire)
    if save_data[8]:
        cv.imwrite("minAreaRectRedPattern.png", red_pattern_minAreaRect_mire)

    return int(angle_tab_mean)

def fullContoursProcess(img):
    """
    Full contour detection process on an image, applying masking, thresholding, and contour detection 
    for each mask defined in the global `mask` list. Results are displayed and/or saved based on global flags.

    Args:
        img (numpy.ndarray): Input image to process.

    Returns:
        None: The function modifies global variables (`modified_mire`, `center_tab`) and optionally saves intermediate steps.

    Notes:
        - The function loops over predefined masks (`mask`), applying each mask to the input image using `maskMotif`.
        - Applies grayscale conversion and thresholding with `grayAndThreshold`.
        - Detects contours in the thresholded image with `findContours`.
        - Optionally displays and saves intermediate results (`mask`, `thresholded` images) based on global `show_data` and `save_data`.

    Global Variables:
        - mask (list): List of color ranges used for masking.
        - threshold (list): List of threshold values used for contour detection.
        - modified_mire (numpy.ndarray): Image where detected contours and bounding boxes are drawn.
        - show_data (list): Flags controlling which intermediate steps are displayed.
        - save_data (list): Flags controlling which intermediate steps are saved.
        - center_tab (list): Stores detected contour centers with their motifs.

    Example:
        >>> img = cv.imread("example.png")
        >>> fullContoursProcess(img)

    """
    for i in range(0,len(mask)):
        img_mask = maskMotif(transformed_mire, mask[i])
        if show_data[2]:
            cv.imshow("mask"+str(i), img_mask)
        if save_data[3]:
            cv.imwrite("data/mask"+str(i)+".png", img_mask)
        img_thresh = grayAndThreshold(img_mask, threshold[i], i)
        if show_data[5]:
            cv.imshow("thresh"+str(i), img_thresh)
        if save_data[6]:
            cv.imwrite("data/thresh"+str(i)+".png", img_thresh)
        findContours2(img_thresh, i)



def find_pixel_dir(img, start_x, start_y, dir, target_color):
    """
    Searches for a pixel of a specified color along a direction from a starting point in an image.

    Args:
        img (numpy.ndarray): Input image to process.
        start_x (int): X-coordinate of the starting point.
        start_y (int): Y-coordinate of the starting point.
        dir (float): Direction in degrees to search from the starting point.
        target_color (list): Target color to search for in BGR format.

    Returns:
        tuple or None: Coordinates (x, y) of the first pixel found with the target color, or None if no such pixel is found.

    Notes:
        - Converts the direction from degrees to radians.
        - Calculates the endpoint of the search line based on a predefined maximum search distance (`max_distance_search_pixel`).
        - Uses OpenCV's `cv.line` to draw a virtual line on a blank image to identify pixels along the search path.
        - Iterates over the pixels on this line to check for the target color.
        - Returns the coordinates of the first matching pixel found.

    Example:
        >>> img = cv.imread("example.png")
        >>> start_x, start_y = 100, 100
        >>> direction = 45.0
        >>> target_color = [0, 0, 255]  # Red in BGR
        >>> result = find_pixel_dir(img, start_x, start_y, direction, target_color)
        >>> if result:
        >>>     print(f"Pixel found at: {result}")
        >>> else:
        >>>     print("No pixel found.")
    """
    direction_radians = math.radians(dir)
    end_x = int(start_x + max_distance_search_pixel * math.cos(direction_radians))
    end_y = int(start_y + max_distance_search_pixel * math.sin(direction_radians))
    line_points = cv.line(np.zeros_like(img), (start_x, start_y), (end_x, end_y), (255, 255, 255), 1)

    for y in range(line_points.shape[0]):
        for x in range(line_points.shape[1]):
            if all(line_points[y, x] == [255, 255, 255]):
                if all(img[y, x] == target_color):
                    return (x, y)
    return None




##################################################################################################
#                                      FONCTION ENCODAGE                                         #
##################################################################################################

def encodeur(img):
    return None


##################################################################################################
#                                            MAIN                                                #
##################################################################################################

def main():

    if show_data[0]:
        cv.imshow("Mire originale", mire_orig)
    if save_data[1]:
        cv.imwrite("data/mire.png", mire_orig)

    t = tz_rxy() @ translationXYZ(t_x,t_y,t_z) @  rotationXYZBis(r_x,r_y,r_z)
    H =  _3Dto2D() @ t @ _2Dto3D() 
    transformed_mire = cv.warpPerspective(mire_orig, H, (ncols, nrows), None, borderValue=(255,255,255))
    if show_data[1]:
        cv.imshow("Mire transformee", transformed_mire)
    if save_data[2]:
        cv.imwrite("data/trans.png", transformed_mire)

    contours_mire=transformed_mire
    fullContoursProcess(contours_mire)
    if show_data[6]:
        cv.imshow("Contours", contours_mire)
    if save_data[7]:
        cv.imwrite("data/contours.png", contours_mire)

    angle = angleRedPattern(transformed_mire)
    print(angle)


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
            "angle_tab": angle_tab,
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

main()

#libcamera pour