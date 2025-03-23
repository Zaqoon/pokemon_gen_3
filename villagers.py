import os
import random
import re
import json
import shutil
from typing import List

from villager_data import VillagerData
from villager_data import TrainerData
from villager_data import EnergyData


with open('data/data.json', 'r', encoding="utf-8") as file:
    data = json.load(file)
    sets = data['sets']

sets = {key: {**value, "abbreviation": key} for key, value in sets.items()}

pokemon_data = {
    "Grass": {},
    "Fire": {},
    "Water": {},
    "Psychic": {},
    "Lightning": {},
    "Fighting": {},
    "Colorless": {},
    "Darkness": {},
    "Metal": {}
}

trainer_data = {
    'supporter': [],
    'item': [],
    'stadium': [],
    'tool': [],
    'technical_machine': []
}

energy_data = {}

evolution_dict = {'Common': {}, 'Uncommon': {}, 'Rare': {}}

data_strings = {
    "data_modify_dict": "execute as @p[x=-52711,y=113,z=108732,limit=1,sort=nearest] at @s run data modify entity @e[type=villager,limit=1,sort=nearest,nbt={VillagerData:{profession:\"minecraft:%s\"}}] Offers.Recipes append value ",
    "card_dict": '''{id: "minecraft:filled_map",count: %s,components: %s}''',
    "rare_card_dict": '''{id: "minecraft:carrot_on_a_stick",count: %s,components: %s}'''
}

deck_color = {"Grass": "green", "Fire": "red", "Water": "blue", "Fighting": "brown","Lightning": "yellow",
              "Psychic": "dark_purple", "Colorless": "gray", "Metal": "dark_gray", "Darkness": "dark_aqua"}

weights = [sets[key]["weight"] for key in sets]

predicate_list = ["Blaine's ", "Brock's ", "Erika's ", "Lt. Surge's ", "Misty's ", "Rocket's ", "Sabrina's ", "Giovanni's ", "Koga's ", "Shining ",
                  "Team Aqua's ", "Team Magma's ", "Holon's ", "Dark "]


def populate_villager_data() -> None:
    for energy_type in deck_color:
        pokemon_data[energy_type] = {'Common': [], 'Uncommon': [], 'Rare': []}
    for set in sets:
        for rarity in ['Common', 'Uncommon', 'Rare']:
            with open(f'loot_tables/{set}/{rarity}.json', 'r') as file:
                loot_table = json.load(file)
            for entry in loot_table['pools'][0]['entries']:
                functions = entry['functions']
                custom_data = [pokemon_type for pokemon_type in functions[0]['components']['custom_data']]
                if 'trainer' in custom_data:
                    data = {
                        'functions': functions,
                        'set': set,
                        'rarity': rarity,
                        'weight': sets[set]['weight']
                    }
                    card_data = TrainerData(data)
                    for cd in card_data.custom_data:
                        if cd != 'trainer':
                            trainer_data[cd].append(card_data)
                    continue
                elif 'energy' in custom_data:
                    continue
                data = {'weight': sets[set]['weight'],
                        'functions': functions,
                        'types': custom_data,
                        'set': set,
                        'rarity': rarity
                        }
                card_data = VillagerData(data)
                for pokemon_type in custom_data:
                    card_type = pokemon_type.capitalize()
                    pokemon_data[card_type][rarity].append(card_data)
                if card_data.evolves_from != 'Basic':
                    if card_data.evolves_from in evolution_dict[rarity]:
                        evolution_dict[rarity][card_data.evolves_from].append(card_data)
                    else:
                        evolution_dict[rarity][card_data.evolves_from] = [card_data]


def populate_energy_cards() -> None:
    entry_numbers = {
        'energy': [0, 1, 2, 3, 4, 5],
        'rare': [10, 11]
    }
    for rarity in entry_numbers:
        with open(f'loot_tables/ex1/{rarity}.json', 'r') as file:
            loot_table = json.load(file)
        for entry_num in entry_numbers[rarity]:
            entry = loot_table['pools'][0]['entries'][entry_num]
            functions = entry['functions']
            data = {
                'functions': functions,
                'rarity': rarity
            }
            card_data = EnergyData(data)
            energy_type = card_data.name.replace(' Energy', '')
            energy_data.update({energy_type: card_data})


