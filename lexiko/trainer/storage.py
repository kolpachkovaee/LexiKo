"""JSON-based storage for LexiKo flashcards."""
import json
import os
import uuid
from datetime import datetime
from django.conf import settings

CARDS_FILE = os.path.join(settings.DATA_DIR, 'cards.json')
PROGRESS_FILE = os.path.join(settings.DATA_DIR, 'progress.json')


def _read_json(path):
    """Read JSON file; return empty dict if missing or corrupt."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return {}


def _write_json(path, data):
    """Write data to JSON file, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def get_all_cards():
    """Return all cards sorted by word."""
    data = _read_json(CARDS_FILE)
    cards = list(data.values())
    cards.sort(key=lambda c: c.get('word', '').lower())
    return cards


def get_user_cards(username):
    """Return cards belonging to a specific user."""
    return [c for c in get_all_cards() if c.get('owner') == username]


def get_card_by_id(card_id):
    """Return a single card by UUID, or None if not found."""
    data = _read_json(CARDS_FILE)
    return data.get(card_id)


def save_card(card):
    """Insert or update a card; return its id."""
    data = _read_json(CARDS_FILE)
    card_id = card.get('id') or str(uuid.uuid4())
    card['id'] = card_id
    card.setdefault('created_at', datetime.now().isoformat(timespec='seconds'))
    card['updated_at'] = datetime.now().isoformat(timespec='seconds')
    data[card_id] = card
    _write_json(CARDS_FILE, data)
    return card_id


def delete_card(card_id, username):
    """Delete a card if it belongs to username; return True on success."""
    data = _read_json(CARDS_FILE)
    card = data.get(card_id)
    if card and card.get('owner') == username:
        del data[card_id]
        _write_json(CARDS_FILE, data)
        return True
    return False


def get_user_progress(username):
    """Return progress dict for a user: {card_id: {correct, wrong}}."""
    data = _read_json(PROGRESS_FILE)
    return data.get(username, {})


def record_answer(username, card_id, correct):
    """Increment correct or wrong counter for a user/card pair."""
    data = _read_json(PROGRESS_FILE)
    user_data = data.setdefault(username, {})
    entry = user_data.setdefault(card_id, {'correct': 0, 'wrong': 0})
    if correct:
        entry['correct'] += 1
    else:
        entry['wrong'] += 1
    _write_json(PROGRESS_FILE, data)


def get_stats(username):
    """Aggregate statistics for the stats page."""
    cards = get_user_cards(username)
    progress = get_user_progress(username)

    total_cards = len(cards)
    total_correct = sum(v['correct'] for v in progress.values())
    total_wrong = sum(v['wrong'] for v in progress.values())
    total_answers = total_correct + total_wrong
    accuracy = round(total_correct / total_answers * 100) if total_answers else 0
    learned = sum(
        1 for v in progress.values()
        if v['correct'] >= 3 and v['correct'] > v['wrong']
    )

    return {
        'total_cards': total_cards,
        'total_correct': total_correct,
        'total_wrong': total_wrong,
        'total_answers': total_answers,
        'accuracy': accuracy,
        'learned': learned,
    }
