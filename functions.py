import os
import shutil
from typing import List

target_set_list = ["ex1", "ex2", "ex3", "ex4", "ex5", "ex6", "ex7", "ex8",
                   "ex9", "ex10", "ex11", "ex12", "ex13", "ex14", "ex15", "ex16"]

file_directory = 'functions'
if not os.path.exists(file_directory):
    os.makedirs(file_directory)

pull_rate_dict = {
    "ex1": {"Common": 4, "Uncommon": 2, "Reverse": 1, "Rare": 1, "Premium": 1},
    "ex2": {"Common": 4, "Uncommon": 2, "Reverse": 1, "Rare": 1, "Premium": 1},
    "ex3": {"Common": 4, "Uncommon": 2, "Reverse": 1, "Rare": 1, "Premium": 1},
    "ex4": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex5": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex6": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex7": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex8": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex9": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex10": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex11": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex12": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex13": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex14": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex15": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
    "ex16": {"Common": 5, "Uncommon": 2, "Reverse": 1, "Rare": 0, "Premium": 1},
}

booster_score = {
    "ex1": 100, "ex2": 200, "ex3": 300, "ex4": 400, "ex5": 500, "ex6": 600, "ex7": 700, "ex8": 800, 
    "ex9": 900, "ex10": 1000, "ex11": 1100, "ex12": 1200, "ex13": 1300, "ex14": 1400, "ex15": 1500, "ex16": 1600,
    "np": 1700
}


template = {
    "set_score": "scoreboard players set @s booster %s",
    "add_score": "scoreboard players add @a[scores={booster=%s}] booster 1",
    "spawn_loot_table": "execute as @a[scores={booster=%s}] at @s run loot spawn ~ ~ ~ loot tcg:%s/%s",
    "playsound": "execute as @s run playsound pokesound.booster_pack_open master @s ~ ~ ~ 10 1",
    "clear_booster": "execute as @s if items entity @s weapon.* minecraft:carrot_on_a_stick[custom_data={%s}] run clear @s minecraft:carrot_on_a_stick[custom_data={%s}] 1",
    "reset_score": "scoreboard players reset @a[scores={booster=%s}] booster",
    "que_next_card": "execute as @a[scores={booster=%s}] at @s run schedule function %s:%s 5t",
    "flip_card": "execute as @a[scores={right_click_carrot=1..}] at @s if items entity @s weapon.* minecraft:carrot_on_a_stick[custom_data={%s}] run function %s:%s",
    "flipped_card": "execute as @s run loot give @s loot tcg:%s/%s",
    "flip_sound": "playsound item.dye.use master @s ~ ~ ~ 1 1 1"
}


def insert_functions(directory:str, rarity:str, pull_rate:int, start:int, booster:int, lines:List[str]) -> tuple:
    for n in range(start, pull_rate):
        file_directory = f"{directory}/{n}.mcfunction"
        with open(file_directory, "w") as file:
            lines.append(template["add_score"] % booster)
            booster += 1
            lines.append(template["spawn_loot_table"] % (booster, set, rarity.lower()))
            lines.append(template["que_next_card"] % (booster, set, n + 1))
            mcfunction = "\n".join(lines)
            file.write(mcfunction)
            lines = []
    
    return lines, booster


flip_card_lines = []
for set in target_set_list:
    directory = f"{file_directory}/{set}/function"
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    booster = booster_score[set]
    custom_data = set.replace('ex', 'ex:')
    lines = []
    lines.append(template["set_score"] % booster_score[set])
    lines.append(template["playsound"])
    lines.append(template["clear_booster"] % (custom_data, custom_data))

    # Common cards
    pull_rate = pull_rate_dict[set]["Common"]
    start = 0
    lines, booster = insert_functions(directory=directory, rarity="Common", start=start, pull_rate=pull_rate, booster=booster, lines=lines)

    pull_rate = pull_rate_dict[set]["Uncommon"] + pull_rate_dict[set]["Common"]
    start = pull_rate_dict[set]["Common"]
    lines, booster = insert_functions(directory=directory, rarity="Uncommon", start=start, pull_rate=pull_rate, booster=booster, lines=lines)

    total_functions = pull_rate_dict[set]["Common"] + pull_rate_dict[set]["Uncommon"]

    with open(f"{directory}/{total_functions}.mcfunction", "w") as file:
        lines.append(template["add_score"] % booster)
        booster += 1
        lines.append(template["spawn_loot_table"] % (booster, set, "reverse"))
        lines.append(template["que_next_card"] % (booster, set, total_functions + 1))
        mcfunction = "\n".join(lines)
        file.write(mcfunction)
    lines = []
    total_functions += pull_rate_dict[set]["Reverse"]
    if pull_rate_dict[set]["Rare"] > 0:
        with open(f"{directory}/{total_functions}.mcfunction", "w") as file:
            lines.append(template["add_score"] % booster)
            booster += 1
            lines.append(template["spawn_loot_table"] % (booster, set, "rare"))
            lines.append(template["que_next_card"] % (booster, set, total_functions + 1))
            mcfunction = "\n".join(lines)
            file.write(mcfunction)
    lines = []
    total_functions += pull_rate_dict[set]["Rare"]
    with open(f"{directory}/{total_functions}.mcfunction", "w") as file:
        lines.append(template["add_score"] % booster)
        booster += 1
        lines.append(template["spawn_loot_table"] % (booster, set, "premium"))
        lines.append(template["reset_score"] % booster)
        mcfunction = "\n".join(lines)
        file.write(mcfunction)
    for card in ["reverse", "premium"]:
        lines = []
        custom_data = f'{set}_{card}_rare:1b'
        flip_card_lines.append(template["flip_card"] % (custom_data, set, card))
        with open(f"{directory}/{card}.mcfunction", "w") as file:
            lines.append(template["clear_booster"] % (custom_data, custom_data))
            lines.append(template["flipped_card"] % (set, f"{card}_rare"))
            lines.append(template["flip_sound"])
            mcfunction = "\n".join(lines)
            file.write(mcfunction)
with open(f"{file_directory}/tick_function.mcfunction", "w") as file:
    mcfunction = "\n".join(flip_card_lines)
    file.write(mcfunction)



# Nintendo Black Star Promos
file_directory = f"C:/Users/Andreas/Desktop/pip_code/tcg_functions"
directory = f"{file_directory}/np/functions"
set = "np"
if os.path.exists(directory):
    shutil.rmtree(directory)
os.makedirs(directory)
booster = booster_score[set]
custom_data = 'np:1'
lines = []
lines.append(template["set_score"] % booster_score[set])
lines.append(template["playsound"])
lines.append(template["clear_booster"] % (custom_data, custom_data))
for n in range(3):
    file_directory = f"{directory}/{n}.mcfunction"
    with open(file_directory, "w") as file:
        lines.append(template["add_score"] % booster)
        booster += 1
        lines.append(template["spawn_loot_table"] % (booster, set, "promos"))
        lines.append(template["que_next_card"] % (booster, set, n + 1))
        mcfunction = "\n".join(lines)
        file.write(mcfunction)
        lines = []