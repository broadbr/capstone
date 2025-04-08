# capstone

citeation
    "Calibre-Regular.tff" - denvash
    https://github.com/denvash/dennisvash.com/blob/master/src/fonts/Calibre/Calibre-Regular.ttf

INSTALLS

    pip install PyQt5==5.15.11
    pip install argostranslate==1.5.2 --no-deps
    pip install ctranslate2
    pip install --upgrade argostranslate


    pip uninstall ctranslate2 pyqt5 sentencepiece -y
    pip install ctranslate2==2.4.0 sentencepiece==0.1.96

    pip install numpy opencv-python paddleocr pynput pillow

    pip install opencv-contrib-python
    -m pip install paddlepaddle
    pip install paddleocr
    pip install argos-translate

    argos-translate-cli --install-lang en fr


LIBRARIES


DO 
    conda create -n argos_env python=3.9
    conda activate argos_env
    conda info --envs

    git clone https://github.com/argosopentech/argos-translate.git
    cd argos-translate
    pip install .


    add 'encoding="utf-8"' to setup.py

    pip show argostranslate
    pip install argostranslate



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

3/12
    text highlighting is working.
    had issues resizing the ourput, using fixed dimensions solved them.
    still need to clean up results before translating
    gitignore keeps tracking my data dir

3/22 
    capture text is proccessed for whitespace and puncuation,
    then stored in sentence structure. 
    **need to get one output windoe instead of two
    **using full path for save dir  

4/5
    Combined both displays into one by changing the display source when ocr starts
    this cause zooming to break, fixed zooming by implimenting a flag
    flag sets whenever a zoom occurs and refreshes the display.

4/6 
    switching to argos-translate to improve performance over transformers.