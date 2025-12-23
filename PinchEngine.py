import time
import mediaControlButtons as mc

class PinchEngine: # adjust thresholds and timings as needed based on hand tracking performance and personal preference
    def __init__(self, downThreshold=0.2, upThreshold=0.4, tapWindow=0.8, holdDelay=0.5, volumeStep=2, actionCooldown=0.3, volumeRepeat=0.12):
        
        self.downThreshold = downThreshold
        self.upThreshold = upThreshold
        self.tapWindow = tapWindow
        self.holdDelay = holdDelay
        self.volumeStep = volumeStep
        self.actionCooldown = actionCooldown
        self.volumeRepeat = volumeRepeat

        self.isDown = False
        self.timeDown = None

        self.tapCount = 0
        self.firstTapTime = None

        self.lastActionTime = 0.0
        self.timeVolumeAction = 0.0

        self.pendingDouble = False
        self.pendingDoubleTime = 0.0
        self.doubleGrace = 0.3

        self.holding = False

    def update(self, pinchStrength, handLabel):
        now = time.time()
        event = None

        if self.pendingDouble and (now - self.pendingDoubleTime) > self.doubleGrace:
            if now - self.lastActionTime >= self.actionCooldown:
                mc.play_pause()
                event = "play_pause"
                self.lastActionTime = now

            self.pendingDouble = False
            self.tapCount = 0
            self.firstTapTime = None

        wentUp = False
        wentDown = False

        if (not self.isDown) and pinchStrength < self.downThreshold:
            self.isDown = True
            self.timeDown = now
            self.holding = False
            wentDown = True
            event = "down"

        elif self.isDown and pinchStrength > self.upThreshold:
            self.isDown = False
            wentUp = True
            event = "up"

        if self.isDown and self.timeDown is not None:
            heldTime = now - self.timeDown
            if heldTime >= self.holdDelay:
                self.holding = True

            if self.holding:
                if (now - self.timeVolumeAction) >= self.volumeRepeat:
                    self.timeVolumeAction = now
                    if handLabel == "Right":
                        mc.volume_up(self.volumeStep)
                        event = "volume_up"
                    elif handLabel == "Left":
                        mc.volume_down(self.volumeStep)
                        event = "volume_down"
                    else:
                        event = "volume_hold_unknown_hand"
                return event

        if wentUp and not self.holding:
            if self.firstTapTime is None or (now - self.firstTapTime) > self.tapWindow:
                self.tapCount = 0
                self.firstTapTime = now

            self.tapCount += 1

            if (now - self.lastActionTime) < self.actionCooldown:
                return event

            if self.tapCount == 3:
                if handLabel == "Right":
                    mc.next_track()
                    event = "next_track"
                elif handLabel == "Left":
                    mc.previous_track()
                    event = "previous_track"
                else:
                    event = "unknown_hand_3_taps"
                self.lastActionTime = now
                self.tapCount = 0
                self.firstTapTime = None
            elif self.tapCount == 2:
                self.pendingDouble = True
                self.pendingDoubleTime = now
                event = "pending_double_tap"

        if wentUp:
            self.timeDown = None
            self.holding = False

        return event
