from pokemontcgsdk import Card
from pokemontcgsdk import RestClient

from poke_data import CardData

from dotenv import load_dotenv
import os
import re
import json
import pickle

load_dotenv()
API_KEY = os.getenv('API_KEY')
RestClient.configure(API_KEY)


def sort_item(card):
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


def populate_data(target: list) -> dict:
    with open('data/prices.json', 'r') as file:
        price_dict = json.load(file)

    card_data = {set_id: [] for set_id in target}

    for set_name in target:
        print(f'Populating cards from \'{set_name}\'')
        cards = Card.where(q=f'set.id:{set_name}')
        sorted_cards = sorted(cards, key=sort_item)
        for card in sorted_cards:
            card_object = CardData(card, price_dict)
            card_object.generate_components()
            card_data[set_name].append(card_object)

    return card_data


def save_data(set_dict: dict):
    with open('data/api_data.pkl', 'wb') as file:
        pickle.dump(set_dict, file)

    print('Data was successfully saved.')


if __name__ == '__main__':
    target_set_list = [
        'ex1', 'ex2', 'ex3', 'ex4', 'ex5', 'ex6', 'ex7', 'ex8', 'ex9', 'ex10',
        'ex11', 'ex12', 'ex13', 'ex14', 'ex15', 'ex16', 'np'
    ]

    card_dict = populate_data(target_set_list)  # Fetch data

    save_data(card_dict)    # Save to api_data.pkl
