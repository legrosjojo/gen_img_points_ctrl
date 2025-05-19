from pypylon import pylon
import cv2
import crop_gui
import numpy as np
import customtkinter as ctk
import os
import time
from datetime import datetime
import code

def fullscreen(image):
    img = cv2.imread(image)
    if img is None:
        raise ValueError("Erreur impossible de lire l'image.")

    app = ctk.CTk()
    app.withdraw()  # Ne pas afficher la fenêtre
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.destroy()
    bg = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    y_offset = max(0, (screen_height - img.shape[0]) // 2)
    x_offset = max(0, (screen_width - img.shape[1]) // 2)
    img_cropped = img[:min(img.shape[0], screen_height), :min(img.shape[1], screen_width)]
    bg[y_offset:y_offset+img_cropped.shape[0], x_offset:x_offset+img_cropped.shape[1]] = img_cropped

    nom = "fullscreen"
    cv2.namedWindow(nom, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(nom, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(nom, bg)
    cv2.waitKey(0)

def capture_color_image(filename):
    
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    if len(devices) == 0:
        raise RuntimeError("Aucune caméra")
    camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[0]))
    camera.Open()

    pixel_formats = camera.PixelFormat.Symbolics
    if "BGR8" in pixel_formats:
        camera.PixelFormat.SetValue("BGR8")
    else:
        raise RuntimeError("Format BGR non supporté")
    
    camera.StartGrabbingMax(1)
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    
    if grab_result.GrabSucceeded():
        image = grab_result.Array

        if grab_result.PixelType == "RGB8":
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif grab_result.PixelType == "Mono8":
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.imwrite(filename, image)
        print(f"Image enregistrée: {filename}")

    else:
        print("Erreur capture")
    grab_result.Release()
    camera.Close()
    cv2.destroyAllWindows()

def process_capture(image, filename):
    fullscreen(image)
    capture_color_image(filename)

def capture_image(camera_index=0, save_path=None):
    """
    Capture une image depuis la caméra et la sauvegarde si demandé.
    
    Args:
        camera_index (int): Index de la caméra à utiliser
        save_path (str): Chemin où sauvegarder l'image. Si None, l'image n'est pas sauvegardée.
        
    Returns:
        numpy.ndarray: Image capturée ou None en cas d'erreur
    """
    # Initialiser la caméra
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra")
        return None
        
    # Capturer une image
    ret, frame = cap.read()
    if not ret:
        print("Erreur: Impossible de capturer l'image")
        cap.release()
        return None
        
    # Sauvegarder l'image si un chemin est spécifié
    if save_path:
        # Créer le dossier s'il n'existe pas
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, frame)
        print(f"Image sauvegardée: {save_path}")
        
    # Libérer la caméra
    cap.release()
    
    return frame

def process_captured_image(image):
    """
    Traite une image capturée pour détecter les motifs.
    
    Args:
        image (numpy.ndarray): Image à traiter
        
    Returns:
        list: Liste des centres des motifs détectés
    """
    if image is None:
        return []
        
    # Initialiser code.center_tab
    code.center_tab = []
    
    # Traiter l'image
    code.fullContoursProcess(image)
    
    return code.center_tab.copy()

def main():
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Capturer une image
    image = capture_image(save_path="data/capture.png")
    if image is None:
        return
        
    # Traiter l'image
    centers = process_captured_image(image)
    print(f"Nombre de motifs détectés: {len(centers)}")
    
    # Afficher l'image avec les centres
    img_centers = image.copy()
    for center in centers:
        cv2.circle(img_centers, (int(center[0]), int(center[1])), 5, (0, 0, 255), -1)
        
    cv2.imshow("Image capturée avec centres", img_centers)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()