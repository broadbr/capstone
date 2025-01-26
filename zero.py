##Deliverable 1: Employing openCV

##Create a virtual camera that is locked to one screen. Create functions to adjust its bounds, position, and source screen.
# Make a function to start and stop the recording.

##Extract each individual frame from the video and calculate if they have changed. 
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
    if window_title:
        try:
            
            window = gw.getWindowsWithTitle(window_title)[0]
            
            #Deafault size of the window
            x1, y1, x2, y2 = window.left, window.top, window.left + window.width, window.top + window.height##auto
            #x1, y1, x2, y2 = 0, 400, 400, 400##manual
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        except:
            print(f"Window '{window_title}' not found.")
            return None
        

    #convert PIL Image to OpenCV
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    return frame


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
    window_title = input("Enter new source window: ")

#def on_press(key):
 #   try:
  #      if key.char == 'r':
   #         start_recording()
    #    if key.char == 'q':
     #       sys.exit()
    #except AttributeError:
     #   pass 

#default window title    
window_title = "File Explorer"



if __name__ == "__main__":

    window_title = input("Enter the source window: ")

    if window_title:
        start_recording(window_title)
    else:
        print("Window not found.")

    

            
#listener = keyboard.Listener(on_press=on_press)
#listener.start()



