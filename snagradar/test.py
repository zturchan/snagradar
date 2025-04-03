# Load image 2048x2048 RGB

import cv2
import numpy as np
import imutils

# Load the image
img = "H:\\Projects\\snagradar\\instance\\upload\\IMG20250327181409.jpg"
image = cv2.imread(img)

#try
#0 79 29, 127, 233, 86

# Convert to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the lower and upper bounds of the color range (e.g., blue)
lower_blue = np.array([0, 79, 29])  # Example: Lower bound for blue
upper_blue = np.array([127, 233, 86]) # Example: Upper bound for blue

# Create the mask using cv2.inRange()
mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

# Apply the mask to the original image (optional)
gray = cv2.bitwise_and(image, image, mask=mask)

# Display the results
cnts = cv2.findContours(
    mask.copy(),
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)
cnts = imutils.grab_contours(cnts)
print('found cnts: ' + str(len(cnts)))
for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
    print(c)
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