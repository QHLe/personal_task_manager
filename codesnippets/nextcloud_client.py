from caldav import DAVClient
from caldav.elements import dav, cdav

# Replace with your actual credentials
nextcloud_url = 'http://example.com/nextcloud'
username = 'your_username'
password = 'your_password'

# Connect to Nextcloud CalDAV
client = DAVClient(nextcloud_url, username=username, password=password)
principal = client.principal()

# Get the list of calendars
calendars = principal.calendars()

# Iterate through the calendars and retrieve tasks
for calendar in calendars:
    # Check if the calendar is a task list
    if calendar.get_supported_component_set().is_supported('VTODO'):
        # Retrieve all tasks
        tasks = calendar.todos()
        for task in tasks:
            print(task.vobject_instance.summary.value)
