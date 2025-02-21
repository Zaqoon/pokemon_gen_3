import pokemontcgsdk
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Rarity
from pokemontcgsdk import RestClient

import re
import copy
import json
import os
import shutil

from poke_data import CardData


RestClient.configure('3f9fba22-cc72-487d-a8fc-e1e5ba5744fc')


targetSetList = ["ex1", "ex2", "ex3", "np", "ex4", "ex5", "ex6", "ex7", "ex8", "ex9", "ex10", "ex11", "ex12", "ex13", "ex14", "ex15", "ex16"]
#targetSetList = ["ex1", "ex2", "ex3", "ex4"]

allPokeData = {
    "ex1": [],  "ex2": [],  "ex3": [],  "ex4": [],  "ex5": [],
    "ex6": [],  "ex7": [],  "ex8": [],  "ex9": [], "ex10": [],
    "ex11": [], "ex12": [], "ex13": [], "ex14": [], "ex15": [],
    "ex16": [], "np": []
}

def sortItem(card):
    match = re.match(r'^([A-Za-z]*)(\d+)(.*)', card.number)
    if match:
        prefix = match.group(1)  # Capture any letters or characters before the numeric part
        numeric_part = int(match.group(2))  # Capture the numeric part as an integer
        suffix = match.group(3)  # Capture any characters after the numeric part
        if prefix:
            return (0, prefix, numeric_part, suffix)  # Sort by prefix, then numeric part, and finally suffix
        else:
            return (1, '', numeric_part, suffix)  # Sort non-prefix cards after prefix cards
    else:
        return (0, '', 0, '')  # Default value if no match is found
    

def populatePokeData(target):
    for set in target:
        print(f"Populating cards from \"{set}\"")
        cards = Card.where(q=f'set.id:{set}')
        sorted_cards = sorted(cards, key=sortItem)
        for card in sorted_cards:
            currPokeData = PokeData(card)
            currPokeData.generateLoreList()
            currPokeData.generateNameLoreDict()
            allPokeData[set].append(currPokeData)


def format_name(name, card_name_list):
    name = name.replace(" \u2605", "")
    name = name.replace(" ", "_")
    name = name.replace("[", "")
    name = name.replace("]", "")
    name = name.replace("\'", "")
    name = name.replace("_\u03b4", "_o")
    name = name.replace("\u03b4", "o")
    name = name.replace("\u2640", "f")
    name = name.replace("\u2642", "m")
    name = name.replace("\u00e9", "e")
    name = name.replace(".", "")
    name = name.replace("!", "")
    name = name.lower()
    if name in card_name_list:
        count = 2
        while name in card_name_list:
            if count > 2:
                name = name[:-1]
            name = name + str(count)
            count += 1

    
    return name


populatePokeData(targetSetList)

for set in targetSetList:
    directory = f"C:/Users/Andreas/Desktop/pip_code/models/{set}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    card_name_list = []
    for card in allPokeData[set]:
        jsonModelDict = {"texture_size": [128, 128], "textures": {"0": "item/backside128", "1": "pokeName", "particle": "item/backside128"}, "elements": [
                {
                    "from": [3, 1, 8],
                    "to": [13, 15, 8],
                    "faces": {
                        "north": {"uv": [0, 0, 16, 16], "texture": "#0"},
                        "east": {"uv": [15, 0, 16, 16], "texture": "#missing"},
                        "south": {"uv": [0, 0, 16, 16], "texture": "#1"},
                        "west": {"uv": [15, 0, 16, 16], "texture": "#missing"},
                        "up": {"uv": [3.5, 0, 12.5, 1], "texture": "#missing"},
                        "down": {"uv": [3.5, 15, 12.5, 16], "texture": "#missing"}
                    }
                }
            ],
            "gui_light": "front",
            "display": {
                "thirdperson_righthand": {
                    "rotation": [0, 0, 0],
                    "translation": [0, 1.75, 1],
                    "scale": [0.3, 0.3, 0.3]
                },
                "thirdperson_lefthand": {
                    "rotation": [0, 0, 0],
                    "translation": [0, 1.75, 1],
                    "scale": [0.3, 0.3, 0.3]
                },
                "firstperson_righthand": {
                    "rotation": [0, 0, 0],
                    "translation": [0, 3.25, 0],
                    "scale": [0.5, 0.5, 0.5]
                },
                "firstperson_lefthand": {
                    "rotation": [0, 0, 0],
                    "translation": [0, 3.25, 0],
                    "scale": [0.5, 0.5, 0.5]
                },
                "ground": {
                    "translation": [0, 2, 0],
                    "scale": [0.5, 0.5, 0.5]
                },
                "gui": {
                    "rotation": [0, 0, 0],
                    "scale": [1.14, 1.14, 1]
                }
            }
        }
        name = format_name(card.name, card_name_list)
        card_name_list.append(name)
        jsonModelDict["textures"]["1"] = f"item/sets/{set}/{name}"
        with open(f"{directory}/{name}.json", "w") as file:
            json_file = json.dumps(jsonModelDict, indent=None)
            file.write(json_file)
        

        overridesList = []
        filledMapDict = {"parent": "item/generated", "textures": {"layer0": "item/filled_map", "layer1": "item/filled_map_markings"}, "overrides": overridesList}
        energyList = ["Fighting_Energy", "Fire_Energy", "Grass_Energy", "Lightning_Energy", "Psychic_Energy", "Water_Energy", "Darkness_Energy", "Metal_Energy"]
        predicateDict = {"predicate": {"custom_model_data": 1}, "model": "item/Bulbasaur"}

        card_count = 30001
        for energy in energyList:
            energiesEntry = copy.deepcopy(predicateDict)
            energiesEntry["predicate"]["custom_model_data"] = card_count
            energiesEntry["model"] = "sets/energy_cards/" + f"{energy}"
            card_count += 1
            overridesList.append(energiesEntry)


for set in targetSetList:
    pokeCountDict = {}
    card_name_list = []
    for card in allPokeData[set]:
        if card.name not in ["Fighting Energy", "Fire Energy", "Grass Energy", "Lightning Energy", "Psychic Energy", "Water Energy", "Darkness Energy", "Metal Energy"]:
            newEntry = copy.deepcopy(predicateDict)
            if card.rarity == "Promo":
                newEntry["predicate"]["custom_model_data"] = card.cardNumber + 66000
            else:
                newEntry["predicate"]["custom_model_data"] = card.cardNumber + 34000
            
            name = format_name(card.name, card_name_list)
            card_name_list.append(name)
            newEntry["model"] = f"sets/{set}/{name}"
            
            overridesList.append(newEntry)

with open("C:/Users/Andreas/Desktop/pip_code/models/filled_map.json", "w") as file:
    json_file = json.dumps(filledMapDict, indent=1)
    file.write(json_file)