import mediaControlButtons as mc 
import cv2 as cv
import time
import numpy as np
import mediapipe as mp


def dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

def midpoint(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

def scaleDistance(lm):
    wrist = lm[0]
    middle_finger_tip = lm[9]
    return dist(wrist, middle_finger_tip)

def pinchDist(lm):
    return dist(lm[4], lm[8])/scaleDistance(lm)

def drawPinch(img, lm):
    if lm[4] is None or lm[8] is None or lm[0] is None or lm[9] is None:
        return

    thumb = lm[4]
    index = lm[8]

    cv.line(img, thumb, index, (255, 0, 255), 3)
    cv.circle(img, thumb, 10, (255, 0, 255), cv.FILLED)
    cv.circle(img, index, 10, (255, 0, 255), cv.FILLED)

    midx, midy = midpoint(thumb, index)
    cv.putText(img, f'Pinch: {pinchDist(lm):.2f}', (int(midx), int(midy)), cv.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)