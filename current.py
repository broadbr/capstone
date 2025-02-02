##Deliverable 1: Employing openCV

# Create a virtual camera that is locked to one screen.(COMPLETE) 
# Create functions to adjust its bounds, position, and source screen.(NEEDS MIN/MAX BOUNDS)
# Make a function to start and stop the recording.(COMPLETE)
# Extract each individual frame from the video and calculate if they have changed.(COMPLETE)
# If the frame is unique enough, process it for hue variation and edge detection to determine what in the frame is text.
# Remove noise from the frames.



#import torch
#import pandas
#import sklearn
#import pyvirtualcam
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


#captures a window
def capture_window(window_title,adjustments):
    h_change = adjustments["horizontal"]
    v_change = adjustments["vertical"]
    z_change = adjustments["zoom"]

    try:
        if window_title:
            
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                print(f"Window '{window_title}' not found.")
                return None
            window = windows[0]
            
            #deafault size of the window
            #x1, y1, x2, y2 = window.left, window.top, window.left + window.width, window.top + window.height

            #desired size of the window
            width = window.width
            height = window.height

            # Apply zoom
            zoom_factor = 1 + z_change / 1000.0
            new_width = int(width * zoom_factor)
            new_height = int(height * zoom_factor)

            # Calculate new coordinates with zoom and position adjustments
            x1 = window.left + h_change - (new_width - width) // 2
            y1 = window.top + v_change - (new_height - height) // 2
            x2 = x1 + new_width
            y2 = y1 + new_height

            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

            # Convert PIL Image to OpenCV
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
        
        else:
            print("No window title provided.")
            return None

    except:
        print(f"Window '{window_title}' not found.")
        return None
        



#while recording
def start_recording(window_title):
    global adjustments
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()

    previous_frame = None
    unique_frames = 0
    count = 0

    while True:
        #calls capture_window
        try:
            frame = capture_window(window_title,adjustments)
            if frame is None:
                break

            #check if the frame is valid size
            if previous_frame is not None and frame.shape != previous_frame.shape:
                previous_frame = None
                count = 0
                cv2.imshow('Screen Capture', frame)
                previous_frame = frame.copy()
                continue

            if previous_frame is not None and count > 9:

                #compare previous frame to current frame
                diffrence = cv2.absdiff(previous_frame, frame)
                grayscale_diffrence = cv2.cvtColor(diffrence, cv2.COLOR_BGR2GRAY)

                #assigns image only if the diffrence exceeds threshold
                retval, diffrent_image = cv2.threshold(grayscale_diffrence, 10, 255, cv2.THRESH_BINARY)# (x,threshold,x,x)

                #if the diffrence is greater than the threshold
                if np.any(diffrent_image):
                    unique_frames += 1
                    print("New image detected: ", unique_frames)
                    count = 0
                

            #display the capture
            cv2.imshow('Screen Capture', frame)

            #reset previous frame
            previous_frame = frame.copy()
            if count < 10:
                count += 1
            #print(count)


            key = cv2.waitKey(1) & 0xFF 
            
            #stop recording
            if key == ord('l'):
                break
            
        
        except:("NO WINDOW FOUND")
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
        adjustments["zoom"] += 100
    elif key.char == 'z':
        adjustments["zoom"] -= 100
    #print(f"Adjustments updated: {adjustments}")
    

def adjust_source():
    window_title = input("Enter the source window title: ")

    if not window_title:
                print("Invalid window title.")
                sys.exit()

    return window_title



if __name__ == "__main__":
    

    while True:
        user_input = input("Type 'r' to start recording, 'l' to stop, or 'e' to terrminate.").lower()
        

        if user_input == "r":
            #begin recording, pass window title
            start_recording(window_title=adjust_source())


        elif user_input == "l":
            print("Capture is not running. Use 'r' to begin recording.")

        elif user_input == "e":
            print("Termminating...")
            break
        else:
            print("Please type 'r', 's', or 'e'.")

            
