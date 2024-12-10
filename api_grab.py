from pokemontcgsdk import Card
from pokemontcgsdk import RestClient

import re
import json
import os
import shutil

from dotenv import load_dotenv
from poke_data import Card_Data
from villagers import sets

load_dotenv()
API_KEY = os.getenv('API_KEY')
RestClient.configure(API_KEY)

target_set_list = ['ex1', 'ex2', 'ex3', 'ex4', 'np', 'ex5', 'ex6', 'ex7', 'ex8',
                   'ex9', 'ex10', 'ex11', 'ex12', 'ex13', 'ex14', 'ex15', 'ex16']

#target_set_list = ['ex1']

card_data = {gen: [] for gen in target_set_list}


set_name = {
    'ex1': 'Ruby & Sapphire', 'ex2': 'Sandstorm', 'ex3': 'Dragon', 'ex4': 'Team Magma vs Team Aqua', 'ex5': 'Hidden Legends',
    'ex6': 'FireRed & LeafGreen', 'ex7': 'Team Rocket Returns', 'ex8': 'Deoxys', 'ex9': 'Emerald', 'ex10': 'Unseen Forces',
    'ex11': 'Delta Species', 'ex12': 'Legend Maker', 'ex13': 'Holon Phantoms', 'ex14': 'Crystal Guardians', 'ex15': 'Dragon Frontiers',
    'ex16': 'Power Keepers', 'np': 'Nintendo Promos'
}

