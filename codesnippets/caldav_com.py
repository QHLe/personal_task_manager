import json
from unicodedata import category
from caldav import DAVClient, objects

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

for task in tasks:
    vtodo = task.instance.vtodo
    uid = getattr(vtodo, 'uid', None)
    summary = getattr(vtodo, 'summary', None)
    status = getattr(vtodo, 'status', None)
    due = getattr(vtodo, 'due', None)
    description = getattr(vtodo, 'description', None)
    start = getattr(vtodo, 'dtstart', None)
    prio = getattr(vtodo, 'priority', None)
    categories = getattr(vtodo, 'categories', None)
    location = getattr(vtodo, 'location', None)
    organizer = getattr(vtodo, 'organizer', None)
    attendee = getattr(vtodo, 'attendee', None)
    print("\n")
    if uid is not None:
        print(f"UID: {uid.value}")
    if summary is not None:
        print(f"Summary: {summary.value}")
    if status is not None:
        print(f"Status: {status.value}")
    if due is not None:
        print(f"Due: {due.value}")
    if description is not None:
        print(f"Description: {description.value}")
    if prio is not None:
        print(f"Prio: {prio.value}")
    if location is not None:
        print(f"location: {location.value}")
    if start is not None:
        print(f"Start date: {start.value}")
    if categories is not None:
        print(f"Categories: {categories.value}")
    if attendee is not None:
        print(f"attendee: {attendee.value}")
    if organizer is not None:
        print(f"organizer: {organizer.value}")
    
# Create a new task
new_task = task_list.add_todo(summary='My new created Task', description='This is a new task', priority=1)
# Save the task
new_task.save()