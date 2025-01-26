##Deliverable 1: Employing openCV

# Create a virtual camera that is locked to one screen.(COMPLETE) 
# Create functions to adjust its bounds, position, and source screen.
# Make a function to start and stop the recording.(COMPLETE)
# Extract each individual frame from the video and calculate if they have changed. 
# If the frame is unique enough, process it for hue variation and edge detection to determine what in the frame is text.
# Remove noise from the frames.

import sys
import numpy as np
import torch
import cv2
import pandas
import sklearn
import pyvirtualcam
from pynput import keyboard
import pygetwindow as gw
from PIL import ImageGrab

#captures a window
def capture_window(window_title=None):
    
    try:
        if window_title:
            
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                print(f"Window '{window_title}' not found.")
                return None
            window = windows[0]
            
            #Deafault size of the window
            x1, y1, x2, y2 = window.left, window.top, window.left + window.width, window.top + window.height##auto
            #x1, y1, x2, y2 = 0, 400, 400, 400##manual
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

                #convert PIL Image to OpenCV
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
    
    while True:
        #calls capture_window
        try:
            frame = capture_window(window_title)

            if frame is None:
                break

            #display the capture
            cv2.imshow('Screen Capture', frame)

            # Exit the loop if 's' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
            
        
        except:("NO WINDOW FOUND")

    cv2.destroyAllWindows()

##    
def adjust_bounds():
    pass

def adjust_position():
    pass

def adjust_source():
    window_title = input("Enter the source window title: ")

    if not window_title:
                print("Invalid window title.")
                sys.exit()

    return window_title




if __name__ == "__main__":

    #TEMP start message
    #print("Type 'r' to start recording, 's' to stop, or 'exit' to terrminate.")

    while True:
        user_input = input("Type 'r' to start recording, 's' to stop, or 'e' to terrminate.").lower()

        if user_input == "r":
            
            #begin recording, pass window title
            start_recording(window_title=adjust_source())


        elif user_input == "s":
            print("Capture is not running. Use 'r' to begin recording.")

        elif user_input == "e":
            print("Termminating.")
            break
        else:
            print("Please type 'r', 's', or 'e'.")

            
#listener = keyboard.Listener(on_press=on_press)
#listener.start()



