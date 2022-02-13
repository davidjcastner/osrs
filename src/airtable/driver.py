from selenium import webdriver


from settings import CHROMEDRIVER_PATH
from type_hints import Driver
from type_hints import WebElement
from utility import pause


def setup_driver() -> Driver:
    '''initializes the chrome driver'''
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
    driver.maximize_window()
    return driver


def goto_url(driver: Driver, url: str) -> None:
    '''goes to a url'''
    driver.get(url)
    pause(long=True)


# not working yet
# def scroll_to_element(driver: Driver, element: WebElement) -> None:
#     '''scrolls to an element'''
#     driver.execute_script("arguments[0].scrollIntoView();", element)


def highlight_element(driver: Driver, element: WebElement) -> None:
    '''highlights an element'''
    driver.execute_script("arguments[0].style.outline='3px solid orange'", element)
