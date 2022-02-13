from driver import goto_url
from driver import highlight_element
# from driver import scroll_to_element
from driver import setup_driver
from settings import OSRS_TASK_URL
from settings import OSRS_USERNAME
from type_hints import Driver
from type_hints import WebElement
from utility import pause


def initialize_wiki() -> Driver:
    '''initializes the wiki driver'''
    driver = setup_driver()
    goto_url(driver, OSRS_TASK_URL)
    pause()
    # load user tasks
    load_user_tasks(driver)
    return driver


def load_user_tasks(driver: Driver) -> None:
    '''enters the users' name into the search bar to load their tasks'''
    fieldset_element = driver.find_element_by_id('rs-qc-form')
    highlight_element(driver, fieldset_element)
    input_element = fieldset_element.find_element_by_tag_name('input')
    submit_button = fieldset_element.find_element_by_tag_name('button')
    input_element.send_keys(OSRS_USERNAME)
    submit_button.click()
    pause()
    # wait for success image to appear
    is_success = False
    for attempt in range(5):
        print(f'loading user tasks attempt {attempt}...')
        success_image = driver.find_element_by_class_name('wikisync-success')
        if success_image:
            highlight_element(driver, success_image)
            is_success = True
            break
        pause()
    if not is_success:
        raise Exception('Failed to load user tasks')


def find_all_task_tables(driver: Driver) -> list[dict[str, str]]:
    '''finds all the task tables'''
    # all tables have an id that starts with 'mw-customcollapsible-'
    # the rest of the id is the type of task
    # e.g. Agility, Cooking, Fishing, Woodcutting
    # all tables have the class of 'mw-collapsible'
    tables = driver.find_elements_by_class_name('mw-collapsible')
    table_ids = [table.get_attribute('id') for table in tables]
    # filter out the tables that don't start with 'mw-customcollapsible-'
    table_ids = [table_id for table_id in table_ids if table_id.startswith('mw-customcollapsible-')]
    table_info = [{'element_id': table_id, 'task_type': table_id.split('-')[2]} for table_id in table_ids]
    return table_info


def get_tasks_from_table(driver: Driver, container_id: str) -> list[dict[str, str]]:
    '''gets tasks from the table'''
    tasks = []
    table_element = driver.find_element_by_id(container_id)
    highlight_element(driver, table_element)
    table_rows = table_element.find_elements_by_tag_name('tr')

    # change the task difficulty when a row
    # with a class of 'sorttop' is found
    # the difficulty is the text inside the child th element
    current_task_difficulty = ''
    for row_index, row_element in enumerate(table_rows):
        highlight_element(driver, row_element)
        # first row is the header column names and can be ignored
        if row_index == 0:
            continue
        row_class = row_element.get_attribute('class')
        # check for task difficulty row
        if 'sorttop' in row_class:
            current_task_difficulty = row_element.find_element_by_tag_name('th').text
            continue
        # get the attributes of task
        task_record = {}
        task_record['difficulty'] = current_task_difficulty
        task_record['is_complete'] = 'wikisync-complete' in row_class
        details = row_element.find_elements_by_tag_name('td')
        # details = [detail.get_attribute('innerHTML') for detail in details]
        details = [detail.text for detail in details]
        if len(details) == 4:
            task_record['name'], task_record['description'], task_record['requirements'], task_record['completion_percent'] = details
            tasks.append(task_record)
    return tasks


def find_all_tasks(driver: Driver) -> list[dict[str, str]]:
    '''finds all the tasks'''
    print('finding all tasks...')
    tasks = []
    tables = find_all_task_tables(driver)
    for table in tables:
        element_id, task_type = table['element_id'], table['task_type']
        print(f'collecting tasks for {task_type}...')
        subtasks = get_tasks_from_table(driver, element_id)
        # add the task type to the task
        for task in subtasks:
            task['task_type'] = task_type
            tasks.append(task)
    print(f'found {len(tasks)} tasks')
    return tasks


def get_all_tasks() -> list[dict[str, str]]:
    '''wraps all driver functionality around finding all tasks'''
    driver = initialize_wiki()
    tasks = find_all_tasks(driver)
    driver.quit()
    return tasks


if __name__ == '__main__':
    # testing driver functionality
    tasks = get_all_tasks()
    import json
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=4)
