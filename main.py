import tkinter as tk
from PIL import Image, ImageTk
import math

# === CONFIG ===
MAT_IMAGE = "fll_mat.png"
PIXELS_PER_INCH = 16

class PathPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("FLL Path Planner")

        # Frame for controls
        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frame for canvas and telemetry input
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Load and scale image
        self.image = Image.open(MAT_IMAGE)
        self.tk_image = ImageTk.PhotoImage(self.image)

        # === Scrollable Canvas Area ===
        canvas_frame = tk.Frame(self.right_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        canvas_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(canvas_frame, width=self.image.width, height=500,
                                yscrollcommand=canvas_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas_scrollbar.config(command=self.canvas.yview)

        self.canvas.create_image(0, self.image.height, anchor=tk.SW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # === Telemetry Input ===
        telemetry_frame = tk.Frame(self.right_frame)
        telemetry_frame.pack(fill=tk.X, pady=5)

        self.telemetry_box = tk.Text(telemetry_frame, height=5, font=("Courier", 10))
        self.telemetry_box.pack(fill=tk.X, padx=5)
        tk.Button(telemetry_frame, text="Load Telemetry", command=self.load_telemetry).pack(pady=3)

        # === Configuration Inputs ===
        self.robot_length_var = tk.DoubleVar(value=2.0)
        self.robot_width_var = tk.DoubleVar(value=1.5)
        self.robot_offset_x_var = tk.DoubleVar(value=0.0)
        self.robot_offset_y_var = tk.DoubleVar(value=0.0)

        self._make_labeled_entry("Robot Length (in)", self.robot_length_var)
        self._make_labeled_entry("Robot Width (in)", self.robot_width_var)
        self._make_labeled_entry("Offset X (in)", self.robot_offset_x_var)
        self._make_labeled_entry("Offset Y (in)", self.robot_offset_y_var)

        self.start_x_entry = self._make_labeled_entry("Start X (in)", default="5")
        self.start_y_entry = self._make_labeled_entry("Start Y (in)", default="5")
        self.start_angle_entry = self._make_labeled_entry("Start Angle (°)", default="0")

        # === Buttons ===
        tk.Button(self.frame, text="Set Start Pose", command=self.update_start_pose).pack(pady=5)
        tk.Button(self.frame, text="Add Turn Step", command=self.add_turn_step).pack(pady=5)
        tk.Button(self.frame, text="Add Marker", command=self.add_marker).pack(pady=5)
        tk.Button(self.frame, text="Reset", command=self.reset).pack(pady=5)
        tk.Button(self.frame, text="Undo", command=self.undo).pack(pady=5)

        # === Text output for generated commands ===
        self.textbox = tk.Text(self.frame, width=30, height=10, bg="white", fg="black", font=("Courier", 10))
        self.textbox.pack(padx=5, pady=5)

        # === State ===
        self.points = []
        self.history = []
        self.robot_angle = 0
        self.robot_position = None
        self.turn_mode = False
        self.marker_count = 1
        self.robot_box = None

        self.canvas.bind("<Button-1>", self.add_point)
        self.update_start_pose()

    def _make_labeled_entry(self, label, variable=None, default=None):
        tk.Label(self.frame, text=label).pack()
        entry = tk.Entry(self.frame, textvariable=variable)
        if default is not None:
            entry.insert(0, default)
        entry.pack(pady=2)
        return entry

    def update_start_pose(self):
        try:
            self.robot_length = self.robot_length_var.get() * PIXELS_PER_INCH
            self.robot_width = self.robot_width_var.get() * PIXELS_PER_INCH
            self.robot_offset = (
                self.robot_offset_x_var.get() * PIXELS_PER_INCH,
                self.robot_offset_y_var.get() * PIXELS_PER_INCH
            )
            x_in = float(self.start_x_entry.get())
            y_in = float(self.start_y_entry.get())
            angle = float(self.start_angle_entry.get()) * -1 + 90
            x_px = x_in * PIXELS_PER_INCH
            y_px = y_in * PIXELS_PER_INCH
            self.set_start_pose(x_px, y_px, angle)
        except ValueError:
            pass

    def set_start_pose(self, x, y, angle):
        self.robot_position = (x, y)
        self.robot_angle = angle
        self.canvas.delete("all")
        self.canvas.create_image(0, self.image.height, anchor=tk.SW, image=self.tk_image)
        self.points.clear()
        self.textbox.delete("1.0", tk.END)
        self.draw_robot(x, y, angle)

    def reset(self):
        self.update_start_pose()

    def add_turn_step(self):
        self.turn_mode = True

    def add_marker(self):
        if self.robot_position:
            x, y = self.robot_position

            # Draw visual marker
            marker_radius = 10
            self.canvas.create_oval(x - marker_radius, self.image.height - y - marker_radius,
                                    x + marker_radius, self.image.height - y + marker_radius,
                                    outline="green", width=2, tags=f"marker_{self.marker_count}")

            # Save in textbox and history
            in_x = x / PIXELS_PER_INCH
            in_y = y / PIXELS_PER_INCH
            self.textbox.insert(tk.END, f"MARKER {self.marker_count} at ({in_x:.2f}, {in_y:.2f})\n")
            self.history.append(('marker', x, y, self.marker_count))  # Save marker count too

            # Save in telemetry box as well
            self.telemetry_box.insert(tk.END, f"MARKER {self.marker_count} at ({in_x:.2f}, {in_y:.2f})\n")
            self.marker_count += 1

    def undo(self):
        if not self.history:
            return
        self.history.pop()
        self.canvas.delete("all")
        self.canvas.create_image(0, self.image.height, anchor=tk.SW, image=self.tk_image)
        self.points.clear()
        self.textbox.delete("1.0", tk.END)
        self.robot_position = None
        self.robot_angle = 0
        self.update_start_pose()
        for action in self.history:
            if action[0] == 'marker':
                self.robot_position = (action[1], action[2])
                self.add_marker()
            elif action[0] == 'move':
                x, y, angle = action[1], action[2], action[3]
                self.robot_position = (x, y)
                self.robot_angle = angle
                self.draw_robot(x, y, angle)
            elif action[0] == 'turn':
                self.robot_angle = (self.robot_angle + action[1]) % 360
                self.draw_robot(*self.robot_position, self.robot_angle)

    def add_point(self, event):
        x, y = event.x, self.image.height - event.y
        if self.turn_mode and self.robot_position:
            rx, ry = self.robot_position
            dx = x - rx
            dy = y - ry
            desired_angle = math.degrees(math.atan2(dy, dx))
            turn_angle = (desired_angle - self.robot_angle + 360) % 360
            if turn_angle > 180:
                turn_angle -= 360
            self.robot_angle = (self.robot_angle + turn_angle) % 360
            self.points.append(("TURN", turn_angle))
            self.textbox.insert(tk.END, f"Rotate {turn_angle:.1f}°\n")
            self.turn_mode = False
            self.history.append(('turn', turn_angle))
        else:
            if self.robot_position:
                x1, y1 = self.robot_position
                dx = x - x1
                dy = y - y1
                distance_px = math.sqrt(dx ** 2 + dy ** 2)
                distance_in = distance_px / PIXELS_PER_INCH
                desired_angle = math.degrees(math.atan2(dy, dx))
                turn_angle = (desired_angle - self.robot_angle + 360) % 360
                if turn_angle > 180:
                    turn_angle -= 360
                turn_angle = -turn_angle
                self.textbox.insert(tk.END, f"Rotate {turn_angle:.1f}°\n")
                self.textbox.insert(tk.END, f"Drive {distance_in:.2f}\"\n")
                self.canvas.create_line(x1, self.image.height - y1, x, self.image.height - y, fill='blue', width=2)
            self.robot_position = (x, y)
            self.robot_angle = math.degrees(math.atan2(dy, dx)) if not self.turn_mode else self.robot_angle
            self.history.append(('move', x, y, self.robot_angle))
        self.draw_robot(x, y, self.robot_angle)

    def draw_robot(self, x, y, angle):
        self.canvas.delete("robot_box")
        offset_x, offset_y = self.robot_offset
        length = self.robot_length
        width = self.robot_width
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        ox = x + offset_x * cos_a - offset_y * sin_a
        oy = y + offset_x * sin_a + offset_y * cos_a

        corners = [(-length/2, -width/2), (length/2, -width/2),
                   (length/2, width/2), (-length/2, width/2)]

        rotated = [(ox + dx * cos_a - dy * sin_a, self.image.height - (oy + dx * sin_a + dy * cos_a)) for dx, dy in corners]

        self.canvas.create_polygon(rotated, outline='black', fill='cyan', width=2, tags="robot_box")

        # Draw pose arrow
        tip_x = x + 10 * cos_a
        tip_y = y + 10 * sin_a
        left_x = x + 10 * math.cos(rad + math.radians(140))
        left_y = y + 10 * math.sin(rad + math.radians(140))
        right_x = x + 10 * math.cos(rad - math.radians(140))
        right_y = y + 10 * math.sin(rad - math.radians(140))
        self.canvas.create_polygon(
            [tip_x, self.image.height - tip_y,
             left_x, self.image.height - left_y,
             right_x, self.image.height - right_y],
            fill="orange",
            tags="pose_arrow"
        )

    def load_telemetry(self):
        telemetry = self.telemetry_box.get("1.0", tk.END).strip().splitlines()
        self.reset()
        for line in telemetry:
            line = line.strip()
            if line.startswith("Rotate"):
                angle = float(line.split()[1].replace("°", ""))
                self.robot_angle = (self.robot_angle - angle) % 360
                self.textbox.insert(tk.END, f"Rotate {angle:.1f}°\n")
                self.history.append(('turn', angle))
            elif line.startswith("Drive"):
                distance_in = float(line.split()[1].replace("\"", ""))
                distance_px = distance_in * PIXELS_PER_INCH
                dx = distance_px * math.cos(math.radians(self.robot_angle))
                dy = distance_px * math.sin(math.radians(self.robot_angle))
                if self.robot_position:
                    x, y = self.robot_position
                    new_x = x + dx
                    new_y = y + dy
                    self.canvas.create_line(x, self.image.height - y, new_x, self.image.height - new_y, fill='blue', width=2)
                    self.robot_position = (new_x, new_y)
                    self.textbox.insert(tk.END, f"Drive {distance_in:.2f}\"\n")
                    self.history.append(('move', new_x, new_y, self.robot_angle))
                    self.draw_robot(new_x, new_y, self.robot_angle)
            elif line.startswith("MARKER"):
                parts = line.split("at")
                if len(parts) == 2:
                    marker_id = int(parts[0].split()[1])
                    coords = parts[1].strip(" ()").split(",")
                    try:
                        x_in = float(coords[0])
                        y_in = float(coords[1])
                        x_px = x_in * PIXELS_PER_INCH
                        y_px = y_in * PIXELS_PER_INCH

                        marker_radius = 10
                        self.canvas.create_oval(x_px - marker_radius, self.image.height - y_px - marker_radius,
                                                x_px + marker_radius, self.image.height - y_px + marker_radius,
                                                outline="green", width=2, tags=f"marker_{marker_id}")
                        self.marker_count = max(self.marker_count,
                                                marker_id + 1)  # Ensure marker count continues correctly
                    except ValueError:
                        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = PathPlanner(root)
    root.mainloop()
