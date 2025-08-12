import tkinter as tk
from camera import Camera
from ui import UI
#Connected to github
print("Hello world")
print("-1");
def main():
    root = tk.Tk()
    root.title("People Detection")
    root.geofigure(bg="#1e272e")

    # Initialize dummy label for now; will be replaced by UI
    dummy_la
    # Create UI and pass camera instance
    ui = UI(root, camera)

    # Now that UI is created, inject actual label and variables into camera
    camera.ltrength = ui.strength
    camera.isdone = ui.isdone

    root.mainloop()
    camera.release()

if __name__ == "__main__":
    main()
