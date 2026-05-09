import os
import re
import json


def edit_text_in_model_folder(path: str, search: list, replace: list):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            if 'credit' in data:
                del data['credit']
            for layer in data['textures']:
                data['textures'][layer] = data['textures'][layer].lower()
                for i in range(len(search)):
                    data['textures'][layer] = data['textures'][layer].replace(search[i], replace[i])

            # data['display']['fixed'] = {
            #     "rotation": [0, 180, 0],
            #     "translation": [0, 0, 0.75]
            # }

            with open(file_path, 'w') as f:
                data = json.dumps(data, indent=None)
                f.write(data)
            print(f'Edited {file_path}')


def edit_text_in_model_file(file_path: str, search: str, replace: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
    for entry in data['model']['entries']:
        entry['model']['model'] = entry['model']['model'].replace(search, replace)
    with open(file_path, 'w') as f:
        data = json.dumps(data, indent=4)
        f.write(data)
    print(f'Edited {file_path}')


def edit_fallback(path: str, search: str, replace: str):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            if 'model' in data and 'fallback' in data['model']:
                data['model']['fallback']['model'] = data['model']['fallback']['model'].replace(search, replace)
                with open(file_path, 'w') as f:
                    data = json.dumps(data, indent=4)
                    f.write(data)
                print(f'Edited {file}')


def lowercase_files(path: str):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.rename(file_path, file_path.lower())
            print(f'Lowercased {file_path}')


def edit_filled_map():
    path = 'C:/Users/Andreas/AppData/Roaming/.minecraft/resourcepacks/Pokemon 5.0/assets/minecraft/items/filled_map.json'
    with open(path, 'r') as f:
        data = json.load(f)
    entry_numbers = {
        'gen1': 32000,
        'gen2': 32682,
        'gen3': 34001
    }
    for entry in data['model']['entries']:
        threshold = entry['threshold']
        if threshold >= entry_numbers['gen3']:
            entry['model']['model'] = entry['model']['model'].replace('minecraft:sets', 'pokemon:card/gen3')
            print(f'Edited {entry["model"]["model"]}')
        elif threshold >= entry_numbers['gen2']:
            entry['model']['model'] = entry['model']['model'].replace('minecraft:sets', 'pokemon:card/gen2')
            print(f'Edited {entry["model"]["model"]}')
        elif threshold >= entry_numbers['gen1']:
            entry['model']['model'] = entry['model']['model'].replace('minecraft:sets', 'pokemon:card/gen1')
            print(f'Edited {entry["model"]["model"]}')
    with open(path, 'w') as f:
        data = json.dumps(data, indent=4)
        f.write(data)
    print(f'Edited {path}')


def assign_model(path: str, json_dict: dict):
    files = []
    for entry in json_dict['model']['entries']:
        model = entry['model']['model']
        search = re.search(r'minecraft:item/(.*)', model)
        if search:
            files.append(search.group(1))
            print(f'Found {search.group(1)}')
    #for file in os.listdir(path):
    #    file_path = os.path.join(path, file)
    #    if os.path.isfile(file_path):


if '__main__' == __name__:
    path = 'C:/Users/Andreas/AppData/Roaming/.minecraft/resourcepacks/Pokemon 5.0/assets/vote/models'
    search = [
        'item/',
    ]
    replace = [
        'vote:item/',
    ]
    edit_text_in_model_folder(path, search, replace)
