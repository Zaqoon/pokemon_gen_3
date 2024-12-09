from poke_data_gen3 import PokeData

import pokemontcgsdk
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Rarity
from pokemontcgsdk import RestClient
import pokemontcgsdk as ptcg

import keyboard
import pyperclip
import re
import os
import time

import shutil

targetSetList = ["ex1", "ex2", "ex3", "np", "ex4", "ex5", "ex6", "ex7", "ex8", "ex9", "ex10", "ex11", "ex12", "ex13", "ex14", "ex15", "ex16"]
#targetSetList = ["ex1", "ex2", "ex3", "ex4"]

allPokeData = {
    "ex1": [],  "ex2": [],  "ex3": [],  "ex4": [],  "ex5": [],
    "ex6": [],  "ex7": [],  "ex8": [],  "ex9": [], "ex10": [],
    "ex11": [], "ex12": [], "ex13": [], "ex14": [], "ex15": [],
    "ex16": [], "np": []
}


def number_name(number, name):
    name = name.replace(" \u2605", "")
    number = number.replace("?", "QM")
    number = number.replace("!", "EM")
    
    return number, name


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

populatePokeData(targetSetList)

destination_folder = 'C:/Users/Andreas/Desktop/mapart/pasted'
for setName in targetSetList:
    for card in allPokeData[setName]:
        if card.name not in ["Fire Energy", "Fighting Energy", "Grass Energy", "Water Energy", "Psychic Energy", "Lightning Energy", "Darkness Energy", "Metal Energy"]:
            number, name = number_name(card.number, card.name)
            static_number = card.static_number
            if card.rarity == "Promo":
                static_number += 66000
            else:
                static_number += 34000
            if os.path.exists(f"C:/Users/Andreas/Downloads/mapart/map_{static_number}.dat"):
                continue
            source_file = f'C:/Users/Andreas/Documents/pokemon_card_templates/finished files/{setName}/{number} {name}.png'
            shutil.copy(source_file, destination_folder)
            keyboard.press('F4')
            keyboard.release('F4')
            keyboard.wait("a")
            time.sleep(1)
            file_path = rf'C:/Users/Andreas/Desktop/mapart/pasted/{number} {name}.png'
            if os.path.exists(file_path):
                os.remove(file_path)
            dat_path = "C:/Users/Andreas/Downloads/mapart/"
            downloaded_file = "map_0.dat"
            if os.path.exists(dat_path + downloaded_file):
                os.rename(dat_path + downloaded_file, f"{dat_path}/map_{static_number}.dat")
                print(f"map_{static_number}.dat was successfully downloaded.")
