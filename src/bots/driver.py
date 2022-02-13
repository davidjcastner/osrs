# an interface for interacting with the game client
# decouples the script from any library for automation, such as clicking
# or taking screenshots

from typing import Callable
import pyautogui
import time
import winsound

from image import Img
from type_hints import RGBA
from type_hints import ScreenBox
from type_hints import ScreenLocation


NOTIFICATION_WAV = './assets/mixkit-click-error-1110.wav'


def play_notification(iterations: int = 1):
    '''
    Plays a notification sound.
    '''
    for count in range(iterations):
        winsound.PlaySound(NOTIFICATION_WAV, winsound.SND_FILENAME)
        if count < iterations - 1:
            time.sleep(0.5)


def pause(amount: float) -> None:
    '''
    Pauses the script for a specified amount of time.
    '''
    time.sleep(amount)


def find_center(box: ScreenBox) -> ScreenLocation:
    '''
    Returns the center of a box on the screen.
    '''
    x1, y1, x2, y2 = box
    return (x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2)


def click_location(location=ScreenLocation) -> None:
    '''
    Clicks a location on the screen.
    '''
    x, y = location
    pyautogui.moveTo(x, y)
    time.sleep(0.01)
    pyautogui.click(x, y)


def click_center(box: ScreenBox) -> None:
    '''
    Clicks the center of a box on the screen.
    '''
    location = find_center(box)
    print(f'clicking location, {location}')
    click_location(location)


def take_screenshot() -> Img:
    '''
    Takes a screenshot of the game client and saves it to the specified location.
    '''
    temp_file = './temp/screenshot.png'
    pyautogui.screenshot(temp_file)
    return Img(temp_file)


def is_same_image(image: Img, box: ScreenBox, compare_image: Img, threshold: float = 0.9) -> bool:
    '''
    Compares an image to another image by comparing counts of pixel colors.

    the comparison should be same size as the box
    the comparison image should already be fuzzy

    image: screenshot of the game client
    box: coordinates in the screenshot to compare
    compare_image: image to compare to
    threshold: the minimum percentage of pixels that must match
    '''
    cropped_section = image.crop(box).fuzzify()
    cropped_section.save_as('./temp/section.png')
    colors = cropped_section.get_colors()
    compare_colors = compare_image.get_colors()
    matches = 0
    total = 0
    for color, amount in compare_colors.items():
        total += amount
        matches += min(colors.get(color, 0), amount)
    return matches / total > threshold


def is_screen_match(box: ScreenBox, compare_image: str) -> bool:
    '''
    Compares the current screen to a specified image.
    '''
    return is_same_image(take_screenshot(), box, compare_image)


def wait_for(is_ready: Callable[[], bool], check_delay: float = 0.1, max_wait_time: float = 5.0) -> bool:
    '''
    Waits for a specified condition to be true. Returns True if the condition is met before the max wait time is reached.

    check_delay: the amount of time to wait between checks in seconds
    max_wait_time: the maximum amount of time to wait in seconds
    '''
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if is_ready():
            return True
        time.sleep(check_delay)
    return False


def hold_for_interupt(max_wait_time: float = 3.0) -> None:
    '''
    Waits for any of the following to be pressed: escape, space, enter. If any of these are pressed, the script will be interrupted.

    max_wait_time: the maximum amount of time to wait in seconds
    '''
    print('holding for interupt')
    time.sleep(max_wait_time)
    print('no key was pressed, continuing script')


def attempt(max_attempt_time: float = 4.0, attempt_delay: float = 0.25) -> bool:
    '''
    A decorator that attempts to perform an action. If the action fails, it will wait for a specified amount of time and then attempt again.

    max_attempt_time: the maximum amount of time to wait for the action to complete
    attempt_delay: the amount of time to wait between attempts
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt_count = 1
            start_time = time.time()
            while time.time() - start_time < max_attempt_time:
                if attempt_count > 1:
                    print(f'attempt number {attempt_count}...')
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f'attempt failed: {e}')
                    time.sleep(attempt_delay)
                attempt_count += 1
            raise Exception('attempts exceeded')
        return wrapper
    return decorator


if __name__ == '__main__':
    pass
