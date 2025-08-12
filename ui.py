import tkinter as tk

class UI:
    def __init__(self, root, camera):
        self.root = root
        self.camera = camera

        # Colors and fonts
        self.BG_MAIN = "#1e272e"
        self.BG_PANEL_LEFT = "#2f3640"
        self.BG_PANEL_RIGHT = "#353b48"
        self.FG_MAIN = "#f5f6fa"
        self.FONT_TITLE = ("Segoe UI", 18, "bold")
        self.FONT_NORMAL = ("Segoe UI", 14)

        self.resolutions = [
            (160, 120),
            (320, 240),
            (640, 480),
            (1280, 720)
        ]

        self.options = [
            "<none>", "Grayscale",
            "Gaussian Blur", "Edge Detection",
            "Negative", "Binary", "Sepia", "Glitch"
        ]

        self.current_width = 0
        self.PANEL_MAX_WIDTH = 300
        self.ANIMATION_STEP = 15
        self.ANIMATION_DELAY = 10
        self.panel_expanded = False
        self.animation_running = False
        self.animation_direction = 0

        self.setup_ui()

    def setup_ui(self):
        # Left panel
        self.panel_left = tk.Frame(self.root, bg=self.BG_PANEL_LEFT)
        self.panel_left.pack(side="left", fill="both", expand=True)
        self.panel_left.pack_propagate(False)

        self.label_camera = tk.Label(self.panel_left, text="Camera Preview", fg=self.FG_MAIN, bg=self.BG_PANEL_LEFT, font=self.FONT_TITLE)
        self.label_camera.pack(pady=10)

        self.label_image = tk.Label(self.panel_left, bg=self.BG_PANEL_LEFT)
        self.label_image.pack(pady=10, expand=True)

        # Right panel
        self.panel_right = tk.Frame(self.root, bg=self.BG_MAIN, width=0)
        self.panel_right.pack_propagate(False)

        # Options label
        self.label_options = tk.Label(self.panel_right, text="Options", fg=self.FG_MAIN, bg=self.BG_MAIN, font=self.FONT_TITLE)
        self.label_options.pack(pady=10)

        # Filters panel
        self.panel_filters = tk.Frame(self.panel_right, bg=self.BG_MAIN, height=250)
        self.panel_filters.pack(fill='x', pady=10)

        self.var_filter = tk.StringVar(self.panel_filters)
        self.var_filter.set("<none>")

        self.filters_label = tk.Label(self.panel_filters, text="Filters", fg=self.FG_MAIN, bg=self.BG_MAIN, font=self.FONT_TITLE)
        self.filters_label.pack(pady=10, expand=True)

        self.dropdown = tk.OptionMenu(self.panel_filters, self.var_filter, *self.options)
        self.dropdown.pack(pady=5)

        self.strength = tk.IntVar(value=50)
        self.scale = tk.Scale(self.panel_filters, from_=-100, to=100, resolution=1, length=200,
                         orient='horizontal', label='Filter Strength',
                         variable=self.strength)
        self.scale.pack(pady=10, expand=True)

        # Resolutions panel
        self.panel_res = tk.Frame(self.panel_right, bg=self.BG_MAIN, height=250)
        self.panel_res.pack(fill='x', pady=0)

        self.res_label = tk.Label(self.panel_res, text="Resolutions", fg=self.FG_MAIN, bg=self.BG_MAIN, font=self.FONT_TITLE)
        self.res_label.pack(pady=10, expand=True)

        self.choice = tk.StringVar(self.panel_right)
        self.choice.set("(640, 480)")

        self.option_res = tk.OptionMenu(self.panel_res, self.choice, *self.resolutions)
        self.option_res.pack(pady=5)

        self.submit = tk.Button(self.panel_res, text="Apply Resolution", font=self.FONT_NORMAL, width=20)
        self.submit.pack(pady=10)

        # Camera actions panel
        self.panel_actions = tk.Frame(self.panel_right, bg=self.BG_MAIN, height=250)
        self.panel_actions.pack(fill='x', pady=10)

        self.actions_label = tk.Label(self.panel_actions, text="Camera Actions", fg=self.FG_MAIN, bg=self.BG_MAIN, font=self.FONT_TITLE)
        self.actions_label.pack(pady=10, expand=True)

        self.panel_cam = tk.Frame(self.panel_actions, bg=self.BG_MAIN)
        self.panel_cam.pack(fill='x', pady=0)

        self.btn_start = tk.Button(self.panel_cam, text="Start", font=self.FONT_NORMAL)
        self.btn_start.pack(pady=5, side='left', expand=True, fill='x')

        self.btn_stop = tk.Button(self.panel_cam, text="Stop", font=self.FONT_NORMAL)
        self.btn_stop.pack(pady=5, side='right', expand=True, fill='x')

        # Other options panel
        self.panel_other = tk.Frame(self.panel_right, bg=self.BG_MAIN, height=250)
        self.panel_other.pack(fill='x', pady=10)

        self.other_label = tk.Label(self.panel_other, text="Other Options", fg=self.FG_MAIN, bg=self.BG_MAIN, font=self.FONT_TITLE)
        self.other_label.pack(pady=10, expand=True)

        self.fps = tk.IntVar(value=30)
        self.scales = tk.Scale(self.panel_other, from_=1, to=120, resolution=2, length=200,
                          orient='horizontal', label='FPS',
                          variable=self.fps)
        self.scales.pack()

        self.ss = tk.Button(self.panel_other, text="Screenshot", font=self.FONT_NORMAL, width=20)
        self.ss.pack(pady=10)

        self.isdone = tk.BooleanVar(value=False)
        self.chk_show_detection = tk.Checkbutton(self.panel_other, text="Show Detection", font=self.FONT_NORMAL,
                                        bg=self.BG_MAIN, fg=self.FG_MAIN,
                                        activebackground=self.BG_PANEL_RIGHT,
                                        activeforeground=self.FG_MAIN,
                                        selectcolor=self.BG_MAIN, variable=self.isdone)
        self.chk_show_detection.pack(pady=10)

        # Bind buttons to camera actions
        self.btn_start.config(command=lambda: self.camera.start(self.root, self.fps))
        self.btn_stop.config(command=self.camera.stop)
        self.ss.config(command=self.camera.screenshot)
        self.submit.config(command=self.apply_resolution)

        # Bind motion for panel animation
        self.root.bind("<Motion>", self.on_motion)

    def apply_resolution(self):
        self.submit.config(state="disabled")
        self.camera.stop()
        self.camera.cap.release()
        val = self.choice.get()
        res_map = {
            "(160, 120)": (160, 120),
            "(320, 240)": (320, 240),
            "(640, 480)": (640, 480),
            "(1280, 720)": (1280, 720),
        }
        width, height = res_map.get(val, (640, 480))
        self.camera.set_resolution(width, height)
        self.root.after(500, self.restart_camera)

    def restart_camera(self):
        self.camera.start(self.root, self.fps)
        self.submit.config(state="normal")

    def update_panel_width(self, width):
        self.panel_right.config(width=width)
        self.panel_right.update_idletasks()

    def animate_expand(self):
        if self.animation_direction != 1:
            return
        if not self.panel_right.winfo_ismapped():
            self.panel_right.pack(side="right", fill="y")
        if self.current_width < self.PANEL_MAX_WIDTH:
            self.current_width += self.ANIMATION_STEP
            if self.current_width > self.PANEL_MAX_WIDTH:
                self.current_width = self.PANEL_MAX_WIDTH
            self.update_panel_width(self.current_width)
            self.root.after(self.ANIMATION_DELAY, self.animate_expand)
        else:
            self.animation_running = False
            self.animation_direction = 0
            self.panel_expanded = True

    def animate_collapse(self):
        if self.animation_direction != -1:
            return
        if self.current_width > 0:
            self.current_width -= self.ANIMATION_STEP
            if self.current_width < 0:
                self.current_width = 0
            self.update_panel_width(self.current_width)
            self.root.after(self.ANIMATION_DELAY, self.animate_collapse)
        else:
            self.panel_right.pack_forget()
            self.animation_running = False
            self.animation_direction = 0
            self.panel_expanded = False

    def show_panel(self):
        if not self.panel_expanded and not self.animation_running:
            self.animation_running = True
            self.animation_direction = 1
            self.animate_expand()

    def hide_panel(self):
        if self.panel_expanded and not self.animation_running:
            self.animation_running = True
            self.animation_direction = -1
            self.animate_collapse()

    def on_motion(self, event):
        x = event.x_root - self.root.winfo_rootx()
        y = event.y_root - self.root.winfo_rooty()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        if x > window_width - 50:
            self.show_panel()
        else:
            if self.panel_expanded:
                panel_x = self.panel_right.winfo_rootx() - self.root.winfo_rootx()
                panel_y = self.panel_right.winfo_rooty() - self.root.winfo_rooty()
                panel_w = self.panel_right.winfo_width()
                panel_h = self.panel_right.winfo_height()
                buffer_left = panel_x - 100
                if not (buffer_left <= x <= panel_x + panel_w and panel_y <= y <= panel_y + panel_h):
                    self.hide_panel()
