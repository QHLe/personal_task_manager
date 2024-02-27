import json
import os

# Specify the file name
file_name = "tasks.json"

# Check if file exists
if os.path.isfile(file_name):
    print(f"The file '{file_name}' exists.")
    
    # Load the JSON file
    with open(file_name, 'r') as file:
        tasks = json.load(file)
        
    # Print the tasks
    print(tasks)
else:
    print(f"The file '{file_name}' does not exist.")
    task = []
    
    
# Create some tasks
tasks.append({
    "id": 1,
    "name": "Task 1",
    "description": "This is task 1",
    "status": "complete"
})
tasks.append({
    "id": 2,
    "name": "Task 2",
    "description": "This is task 2",
    "status": "incomplete"
})

# Convert the list of tasks to JSON
json_tasks = json.dumps(tasks, indent=4)

# Write the JSON tasks to a file
with open(file_name, 'w') as file:
    file.write(json_tasks)

print("Tasks saved to tasks.json")
