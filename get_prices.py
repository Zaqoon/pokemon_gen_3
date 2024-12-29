import os
import json

from pokemontcgsdk import Card
from pokemontcgsdk import RestClient

from api_grab import target_set_list, sort_item

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

RestClient.configure(API_KEY)


def get_prices(target) -> dict:
    crd_nmbr = 0
    promo_nmbr = 0
    prices_dict = {}
    energy_type_list = ['Grass', 'Water', 'Fire', 'Lightning', 'Fighting', 'Psychic', 'Colorless', 'Darkness', 'Metal']
    energy_price = {
        'Darkness Energy': {
            'Price': 0,
            'Number': 30007
        },
        'Metal Energy': {
            'Price': 15.84,
            'Number': 30008
        }
    }
    for set in target:
        print(f"Populating cards from \"{set}\"")
        cards = Card.where(q=f'set.id:{set}')
        sorted_cards = sorted(cards, key=sort_item)
        for card in sorted_cards:
            nmbr = None
            if card.name not in energy_price and card.name.replace(" Energy", "") in energy_type_list:
                continue

            try:
                price = card.cardmarket.prices.trendPrice
                converted_price = euro_to_usd(price)
            except AttributeError:
                converted_price = 0.01

            if card.rarity == 'Promo':
                promo_nmbr += 1
                nmbr = promo_nmbr + 66000
            elif card.name not in energy_price:
                crd_nmbr += 1
                nmbr = crd_nmbr + 34000

            if card.name in energy_price:
                nmbr = energy_price[card.name]['Number']
                if energy_price[card.name]['Price'] == 0:
                    energy_price[card.name]['Price'] = converted_price
                elif energy_price[card.name]['Price'] > 0:
                    converted_price = energy_price[card.name]['Price']

            if str(nmbr) in prices_dict:
                continue

            prices_dict[str(nmbr)] = converted_price
            print(f'{nmbr}: {converted_price}')

    return prices_dict


def euro_to_usd(euro: float) -> float:
    usd = euro * 1.04
    usd = str(round(usd, 2))
    while usd[-1] == '0' or usd[-1] == '.':
        if len(usd) == 1:
            break
        usd = usd[:-1]

    return float(usd)


def write_to_file(price_dict: dict):
    with open('prices.json', 'w') as file:
        data = json.dumps(price_dict, indent=4)
        file.write(data)


if __name__ == '__main__':
    price_dict = get_prices(target_set_list)
    write_to_file(price_dict)
