import cv2
import numpy as np

def get_affected_stat(img_width, img_height, point):
    #deteremine which stats are affected by which arrows:

    # Given an image of size 1198 x 674
    # HP 911/176
    # ATK 1002/230
    # DEF 1002/330
    # SPATK  817/230
    # SPDEF 817/330
    # SPE 911/384
    
    IDEAL_SCREENSHOT_WIDTH = 1198
    IDEAL_SCREENSHOT_HEIGHT = 674

    # the x axis location halfway between the special stats and hp/speed stats in the hexagon view
    HEXAGON_DIVIDING_LINE_1_X_RAW = (817 + 911) / 2
    HEXAGON_DIVIDING_LINE_1_X_PERCENT = HEXAGON_DIVIDING_LINE_1_X_RAW / IDEAL_SCREENSHOT_WIDTH

    # the x axis location halfway between the physical stats and hp/speed stats in the hexagon view
    HEXAGON_DIVIDING_LINE_2_X_RAW = (911 + 1002) / 2
    HEXAGON_DIVIDING_LINE_2_X_PERCENT = HEXAGON_DIVIDING_LINE_2_X_RAW / IDEAL_SCREENSHOT_WIDTH

    # the y axis location halway between both attack and both defense stats
    HEXAGON_DIVIDING_LINE_Y_RAW = (230 + 330) / 2
    HEXAGON_DIVIDING_LINE_Y_PERCENT = HEXAGON_DIVIDING_LINE_Y_RAW / IDEAL_SCREENSHOT_HEIGHT
    
    arrow_x = point[0]
    arrow_y = point[1]
    
    #print('Arrow X, Y ' + str(arrow_x) + ',' + str(arrow_y))
    
    if (arrow_y < img_height * HEXAGON_DIVIDING_LINE_Y_PERCENT):
        # Either HP, ATK, or SPATK
        if (arrow_x < img_width * HEXAGON_DIVIDING_LINE_1_X_PERCENT):
            return 'spatk'
        if (arrow_x > img_width * HEXAGON_DIVIDING_LINE_2_X_PERCENT):
            return 'atk'
        return 'hp'
    else: 
        # Either SPEED, SPATK, or SPDEF
        if (arrow_x < (img_width * HEXAGON_DIVIDING_LINE_1_X_PERCENT)):
            return 'spdef'
        if (arrow_x > (img_width * HEXAGON_DIVIDING_LINE_2_X_PERCENT)):
            return 'defense'
        return 'speed'
        

def get_affected_stats(img_path):
    # Returns a tuple of (increased stat, decreased stat) from an image.
    # Returns None if neutral nature.

    #load image into variable
    img_rgb = cv2.imread(img_path)

    #load template
    template = cv2.imread('img/nature-neg.jpg')
    #load template
    template2 = cv2.imread('img/nature-pos.jpg')

    #read height and width of template image
    w, h = template.shape[0], template.shape[1]
    w2, h2 = template2.shape[0], template2.shape[1]

    res = cv2.matchTemplate(img_rgb,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    location_negative = list(zip(*np.where( res >= threshold)[::-1]))
    '''
    for pt in location_negative:
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
    '''
    res = cv2.matchTemplate(img_rgb,template2,cv2.TM_CCOEFF_NORMED)
    location_positive = list(zip(*np.where( res >= threshold)[::-1]))
    '''
    for pt in location_positive:
        cv2.rectangle(img_rgb, pt, (pt[0] + w2, pt[1] + h2), (0,255,0), 2)
    img_rgb = cv2.resize(img_rgb,(800,600))
    cv2.imshow("result",img_rgb)
    cv2.waitKey(1000)
    '''
      
    # We just need to get the general area of the image, so  the first point in the list is fine

    point_pos = location_positive[0]
    point_neg = location_negative[0]

    img_width = img_rgb.shape[1]
    img_height = img_rgb.shape[0]

    #print (f'Nature is increasing: {get_affected_stat(img_width, img_height, point_pos)}')
    #print (f'Nature is decreasing: {get_affected_stat(img_width, img_height, point_neg)}')
    
    return (get_affected_stat(img_width, img_height, point_pos), get_affected_stat(img_width, img_height, point_neg))



