## Note that I'mm running this in python 3.12, may not work in more recent versions since some mediapipe legacy solutions support was stopped as of March 1st, 2023

## adjust the detectionCon and trackCon parameters to change sensitivity of hand detection and tracking if needed

## 2 pinches for play/pause, pinch and hold for volume adjustment, and 3 pinches for next/previous track

import cv2 as cv
import mediapipe as mp
import time

import usefulFunctions as f
import PinchEngine as p


class HandDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5): # default parameters, detection confidence and tracking confidence can be adjusted
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands, min_detection_confidence=self.detectionCon, min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw = True):

        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self, img, handNo = 0, draw = True):

        lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((id, cx, cy))
                    if draw:
                        self.mpDraw.draw_landmarks(img, myHand, self.mpHands.HAND_CONNECTIONS)
        return lmList
    
    def findHandsData(self, img, draw = True):
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape

        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                lmList = []

                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((id, cx, cy))

                myHand["lmList"] = lmList
                myHand["type"] = handType.classification[0].label

                allHands.append(myHand)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return allHands

def toXYList(lmList): # convert lmList from (id, x, y) tuples to list of (x, y) indexed by id, makes everything a bit easier to work with
    xyList = [None] * 21
    for (id, x, y) in lmList:
        xyList[id] = (x, y)
    return xyList

def main():
    right = p.PinchEngine()
    left = p.PinchEngine()

    t0 = 0
    t1 = 0
    cap = cv.VideoCapture(0)
    detector = HandDetector()


    while True:
        success, img = cap.read()

        hands = detector.findHandsData(img, draw=True)
        for hand in hands:
            engine = right if hand["type"] == "Right" else left

            swappedHand = "Right" if hand["type"] == "Left" else "Left" ## camera is mirrored so swap hand labels, adjust if not mirrored

            pinchStrength = f.pinchDist(toXYList(hand["lmList"]))

            engine.update(pinchStrength, swappedHand)

            lmlist = toXYList(hand["lmList"])
            label = "Right" if hand["type"] == "Left" else "Left" # swap for mirrored camera, adjust if not mirrored

            cv.putText(img, label, (lmlist[0]), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            f.drawPinch(img, lmlist)

        # Calculate FPS and display
        ct = time.time()
        fps = 1/(ct - t1) if (ct - t1) > 0 else 0
        t1 = ct
        cv.putText(img, f'FPS: {int(fps)}', (10, 70), cv.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        # q to quit
        cv.imshow("Image", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()