weight_dict_odds = {
    "ex1": {
        "Rare Holo": 3,
        "Rare Holo EX": 6,
        "Rare Secret": 0,
        "Rare Holo Star": 0,
        "Common": -1,
        "basic_energy": 3,
        "Rare": 0
    },
    "ex2": {
        "Rare Holo": 3,
        "Rare Holo EX": 6,
        "Rare Secret": 0,
        "Rare Holo Star": 0,
        "Common": -1,
        "basic_energy": 0,
        "Rare": 0
    },
    "ex3": {
        "Rare Holo": 3,
        "Rare Holo EX": 6,
        "Rare Secret": 36,
        "Rare Holo Star": 0,
        "Common": -1,
        "basic_energy": 0,
        "Rare": 0
    },
    "ex4": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 108,
        "Rare Holo Star": 0,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex5": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 72,
        "Rare Holo Star": 0,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex6": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 36,
        "Rare Holo Star": 0,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex7": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 108,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex8": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 72,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex9": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 72,
        "Rare Holo Star": 0,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex10": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 72,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex11": {
        "Rare Holo": 3,
        "Rare Holo EX": 36,
        "Rare Secret": 72,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex12": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 72,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex13": {
        "Rare Holo": 3,
        "Rare Holo EX": 36,
        "Rare Secret": 72,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex14": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 0,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex15": {
        "Rare Holo": 3,
        "Rare Holo EX": 12,
        "Rare Secret": 0,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    },
    "ex16": {
        "Rare Holo": 3,
        "Rare Holo EX": 9,
        "Rare Secret": 0,
        "Rare Holo Star": 72,
        "Common": 0,
        "basic_energy": 0,
        "Rare": -1
    }
}


def weight_calculation(rarity_dict:dict, set:str) -> dict:
    card_count = {rarity: 0 for rarity in rarity_dict}
    weight_dict = card_count.copy()
    for card in card_data[set]: # Count cards in all rarity groups
        if card.rarity in rarity_dict and rarity_dict[card.rarity] > 0:
            card_count[card.rarity] += 1

    if rarity_dict['basic_energy'] > 0:
        card_count['basic_energy'] = 1
    
    base_weight = 100008
    total_weight = 0
    premium_weight = 0

    for rarity in rarity_dict:
        if rarity_dict[rarity] > 0:
            weight = base_weight / rarity_dict[rarity]  # Calculate combined weight of cards in rarity group
            total_weight += weight
            weight_dict[rarity] = weight / card_count[rarity]   # Divide weight among all cards in rarity group

            if rarity in ['Rare Holo', 'Rare Holo EX', 'Rare Holo Star', 'Rare Secret']:
                premium_weight += base_weight / rarity_dict[rarity]
        elif rarity_dict[rarity] == -1:
            remainder_rarity = rarity   # Remaining weight will be allocated to 'remainder rarity'

    weight_dict['Premium'] = premium_weight
    weight_dict[remainder_rarity] = base_weight - total_weight

    return weight_dict


set_color = {
    "ex1": "red", "ex2": "#D2B48C", "ex3": "#00FF00", "ex4": "#018787", "ex5": "#8B0000",
    "ex6": "#a1cc47", "ex7": "#ba3504", "ex8": "#bd33ff", "ex9": "#50c878", "ex10": "#02c2c2",
    "ex11": "#C0C0C0", "ex12": "#d2b48c", "ex13": "#9966CC", "ex14": "#b0e0e6", "ex15": "#fcb738",
    "ex16": "#820000", "np": "purple"
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


def populateCard_Data(target):
    for set in target:
        print(f'Populating cards from \'{set}\'')
        cards = Card.where(q=f'set.id:{set}')
        sorted_cards = sorted(cards, key=sortItem)
        for card in sorted_cards:
            currCard_Data = Card_Data(card)
            currCard_Data.generate_components()
            card_data[set].append(currCard_Data)


def add_entry(pokeTag, weight_dict):
    newEntry = {'type': 'item', 'weight': 1, 'name': 'minecraft:filled_map', 'functions': pokeTag[0]}
    if loot_table == 'Premium_rare':
        weight = weight_dict[pokeTag[1]]
        try:
            newEntry['weight'] = round(weight)
        except:
            print(f'Error: {card.name} in {set} has weight: {weight}')
    elif loot_table == 'Reverse':
        weight = reverse_weight[pokeTag[1]]
        newEntry['weight'] = round(weight)
    elif card.rarity == 'Promo' or isinstance(weight_dict, int):
        newEntry['weight'] = weight_dict
        
    file_dict['pools'][0]['entries'].append(newEntry)


def add_loot_table(set, rarity, weight):
    newEntry = {'type': 'loot_table', 'weight': round(weight), 'value': f'tcg:{set}/{rarity}'}
    file_dict['pools'][0]['entries'].append(newEntry)


def add_rare_card(set, loot_table, weight):
    card_dict = {
          'type': 'item',
          'weight': round(weight),
          'name': 'minecraft:carrot_on_a_stick',
          'functions': [
            {
              'function': 'set_components',
              'components': {
                'minecraft:custom_model_data': 1,
                'minecraft:custom_data': {
                f'{set}_{loot_table.lower()}_rare': 1
                },
                'minecraft:enchantment_glint_override': True
              }
            },
            {
              'function': 'set_name',
              'name': [
                {
                  'color': 'aqua',
                  'italic': False,
                  'text': 'Holographic Card'
                }
              ]
            },
            {
              'function': 'set_lore',
              'lore': [
                {
                  'italic': True,
                  'text': 'Right click to reveal card.'
                },
                {
                  'color': set_color[set],
                  'italic': False,
                  'text': set_name[set]
                }
              ],
              'mode': 'append'
            }
          ]
        }
    file_dict['pools'][0]['entries'].append(card_dict)


def reverse_weights(set):
    rarity_dict = {
        'Rare Holo': 0, 'Rare': 0, 'Uncommon': 0, 'Common': 0,
    }
    weight_dict = rarity_dict.copy()
    for card in card_data[set]:
        if card.rarity in rarity_dict and card.name not in energy_list:
            rarity_dict[card.rarity] += 1
    total_weight = 100800
    total_cards = sum(value for value in rarity_dict.values())


    for rarity in rarity_dict:
        if rarity_dict[rarity] > 0:
            if rarity != 'Common':
                weight_dict[rarity] = (total_weight / total_cards) * rarity_dict[rarity]
            else:
                weight_dict[rarity] = total_weight / total_cards
    
    return weight_dict


def deck_special_cards(type_specific_cards: dict):
    for loot_table in type_specific_cards:
        print(f'Creating loot table for {loot_table} Holo Cards ...')
        file_directory = f'loot_tables/type_rares_gen3'
        if os.path.exists(file_directory):
            shutil.rmtree(file_directory)
        os.makedirs(file_directory)

        file_dict = { 'type': 'minecraft:chest', 'pools': [{'rolls': 1, 'entries': []}]}
        with open(f'{file_directory}/{loot_table.lower()}.json', 'w') as file:
            for card_tag in type_specific_cards[loot_table]:
                weight = card_tag[1]
                add_entry(card_tag, weight)
            file_dict = json.dumps(file_dict, indent=4)
            file.write(file_dict)


populateCard_Data(target_set_list)

if __name__ == '__main__':
    energy_list = ['Fighting Energy', 'Fire Energy', 'Grass Energy', 'Lightning Energy', 'Psychic Energy', 'Water Energy']
    type_specific_cards = {
            'Grass': [],
            'Fire': [],
            'Water': [],
            'Psychic': [],
            'Fighting': [],
            'Lightning': [],
            'Colorless': [],
            'Darkness': [],
            'Metal': []
        }
    for set in target_set_list:
        print(f'Creating loot table for {set} ...')

        directory = f'loot_tables/{set}'
        if os.path.exists(directory):
            shutil.rmtree(directory)

        os.makedirs(directory)

        tag_lines = {
            'Common': [],
            'Uncommon': [],
            'Rare': [],
            'Premium': [],
            'Premium_rare': [],
            'Reverse': [],
            'Reverse_rare': [],
            'Energy': []
        }

        if set == 'np':
            weight = len(card_data[set]) + 90
            file_dict = {'type': 'minecraft:chest', 'pools': [{'rolls': 1, 'entries': []}]}
            with open(f'{directory}/promos.json', 'w') as file:
                for card in card_data[set]:
                    card_object = [card.functions, card.rarity]
                    add_entry(card_object, weight)
                    weight -= 2
                file_dict = json.dumps(file_dict, indent=4)
                file.write(file_dict)
            continue
        else:
            weight_dict = weight_calculation(weight_dict_odds[set], set)
            reverse_weight = reverse_weights(set)

        for card in card_data[set]:
            card_object = [card.functions, card.rarity]
            if card.rarity in ['Common', 'Uncommon', 'Rare', 'Promo']:
                tag_lines[card.rarity].append(card_object)
            if card.rarity in ['Rare Holo', 'Rare Holo EX', 'Rare Holo Star', 'Rare Secret']:
                tag_lines['Premium_rare'].append(card_object)
            if card.rarity in ['Common'] and card.name not in energy_list:
                tag_lines['Reverse'].append(card_object)
            if card.rarity in ['Rare Holo'] and card.name not in energy_list:
                tag_lines['Reverse_rare'].append(card_object)
            if card.name in energy_list:
                tag_lines['Energy'].append(card_object)
            
            if card.rarity == 'Rare Holo' and card.supertype == 'Pokémon':
                card_object = [card.functions, sets[set]['weight']]
                for card_type in card.types:
                    type_specific_cards[card_type].append(card_object)

        for loot_table in tag_lines.keys():
            if len(loot_table) > 0:
                file_dict = {'type': 'minecraft:chest', 'pools': [{'rolls': 1, 'entries': []}]}
                if len(loot_table) > 0:
                    with open(f'{directory}/{loot_table.lower()}.json', 'w') as file:
                        if loot_table != 'Reverse':
                            for card_tag in tag_lines[loot_table]:
                                add_entry(card_tag, weight_dict)
                        else:
                            for card_tag in tag_lines['Common']:
                                if card_tag not in tag_lines['Energy']:
                                    add_entry(card_tag, weight_dict)
                        if loot_table == 'Premium':
                            if weight_dict['Common'] > 0:
                                add_loot_table(set, 'common', weight_dict['Common'])
                            if weight_dict['basic_energy'] > 0:
                                add_loot_table(set, 'energy', weight_dict['basic_energy'])
                            if weight_dict['Rare'] > 0:
                                add_loot_table(set, 'rare', weight_dict['Rare'])
                            add_rare_card(set, loot_table, weight_dict['Premium'])
                        if loot_table == 'Reverse':
                            add_loot_table(set, 'uncommon', reverse_weight['Uncommon'])
                            add_loot_table(set, 'rare', reverse_weight['Rare'])
                            add_rare_card(set, loot_table, reverse_weight['Rare Holo'])
                        file_dict = json.dumps(file_dict, indent=4)
                        file.write(file_dict)

    # Rares for types in decks
    file_directory = 'loot_tables/type_rares_gen3'
    if os.path.exists(file_directory):
        shutil.rmtree(file_directory)
    os.makedirs(file_directory)
    for loot_table in type_specific_cards.keys():
        print(f'Creating loot table for {loot_table} Holo Cards ...')
        file_dict = {'type': 'minecraft:chest', 'pools': [{'rolls': 1, 'entries': []}]}
        with open(f'{file_directory}/{loot_table.lower()}.json', 'w') as file:
            for card_tag in type_specific_cards[loot_table]:
                weight = card_tag[1]
                add_entry(card_tag, weight)
            file_dict = json.dumps(file_dict, indent=4)
            file.write(file_dict)
