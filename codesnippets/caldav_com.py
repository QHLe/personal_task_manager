import json
from unicodedata import category
from caldav import DAVClient, objects
import vobject

# Load user credentials from a JSON file
with open('config.json') as json_data_file:
    data = json.load(json_data_file)
# Connect to the CalDAV server
client = DAVClient(url=data["caldav_url"], username=data["username"], password=data["password"], ssl_verify_cert=False)

# Get the principal
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
            vtodos.append(vtodo_dict)
    
import pandas as pd

df = pd.DataFrame(vtodos)

print(df)

print(df.columns)

# Create a new task
new_task = task_list.add_todo(summary='My new created Task', description='This is a new task', priority=1, dtstart='2020-08-07T15:30:00Z', due='2020-08-07T16:30:00Z', status=objects.VTODO_STATUS_NEEDS_ACTION)
# Save the task
new_task.save()