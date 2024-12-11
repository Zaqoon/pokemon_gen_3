import os
import shutil
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('USER')


def export_decks(path: str):
    print('Exporting decks...')
    path = f'{path}/gen3_decks/function'
    origin_path = 'decks/function'
    folder_list = os.listdir(origin_path)
    for folder in folder_list:
        destination = f'{path}/{folder}'
        if os.path.exists(destination):
            shutil.rmtree(destination)
        # Move folder
        source = f'{origin_path}/{folder}'
        destination_path = f'{path}/{folder}'
        copy_paste_folder(source, destination_path)


def export_boosters(path: str):
    print('Exporting boosters...')
    destination = f'{path}/gen3_boosters/function'
    source = 'boosters/function'
    # Delete existing folder
    if os.path.exists(destination):
        shutil.rmtree(destination)
    # Paste boosters
    copy_paste_folder(source, f'{path}/gen3_boosters/function')


def export_expansion_files(path: str):
    print('Exporting expansion files...')
    path = f'{path}/expansions/function'
    source = 'expansions/function'
    for file in os.listdir(source):
        source_file = os.path.join(source, file)
        destination = os.path.join(path, file)

        copy_paste_file(source_file, destination)


def export_functions(path: str):
    print('Exporting functions...')
    source = 'functions'
    for set_id in os.listdir(source):
        dest = f'{path}/{set_id}'
        if os.path.exists(dest):
            shutil.rmtree(dest)

        # Paste folder
        s = f'{source}/{set_id}'
        copy_paste_folder(s, dest)


def copy_paste_file(source: str, destination: str):
    if os.path.isfile(source):
        shutil.copy2(source, destination)
        print(f'    Successfully transferred {source} to {destination}.')
    else:
        print(f'    {source} is not a file.')


def copy_paste_folder(source: str, destination: str):
    try:
        shutil.copytree(source, destination)
        print(f'    Successfully transferred {source} to {destination}.')
    except FileExistsError:
        print(f'    {destination} already exists.')
    except Exception as e:
        print(f'    An error occurred: {e}')


if __name__ == '__main__':
    destination = f'C:/Users/{USER}/AppData/Roaming/.minecraft/saves/Naraka/datapacks/tcg/data'
    export_decks(destination)
    export_boosters(destination)
    export_expansion_files(destination)
    export_functions(destination)
