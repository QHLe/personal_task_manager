import json
from caldav import DAVClient, Calendar

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
