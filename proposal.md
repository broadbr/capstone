# capstone

Ryan Broadbent 11/11/24

CS 498 capstone proposal


Objective:

Develop a windows application capable of capturing a screen recording, and displaying a translated version of the text visible in the recording.

Requirements:

The application will feature an interface allowing the user to select and preview a source window and a desired output language. Static text in the video will be processed, translated, and displayed in the application.



Deliverable 1: Employing openCV

Create a virtual camera that is locked to one screen. Create functions to adjust its bounds, position, and source screen. Make a function to start and stop the recording.

Extract each individual frame from the video and calculate if they have changed. If the frame is unique enough, process it for hue variation and edge detection to determine what in the frame is text. Remove noise from the frames.

Deliverable 2: Employing easyOCR

Highlight areas of interest and develop a mask for the frames. Use language identification to extract text from highlighted regions. Develop an overlay to display the regions as highlighted in the recording preview. Segment and format the resulting text into chunks suitable for translation. Store text chunks in a structured format.


Deliverable 3: Employing googletrans

Implement a function to periodically send and receive text files from the library. Integrate compatibility with an offline translation model. Create a function to safely edit the target language.

Read format and display the translated text to a separate window. Refine the text detection and identification methods. Add function to save current translation and original frame.


Deliverable 4: GUI

Create an interface that is easy to understand and operate that interacts with the functions to select a source window, adjust the screen recorder, control the recording, save translation, select the target language, and translate the model.

The text output window and the preview of the screen recording will be contained in the window. It will need to adjust dynamically. Package the executable application in a container.