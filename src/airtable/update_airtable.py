from flask import request
from numpy import full
import requests
import time


from wiki_driver import get_all_tasks
from settings import AIRTABLE_API_KEY
from settings import AIRTABLE_DATABASE_KEY


TABLE_DIFFICULTY = 'Task%20Difficulties'
TABLE_TASKS = 'League%20Tasks'


def debug_json(data) -> None:
    '''prints the json of the data'''
    import json
    data_string = json.dumps(data, indent=4, sort_keys=True)
    print(data_string[:100])
    with open('debug.json', 'w') as f:
        f.write(data_string)


def airtable_url(table_name: str) -> str:
    '''returns the url for the airtable'''
    return f'https://api.airtable.com/v0/{AIRTABLE_DATABASE_KEY}/{table_name}'


def airtable_headers() -> dict[str, str]:
    '''returns the headers for the airtable'''
    return {'Authorization': f'Bearer {AIRTABLE_API_KEY}'}


def get_current_records(table_name: str, max_requests: int = 0) -> list[dict[str, str]]:
    '''returns all records from the airtable'''
    base_url = airtable_url(table_name) + '?view=Default'
    offset = ''
    records = []
    request_count = 0
    while max_requests == 0 or request_count < max_requests:
        print(f'making request {request_count + 1} from {table_name}...')
        full_url = base_url if offset == '' else base_url + '&offset=' + offset
        response = requests.get(full_url, headers=airtable_headers())
        # check for 200 status code
        if response.status_code != 200:
            raise Exception(f'Code: {response.status_code}, Error: {response.content}')
        data = response.json()
        records += data['records']
        # check if there are more records
        if 'offset' in data:
            offset = data['offset']
        else:
            break
        request_count += 1
        # wait 1/4 for rate limit
        time.sleep(0.25)
    return records


def update_records(records: list[dict[str, str]], create: bool = False) -> None:
    '''updates the records in the database'''
    # to update a record use the patch method
    # to create a record use the post method
    request_method = requests.post if create else requests.patch
    # split the records into chunks of 10
    # so that the airtable doesn't get overloaded
    chunk_size = 10
    total_chunks = (len(records) - 1) // chunk_size + 1
    chunks = [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
    # send each chunk with a rate limit of 4 per second
    for chunk_id, chunk_data in enumerate(chunks):
        print(f'updating chunk {chunk_id + 1} of {total_chunks}...')
        # send a patch
        response = request_method(airtable_url(TABLE_TASKS), json={'records': chunk_data}, headers=airtable_headers())
        # check for 200 status code
        if response.status_code != 200:
            print({'records': chunk_data})
            raise Exception(f'Code: {response.status_code}, Error: {response.content}')
        # rate limit is 5 per second, attempt 4 per second to avoid being blocked
        time.sleep(0.25)  # 1/4 of second for delay


def format_record(task: dict[str, str], difficulty_lookup: dict[str, str], use_id: bool = False, id: str = '') -> dict[str, str]:
    '''formats a task record'''
    record = {
        'fields': {
            'Task Name': task['name'],
            'Task Difficulty': [difficulty_lookup[task['difficulty']]],
            'Completion Status': 'Completed' if task['is_complete'] else 'Incomplete',
            'Description': task['description'],
            'Requirements': task['requirements'],
            'Completion Amount': float(task['completion_percent'].strip('<%')) / 100,
            'Type': task['task_type']
        }
    }
    if use_id:
        record['id'] = id
    return record


def get_task_ids_by_name() -> dict[str, str]:
    '''returns a dictionary of task names and their ids'''
    records = get_current_records(TABLE_TASKS)
    return {record['fields']['Task Name']: record['id'] for record in records}


def get_difficulty_ids_by_name() -> dict[str, str]:
    '''returns a dictionary of difficulty names and their ids'''
    records = get_current_records(TABLE_DIFFICULTY)
    return {record['fields']['Difficulty Id']: record['id'] for record in records}


def update_airtable() -> None:
    '''updates the airtable with all tasks'''
    task_ids = get_task_ids_by_name()
    assert len(task_ids) == 1260, 'did not find all tasks'
    difficulty_ids = get_difficulty_ids_by_name()
    assert len(difficulty_ids) == 6, 'did not find all difficulties'
    tasks = get_all_tasks()
    # match the tasks to the records
    # if the task is already in the records, update it
    # otherwise, create a new record
    records_to_create = []
    records_to_update = []
    for task in tasks:
        if task['name'] in task_ids:
            records_to_update.append(format_record(task, difficulty_lookup=difficulty_ids, use_id=True, id=task_ids[task['name']]))
        else:
            records_to_create.append(format_record(task, difficulty_lookup=difficulty_ids))
    # create and update the records
    update_records(records_to_create, create=True)
    update_records(records_to_update)


if __name__ == '__main__':
    update_airtable()
