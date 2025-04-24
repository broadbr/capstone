##CURRENT_BUILD: Employing easyOCR
                 #3/2NOTE: NOW USING PADDLEOCR INSTEAD

#####################deliverable 3 requirements####################

#Implement a function to periodically send and receive text files from the library.(user can send text munually)
#Integrate compatibility with an offline translation model.(This caused compatibility issues with the paddleOCR model)(removed)
#Create a function to safely edit the target language.(complete)
#Read format and display the translated text to a separate window.(outputs to terminal)(functionally complete)
#Refine the text detection and identification methods.(completed)
#Add function to save current translation and original frame.(user can view original frame and translated text)(screenshots are temporaroly saved)

#additional updates:
## 4/5 merged windows, fixed zooming by adding a flag
## 4/11 added screenshots, and translation
## 4/19 added character limmit detection and language selection

import sys
import numpy as np
import cv2
import json
import os
import re
import pynput
from PIL import ImageGrab
from paddleocr import PaddleOCR, draw_ocr
import tkinter as tk
import threading

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
directory = "C:\\Users\\Ryan Broadbent\\Desktop\\capstone\\capstone\\data\\photos"
os.makedirs(save_dir, exist_ok=True)
json_path = os.path.join(save_dir, "ocr_results.json")
formatted_json_path = os.path.join(save_dir, "formatted_ocr_results.json")

adjustments_changed = False

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
    global adjustments, adjustments_changed, ocr_results

    clear_screenshots(directory)

    if os.path.exists(json_path):
        with open(json_path, "w") as json_file:
            json.dump([], json_file)
            
    if os.path.exists(formatted_json_path):
        with open(formatted_json_path, "w") as formatted_file:
            json.dump([], formatted_file)


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

            original_size = (frame.shape[1], frame.shape[0])
            upscale_factor = 2
            processed_frame = cv2.resize(frame, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)
            masked_frame = detect_text_regions(processed_frame)
            display_frame = cv2.resize(processed_frame, original_size, interpolation=cv2.INTER_AREA)

            #display frame
            if highlighted_frame is not None:
                highlighted_display = cv2.resize(highlighted_frame, original_size, interpolation=cv2.INTER_AREA)
                cv2.imshow('Highlighted Text', highlighted_display)
            else:
                cv2.imshow('Highlighted Text', display_frame)

            #check for adjustments or size change
            if (previous_frame is None or processed_frame.shape != previous_frame.shape) or adjustments_changed:
                previous_frame = processed_frame.copy()
                count = 0
                adjustments_changed = False
                unique_frames += 1
                print("New image detected (resize or adjustment):", unique_frames)
                highlighted_frame = paddle_ocr(processed_frame, unique_frames)

            #process every 10 frames
            elif count > 9:
                difference = cv2.absdiff(previous_frame, processed_frame)
                grayscale_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
                _, diff_image = cv2.threshold(grayscale_diff, 10, 255, cv2.THRESH_BINARY)

                if np.any(diff_image):
                    unique_frames += 1
                    print("New image detected (diff):", unique_frames)
                    highlighted_frame = paddle_ocr(processed_frame, unique_frames)
                    count = 0

            previous_frame = processed_frame.copy()
            count += 1

            key = cv2.waitKey(1) & 0xFF
            if key == ord('l'):
                break

        except Exception as e:
            print(f"Error capturing display: {e}")

    listener.stop()
    cv2.destroyAllWindows()

##    
def on_press(key):
    global adjustments, adjustments_changed

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

        adjustments_changed = True

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

    screenshots_dir = os.path.join(save_dir, "photos")
    screenshot_path = os.path.join(screenshots_dir, f"frame_{unique_frame_count}.png")
    cv2.imwrite(screenshot_path, frame)
    
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

    #format data
    ocr_results = load_data(json_path)
    formatted_results = format_json(ocr_results)
    save_formatted_data(formatted_results, formatted_json_path)

    return highlighted_frame


