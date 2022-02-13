# this script does runecrafting at the zmi altar in shattered leagues
# by teleporting to and from the crafting guild and making use of last recall

# type hints and imports
from image import Img
from driver import attempt
from driver import click_center
from driver import hold_for_interupt
from driver import is_screen_match
from driver import pause
from driver import play_notification
from driver import wait_for
from type_hints import ScreenBox
# from type_hints import ScreenLocation

# setup for consistant running
# turn on hide entities plugin for better image recognition
# click on the compass to look north and zoom camera all the way out
# then start by opening the bank chest in the crafting guild
# ensure there are bank fillers to keep the crafting cape and recall orb when banking
# make sure recall orb is in inventory slot 1
# make sure crafting cape is in inventory slot 2

# update the screen locations of the crafting guild bank and the altar
# it will change depending on the orientation of the camera

# locations
LOC_BANK_CHEST: ScreenBox = (1129, 764, 1204, 834)
LOC_CLOSE_BANK: ScreenBox = (973, 37, 999, 63)
LOC_CRAFTING_CAPE: ScreenBox = (1455, 630, 1482, 663)
LOC_DEPOSIT_ALL: ScreenBox = (901, 750, 949, 796)
LOC_ESSENCE: ScreenBox = (749, 197, 782, 222)
LOC_RECALL_ORB: ScreenBox = (1393, 630, 1428, 663)
LOC_ZMI_ALTAR: ScreenBox = (670, 485, 784, 558)

# C:\Users\david\git\osrs\screenshots\bots\leagues_runecrafting

# image names
SOURCE_IMG_NAME_CRAFT_GUI: str = './screenshots/bots/leagues_runecrafting/source_crafting_guild.png'
SOURCE_IMG_NAME_OPEN_BANK: str = './screenshots/bots/leagues_runecrafting/source_open_bank.png'
SOURCE_IMG_NAME_ZMI_ALTAR: str = './screenshots/bots/leagues_runecrafting/source_zmi_altar.png'

# images for comparison
IMG_NAME_BANK_CHEST: str = './screenshots/bots/leagues_runecrafting/cropped_bank_chest.png'
IMG_NAME_CLOSE_BANK: str = './screenshots/bots/leagues_runecrafting/cropped_close_bank.png'
IMG_NAME_CRAFTING_CAPE: str = './screenshots/bots/leagues_runecrafting/cropped_crafting_cape.png'
IMG_NAME_DEPOSIT_ALL: str = './screenshots/bots/leagues_runecrafting/cropped_deposit_all.png'
IMG_NAME_ESSENCE: str = './screenshots/bots/leagues_runecrafting/cropped_essence.png'
IMG_NAME_RECALL_ORB: str = './screenshots/bots/leagues_runecrafting/cropped_recall_orb.png'
IMG_NAME_ZMI_ALTAR: str = './screenshots/bots/leagues_runecrafting/cropped_zmi_altar.png'


def load_image(source: str, box: ScreenBox, output: str) -> Img:
    '''loads an image from the source and crops it to the box'''
    img = Img(source)
    img.crop(box)
    img.fuzzify()
    img.save_as(output)
    return img


IMG_BANK_CHEST: Img = load_image(SOURCE_IMG_NAME_CRAFT_GUI, LOC_BANK_CHEST, IMG_NAME_BANK_CHEST)
IMG_CLOSE_BANK: Img = load_image(SOURCE_IMG_NAME_OPEN_BANK, LOC_CLOSE_BANK, IMG_NAME_CLOSE_BANK)
IMG_CRAFTING_CAPE: Img = load_image(SOURCE_IMG_NAME_CRAFT_GUI, LOC_CRAFTING_CAPE, IMG_NAME_CRAFTING_CAPE)
IMG_DEPOSIT_ALL: Img = load_image(SOURCE_IMG_NAME_OPEN_BANK, LOC_DEPOSIT_ALL, IMG_NAME_DEPOSIT_ALL)
IMG_ESSENCE: Img = load_image(SOURCE_IMG_NAME_OPEN_BANK, LOC_ESSENCE, IMG_NAME_ESSENCE)
IMG_RECALL_ORB: Img = load_image(SOURCE_IMG_NAME_CRAFT_GUI, LOC_RECALL_ORB, IMG_NAME_RECALL_ORB)
IMG_ZMI_ALTAR: Img = load_image(SOURCE_IMG_NAME_ZMI_ALTAR, LOC_ZMI_ALTAR, IMG_NAME_ZMI_ALTAR)


