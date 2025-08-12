import tkinter as tk
from camera import Camera
from ui import UI

def main():
    root = tk.Tk()
    root.title("People Detection")
    root.geometry("1000x700")
    root.state('zoomed')
    root.configure(bg="#1e272e")

    # Initialize dummy label for now; will be replaced by UI
    dummy_label = tk.Label(root)

    # Create Camera instance without UI elements yet
    camera = Camera(dummy_label, None, None, None)

    # Create UI and pass camera instance
    ui = UI(root, camera)

    # Now that UI is created, inject actual label and variables into camera
    camera.label_image = ui.label_image
    camera.var_filter = ui.var_filter
    camera.strength = ui.strength
    camera.isdone = ui.isdone

    root.mainloop()
    camera.release()

if __name__ == "__main__":
    main()
