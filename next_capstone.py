##Deliverable 1: Employing openCV

# Create a virtual camera that is locked to one screen.(COMPLETE) 
# Create functions to adjust its bounds, position, and source screen.(NO MIN/MAX BOUNDS)
# Make a function to start and stop the recording.(COMPLETE)
# Extract each individual frame from the video and calculate if they have changed.(COMPLETE)
# If the frame is unique enough, process it for hue variation and edge detection to determine what in the frame is text.(NEEDS_NUE_VARIATION)
# Remove noise from the frames.(COMPLETE~)

##2/8 works well for text files, does not work well for images, needs tuning and hue detection!!

import sys
import numpy as np
import cv2
import pynput
import pygetwindow as gw
from PIL import ImageGrab

adjustments = {
    "horizontal": 0,
    "vertical": 0,
    "zoom": 0
}


#captures a display
def capture_display(adjustments):
    screen_width, screen_height = ImageGrab.grab().size

    h_change = adjustments["horizontal"]
    v_change = adjustments["vertical"]
    z_change = adjustments["zoom"]

    #default size
    viewport_width = 800
    viewport_height = 600

    #apply zoom
    zoom_factor = 1 + z_change / 1000.0
    new_width = int(viewport_width * zoom_factor)
    new_height = int(viewport_height * zoom_factor)

    #check screen bounds
    x1 = min(max(0 + h_change, 0), screen_width - new_width)
    y1 = min(max(0 + v_change, 0), screen_height - new_height)
    x2 = x1 + new_width
    y2 = y1 + new_height

    #capture adjusted region
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    #convert PIL Image to OpenCV format
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame
        


#while recording
def start_recording():
    global adjustments
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

    previous_frame = None
    unique_frames = 0
    count = 0

    while True:
        try:
            #capture display
            frame = capture_display(adjustments)
            if frame is None:
                break

            original_size = (frame.shape[1], frame.shape[0]) #(width, height)

            #resize for text detection
            upscale_factor = 2.5
            processed_frame = cv2.resize(frame, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)
            masked_frame = detect_text_regions(processed_frame)

            #downscale for display
            display_frame = cv2.resize(processed_frame, original_size, interpolation=cv2.INTER_AREA)
            #cv2.imshow('Screen Capture', display_frame)
            cv2.imshow('Text Regions', cv2.resize(masked_frame, original_size, interpolation=cv2.INTER_AREA))

            #record unique frames
            previous_frame = processed_frame.copy()
            if count < 10:
                count += 1

            key = cv2.waitKey(1) & 0xFF 

            #stop recording
            if key == ord('l'):
                break

        except Exception as e:
            print(f"Error capturing display: {e}")

    listener.stop()
    cv2.destroyAllWindows()

##    
def on_press(key):
    global adjustments
    
    if key.char =='a':
        adjustments["horizontal"] -= 100
    elif key.char == 'd':
        adjustments["horizontal"] += 100
    elif key.char =='w':
        adjustments["vertical"] -= 100
    elif key.char == 's':
        adjustments["vertical"] += 100
    elif key.char == 'x':
        adjustments["zoom"] -= 100## + = out, - = in
    elif key.char == 'z':
        adjustments["zoom"] += 100
    #print(f"Adjustments updated: {adjustments}")
    

def adjust_source():
    window_title = input("Enter the source window title: ")

    if not window_title:
                print("Invalid window title.")
                sys.exit()

    return window_title

def detect_text_regions(frame):##NEEDS_TUNING

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)##redundant??

    #reduce noise with gaussian blur
    blur_frame = cv2.GaussianBlur(gray_frame, (5,5), 0)## (width,hight)

    #detect edges
    edge_frame = cv2.Canny(blur_frame, 30, 100)## (x, min, max)  --  30, 100

    #find contours
    contours, _ = cv2.findContours(edge_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #mask non-text regions
    mask = np.zeros_like(gray_frame)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h

        #filter out non-text regions
        if aspect_ratio > 0.1 and aspect_ratio < 10:## (min,max) text aspect ratio  --  .1, 10
            cv2.drawContours(mask, [contour], -1, (255), -1)## (image, x, contour, color, x)

    #apply mask
    masked_frame = cv2.bitwise_and(gray_frame, gray_frame, mask=mask)

    return masked_frame

    
##HUE DETECTION


if __name__ == "__main__":
    

    while True:
        user_input = input("Type 'r' to start recording, 'l' to stop, or 'e' to terrminate.").lower()
        

        if user_input == "r":
            #begin recording, pass window title
            start_recording()


        elif user_input == "l":
            print("Capture is not running. Use 'r' to begin recording.")

        elif user_input == "e":
            print("Termminating...")
            break
        else:
            print("Please type 'r', 's', or 'e'.")

            

