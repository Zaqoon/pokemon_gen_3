import win32com.client
import os
import re
from poke_data import Card_Data

import requests
import keyboard
import comtypes.client

import pokemontcgsdk
from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Rarity
from pokemontcgsdk import RestClient
import pokemontcgsdk as ptcg

import photoshop as ps
from photoshop import Session

RestClient.configure('3f9fba22-cc72-487d-a8fc-e1e5ba5744fc')

psApp = win32com.client.Dispatch("Photoshop.Application")

#targetSetList = ["ex1", "ex2", "np", "ex3", "ex4", "ex5", "ex6", "ex7", "ex8", "ex9", "ex10", "ex11", "ex12", "ex13", "ex14", "ex15", "ex16"]
targetSetList = ["ex3"]
allPokeData = {"ex1": [], "ex2": [], "ex3": [], "np": [], "ex4": [], "ex5": [], "ex6": [], "ex7": [], "ex8": [], "ex9": [], "ex10": [], "ex11": [], "ex12": [], "ex13": [], "ex14": [], "ex15": [], "ex16": []}

keywords = ["Blaine's ", "Brock's ", "Erika's ", "Lt. Surge's ", "Misty's ", "Rocket's ", "Sabrina's ", "Giovanni's ", "Koga's ", "Shining ",
            "Team Aqua's ", "Team Magma's ", "Dark "]


def format_name(name, card_name_list):
    name = name.replace(" \u2605", "")
    name = name.replace(" ", "_")
    name = name.replace("[", "")
    name = name.replace("]", "")
    name = name.replace("\'", "")
    name = name.replace(" \u03B4", "")
    name = name.lower()
    if name in card_name_list:
        count = 2
        while name in card_name_list:
            if count > 2:
                name = name[:-1]
            name = name + str(count)
            count += 1

    
    return name


def download_images(key):
    failed_downloads = []
    for set in targetSetList:
        card_name_list = []
        directory = f"C:/Users/Andreas/Documents/pokemon_card_templates/resource_pack/small_downloaded/{set}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        for card in allPokeData[set]:
            if card.name not in ["Fire Energy", "Fighting Energy", "Grass Energy", "Water Energy", "Psychic Energy", "Lightning Energy", "Darkness Energy", "Metal Energy"]:
                name = format_name(card.name, card_name_list)
                card_name_list.append(name)
                if key.lower() == "r":
                    card_path = f"C:/Users/Andreas/Documents/pokemon_card_templates/resource_pack/finished_images/{set}/{name}.png"
                    if os.path.exists(card_path):
                        continue
                if card.rarity != "":
                    imageURL = card.images['large']
                    save_path = directory + "/" + name + ".png"
                    response = requests.get(imageURL)
                    if response.status_code == 200:
                        with open(save_path, "wb") as file:
                            file.write(response.content)
                        print(f"{card.number}/{card.printedTotal} {name}: Image downloaded successfully!")
                    else:
                        image_details = f"{card.number} {card.name} {set}"
                        print(f"Failed to download image: {image_details}")
                        failed_downloads.append(image_details)
                        continue
                    imagePath = rf"C:/Users/Andreas/Documents/pokemon_card_templates/resource_pack/small_downloaded/{set}/{name}.png"
                    doc = psApp.Open(imagePath)
                    doc.ResizeImage(128, 128)
                    save_path = f"C:/Users/Andreas/Documents/pokemon_card_templates/resource_pack/finished_images/{set}"
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    save_path = save_path + f"/{name}.png"
                    save_image(save_path)
    
    return failed_downloads


def save_image(save_path):
    doc = psApp.Application.ActiveDocument
    options = win32com.client.Dispatch("Photoshop.PNGSaveOptions")
    doc.SaveAs(save_path, options)
    doc.Close(2)


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
    

def populatePokeData():
    for set in targetSetList:
        print(f"Populating cards from \"{set}\"")
        cards = Card.where(q=f'set.id:{set}')
        sorted_cards = sorted(cards, key=sortItem)
        for card in sorted_cards:
            currPokeData = PokeData(card)
            currPokeData.generateLoreList()
            currPokeData.generateNameLoreDict()
            allPokeData[set].append(currPokeData)


def continue_prompt():
    print("Do you wish to download all images or resume from last? Type \'Y\' for Yes or \'R\' to resume from last saved image.")
    key = keyboard.read_key()
    if key.lower() == "y":
        print("Downloading images...")
        populatePokeData()
        failed_downloads = download_images(key)
    elif key.lower() == "r":
        print("Resuming from the last saved image.")
        populatePokeData()
        failed_downloads = download_images(key)
    else:
        print("Invalid key.")
    print(failed_downloads)


continue_prompt()