##FIRST COMPLETE DELIVERABLE
#Ryan Broadbent 2/2x?

##Deliverable 1: Employing openCV

# Create a virtual camera that is locked to one screen.(COMPLETE) 
# Create functions to adjust its bounds, position, and source screen.(COMPLETE)
# Make a function to start and stop the recording.(COMPLETE)
# Extract each individual frame from the video and calculate if they have changed.(COMPLETE)
# If the frame is unique enough, process it for hue variation and edge detection to determine what in the frame is text.(~COMPLETE)
    ###NOTE REPLACED EDGE DETECTION WITH MORPHOLOGICAL OPENING
# Remove noise from the frames.(~COMPLETE)

##2/16 preprocesses txt format images, may not work well low contrast images with complex backgrounds

import sys
import numpy as np
import cv2
import pynput
#import pygetwindow as gw
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
            upscale_factor = 2
            processed_frame = cv2.resize(frame, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)
            masked_frame = detect_text_regions(processed_frame)

            #downscale for display
            display_frame = cv2.resize(processed_frame, original_size, interpolation=cv2.INTER_AREA)
            cv2.imshow('Screen Capture', display_frame)
            cv2.imshow('Text Regions', cv2.resize(masked_frame, original_size, interpolation=cv2.INTER_AREA))


            #check if the frame is valid size
            if previous_frame is not None and processed_frame.shape != previous_frame.shape:
                previous_frame = None
                count = 0
                #cv2.imshow('Screen Capture', frame)
                previous_frame = processed_frame.copy()
                continue
            if previous_frame is not None and count > 9:

                #compare previous frame to current frame
                diffrence = cv2.absdiff(previous_frame, processed_frame)
                grayscale_diffrence = cv2.cvtColor(diffrence, cv2.COLOR_BGR2GRAY)

                #assigns image only if the diffrence exceeds threshold
                retval, diffrent_image = cv2.threshold(grayscale_diffrence, 10, 255, cv2.THRESH_BINARY)# (x,threshold,x,x)

                #if the diffrence is greater than the threshold
                if np.any(diffrent_image):
                    unique_frames += 1
                    print("New image detected: ", unique_frames)
                    count = 0


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
    
    try:
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
    except AttributeError:
        pass
    

def adjust_source():
    window_title = input("Enter the source window title: ")

    if not window_title:
                print("Invalid window title.")
                sys.exit()

    return window_title

def detect_text_regions(frame):##NEEDS_TUNING

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)##redundant??

    #reduce noise
    filter_frame = cv2.GaussianBlur(gray_frame, (5,5), 0)## (width,hight)  --  5,5

    #thresholding
    threshold_frame = cv2.adaptiveThreshold(filter_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, #  --  255,21,5
                                         cv2.THRESH_BINARY_INV, 21, 5) #(block size, constant)larger mor aggresive filtering

    #deskewing
    ##############################
    ##############################


    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))#  --  3,3
    #dialation
    edge_frame = cv2.morphologyEx(threshold_frame, cv2.MORPH_OPEN, kernel)#morph close too

    processed_frame = edge_frame

    return processed_frame

        
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

            

