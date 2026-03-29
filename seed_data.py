"""Загрузка тестовых карточек. Запуск: python seed_data.py"""
import json
import os
import uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'cards.json')
DEMO_USER = 'demo'

WORDS = [
    ('resilient',    'стойкий',          'She is resilient in difficult times.',        'B2', 'adjectives'),
    ('eloquent',     'красноречивый',    'The eloquent speaker moved everyone.',        'B2', 'adjectives'),
    ('perseverance', 'настойчивость',    'Perseverance leads to success.',              'B1', 'nouns'),
    ('candor',       'искренность',      'I appreciate your candor.',                   'C1', 'nouns'),
    ('meticulous',   'дотошный',         'She is meticulous about details.',            'C1', 'adjectives'),
    ('diligent',     'прилежный',        'A diligent student does homework.',           'B1', 'adjectives'),
    ('alleviate',    'облегчать',        'This will alleviate the pain.',               'B2', 'verbs'),
    ('nuance',       'нюанс',            'Poetry is full of nuance.',                   'B2', 'nouns'),
    ('tenacious',    'упорный',          'He is tenacious in his goals.',               'C1', 'adjectives'),
    ('gratitude',    'благодарность',    'She expressed gratitude for the help.',       'A2', 'nouns'),
]

os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {}

added = 0
for word, translation, example, level, category in WORDS:
    card_id = str(uuid.uuid4())
    data[card_id] = {
        'id': card_id,
        'word': word,
        'translation': translation,
        'example': example,
        'level': level,
        'category': category,
        'owner': DEMO_USER,
        'drawing_svg': '',
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'updated_at': datetime.now().isoformat(timespec='seconds'),
    }
    added += 1

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Добавлено {added} карточек для пользователя «{DEMO_USER}».')