def sort_card_weights() -> dict:
    rarities = ['Common', 'Uncommon', 'Rare']
    card_weights = {pokemon_type: {rarity: [] for rarity in rarities} for pokemon_type in pokemon_data}
    for pokemon_type in deck_color:
        for rarity in rarities:
            villager_data_weights = [villager_data.weight for villager_data in pokemon_data[pokemon_type][rarity]]
            card_weights[pokemon_type][rarity] = villager_data_weights
    
    return card_weights


def sort_trainer_weights() -> dict:
    card_weights = {subtype: [] for subtype in trainer_data}
    for subtype in card_weights:
        card_weights[subtype] = [trainer.weight for trainer in trainer_data[subtype]]

    return card_weights


def add_pokemon_cards(evolution_names:List[str], pokemon_type:str, deck_dict:str, rarity:str) -> tuple:
    card_amount = {
        "Common": {
            "Unique Cards": 5,
            "Stack Min": 2,
            "Stack Max": 4
            },
        "Uncommon": {
            "Unique Cards": 3,
            "Stack Min": 1,
            "Stack Max": 2
            },
        "Rare": {
            "Unique Cards": 1,
            "Stack Min": 2,
            "Stack Max": 2
            },
        "Trainer": {
            "Unique Cards": 5,
            "Stack Min": 2,
            "Stack Max": 4
            }
        }
    card_list = []
    added_cards = 0
    weights = card_weights[pokemon_type][rarity][:]
    basic_count = 0
    evolution_count = 0
    if rarity != 'Common':
        for card in pokemon_data[pokemon_type][rarity]:
            if card.evolves_from == 'Basic':
                basic_count += 1
            elif card.evolves_from in evolution_names:
                evolution_count += 1

        for i, card in enumerate(pokemon_data[pokemon_type][rarity]):
            if card.evolves_from not in evolution_names and card.evolves_from != 'Basic':
                weights[i] = 0
            elif card.evolves_from in evolution_names and card.evolves_from != 'Basic':
                weights[i] *= (8 * basic_count) // evolution_count

            if weights[i] > 0 and card.name in [c.name for c in card_list]:
                weights[i] *= 0.5
    
    while added_cards < card_amount[rarity]['Unique Cards']:
        card = random.choices(pokemon_data[pokemon_type][rarity], weights=weights, k=1)[0]

        card_index = pokemon_data[pokemon_type][rarity].index(card)
        weights[card_index] = 0

        min = card_amount[rarity]['Stack Min']
        max = card_amount[rarity]['Stack Max']

        components = card.components

        deck_dict = add_to_deck(deck_dict, min=min, max=max, components=components, item_type='card_dict')
        evolution_names.append(card.name)
        card_list.append(card)
        if card.evolves_from in evolution_names:
            evolution_names.remove(card.evolves_from)
            for i, card in enumerate(pokemon_data[pokemon_type][rarity]):
                if card.evolves_from not in evolution_names and card.evolves_from != 'Basic':
                    weights[i] = 0
        added_cards += 1

    return deck_dict, evolution_names


def unescape_string(escaped_string: str) -> str:
    unescaped_string = escaped_string.encode().decode('unicode_escape')
    unescaped_string = unescaped_string.replace('\\,', ',')
    return unescaped_string


def add_to_deck(deck_dict: dict, min: int, max: int, components: dict, item_type: str) -> dict:
    stack_amount = random.randrange(min, max + 1)
    card_dict = data_strings[item_type] % (stack_amount, components)
    deck_dict["sell"]["components"]["bundle_contents"].append(card_dict)

    return deck_dict


