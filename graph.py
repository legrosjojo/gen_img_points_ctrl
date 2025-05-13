
"""
@file graph.py
@brief This file defines the CustomGUI class, which creates a graphical user interface (GUI) for image processing.
@details The GUI allows users to adjust image transformation parameters, view the transformed image,
         and control data saving options. It uses the customtkinter library for the GUI and OpenCV for image processing.
"""

import sys
import os
import math
import tkinter
import tkinter.messagebox
import customtkinter
import cv2 as cv
import numpy as np
from PIL import Image
import code2

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class CustomGUI(customtkinter.CTk):
    """
    @brief A custom GUI for image processing with sliders, checkboxes, and image display.

    @details This class creates a GUI using customtkinter for adjusting image transformation parameters,
             displaying the transformed image, and controlling data saving options.
    """
    def __init__(self):
        """
        @brief Initializes the CustomGUI class, setting up the main window, frames, sliders, and checkboxes.

        @details Sets up the main window with a title and geometry, creates frames for different GUI elements,
                 initializes sliders for variable selection, creates checkboxes for data options,
                 loads the initial image, and adds a validation button to trigger processing.

        @param None

        @return None

        @note
            - Sets up the main window with a title and geometry.
            - Creates frames for the title, variable selection, image display, and checkboxes.
            - Initializes sliders for variable selection.
            - Creates checkboxes for show_data and save_data options.
            - Loads the initial image to be displayed.
            - Adds a validation button to trigger processing.
        """
        super().__init__()

        self.title("Projet Ingénieur Groupe 3")
        self.geometry("1200x600")

        # Frame for title
        self.title_frame = customtkinter.CTkFrame(self)
        self.title_frame.pack(side="top", fill="x")
        self.title_label = customtkinter.CTkLabel(self.title_frame, text="Projet Ingénieur Groupe 3", font=("Roboto", 20))
        self.title_label.pack(pady=10)

        # Frame for variable selection
        self.left_frame = customtkinter.CTkFrame(self, width=200)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        self.create_sliders()

        # Frame for image display
        self.right_frame = customtkinter.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.image_label = customtkinter.CTkLabel(self.right_frame, text="Image will be displayed here")
        self.image_label.pack(fill="both", expand=True)

        # Frame for checkboxes
        self.checkbox_frame = customtkinter.CTkFrame(self)
        self.checkbox_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Frame for show_data checkboxes
        self.show_data_frame = customtkinter.CTkFrame(self.checkbox_frame)
        self.show_data_frame.pack(side="top", fill="x", pady=5)
        customtkinter.CTkLabel(self.show_data_frame, text="Show Data Options").pack(anchor="w")

        # Frame for save_data checkboxes
        self.save_data_frame = customtkinter.CTkFrame(self.checkbox_frame)
        self.save_data_frame.pack(side="top", fill="x", pady=5)
        customtkinter.CTkLabel(self.save_data_frame, text="Save Data Options").pack(anchor="w")

        self.show_data_vars = []
        show_data_labels = [
            "Original Image", "Transformed Image", "Mask", "HSV", "Grey",
            "Threshold", "Contours", "Contours Min Rouge"
        ]

        for i, label in enumerate(show_data_labels):
            var = tkinter.BooleanVar(value=code2.show_data[i])
            checkbox = customtkinter.CTkCheckBox(self.show_data_frame, text=label, variable=var)
            checkbox.pack(anchor="w")
            self.show_data_vars.append(var)

        self.save_data_vars = []
        save_data_labels = [
            "Parameters", "Original Image", "Transformed Image", "Mask", "HSV",
            "Grey", "Threshold", "Contours", "Contours Min Rouge"
        ]

        for i, label in enumerate(save_data_labels):
            var = tkinter.BooleanVar(value=code2.save_data[i])
            checkbox = customtkinter.CTkCheckBox(self.save_data_frame, text=label, variable=var)
            checkbox.pack(anchor="w")
            self.save_data_vars.append(var)

        # Load initial image
        self.load_image("mire_315a.png")  # Ensure this path is correct

        # Button for validation
        self.validate_button = customtkinter.CTkButton(self.right_frame, text="Validate", command=self.validate)
        self.validate_button.pack(side="bottom", pady=10)

    def create_sliders(self):
        """
        @brief Creates sliders for variable selection.

        @details Creates sliders for translation and rotation variables, pairing each slider with an entry field for manual input.

        @param None

        @return None

        @note
            - Creates sliders for translation and rotation variables.
            - Each slider is paired with an entry field for manual input.
        """
        slider_params = [
            ("Translation X", -512, 512, 200),
            ("Translation Y", -512, 512, 200),
            ("Translation Z (Zoom)", -250, 250, 200),
            ("Rotation X", -180, 180, 360),
            ("Rotation Y", -180, 180, 360),
            ("Rotation Z", -180, 180, 360),
        ]

        self.sliders = {}
        self.entry_vars = {}
        for label, min_val, max_val, step in slider_params:
            frame = customtkinter.CTkFrame(self.left_frame)
            frame.pack(fill="x", pady=5)

            slider_label = customtkinter.CTkLabel(frame, text=label)
            slider_label.pack(anchor="w")

            slider = customtkinter.CTkSlider(frame, from_=min_val, to=max_val, number_of_steps=step, command=self.update_slider_value)
            slider.pack(fill="x")

            self.sliders[label] = slider

            entry_var = tkinter.StringVar()
            entry = customtkinter.CTkEntry(frame, textvariable=entry_var)
            entry.pack(fill="x")
            entry.bind("<Return>", lambda event, l=label: self.update_entry_value(l))
            self.entry_vars[label] = entry_var

            # Set initial value
            entry_var.set(str(slider.get()))

    def update_slider_value(self, value):
        """
        @brief Updates the entry fields with the current slider values.

        @details Updates the entry field corresponding to each slider, then calls update_image to refresh the displayed image.

        @param value (float): The current value of the slider.

        @return None

        @note
            - Updates the entry field corresponding to each slider.
            - Calls update_image to refresh the displayed image.
        """
        for label, slider in self.sliders.items():
            self.entry_vars[label].set(f"{slider.get():.2f}")
        self.update_image()

    def update_entry_value(self, label):
        """
        @brief Updates the slider values with the current entry field values.

        @details Updates the slider with the value from the corresponding entry field, then calls update_image to refresh the displayed image.

        @param label (str): The label of the slider to update.

        @return None

        @note
            - Updates the slider with the value from the corresponding entry field.
            - Calls update_image to refresh the displayed image.
        """
        try:
            value = float(self.entry_vars[label].get())
            self.sliders[label].set(value)
            self.update_image()
        except ValueError:
            pass

    def validate(self):
        """
        @brief Validates the current settings and triggers the main processing function.

        @details Updates the global variables with the current slider values, updates the global show_data and save_data
                variables with the checkbox values, calls the main function from code2, and exits the application.

        @param None

        @return None
        """
        # Update the global variables with slider values
        code2.t_x = self.sliders["Translation X"].get()
        code2.t_y = self.sliders["Translation Y"].get()
        code2.t_z = self.sliders["Translation Z (Zoom)"].get()
        code2.r_x = self.sliders["Rotation X"].get()
        code2.r_y = self.sliders["Rotation Y"].get()
        code2.r_z = self.sliders["Rotation Z"].get()

        # Update checkboxes
        code2.show_data = [var.get() for var in self.show_data_vars]
        code2.save_data = [var.get() for var in self.save_data_vars]

        # Call the main processing function
        code2.main()

        # Quit the application completely
        self.destroy()
        sys.exit()


    def load_image(self, path):
        """
        @brief Loads an image from the given path and displays it.

        @details Loads the image using OpenCV, converts the image to RGB format, and calls update_image to display the image.

        @param path (str): The path to the image file.

        @return None

        @note
            - Loads the image using OpenCV.
            - Converts the image to RGB format.
            - Calls update_image to display the image.
        """
        self.original_image = cv.imread(path)
        self.original_image = cv.cvtColor(self.original_image, cv.COLOR_BGR2RGB)
        self.update_image()

    def update_image(self):
        """
        @brief Updates the displayed image with the current transformations.

        @details Applies the current transformations to the original image, converts the transformed image to a format
                 compatible with Tkinter, and updates the image label with the new image.

        @param None

        @return None

        @note
            - Applies the current transformations to the original image.
            - Converts the transformed image to a format compatible with Tkinter.
            - Updates the image label with the new image.
        """
        if hasattr(self, 'original_image'):
            # Apply transformations based on slider values
            t_x = self.sliders["Translation X"].get()
            t_y = self.sliders["Translation Y"].get()
            t_z = self.sliders["Translation Z (Zoom)"].get()
            r_x = self.sliders["Rotation X"].get()
            r_y = self.sliders["Rotation Y"].get()
            r_z = self.sliders["Rotation Z"].get()

            # Apply transformations
            transformed_image = self.apply_transformations(self.original_image, t_x, t_y, t_z, r_x, r_y, r_z)

            # Convert the image to a format compatible with Tkinter
            self.photo = self.convert_cv_to_ctk(transformed_image)
            self.image_label.configure(image=self.photo, text="")

    def apply_transformations(self, image, t_x, t_y, t_z, r_x, r_y, r_z):
        """
        @brief Applies the current transformations to the given image.

        @details Creates a transformation matrix using the current translation and rotation values,
                 and applies the transformation matrix to the image using warpPerspective.

        @param image (numpy.ndarray): The image to transform.
        @param t_x (float): Translation along the X-axis.
        @param t_y (float): Translation along the Y-axis.
        @param t_z (float): Translation along the Z-axis.
        @param r_x (float): Rotation around the X-axis.
        @param r_y (float): Rotation around the Y-axis.
        @param r_z (float): Rotation around the Z-axis.

        @return numpy.ndarray: The transformed image.

        @note
            - Creates a transformation matrix using the current translation and rotation values.
            - Applies the transformation matrix to the image using warpPerspective.
        """
        nrows, ncols = image.shape[:2]
        virtual_focal = 75
        virtual_focal_dist = ncols / (2 * np.tan(np.radians(virtual_focal / 2)))

        # Create transformation matrix
        t = code2.tz_rxy() @ code2.translationXYZ(t_x, t_y, t_z) @ code2.rotationXYZBis(r_x, r_y, r_z)
        H = code2._3Dto2D() @ t @ code2._2Dto3D()

        # Apply transformation
        transformed_image = cv.warpPerspective(image, H, (ncols, nrows), None, borderValue=(255, 255, 255))

        return transformed_image

    def convert_cv_to_ctk(self, cv_image):
        """
        @brief Converts an OpenCV image to a format compatible with Tkinter.

        @details Converts the image from BGR to RGB format, creates a PIL Image from the converted image,
                 and returns a CTkImage object that can be displayed in a Tkinter widget.

        @param cv_image (numpy.ndarray): The image to convert.

        @return customtkinter.CTkImage: The converted image.

        @note
            - Converts the image from BGR to RGB format.
            - Creates a PIL Image from the converted image.
            - Returns a CTkImage object that can be displayed in a Tkinter widget.
        """
        cv_image = cv.cvtColor(cv_image, cv.COLOR_RGB2RGBA)
        pil_image = Image.fromarray(cv_image)
        return customtkinter.CTkImage(pil_image, size=(pil_image.width, pil_image.height))

if __name__ == "__main__":
    app = CustomGUI()
    app.mainloop()