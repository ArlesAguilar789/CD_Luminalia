import cv2 as cv
import numpy as np

img = np.ones([400, 400], np.uint8) * 255

img[1, 1] = 0

cv.imshow("imagen", img)
cv.waitKey(0)
cv.destroyAllWindows()
