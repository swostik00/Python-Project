import cv2
import numpy as np
from tkinter import *
from tkinter.messagebox import askyesno
from tkinter import filedialog
from PIL import Image, ImageTk
from a_star_algorithm import a_star, Node

class SmartParkingSystem:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Smart Parking System")
        self.points = []
        self.video_loaded = False
        self.choosing_path = False
        
        self.canvas = Canvas(self.root, bg="white", bd=2, relief=SUNKEN)
        self.canvas.place(x=400, y=10, width=710, height=710)

        load_video_button = Button(self.root, text="Load Video", command=self.load_video)
        load_video_button.place(x=20, y=130, width=220, height=40)

        choose_path_button = Button(text="Choose Path", command=self.choose_path)
        choose_path_button.place(x=20, y=190, width=220, height=40)

        find_space_button = Button(text="Find Space", command=self.find_space)
        find_space_button.place(x=20, y=250, width=220, height=40)

        remove_video_button = Button(self.root, text="Remove Video", command=self.remove_video)
        remove_video_button.place(x=20, y=310, width=220, height=40)

        exit_button = Button(text="Exit", command=self.exit_program)
        exit_button.place(x=20, y=370, width=220, height=40)

        self.cap = None
        self.img = None

    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if file_path:
            self.cap = cv2.VideoCapture(file_path)
            self.video_loaded = True
            self.canvas.create_text(355, 355, text="Video Loaded", fill="green", font=("Helvetica", 14))
            self.root.after(10, self.load_and_display_frame)

    def remove_video(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = None
        self.video_loaded = False
        self.canvas.delete("all")
        self.img = None
        self.canvas.create_text(355, 355, text="Video Removed", fill="red", font=("Helvetica", 14))

    def load_and_display_frame(self):
        if self.video_loaded and not self.choosing_path:
            success, frame = self.cap.read()
            if success and frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (710, 710))

                self.img = frame

                self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.img))
                self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
            else:
                if not success:
                    print("Error reading frame from video.")
                else:
                    print("Empty frame received.")

        self.root.after(10, self.load_and_display_frame)

    def choose_path(self):
        if not self.video_loaded:
            self.canvas.create_text(355, 355, text="Load a video first", fill="red", font=("Helvetica", 14))
            return

        self.canvas.delete("all")

        self.load_and_display_frame()

        self.canvas.bind("<Button-1>", self.on_click)
        self.points = []
        self.choosing_path = True

        choose_path_button = Button(self.root, text="Confirm Path", command=self.confirm_path)
        choose_path_button.place(x=20, y=190, width=220, height=40)

    def confirm_path(self):
        if len(self.points) < 2:
            self.canvas.create_text(355, 355, text="Select at least two points", fill="red", font=("Helvetica", 14))
            return

        path = self.find_complex_path()
        if path:
            self.canvas.delete("path")
            has_obstacles = self.check_for_obstacles(path)

            if has_obstacles:
                cv2.putText(self.img, "Obstacles detected along the path!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                for i in range(len(path) - 1):
                    start_x, start_y = path[i]
                    end_x, end_y = path[i + 1]
                    cv2.line(self.img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
                    self.canvas.create_line(start_x, start_y, end_x, end_y, fill="green", width=2, tags="path")

                cv2.putText(self.img, "Path Found!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(self.img, "No Path Found!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

        self.points = []

    def on_click(self, event):
        x, y = event.x, event.y  
        self.points.append((x, y))

        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red", outline="red", width=2)

        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                start_x, start_y = self.points[i - 1]
                end_x, end_y = self.points[i]
                cv2.line(self.img, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)

        self.canvas.update()


    def find_complex_path(self):
        if len(self.points) < 2:
            return None

        grid_width = 710
        grid_height = 710
        cell_size = 20

        grid = [[0 for _ in range(grid_width // cell_size)] for _ in range(grid_height // cell_size)]

        for point in self.points:
            x, y = point
            grid_x = x // cell_size
            grid_y = y // cell_size
            grid[grid_y][grid_x] = 1

        start_point = self.points[0]
        end_point = self.points[-1]

        start_node = Node(start_point[0] // cell_size, start_point[1] // cell_size)
        end_node = Node(end_point[0] // cell_size, end_point[1] // cell_size)

        path = a_star(grid, (start_node.x, start_node.y), (end_node.x, end_node.y))

        if path is not None:
            return path
        else:
            return None

    def detect_parking_spaces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mask = np.zeros_like(frame)
        parking_spaces = []

        for contour in contours:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == 4 and cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 255, 0), 2)
                parking_spaces.append((x, y, x + w, y + h))

        frame_with_spaces = cv2.addWeighted(frame, 1, mask, 0.5, 0)

        return parking_spaces, frame_with_spaces

    def check_for_obstacles(self, path):
        # Implement advanced obstacle detection logic here
        # For demonstration purposes, we use a simple check.
        # You should replace this with a more sophisticated algorithm.
        # For example, you can use deep learning-based object detection.
        return False

    def find_space(self):
        if not self.video_loaded:
            self.canvas.create_text(355, 355, text="To find space, load a video first", fill="black", font=("Helvetica", 14))
        elif self.img is None:
            self.canvas.create_text(355, 355, text="No image available", fill="red", font=("Helvetica", 14))
        else:
            # Implement the functionality for finding parking spaces here
            # For demonstration purposes, we'll draw rectangles on the canvas
            # to represent parking spaces.
            parking_spaces, _ = self.detect_parking_spaces(self.img)
            for space in parking_spaces:
                x1, y1, x2, y2 = space
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=2)
    
    def exit_program(self):
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = SmartParkingSystem(root)
    root.mainloop()
