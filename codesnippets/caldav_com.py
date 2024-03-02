#%%
import json
from unicodedata import category
from caldav import DAVClient, objects
import vobject

# Load user credentials from a JSON file
with open('config.json') as json_data_file:
    data = json.load(json_data_file)

# Connect to the CalDAV server
client = DAVClient(url=data["caldav_url"], username=data["username"], password=data["password"], ssl_verify_cert=False)
print(type(client))
# Get the principal

#%%
principal = client.principal()

# Get the calendars
calendars = principal.calendars()

for calendar in calendars: 
    if calendar.name == 'Todo':
        task_list = calendar

tasks = task_list.todos()

# Print the names of the calendars
print(task_list.name)

vtodos = []
for task in tasks:
    cal = vobject.readOne(task.data)
    for component in cal.components():
        if component.name == 'VTODO':
            vtodo_dict = {}
            for key in component.contents:
                vtodo_dict[key] = component.contents[key][0].value
                print(key)
            vtodos.append(vtodo_dict)
    
import pandas as pd

df = pd.DataFrame(vtodos)

print(df)

print(df.columns)

from datetime import datetime

start = datetime.strptime('2020-08-07T15:30:00Z', '%Y-%m-%dT%H:%M:%SZ')
due_date = datetime.strptime('2020-08-07T16:30:00Z', '%Y-%m-%dT%H:%M:%SZ')
# Create a new task
# new_task = task_list.add_todo(summary='My new created Task', description='This is a new task', priority=1, dtstart=start, due=due_date, status='NEEDS-ACTION')
# Save the task
# new_task.save()

# Assuming you have a client and a task_list already
task = tasks[8]
cal = vobject.readOne(task.data)
for component in cal.components():
    if component.name == 'VTODO':
        for key in component.contents:
            print(key)
            print(component.contents[key][0].value)

# Modify the task
task.instance.vtodo.summary.value = 'New Task Name1'
# Check if 'priority' attribute exists
if hasattr(task.instance.vtodo, 'priority'):
    task.instance.vtodo.priority.value = '2'
else:
    # Add 'priority' attribute
    task.instance.vtodo.add('priority').value = '2'

# Check if 'description' attribute exists
if hasattr(task.instance.vtodo, 'description'):
    task.instance.vtodo.description.value = 'New Task Description1'
else:
    # Add 'description' attribute
    task.instance.vtodo.add('description').value = 'New Task Description1'


# Save the changes
print('save')
# task.save()