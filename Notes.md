# capstone

INSTALLS
    pip install opencv-contrib-python
    -m pip install paddlepaddle
    pip install paddleocr

LIBRARIES


IMPORTANT INFO
    current_capstone.py is the up to date project file
    next_capstone.py is the in progress project file
    other .py files contain functions that are no longer being implimented


CS 498 capstone Notes

2/__


2/15
    Need to add text color selection.
    Move from capturing a window to a screen, starting with default location and size.

2/17
    using addaptive theresholding instead of hue selection.

2/18
    preprocesses txt format images, may not work well low contrast images with complex backgrounds
    replaced edge detection with morphilogical open.

2/25
    creating data folder for saving text
    performance issues


3/2 
    switching to cpu based OCR