from pypylon import pylon
import cv2
import globals_
import crop_gui

def fullscreen(image):
    if image is None:
        raise ValueError("erreur image")

    nom="fullscreen"
    cv2.namedWindow(nom, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(nom, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(nom, image)

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

def process_capture(image, filename):
    fullscreen(image)
    capture_color_image(filename)

if __name__ == "__main__":
    process_capture("data/mire_315a.png", "data/mire_photo.png"):
    crop_gui.main_crop_gui()