def get_trainer_cards(deck_dict: dict) -> dict:
    weights = trainer_weights.copy()
    subtype_weights = {
        'supporter': 35,
        'item': 60,
        'tool': 19,
        'stadium': 20,
        'technical_machine': 10
    }
    subtype_selector = {
        1: 'supporter',
        2: 'item',
        3: 'item',
        4: random.choices(list(subtype_weights.keys()), weights=subtype_weights.values())[0]
    }

    trainer_cards = []
    for i in range(1, 5):
        subtype = subtype_selector[i]
        while True:
            random_card = random.choices(trainer_data[subtype], weights=weights[subtype])[0]
            if random_card in trainer_cards:
                continue
            else:
                trainer_cards.append(random_card)
                break

        card_index = trainer_data[subtype].index(random_card)
        weights[card_index] = 0
        components = random_card.components
        deck_dict = add_to_deck(deck_dict, min=2, max=4, components=components, item_type="card_dict")

    return deck_dict


def energy_cards(deck_type, deck_dict) -> dict:
    energies = []

    def random_energy(energies: List[str]) -> str:
        if not energies:
            energies = [energy for energy in energy_data if energy not in ['Darkness', 'Metal', deck_type]]
        energy = energies.pop(random.randint(0, len(energies) - 1))
        
        return energy
    
    energy_dict = {
        "Grass": {
            "energy_entry": 'Grass',
            "type_sub_entry": 'Fighting',
            "color": "#4CAF50"
        },
        "Fire": {
            "energy_entry": 'Fire',
            "type_sub_entry": 'Lightning',
            "color": "#E53935"
        },
        "Water": {
            "energy_entry": 'Water',
            "type_sub_entry": 'Psychic',
            "color": "#2979FF"
        },
        "Fighting": {
            "energy_entry": 'Fighting',
            "type_sub_entry": random_energy(energies),
            "color": "#8D6E63"
        },
        "Lightning": {
            "energy_entry": 'Lightning',
            "type_sub_entry": random_energy(energies),
            "color": "#FDD835"
        },
        "Psychic": {
            "energy_entry": 'Psychic',
            "type_sub_entry": random_energy(energies),
            "color": "#BA68C8"
        },
        "Colorless": {
            "energy_entry": random_energy(energies),
            "type_sub_entry": random_energy(energies),
            "color": "#003f3f"
        },
        "Darkness": {
            "energy_entry": 'Darkness',
            "type_sub_entry": random_energy(energies),
            "color": "#003f3f"
        },
        "Metal": {
            "energy_entry": 'Metal',
            "type_sub_entry": random_energy(energies),
            "color": "#C0C0C0"
        }
    }

    stack_dict = {0: {'min': 15, 'max': 17}, 1: {'min': 7, 'max': 9}}
    for i in range(0, 2):
        if i == 0:
            energy_entry = energy_dict[deck_type]['energy_entry']
            energy = energy_data[energy_entry]
        else:
            energy_entry = energy_dict[deck_type]["type_sub_entry"]
            energy = energy_data[energy_entry]
        if deck_type in ["Darkness", "Metal"] and i == 0:
            stack_min = 3
            stack_max = 5
        else:
            stack_min = stack_dict[i]['min']
            stack_max = stack_dict[i]['max']

        components = energy.components
        deck_dict = add_to_deck(deck_dict, stack_min, stack_max, components, "card_dict")

    return deck_dict