def action_click_image(box: ScreenBox, compare_image: Img):
    '''takes the generic action of clicking in the center of a screen box if an image is found'''
    assert is_screen_match(box, compare_image), 'Image not found'
    click_center(box)
    pause(0.1)


@attempt()
def deposit_items():
    '''attempts to click the deposit all button by clicking deposit all button'''
    action_click_image(LOC_DEPOSIT_ALL, IMG_DEPOSIT_ALL)


@attempt()
def withdraw_essence():
    '''withdraws essence from the bank by clicking on essence'''
    action_click_image(LOC_ESSENCE, IMG_ESSENCE)


@attempt()
def close_bank():
    '''closes the bank'''
    action_click_image(LOC_CLOSE_BANK, IMG_CLOSE_BANK)


def wait_for_bank_close():
    '''waits for the bank to close'''
    def is_bank_closed(): return not is_screen_match(LOC_CLOSE_BANK, IMG_CLOSE_BANK)
    is_closed = wait_for(is_bank_closed)
    assert is_closed, 'Bank was not closed'


@attempt()
def teleport_to_altar():
    '''teleports to the zmi altar by clicking on the recall orb'''
    action_click_image(LOC_RECALL_ORB, IMG_RECALL_ORB)


def wait_for_crafting_runes():
    '''waits for the altar to be ready, then adds a short delay'''
    def is_at_zmi_altar(): return not is_screen_match(LOC_ZMI_ALTAR, IMG_ZMI_ALTAR)
    is_found = wait_for(is_at_zmi_altar)
    assert is_found, 'Altar was not found'
    pause(0.5)


@attempt()
def craft_runes():
    '''crafts runes by clicking the altar'''
    action_click_image(LOC_ZMI_ALTAR, IMG_ZMI_ALTAR)


@attempt()
def teleport_to_crafting_guild():
    '''teleports to the crafting guild by clicking the crafting cape'''
    action_click_image(LOC_CRAFTING_CAPE, IMG_CRAFTING_CAPE)


def wait_for_open_bank():
    '''waits for the bank to be ready, then adds a short delay'''
    def is_at_crafting_guild(): return not is_screen_match(LOC_BANK_CHEST, IMG_BANK_CHEST)
    is_found = wait_for(is_at_crafting_guild)
    assert is_found, 'Bank was not found'
    pause(1.0)


@attempt()
def open_bank():
    '''opens the bank by clicking on bank chest'''
    action_click_image(LOC_BANK_CHEST, IMG_BANK_CHEST)


def main(max_iterations: int = 200):
    '''main function'''
    iteration = 0
    while iteration < max_iterations:
        print('crafting runes - iteration: ' + str(iteration))
        print('depositing items...')
        deposit_items()
        print('withdrawing essence...')
        withdraw_essence()
        print('closing bank...')
        close_bank()
        wait_for_bank_close()
        print('teleporting to altar...')
        teleport_to_altar()
        pause(2.0)  # teleport time
        wait_for_crafting_runes()
        print('crafting runes...')
        craft_runes()
        pause(2.0)  # crafting animation
        print('teleporting to crafting guild...')
        teleport_to_crafting_guild()
        pause(1.5)  # teleport time
        wait_for_open_bank()
        print('opening bank...')
        open_bank()
        hold_for_interupt()
        iteration += 1


if __name__ == '__main__':
    # start_delay = 10
    # while start_delay > 0:
    #     print('starting in ' + str(start_delay) + '...')
    #     pause(1.0)
    #     start_delay -= 1
    try:
        main()
    except Exception as e:
        play_notification()
        raise e
