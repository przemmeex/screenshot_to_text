#! /usr/bin/env python
import argparse
import os

import cv2
import pyscreenshot as ImageGrab
import pytesseract
from PIL import Image
from pynput.keyboard import KeyCode
from pynput.keyboard import Listener as KListener
from pynput.mouse import Listener


def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))


def on_click(x, y, button, pressed):
    '''
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    '''
    global x1, x2, y1, y2, was_clicked
    if pressed:
        if was_clicked == 0:
            x1, y1 = x, y

        was_clicked += 1

    if not pressed and was_clicked == 2:
        x2, y2 = x, y

        # Stop listener

        return False


def on_scroll(x, y, dx, dy):
    print('Scrolled {0}'.format((x, y)))


# Collect events until released

def on_release(key):
    print('{0} release'.format(
        key))

    if key == KeyCode(char='b'):
        # Stop listener
        return False


def on_press(key):
    print('{0} pressed'.format(
        key))


def get_text():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="path to input image to be OCR'd")
    ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                    help="type of preprocessing to be done")
    args = vars(ap.parse_args())
    image = cv2.imread(args["image"])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # check to see if we should apply thresholding to preprocess the
    # image
    if args["preprocess"] == "thresh":
        gray = cv2.threshold(gray, 0, 255,
                             cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # make a check to see if median blurring should be done to remove
    # noise
    elif args["preprocess"] == "blur":
        gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temporary file so we can
    # apply OCR to it
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    print(text)


if __name__ == '__main__':
    was_clicked = 0

    with KListener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    with Listener(
            on_click=on_click) as listener:
        listener.join()

    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    print(x1, y1, x2, y2)
    im = ImageGrab.grab(bbox=(x1, y1, x2, y2))

    im.save('im.png')

    get_text()
    print("done")

