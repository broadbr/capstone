##Deliverable 2: Employing easyOCR
                 #3/2NOTE: NOW USING PADDLEOCR INSTEAD

##Highlight areas of interest and develop a mask for the frames.(REDUNDANT)
##Use language identification to extract text from highlighted regions.(COMPLETE)
##Develop an overlay to display the regions as highlighted in the recording preview.(~complete)
                                        ##currently have two seperate windows could be combined
##Segment and format the resulting text into chunks suitable for translation. ()
##Store text chunks in a structured format.(UNFORMATTED JSON)


import sys
import numpy as np
import cv2
import json
import os
import pynput
from PIL import ImageGrab
from paddleocr import PaddleOCR, draw_ocr

adjustments = {
    "horizontal": 0,
    "vertical": 0,
    "zoom": 0
}

paddle_reader = PaddleOCR(use_angle_cls=True, lang='en')
ocr_results = []
processor = ""

##### DESIRED SAVE DIRECTORY #####
save_dir = "C:\\Users\\Ryan Broadbent\\Desktop\\capstone\\capstone\\data"
os.makedirs(save_dir, exist_ok=True)
json_path = os.path.join(save_dir, "ocr_results.json")



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

    highlighted_frame = None

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

            ## capture and garyscale
            ##cv2.imshow('Screen Capture', display_frame)############
            cv2.imshow('Text Regions', cv2.resize(masked_frame, original_size, interpolation=cv2.INTER_AREA))############

            if highlighted_frame is not None:
                ##cv2.imshow('Highlighted Text', cv2.resize(highlighted_frame, None, fx=.25, fy=.25, interpolation=cv2.INTER_AREA))## current display
                desired_width = 400
                desired_height = 400
                resized_highlighted = cv2.resize(highlighted_frame, (desired_width, desired_height), interpolation=cv2.INTER_AREA)

                cv2.imshow('Highlighted Text', resized_highlighted)

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

                    #proccess frame ocr
                    ##paddle_ocr(processed_frame, unique_frames)
                    highlighted_frame = paddle_ocr(processed_frame, unique_frames)##

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


        
def paddle_ocr(frame, unique_frame_count):

    global ocr_results

    results = paddle_reader.ocr(frame, cls=True)

    extracted_text = []
    boxes = []
    texts = []
    scores = []

    for line in results:
        for word_info in line:
            extracted_text.append(word_info[1][0]) ##word_info[1][0] is text
            boxes.append(word_info[0])             ##word_info[0] is bounding box
            texts.append(word_info[1][0])          ##word_info[1][0] is text
            scores.append(word_info[1][1])         ##word_info[1][1] is confidence score

                                                                        ##relative path to font file
    
    ## creates wide frame with all data
    ##highlighted_frame = draw_ocr(frame, boxes, texts, scores, font_path='Calibre-Regular.ttf')
    highlighted_frame = draw_ocr(frame, boxes, None, None, font_path='Calibre-Regular.ttf')


    highlighted_frame = cv2.cvtColor(np.array(highlighted_frame), cv2.COLOR_RGB2BGR)
    ##cv2.imshow('Highlighted Text', highlighted_frame)## current display

    ocr_data = {
        "frame_index": unique_frame_count,
        "text": extracted_text
    }
    ocr_results.append(ocr_data)

    with open(json_path, "w") as json_file:
        json.dump(ocr_results, json_file, indent=4)

    return highlighted_frame


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

            