def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_formatted_data(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def format_json(ocr_results):
    formatted_data = []

    for entry in ocr_results:
        frame_index = entry["frame_index"]
        orignal_text = " ".join(entry["text"])

        #whitespace
        raw_text = re.sub(r'\s+', ' ', orignal_text).strip()

        sentences = re.split(r'(?<=[.!?])\s+', raw_text)

        #store segmented data
        formatted_data.append({
            "frame_index": frame_index,
            "formated_text": sentences
        })
    return formatted_data

def clear_screenshots(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

target_language = "fr"

if __name__ == "__main__":


    root = tk.Tk()
    root.title("Screen Capture Control")
    root.geometry("300x300")

    #deafult to french
    #target_language = "fr"

    def on_start_recording():
        print("Starting recording...")
        start_recording()
        print("Recording stopped. You can now use console commands ('t', 'v', 'c', 'e').")

    def toggle_language():
        global target_language
        if target_language == "fr":
            target_language = "es"
            print("Target language is now Spanish.")
            language_label.config(text=f"Current Language: Spanish")
        else:
            target_language = "fr"
            print("Target language is now French.")
            language_label.config(text=f"Current Language: French")

    def terminate_program():
        print("Terminating...")
        root.destroy()
        sys.exit()

    #recording UI
    start_button = tk.Button(root, text="Start Recording", command=on_start_recording, font=("Arial", 14))
    start_button.pack(pady=20)

    toggle_button = tk.Button(root, text="Toggle Language", command=toggle_language, font=("Arial", 12))
    toggle_button.pack(pady=10)

    language_label = tk.Label(root, text=f"Current Language: French", font=("Arial", 10))
    language_label.pack(pady=5)

    terminate_button = tk.Button(root, text="Terminate", command=terminate_program, font=("Arial", 12))
    terminate_button.pack(pady=10)

    ##viewing, translating/ouputting

    # label
    instruction_label = tk.Label(root, 
    text="Click 'Start Recording' to begin.\nPress 'l' to stop recording\nUse 'w,a's,d' to pan.\n"
         "Use 'z,x' to zoom.\nUse console for other commands ('t', 'v', 'c', 'e').", 
    font=("Arial", 10))
    instruction_label.pack(pady=10)


    def run_gui():
        root.mainloop()


    run_gui()


## ADD FUNTION TO VIEW CAPTURED FRAMES

    while True:
        user_input = input("Type 't' to translate, 'v' to view, 'c' to change target language, or 'e' to terrminate.").lower()
        

        #if user_input == "r":
            #begin recording, pass window title
            #start_recording()


        if user_input == "l":
            print("Capture is not running. Use 'r' to begin recording.")

        elif user_input == "c":
            #change the target language
            if target_language == "fr":
                target_language = "es"
                print("Target language is now Spanish.")
            else:
                target_language = "fr"
                print("Target language is now French.")

        elif user_input == "t":
            try:
                #load formatted OCR results
                if not os.path.exists(formatted_json_path):
                    print("No captures found. Please run a capture first.")
                    continue

                formatted_results = load_data(formatted_json_path)

                #ask the for frame index
                frame_index = input("Enter the frame index you want to translate: ")
                if not frame_index.isdigit():
                    print("Invalid index. Please enter a valid number.")
                    continue

                frame_index = int(frame_index)

                #find the frame in the formatted results
                frame_data = next((entry for entry in formatted_results if entry["frame_index"] == frame_index), None)
                if not frame_data:
                    print(f"Invalid index {frame_index}.")
                    continue

                #get text
                text_to_translate = " ".join(frame_data["formated_text"])
                print(f"Original text for frame {frame_index}: {text_to_translate}")

                #check char limit
                if len(text_to_translate) > 500:
                    print("Translation exceeds 500 character limit.")
                    continue

                #translate text
                from translate import Translator
                translator = Translator(from_lang="en", to_lang="fr")
                translated_text = translator.translate(text_to_translate)

                # Print the translated text
                print(f"Translated text for frame {frame_index}: {translated_text}\n")

            except Exception as e:
                print(f"Error during translation: {e}")

        elif user_input == "v":
            try:
                if not os.path.exists(formatted_json_path):
                    print("No existing captures.")
                    continue

                formatted_results = load_data(formatted_json_path)

                #list entrie count
                num_entries = len(formatted_results)
                print(f"There are {num_entries} captured images to traslate.")

                #select frame index
                frame_index = input("Enter the frame index you want to view: ")
                if not frame_index.isdigit():
                    print("Invalid index.")
                    continue

                frame_index = int(frame_index)

                #check for frame
                frame_data = next((entry for entry in formatted_results if entry["frame_index"] == frame_index), None)
                if not frame_data:
                    print(f"Invalid index")
                    continue

                #display the screenshot
                screenshot_path = os.path.join(directory, f"frame_{frame_index}.png")
                screenshot = cv2.imread(screenshot_path)
                screenshot_width = 800
                screenshot_height = 600
                resized_screenshot = cv2.resize(screenshot, (screenshot_width, screenshot_height))

                cv2.imshow(f"Frame {frame_index}", resized_screenshot)
                print(f"Press 'l' to close.")

                key = cv2.waitKey(0)
                if key == ord('l'):
                    break
                cv2.destroyAllWindows()

            except Exception as e:
                print(f"Error while viewing screenshot: {e}")



        elif user_input == "e":
            print("Termminating...")
            break
        else:
            print("Please type 'r', 's', or 'e'.")

            

