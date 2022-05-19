import json
import random
from pathlib import Path
from config import CHANCE

script_location = Path(__file__).absolute().parent

with open(script_location / 'letters.json', 'r', encoding='utf-8') as f:
    letters = json.load(f)


def randomise(text):
    def __randomise(text_part):
        return ''.join([random.choice(letters[i]) if i in letters and random.random() < CHANCE else i for i in text_part])
    return '<@{user}>'.join([__randomise(i) for i in text.split('{user}')]).replace('\\n', '\n')
