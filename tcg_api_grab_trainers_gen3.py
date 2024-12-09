import re
import copy
import json
import os
from itertools import chain


from villagers4 import sets
from villagers4 import unescape_string




set_list = ["ex1", "ex2", "ex3", "ex4", "ex5", "ex6", "ex7", "ex8", "ex9", "ex10", "ex11", "ex12", "ex13", "ex14", "ex15", "ex16"]

json_dicts = {
    "entry": {"type": "minecraft:item", "name": "minecraft:filled_map", "functions": [{"function": "minecraft:set_nbt", "tag": "tempTag"}], "weight": 1},
    "chest": {"type": "minecraft:chest", "pools": [{"rolls": 1, "entries": []}]}
}


def generate_tag_lines():
    tag_lines = {}
    patterns_list = ['> Item', '> Supporter', '> Pokémon Tool', '> Stadium', '> Technical Machine', "> Rocket's Secret Machine"]
    loot_tablesDirectory = f"C:/Users/Andreas/Desktop/pip_code/loot_tables/"
    if not os.path.exists(loot_tablesDirectory):
        os.makedirs(loot_tablesDirectory)
    for set in set_list:
        tag_lines[set] = {}
        tag_lines[set]["weight"] = sets[set]["weight"]
        for rarity in ["common", "uncommon"]:
            tag_lines[set][rarity] = []
            with open(f"C:/Users/Andreas/Desktop/pip_code/loot_tables/{set}/{rarity}.json", "r") as file:
                data = json.load(file)
            
            for tag_line in data['pools'][0]['entries']:
                tag_string = tag_line['functions'][0]['tag']
                for pattern in patterns_list:
                    trainer_match = re.search(pattern, tag_string)
                    if trainer_match:
                        unescaped_string = unescape_string(tag_string)
                        tag_lines[set][rarity].append(unescaped_string)
                        break
    
    return tag_lines


def adjust_weight(tag_lines):
    tag_lines_length = sum(len(tag_lines[set]["common"]) for set in tag_lines) + sum(len(tag_lines[set]["uncommon"]) for set in tag_lines)
    for set in set_list:
        tag_lines[set]["weight"] = tag_lines[set]["weight"] * 1000 / tag_lines_length
        for tag in chain(tag_lines[set]["common"], tag_lines[set]["uncommon"]):
            entry = copy.deepcopy(json_dicts["entry"])
            entry["functions"][0]["tag"] = tag
            entry["weight"] = round(tag_lines[set]["weight"])
            json_dicts["chest"]["pools"][0]["entries"].append(entry)

    
def write_to_json():
    path = 'C:/Users/Andreas/Desktop/pip_code/loot_tables/trainer_cards_gen3.json'
    with open(path, 'w') as file:
        json.dump(json_dicts["chest"], file, indent=4)


if __name__ == "__main__":
    tag_lines = generate_tag_lines()
    adjust_weight(tag_lines)
    write_to_json()
