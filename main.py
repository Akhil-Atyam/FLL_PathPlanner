import tkinter as tk
from tkinter import simpledialog, font

from PIL import Image, ImageTk
import math

import sys
import os


# TODO: Important, teams that choose to use their own image, or teams that are playing previous years games must
#  change the pixels per inch for tuning to be accurate.

MAT_IMAGE = "fll_mat.png"  # Replace with your image path
PIXELS_PER_INCH = 16  # Image size in px / image size in inches


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class PathPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("FLL Path Planner")

        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family="Sans-serif", weight=font.NORMAL)

        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.LEFT)

        self.image = Image.open(resource_path("fll_mat.png"))
        self.tk_image = ImageTk.PhotoImage(self.image)

        self.canvas = tk.Canvas(self.canvas_frame, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.canvas.create_image(0, self.image.height, anchor=tk.SW, image=self.tk_image)

        tk.Label(self.frame, text="Telemetry").pack()
        self.textbox = tk.Text(self.frame, width=30, height=8, bg="white", fg="black", font=("Courier", 10))
        self.textbox.pack(padx=5, pady=2)

        self.regen_button = tk.Button(self.frame, text="Regenerate Path", command=self.regen)
        self.regen_button.pack(pady=1)

        # tk.Label(self.frame, text="").pack()
        self.robot_length_var = tk.DoubleVar(value=2.0)
        self.robot_width_var = tk.DoubleVar(value=1.5)
        self.robot_offset_x_var = tk.DoubleVar(value=0.0)
        self.robot_offset_y_var = tk.DoubleVar(value=0.0)

        for label, var in [
            ("Robot Length (in)", self.robot_length_var),
            ("Robot Width (in)", self.robot_width_var),
            ("Offset X (in)", self.robot_offset_x_var),
            ("Offset Y (in)", self.robot_offset_y_var),
        ]:
            tk.Label(self.frame, text=label).pack()
            tk.Entry(self.frame, textvariable=var).pack(pady=1)

        tk.Label(self.frame, text="Start X (in)").pack()
        self.start_x_entry = tk.Entry(self.frame)
        self.start_x_entry.insert(0, "5")
        self.start_x_entry.pack(pady=1)

        tk.Label(self.frame, text="Start Y (in)").pack()
        self.start_y_entry = tk.Entry(self.frame)
        self.start_y_entry.insert(0, "5")
        self.start_y_entry.pack(pady=1)

        tk.Label(self.frame, text="Start Angle (°)").pack()
        self.start_angle_entry = tk.Entry(self.frame)
        self.start_angle_entry.insert(0, "0")
        self.start_angle_entry.pack(pady=1)

        self.set_pose_button = tk.Button(self.frame, text="Set Start Pose", command=self.update_start_pose)
        self.set_pose_button.pack(pady=1)

        self.turn_button = tk.Button(self.frame, text="Add Turn Step", command=self.add_turn_step)
        self.turn_button.pack(pady=1)

        self.turn_button = tk.Button(self.frame, text="Add Move Step", command=self.move_only_step)
        self.turn_button.pack(pady=1)

        self.marker_button = tk.Button(self.frame, text="Add Marker", command=self.add_marker)
        self.marker_button.pack(pady=1)

        self.undo_button = tk.Button(self.frame, text="Undo", command=self.undo)
        self.undo_button.pack(pady=1)

        self.clear_button = tk.Button(self.frame, text="Reset", command=self.reset)
        self.clear_button.pack(pady=1)

        # tk.Label(self.frame, text="").pack()
        tk.Label(self.frame, text="Telemetry Loader").pack()
        self.telemetry_entry = tk.Text(self.frame, height=5, width=30)
        self.telemetry_entry.pack(pady=2)

        self.load_button = tk.Button(self.frame, text="Load Telemetry", command=self.load_telemetry)
        self.load_button.pack(pady=2)

        self.points = []
        self.robot_angle = 0
        self.turn_mode = False
        self.robot_box = None
        self.robot_position = None
        self.marker_count = 1
        self.history = []

        self.canvas.bind("<Button-1>", self.add_point)
        self.update_start_pose()



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
        self.history.clear()
        self.marker_count = 1
        self.draw_robot(x, y, angle)

    def reset(self):
        self.update_start_pose()

    def add_turn_step(self):
        self.turn_mode = True

    def add_marker(self):
        if self.robot_position:
            x, y = self.robot_position
            marker_radius = 10
            self.canvas.create_oval(x - marker_radius, self.image.height - y - marker_radius,
                                    x + marker_radius, self.image.height - y + marker_radius,
                                    outline="green", width=2)
            self.textbox.insert(tk.END,
                                f"MARKER {self.marker_count} at ({x / PIXELS_PER_INCH:.2f}, {y / PIXELS_PER_INCH:.2f})\n")
            self.history.append(('marker', x, y))
            self.marker_count += 1

    def undo(self):
        text = self.textbox.get("1.0", tk.END).strip().splitlines()
        self.reset()
        previous1 = "Drive"
        for line in text[:-1]:
            line = line.strip()
            if line.startswith("Rotate"):
                x1, y1 = self.robot_position
                if previous1 == "Rotate":
                    self.draw_robot(x1, y1, self.robot_angle)
                angle = float(line.split()[1].replace("°", ""))
                angle = angle * -1
                self.robot_angle = (self.robot_angle + angle) % 360
                self.textbox.insert(tk.END, f"Rotate {angle*-1:.1f}°\n")
                self.history.append(('turn', angle))

                previous1 = "Rotate"
            elif line.startswith("Drive"):
                distance = float(line.split()[1].replace("\"", ""))
                dx = distance * PIXELS_PER_INCH * math.cos(math.radians(self.robot_angle))
                dy = distance * PIXELS_PER_INCH * math.sin(math.radians(self.robot_angle))

                x1, y1 = self.robot_position
                x2 = x1 + dx
                y2 = y1 + dy

                self.canvas.create_line(x1, self.image.height - y1, x2, self.image.height - y2, fill='blue', width=2)
                self.textbox.insert(tk.END, f"Drive {distance:.2f}\"\n")
                self.history.append(('move', x2, y2, self.robot_angle,
                                     (x1, self.image.height - y1, x2, self.image.height - y2), 0, distance))
                self.robot_position = (x2, y2)
                self.draw_robot(x2, y2, self.robot_angle)
                previous1 = "Drive"
            elif line.startswith("MARKER"):
                self.add_marker()
        if previous1 == "Rotate":
            x1, y1 = self.robot_position
            self.draw_robot(x1, y1, self.robot_angle)

    def add_point(self, event):
        x, y = event.x, self.image.height - event.y

        if self.turn_mode:
            rx, ry = self.robot_position
            dx = x - rx
            dy = y - ry
            desired_angle = math.degrees(math.atan2(dy, dx))
            turn_angle = (desired_angle - self.robot_angle + 360) % 360
            if turn_angle > 180:
                turn_angle -= 360
            self.robot_angle = desired_angle % 360
            self.points.append(("TURN", turn_angle))
            self.textbox.insert(tk.END, f"Rotate {turn_angle*-1:.1f}°\n")
            self.history.append(('turn', turn_angle))
            self.turn_mode = False
            self.draw_robot(rx, ry, self.robot_angle)
        else:
            x1, y1 = self.robot_position
            dx = x - x1
            dy = y - y1
            distance_px = math.sqrt(dx ** 2 + dy ** 2)
            distance_in = distance_px / PIXELS_PER_INCH
            desired_angle = math.degrees(math.atan2(dy, dx))
            turn_angle = (desired_angle - self.robot_angle + 360) % 360
            if turn_angle > 180:
                turn_angle -= 360
            self.robot_angle = desired_angle % 360

            self.canvas.create_line(x1, self.image.height - y1, x, self.image.height - y, fill='blue', width=2)
            self.textbox.insert(tk.END, f"Rotate {turn_angle*-1:.1f}°\n")
            self.textbox.insert(tk.END, f"Drive {distance_in:.2f}\"\n")

            self.history.append(('move', x, y, self.robot_angle, (x1, self.image.height - y1, x, self.image.height - y),
                                 turn_angle, distance_in))
            self.robot_position = (x, y)
            self.draw_robot(x, y, self.robot_angle)

    def regen(self):
        text = self.textbox.get("1.0", tk.END).strip().splitlines()
        self.reset()
        previous1 = "Drive"
        for line in text:
            line = line.strip()
            if line.startswith("Rotate"):
                x1, y1 = self.robot_position
                if previous1 == "Rotate":
                    self.draw_robot(x1, y1, self.robot_angle)
                angle = float(line.split()[1].replace("°", ""))
                angle = angle * -1
                self.robot_angle = (self.robot_angle + angle) % 360
                self.textbox.insert(tk.END, f"Rotate {angle*-1:.1f}°\n")
                self.history.append(('turn', angle))

                previous1 = "Rotate"
            elif line.startswith("Drive"):
                distance = float(line.split()[1].replace("\"", ""))
                dx = distance * PIXELS_PER_INCH * math.cos(math.radians(self.robot_angle))
                dy = distance * PIXELS_PER_INCH * math.sin(math.radians(self.robot_angle))

                x1, y1 = self.robot_position
                x2 = x1 + dx
                y2 = y1 + dy

                self.canvas.create_line(x1, self.image.height - y1, x2, self.image.height - y2, fill='blue',
                                        width=2)
                self.textbox.insert(tk.END, f"Drive {distance:.2f}\"\n")
                self.history.append(('move', x2, y2, self.robot_angle,
                                     (x1, self.image.height - y1, x2, self.image.height - y2), 0, distance))
                self.robot_position = (x2, y2)
                self.draw_robot(x2, y2, self.robot_angle)
                previous1 = "Drive"
            elif line.startswith("MARKER"):
                self.add_marker()
        if previous1 == "Rotate":
            x1, y1 = self.robot_position
            self.draw_robot(x1, y1, self.robot_angle)



    def draw_robot(self, x, y, angle):
        if self.robot_box:
            self.canvas.delete(self.robot_box)

        offset_x, offset_y = self.robot_offset
        length = self.robot_length
        width = self.robot_width

        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        ox = x + offset_x * cos_a - offset_y * sin_a
        oy = y + offset_x * sin_a + offset_y * cos_a

        corners = [(-length / 2, -width / 2), (length / 2, -width / 2),
                   (length / 2, width / 2), (-length / 2, width / 2)]

        rotated = []
        for dx, dy in corners:
            rx = ox + dx * cos_a - dy * sin_a
            ry = oy + dx * sin_a + dy * cos_a
            rotated.append((rx, self.image.height - ry))

        self.robot_box = self.canvas.create_polygon(rotated, outline='black', fill='cyan', width=2)

        # Draw direction arrow
        arrow_size = 10
        tip_x = x + arrow_size * math.cos(rad)
        tip_y = y + arrow_size * math.sin(rad)
        left_x = x + arrow_size * math.cos(rad + math.radians(140))
        left_y = y + arrow_size * math.sin(rad + math.radians(140))
        right_x = x + arrow_size * math.cos(rad - math.radians(140))
        right_y = y + arrow_size * math.sin(rad - math.radians(140))

        self.canvas.create_polygon(
            [tip_x, self.image.height - tip_y,
             left_x, self.image.height - left_y,
             right_x, self.image.height - right_y],
            fill="orange"
        )

    def move_only_step(self):
        if self.robot_position:
            distance = simpledialog.askfloat("Move Only",
                                             "Enter distance in inches (positive = forward, negative = back):")
            if distance is not None:
                angle_rad = math.radians(self.robot_angle)
                dx = distance * PIXELS_PER_INCH * math.cos(angle_rad)
                dy = distance * PIXELS_PER_INCH * math.sin(angle_rad)
                x1, y1 = self.robot_position
                x2 = x1 + dx
                y2 = y1 + dy
                self.canvas.create_line(x1, self.image.height - y1, x2, self.image.height - y2, fill='blue', width=2)
                self.textbox.insert(tk.END, f"Drive {distance:.2f}\"\n")
                self.history.append(('move', x2, y2, self.robot_angle,
                                     (x1, self.image.height - y1, x2, self.image.height - y2), 0, distance))
                self.robot_position = (x2, y2)
                self.draw_robot(x2, y2, self.robot_angle)

    def load_telemetry(self):
        text = self.telemetry_entry.get("1.0", tk.END).strip().splitlines()

        self.reset()
        previous1 = "Drive"
        for index, line in enumerate(text):  # Use enumerate to get both index and line
            line = line.strip()
            if line.startswith("Rotate"):
                x1, y1 = self.robot_position
                # Check if previous1 is "Rotate" or if this is the last line
                if previous1 == "Rotate":
                    self.draw_robot(x1, y1, self.robot_angle)
                angle = float(line.split()[1].replace("°", ""))
                angle = angle * -1
                self.robot_angle = (self.robot_angle + angle) % 360
                self.textbox.insert(tk.END, f"Rotate {angle*-1:.1f}°\n")
                self.history.append(('turn', angle))

                previous1 = "Rotate"
            elif line.startswith("Drive"):
                distance = float(line.split()[1].replace("\"", ""))
                dx = distance * PIXELS_PER_INCH * math.cos(math.radians(self.robot_angle))
                dy = distance * PIXELS_PER_INCH * math.sin(math.radians(self.robot_angle))

                x1, y1 = self.robot_position
                x2 = x1 + dx
                y2 = y1 + dy

                self.canvas.create_line(x1, self.image.height - y1, x2, self.image.height - y2, fill='blue', width=2)
                self.textbox.insert(tk.END, f"Drive {distance:.2f}\"\n")
                self.history.append(('move', x2, y2, self.robot_angle,
                                     (x1, self.image.height - y1, x2, self.image.height - y2), 0, distance))
                self.robot_position = (x2, y2)
                self.draw_robot(x2, y2, self.robot_angle)
                previous1 = "Drive"
            elif line.startswith("MARKER"):
                self.add_marker()
        if previous1 == "Rotate":
            x1, y1 = self.robot_position
            self.draw_robot(x1, y1, self.robot_angle)


if __name__ == "__main__":
    root = tk.Tk()
    app = PathPlanner(root)
    root.mainloop()
