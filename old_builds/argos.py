##CURRENT_BUILD: Employing easyOCR
                 #3/2NOTE: NOW USING PADDLEOCR INSTEAD

#####################deliverable 3 requirements####################

#Implement a function to periodically send and receive text files from the library. 
#Integrate compatibility with an offline translation model. 
#Create a function to safely edit the target language.

#Read format and display the translated text to a separate window. 
#Refine the text detection and identification methods. 
#Add function to save current translation and original frame.

#additional updates:
## 4/5 merged windows, fixed zooming by adding a flag

import sys
import numpy as np
import cv2
import json
import os
import re
import pynput
from PIL import ImageGrab
from paddleocr import PaddleOCR, draw_ocr

import argostranslate.package
import argostranslate.translate
import torch
torch.utils.logging.set_verbosity(torch.utils.logging.DEBUG)

installed_languages = argostranslate.translate.get_installed_languages()

#from translate import Translator
#translator = Translator(from_lang="en", to_lang="fr")
#print(translator.translate("translate opperational"))


adjustments = {
    "horizontal": 0,
    "vertical": 0,
    "zoom": 0
}

paddle_reader = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
ocr_results = []
processor = ""

##### DESIRED SAVE DIRECTORY #####
save_dir = "C:\\Users\\Ryan Broadbent\\Desktop\\capstone\\capstone\\data"
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
    global adjustments, adjustments_changed
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


        
def paddle_ocr(frame, unique_frame_count,  from_lang="en", to_lang="fr"):

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
    

    #translated_text = [translate_text(text, from_lang, to_lang) for text in extracted_text]
    translated_text = []
    for text in extracted_text:
        translated = translate_text(text, from_lang, to_lang)
        translated_text.append(translated)


    #display text  4/6
    translated_display = np.zeros((500, 300, 3), dtype=np.uint8)
    y_offset = 20
    for line in translated_text:
        cv2.putText(translated_display, line, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 30
    cv2.imshow('Translated Text', translated_display)


    ## creates wide frame with all data
    ##highlighted_frame = draw_ocr(frame, boxes, texts, scores, font_path='Calibre-Regular.ttf')
    highlighted_frame = draw_ocr(frame, boxes, None, None, font_path='Calibre-Regular.ttf')


    highlighted_frame = cv2.cvtColor(np.array(highlighted_frame), cv2.COLOR_RGB2BGR)
    ##cv2.imshow('Highlighted Text', highlighted_frame)## current display

    ocr_data = {
        "frame_index": unique_frame_count,
        "text": extracted_text,
        "translated_text": translated_text ##4/6
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


def translate_text(text, from_lang="en", to_lang="fr"):
    try:
        #translation direction
        from_lang_obj = next((lang for lang in installed_languages if lang.code == from_lang), None)
        to_lang_obj = next((lang for lang in installed_languages if lang.code == to_lang), None)

        if not from_lang_obj or not to_lang_obj:
            raise ValueError(f"Language codes not installed: {from_lang}, {to_lang}")

        translation = from_lang_obj.get_translation(to_lang_obj)
        return translation.translate(text)
    
    except Exception as e:
        print(f"[Translation Error] {text} — {e}")
        return text  ##fallback

def install_argos_package(from_lang="en", to_lang="fr"):
    available_packages = argostranslate.package.get_available_packages()
    matching_package = next(
        (p for p in available_packages if p.from_code == from_lang and p.to_code == to_lang),
        None
    )
    
    if matching_package:
        print(f"Downloading {from_lang} → {to_lang} model...")
        download_path = matching_package.download()
        argostranslate.package.install_from_path(download_path)
        print("Installation complete!")
    else:
        print("Requested language pair not found.")


if __name__ == "__main__":
    install_argos_package("en", "fr")

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

            