def deck(deck_amount: int) -> dict:
    decks = {}
    for i in range(1, deck_amount + 1):
        decks[f"Deck{i}"] = None

    custom_model_data_dict = {"Grass": 101, "Fire": 102, "Water": 103, "Fighting": 5, "Lightning": 14, "Psychic": 9, "Colorless": 16, "Darkness": 1, "Metal": 3}
    bundle_dict = {
        "Grass": "green", "Fire": "red", "Water": "blue", "Fighting": "brown", "Lightning": "yellow",
        "Psychic": "purple", "Colorless": "light_gray", "Darkness": "black", "Metal": "dark_gray"
    }
    deck_types = ["Grass", "Fire", "Water", "Fighting", "Lightning", "Psychic", "Colorless", "Darkness", "Metal"]
    deck_weight = {"Grass": 300,"Fire": 300,"Water": 300,"Fighting": 150,"Lightning": 150,"Psychic": 150, "Colorless": 150, "Darkness": 20, "Metal": 12}
    type_hex = {"Grass": "#4CAF50","Fire": "#E53935","Water": "#2979FF","Fighting": "#8D6E63","Lightning": "#FDD835","Psychic": "#BA68C8",
                "Colorless": "gray", "Darkness": "#087575", "Metal": "#C0C0C0" }
    
    while decks[f"Deck{deck_amount}"] is None:
        deck_type = random.choices(deck_types, weights=list(deck_weight.values()))[0]
        deck_types.remove(deck_type)
        del deck_weight[deck_type]
        deck_dict = {
            "maxUses": 1,
            "buy": {
                "id": "minecraft:emerald",
                "count": 1,
                "components": {
                    "minecraft:custom_name": '{"text":"Sapphire","italic":false,"color":"aqua"}',
                    "custom_model_data": {"floats": [1]},
                    "custom_data": {"sapphire": "1b"}}},
            "sell": {
                "id": f"{bundle_dict[deck_type]}_bundle",
                "count": 1,
                "components": {
                    "custom_name": f'{{"bold":true,"color":"{type_hex[deck_type]}","italic":false,"text":"{deck_type} Deck"}}',
                    "bundle_contents": []
                }
            }
        }
        evolution_names = []
        # rarity, evolution_names, deck_type, deck_dict
        for rarity in ["Common", "Uncommon", "Rare"]:
            deck_dict, evolution_names = add_pokemon_cards(evolution_names, deck_type, deck_dict, rarity)

        rare_card_string = f"{{\"custom_name\":'{{\"text\":\"Holographic {deck_type} Card\",\"color\":\"aqua\",\"italic\":false}}',\"lore\":['{{\"text\":\"Right click to reveal card.\"}}'],\"custom_model_data\":{{\"floats\": [1]}},\"enchantment_glint_override\":true,\"custom_data\":{{{deck_type.lower()}_rares_gen3:1b}}}}"
        deck_dict = add_to_deck(deck_dict, 1, 1, rare_card_string, "rare_card_dict")
        deck_dict = get_trainer_cards(deck_dict)
        deck_dict = energy_cards(deck_type, deck_dict)
        deck_dict = fix_dict(deck_dict)

        for deck in decks:
            if decks[deck] is None:
                decks[deck] = deck_dict
                break

    return decks


def promo() -> str:
    promo_dict = """{maxUses:9,buy:{id:"minecraft:emerald",count:1,components:{"minecraft:custom_name":'{"color":"light_purple","italic":false,"text":"Star"}',"minecraft:custom_model_data":{"floats": [5]},"minecraft:custom_data":{greenstar:1b}}},sell:{id:"minecraft:carrot_on_a_stick",count:1,components:{"minecraft:custom_name":'{"bold":true,"italic":false,"text":"Promo Pack"}',"minecraft:lore":['{"color":"#9fd0e0","italic":false,"text":"Nintendo Black Star Promos"}','{"text":"2003-2006","color":"dark_purple","italic":true}'],"minecraft:custom_model_data":{"floats":[20]},"minecraft:custom_data":{np:1}}}}"""
    
    return data_strings["data_modify_dict"] % "cartographer" + promo_dict


