from pynput.keyboard import Controller, Key

keyboard = Controller()

def play_pause():
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)

def volume_up(steps):
    for i in range(steps):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)

def volume_down(steps):
    for i in range(steps):
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        
def next_track():
    keyboard.press(Key.media_next)
    keyboard.release(Key.media_next)

def previous_track():
    keyboard.press(Key.media_previous)
    keyboard.release(Key.media_previous)


