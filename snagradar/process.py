import cv2 
import numpy as np 
import os
import uuid
from scipy.ndimage import interpolation as inter

def write_cropped(path):
    """Given a picture of a Nintendo Switch screen, attempts to use the black screen
    borders as a bounding rectangle to crop the image. Then, if the screen is still at
    a bad angle, attempt to correct the skew as best we can.

    Saves the modified result to the upload directory.
    """
    print('Reading file for crop: ' + path)
    angle, crop_img = correct_skew(crop_switch_screen(path))
    cropped_filename = os.path.join(os.path.dirname(path), os.path.splitext(os.path.basename(path))[0] + '-cropped.jpg')
    print('Saving cropped file: ' + cropped_filename)
    cv2.imwrite(cropped_filename, crop_img)
    return cropped_filename

def crop_switch_screen(path):
    image = cv2.imread(path) 
    # convert the image to grayscale, blur it, and find edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    # find contours
    cnts, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # sort by area and leave only 5 largest
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]  

    screenCnt = cnts[0] # this is the switch screen.

    # iterate over contours and find which satisfy some conditions
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) # you could tune value of 0.02
        x, y, w, h = cv2.boundingRect(approx)

        # this is the red rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 5)

        if h >= 15 and len(approx) == 4:
            screenCnt = approx
            break
    
    if screenCnt is not None:  
        x, y, w, h = cv2.boundingRect(screenCnt)
        
    xcoords = []
    ycoords = []
    for c in screenCnt:
        xcoords.append(c[0][0])
        ycoords.append(c[0][1])

    x_min = min(xcoords)
    x_max = max(xcoords)
    y_min = min(ycoords)
    y_max = max(ycoords)

    crop_img = image[y_min:y_max, x_min:x_max]
    return crop_img
    
# from https://stackoverflow.com/questions/57964634/python-opencv-skew-correction-for-ocr

def correct_skew(image, delta=1, limit=5):
    def determine_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] 

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
            borderMode=cv2.BORDER_REPLICATE)

    return best_angle, corrected