def booster(total_boosters:int) -> List[str]:
    trade_dict = """{maxUses:%s,buy:{id:"minecraft:emerald",count:1,components:{"minecraft:custom_name":'{"color":"yellow","italic":false,"text":"Ruby"}',"minecraft:custom_model_data":{"floats": [2]},"minecraft:custom_data":{ruby:1b}}},sell:{id:"minecraft:carrot_on_a_stick",count:1,components:{"minecraft:custom_name":'{"bold":true,"italic":false,"text":"Booster Pack"}',"minecraft:lore":['{"text":"%s","color":"%s","italic":false}','{"text":"%s","color":"dark_purple","italic":true}'],"minecraft:custom_model_data":{"floats":[%s]},"minecraft:custom_data":{ex:%s}}}}"""

    trades = []
    exclude_set_cmd = []
    selected_sets = {}
    while len(selected_sets) < total_boosters:
        random_set_key = random.choices(list(sets.keys()), weights=[sets[set_name]["weight"] for set_name in sets], k=1)[0]
        random_set = sets[random_set_key]
        if random_set in selected_sets.values():
            continue
        custom_model_data_list = random_set["custom_model_data"]
        available_custom_model_data = [item for item in custom_model_data_list if item not in exclude_set_cmd]
        custom_model_data = random.choice(available_custom_model_data)
        exclude_set_cmd.append(custom_model_data)
        selected_sets[custom_model_data] = random_set
    sorted_selected_sets = dict(sorted(selected_sets.items()))
    for cmd, ss in sorted_selected_sets.items():
        trade_str = trade_dict % (ss["max_uses"], ss["name"], ss["color"], ss["date"], cmd, ss["abbreviation"].replace('ex', ''))
        trade_str = data_strings["data_modify_dict"] % "cartographer" + trade_str
        trade_str = trade_str.replace("\n", "").replace("    ", "")
        trades.append(trade_str)
    
    return trades


def fix_dict(deck_dict):
    # Convert deckDict to JSON string
    deckDictString = json.dumps(deck_dict)

    unquote = re.sub(r"\"maxUses\"", r"maxUses", deckDictString)
    unquote = re.sub(r"\"buy\"", r"buy", unquote)
    unquote = re.sub(r"\"id\"", r"id", unquote)
    unquote = re.sub(r"\"count\"", r"count", unquote)
    unquote = re.sub(r"\"ruby\"", r"ruby", unquote)
    unquote = re.sub(r"\"sapphire\"", r"sapphire", unquote)
    unquote = re.sub(r"\"1b\"", r"1b", unquote)
    unquote = re.sub(r"\"display\"", r"display", unquote)
    unquote = re.sub(r"\"tag\"", r"tag", unquote)
    unquote = re.sub(r"\"sell\"", r"sell", unquote)
    unquote = re.sub(r"\"CustomModelData\"", r"CustomModelData", unquote)
    unquote = re.sub(r"\"Items\"", r"Items", unquote)
    unquote = re.sub(r"\"Name\": \"\{\\\"text\\\":\\\"Sapphire\\\",\\\"italic\\\":false,\\\"color\\\":\\\"aqua\\\"\}\"", r"Name: '{\"text\":\"Sapphire\",\"italic\":false,\"color\":\"aqua\"}'", unquote)
    unquote = re.sub(r"\"Name\": \"\{\\\"text\\\":\\\"Ruby\\\",\\\"italic\\\":false,\\\"color\\\":\\\"aqua\\\"\}\"", r"Name: '{\"text\":\"Ruby\",\"italic\":false,\"color\":\"yellow\"}'", unquote)
    unquote = re.sub(r"\"Name\": \"\{\\\"text\\\":\\\"(.*?) Deck\\\",\\\"color\\\":\\\"(.*?)\\\",\\\"italic\\\":false\}\"",lambda match: f"Name: '{{\"text\":\"{match.group(1)} Deck\",\"color\":\"{match.group(2)}\",\"italic\":false}}'",unquote)
    unquote = re.sub(r"}\", \"{", r"},{", unquote)

    unquote = re.sub(r"\"components\"", r"components", unquote)
    unquote = re.sub(r"\"count\"", r"count", unquote)


    # Remove backslashes before the separators (',')
    deckDictString = unescape_string(unquote)
    escaped_string = deckDictString.encode('unicode_escape').decode()
    escaped_string = re.sub(r"([a-zA-Z])'", r"\1\\'", escaped_string)
    escaped_string = re.sub(r"}}\"]}}}", r"}}]}}}", escaped_string)
    escaped_string = re.sub(r"\[\"{id:", r"[{id:", escaped_string)
    escaped_string = re.sub(r"\\\\'", r"\\'", escaped_string)

    escaped_string = escaped_string.replace('"{"', '\'{"')
    escaped_string = escaped_string.replace('"}"', '"}\'')
    escaped_string = escaped_string.replace('"[{"', '\'[{"')
    escaped_string = escaped_string.replace('}]"', "}]'")
    escaped_string = escaped_string.replace('"lore": \'[{', '"lore": [\'{')
    escaped_string = escaped_string.replace('"lore": [""]', '"lore": []')

    return escaped_string


