import os
import shutil
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('USER')


def export(path: str):
    origin_path = 'decks/function'
    folder_list = os.listdir(origin_path)
    for folder in folder_list:
        destination = f'{path}/{folder}'
        if os.path.exists(destination):
            shutil.rmtree(destination)
        # Move folder
        source = f'{origin_path}/{folder}'
        copy_paste_folder(source, destination)


def copy_paste_folder(source: str, destination: str):
    try:
        shutil.copytree(source, destination)
    except FileExistsError:
        print(f'{destination} already exists.')
    except Exception as e:
        print(f'An error occurred: {e}')


if __name__ == '__main__':
    destination = f'C:/Users/{USER}/AppData/Roaming/.minecraft/saves/Naraka/datapacks/tcg/data/gen3_decks/function'

