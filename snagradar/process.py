# importing libraries 
import cv2 
import numpy as np 
import os
import uuid
import imutils
from scipy.ndimage import interpolation as inter
import time

def write_cropped(path):
    print('Reading file for crop: ' + path)
    angle, crop_img = correct_skew(crop_switch_screen(path))
    cropped_filename = os.path.join(os.path.dirname(path), 'crop' + str(uuid.uuid4()) + '.png')
    print('Saving file: ' + cropped_filename)
    cv2.imwrite(cropped_filename, crop_img)
    return cropped_filename

blackLower = (0, 0, 0)
blackUpper = (50, 50, 50)

def blur_and_mask(frame, lower_color, upper_color):
    blurred = cv2.GaussianBlur(frame, (5, 5), 3)
    mask = cv2.inRange(blurred, blackLower, blackUpper)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel)
    return mask

def crop2(path):
    image = cv2.imread(path) 
    # Grayscale the image and apply a gaussian blur to it
    mask = blur_and_mask(image, blackLower, blackUpper)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cnts = cv2.findContours(
        mask.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = imutils.grab_contours(cnts)
    #print('found cnts: ' + str(len(cnts)))
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
        #c = max(cnts, key=cv2.contourArea)
        rect = cv2.boundingRect(c)
        # This area is too small to be of our
        # interest, disregard it and go to the
        # next frame
        if rect[2] < 100 or rect[3] < 100: 
            continue
                # Unpack the bounding box
        x,y,w,h = rect
        y1 = y
        y2 = y + h
        x1 = x
        x2 = x + w
        # Draw the bounding box on the frame
        cv2.rectangle(
            image, (x,y),
            (x+w,y+h), (0,255,0),
            2
        )
        # Take a canny edge detection of the newly drawn
        # rectangle from the original grey scale image.
        # This will perform edge detection in only the
        # area of interect (the cv2 rectangle defined above).
        # This will make all the edges white and the
        # rest of the pixels black. So, we have to invert it
        # so the black becomes white and the
        # white becomes black (to fit the AHA video)
        to_canny = cv2.GaussianBlur(
            gray[y:y+h, x:x+w],
            (5, 5),
            3
        )
        edges = cv2.bitwise_not(cv2.Canny(to_canny, 0, 50))
        # Since the edges are only a 2-channel frame,
        # we can overlay it on to each channel in the
        # original frame
        image[y1:y2, x1:x2, 0] = edges
        image[y1:y2, x1:x2, 1] = edges
        image[y1:y2, x1:x2, 2] = edges
        # Display the resulting frame
        cv2.imshow('crop2',image)
        cv2.waitKey(0)
    return image

def crop_switch_screen(path):
    #image = cv2.imread('img/landopicture.jpg') 
    image = cv2.imread(path) 
    # convert the image to grayscale, blur it, and find edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    '''
    cv2.imshow("image", gray)
    cv2.waitKey(0)
    '''
    # find contours
    cnts, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # sort by area and leave only 5 largest
    #print('found contours: ' + str(cnts))
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]  

    screenCnt = cnts[0] # this is the switch screen.



    # iterate over contours and find which satisfy some conditions
    
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) # you could tune value of 0.02
        x, y, w, h = cv2.boundingRect(approx)

        # this is the red rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 5)
        # or draw contour (blue)
        newimg = cv2.drawContours(image, [screenCnt], -1, (255, 0, 0), 7)
        #cv2.imshow("image", newimg)
        #cv2.waitKey(0)

        if h >= 15 and len(approx) == 4:
            screenCnt = approx
            break
    
    # if found
    
    if screenCnt is not None:  
        # draw rect
        x, y, w, h = cv2.boundingRect(screenCnt)
        # this is the red rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 5)
        # or draw contour (blue)
        newimg = cv2.drawContours(image, [screenCnt], -1, (255, 0, 0), 7)
        #cv2.imshow("image", newimg)
        #cv2.waitKey(0)
    
        
    #coords = zip(*screenCnt)
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
    #cv2.imshow("cropped", crop_img)
    #cv2.waitKey(0)
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

def nothing(x):
    pass

def remove_nonwhite_cells(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # pretty good (0, 0, 168), (172,111,255)
    # determined via whiteprocessing.py
    only_white = cv2.inRange(hsv, (0, 0, 137), (179,124,255))
    return only_white


if(__name__=="__main__"):
    img = "H:\\Projects\\snagradar\\instance\\upload\\IMG20250327181409.jpg"
    crop = crop_switch_screen(img)
    cv2.imshow("cropped", crop)
    angle, corrected = correct_skew(crop)
    only_white = remove_nonwhite_cells(corrected)
    #print('Skew angle:', angle)
    #cv2.imshow('corrected', corrected)
    cv2.imshow('only_white', only_white)
    
    cv2.waitKey()
    cv2.imwrite('img/landocrop.jpg', corrected)
    cv2.imwrite('img/landowhite.jpg', only_white)