def construct_deck_files(total_files, total_decks) -> None:
    total_files += 1
    paths = ["decks/function/decks1"]
    for i in range(1, total_decks + 1):
        base_path = paths[0][:-1]
        new_path = base_path + f"{+ i}"
        if new_path not in paths:
            paths.append(new_path)
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    for i in range(1, total_files):
        print(f"Creating decks for set {i}")
        decks = deck(total_decks)
    
        link_template = "execute as @p[x=-52711,y=113,z=108732,limit=1,sort=nearest] run function gen3_decks:decks%s/"
        links = []
        for index in range(1, total_decks):
            links.append(link_template % int(index + 1))

        for n, path in enumerate(paths):
            deck_name = "Deck" + str(n + 1)
            file_path = path + f"/{i}"
            file_path = file_path + ".mcfunction"
            with open(file_path, "w") as file:
                file.write(data_strings["data_modify_dict"] % "librarian" + decks[deck_name] + "\n")
                if n < len(paths) - 1:
                    file.write(links[n] + str(i))
            print(f"    Created deck {n + 1}")
    
    replace_villager_trades(total_files, profession='librarian')


def construct_booster_files(total_files, booster_amount) -> None:
    total_files += 1
    directory = "boosters/function/"
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    
    for i in range(1, total_files):
        promos = promo()
        boosters = booster(booster_amount)

        path = f'{directory}{i}.mcfunction'

        with open(path, 'w') as file:
            file.write(promos + '\n')
            for b in boosters:
                file.write(b + '\n')
        print(f"Successfully created booster file {i}")
    
    replace_villager_trades(total_files, profession='cartographer')


def replace_villager_trades(num_files: int, profession: str) -> None:
    profession_dict = {
        'librarian': 'decks',
        'cartographer': 'boosters'
    }
    function_dict = {
        'min': 'scoreboard players set $min random 1',
        'max': f'scoreboard players set $max random {num_files - 1}',
        'function': 'function random:uniform',
        'execute': f'execute as @p[x=-52711,y=113,z=108732,limit=1,sort=nearest] run data modify entity @e[type=villager,limit=1,sort=nearest,nbt={{VillagerData:{{profession:"minecraft:{profession}"}}}}] Offers.Recipes set value []'
    }
    function_path = f"gen3_{profession_dict[profession]}:"
    path = f"expansions/function/"
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + f'replace_villager_{profession_dict[profession]}_gen3.mcfunction'
    with open(path, 'w') as file:
        for function in function_dict.values():
            file.write(function + '\n')
        file.write('\n')
        for n in range(1, num_files):
            function_path_dict = {'librarian': f'decks1/{n}', 'cartographer': str(n)}
            function_path_num = function_path + function_path_dict[profession]
            line = f'execute if score $out random matches {n} run function {function_path_num}'
            file.write(line + '\n')


if __name__ == "__main__":
    directory = 'decks'
    if os.path.exists(directory):
        shutil.rmtree(directory)
    
    # Populate pokemon cards
    populate_villager_data()
    populate_energy_cards()
    
    card_weights = sort_card_weights()
    trainer_weights = sort_trainer_weights()

    construct_deck_files(300, 6)
    construct_booster_files(200, 5)
