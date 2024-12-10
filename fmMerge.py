import json
import os
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('USER')

# Load the filled_map.json from the first location
with open('C:/Users/Andreas/Desktop/pip_code/models/filled_map.json', 'r') as source_file:
    source_data = json.load(source_file)

# Load the filled_map.json from the second location
with open(f'C:/Users/{USER}/AppData/Roaming/.minecraft/resourcepacks/Pokemon 4.0/assets/minecraft/models/item/filled_map.json', 'r') as target_file:
    target_data = json.load(target_file)

# Replace the predicate data in the target data
for override in target_data['overrides']:
    custom_model_data = override['predicate']['custom_model_data']
    for source_predicate in source_data['overrides']:
        if source_predicate['predicate']['custom_model_data'] == custom_model_data:
            override['model'] = source_predicate['model']
            break

# Iterate through the source predicates to add new entries for missing custom_model_data numbers
for source_predicate in source_data['overrides']:
    custom_model_data = source_predicate['predicate']['custom_model_data']
    
    # Check if the custom_model_data exists in the target data
    found = False
    for target_override in target_data['overrides']:
        if target_override['predicate']['custom_model_data'] == custom_model_data:
            found = True
            break
    
    # If not found, add a new entry to the target data
    if not found:
        target_data['overrides'].append(source_predicate)

# Sort the overrides based on custom_model_data
target_data['overrides'] = sorted(target_data['overrides'], key=lambda x: x['predicate']['custom_model_data'])

# Save the modified target data
with open(f'C:/Users/{USER}/AppData/Roaming/.minecraft/resourcepacks/Pokemon 4.0/assets/minecraft/models/item/filled_map.json', 'w') as target_file:
    json.dump(target_data, target_file, indent=1)
