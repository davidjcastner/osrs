import time


from settings import LOAD_TIME


def pause(long: bool = False) -> None:
    '''generic pause, allows for changing all pauses at once'''
    time.sleep(LOAD_TIME * 2) if long else time.sleep(LOAD_TIME)
