import json
import os


# Caminha e nome do arquivo
CFG_FOLDER = 'database'
CFG_NAME = 'config'
CFG_PATH = os.path.join(CFG_FOLDER, f'{CFG_NAME}.json')


def load_json() -> dict:
    base_cfg_file = {'graham_cfg': {'max_pl': 0, 'max_pvp': 0}}

    # Cria a pasta se não existir
    os.makedirs(CFG_FOLDER, exist_ok=True)
    if not os.path.exists(f'{CFG_PATH}'):
        op = open(f'{CFG_PATH}', 'w+')
        json.dump(base_cfg_file, op)
        op.close()

    with open(f'{CFG_PATH}', 'r') as file:
        cfg = json.load(file)
        file.close()

    return cfg


def write_json(data):
    # Cria a pasta se não existir
    os.makedirs(CFG_FOLDER, exist_ok=True)
    if not os.path.exists(f'{CFG_PATH}'):
        op = open(f'{CFG_PATH}', 'w+')
        json.dump({}, op)
        op.close()

    with open(f'{CFG_PATH}', 'w') as file:
        json.dump(data, file, indent=True, sort_keys=True)
        file.close()
