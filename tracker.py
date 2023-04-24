import cv2
import numpy as np
import csv
import time
import tkinter as tk
from tkinter import filedialog

# Function to detect ball color
def detect_color(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        contour_area = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour_area) > 100:
            (x, y, w, h) = cv2.boundingRect(contour_area)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            return True, (x + w // 2, y + h // 2)
    return False, None

# Define color ranges for each ball color
color_ranges = {
    "orange": ((0, 70, 50), (20, 255, 255)),
    "green": ((50, 70, 50), (70, 255, 255)),
    "yellow": ((20, 70, 50), (40, 255, 255)),
    "white": ((100, 70, 50), (130, 255, 255))
}

# Initialize counters for entering and exiting balls for each quadrant
entering_balls = {1: 0, 2: 0, 3: 0, 4: 0}
exiting_balls = {1: 0, 2: 0, 3: 0, 4: 0}

# Open video file
root = tk.Tk()
root.withdraw()

# Ask the user to select the video file
video_path = filedialog.askopenfilename(title="Select video file", filetypes=[("MP4 files", "*.mp4")])
cap = cv2.VideoCapture(video_path)
frame_rate = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Create CSV file to save event data
timestamp = time.strftime("%Y%m%d-%H%M%S")
csv_file = open(f"event_data_{timestamp}.csv", mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Time", "Quadrant Number", "Ball Colour", "Type"])

# Define font for text overlay
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_thickness = 1
font_color = (255, 255, 255)
thickness = 1

# Define codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(f"tracking_video_{timestamp}.mp4", fourcc, frame_rate, (1920, 1080))

# Loop through each frame in the video
for frame_num in range(total_frames):
    ret, frame = cap.read()
    if not ret:
        break

    # Detect ball colors
    for color, (lower, upper) in color_ranges.items():
        detected, center = detect_color(frame, np.array(lower), np.array(upper))
        if detected:
            # Check quadrant of ball based on its position
            x, y = center
            quadrant = 0
            if x < frame.shape[1] // 2 and y < frame.shape[0] // 2:
                quadrant = 1
            elif x >= frame.shape[1] // 2 and y < frame.shape[0] // 2:
                quadrant = 2
            elif x < frame.shape[1] // 2 and y >= frame.shape[0] // 2:
                quadrant = 3
            else:
                quadrant = 4

            # Update event data and CSV file
            timestamp = frame_num / frame_rate
            if entering_balls[quadrant] == exiting_balls[quadrant]:
                csv_writer.writerow([timestamp, quadrant, color, "Entry"])
                cv2.putText(frame, f"Entry - {color}", (x, y), font, font_scale, (0, 255, 0), font_thickness)
                entering_balls[quadrant] += 1
            else:
                csv_writer.writerow([timestamp, quadrant, color, "Exit"])
                cv2.putText(frame, f"Exit - {color}", (x, y), font, font_scale, (0, 0, 255), font_thickness)
                exiting_balls[quadrant] += 1

            # Add text to frame for each quadrant
            for i in range(1, 5):
                text = f"Q{i} - Entry: {entering_balls[i]}, Exit: {exiting_balls[i]}"
                cv2.putText(frame, text, (10, 30*i), font, font_scale, font_color, thickness, cv2.LINE_AA)
                
    # Write frame to video file
    out.write(frame)

    # Display video frame
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video file and close CSV file
cap.release()
cv2.destroyAllWindows()
csv_file.close()
out.release() # returns the output tracking video file
