"""Views for LexiKo trainer application."""
import json
import random

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import storage
from .forms import CardForm, ImportCsvForm, ImportTextForm, RegisterForm


def index(request):
    """Home page with overview and quick stats."""
    context = {}
    if request.user.is_authenticated:
        context['stats'] = storage.get_stats(request.user.username)
        context['recent_cards'] = storage.get_user_cards(request.user.username)[:4]
    return render(request, 'trainer/index.html', context)


def register(request):
    """Registration page with validated form."""
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! 🌸')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def card_list(request):
    """Page: list of user flashcards with filter."""
    level_filter = request.GET.get('level', '')
    category_filter = request.GET.get('category', '')
    cards = storage.get_user_cards(request.user.username)

    if level_filter:
        cards = [c for c in cards if c.get('level') == level_filter]
    if category_filter:
        cards = [c for c in cards if c.get('category') == category_filter]

    progress = storage.get_user_progress(request.user.username)
    for card in cards:
        prog = progress.get(card['id'], {'correct': 0, 'wrong': 0})
        total = prog['correct'] + prog['wrong']
        card['accuracy'] = round(prog['correct'] / total * 100) if total else None

    return render(request, 'trainer/card_list.html', {
        'cards': cards,
        'level_filter': level_filter,
        'category_filter': category_filter,
    })


@login_required
def card_add(request):
    """Page: form to add a new flashcard."""
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = {
                'word': form.cleaned_data['word'],
                'translation': form.cleaned_data['translation'],
                'example': form.cleaned_data.get('example', ''),
                'level': form.cleaned_data['level'],
                'category': form.cleaned_data['category'],
                'owner': request.user.username,
                'drawing_svg': '',
            }
            storage.save_card(card)
            messages.success(request, f'Карточка «{card["word"]}» добавлена! 🌿')
            return redirect('card_list')
    else:
        form = CardForm()
    return render(request, 'trainer/card_form.html', {'form': form, 'action': 'Добавить'})


@login_required
def card_edit(request, card_id):
    """Page: form to edit an existing flashcard."""
    card = storage.get_card_by_id(card_id)
    if not card or card.get('owner') != request.user.username:
        messages.error(request, 'Карточка не найдена.')
        return redirect('card_list')

    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card.update({
                'word': form.cleaned_data['word'],
                'translation': form.cleaned_data['translation'],
                'example': form.cleaned_data.get('example', ''),
                'level': form.cleaned_data['level'],
                'category': form.cleaned_data['category'],
            })
            storage.save_card(card)
            messages.success(request, f'Карточка «{card["word"]}» обновлена!')
            return redirect('card_list')
    else:
        form = CardForm(initial=card)
    return render(request, 'trainer/card_form.html', {
        'form': form,
        'action': 'Сохранить',
        'card': card,
    })


@login_required
def card_delete(request, card_id):
    """Delete a card (POST only)."""
    if request.method == 'POST':
        deleted = storage.delete_card(card_id, request.user.username)
        if deleted:
            messages.success(request, 'Карточка удалена.')
        else:
            messages.error(request, 'Не удалось удалить карточку.')
    return redirect('card_list')


@login_required
def card_detail(request, card_id):
    """Page: full card view with canvas drawing."""
    card = storage.get_card_by_id(card_id)
    if not card or card.get('owner') != request.user.username:
        messages.error(request, 'Карточка не найдена.')
        return redirect('card_list')
    return render(request, 'trainer/card_detail.html', {'card': card})


@login_required
def import_cards(request):
    """Page: import cards via text paste or CSV upload."""
    text_form = ImportTextForm()
    csv_form = ImportCsvForm()

    if request.method == 'POST':
        import_type = request.POST.get('import_type', 'text')

        if import_type == 'text':
            text_form = ImportTextForm(request.POST)
            if text_form.is_valid():
                pairs = text_form.cleaned_data['text']
                level = text_form.cleaned_data['level']
                category = text_form.cleaned_data['category']
                count = _save_imported_pairs(pairs, level, category, request.user.username)
                messages.success(request, f'Импортировано {count} карточек! 🌸')
                return redirect('card_list')

        elif import_type == 'csv':
            csv_form = ImportCsvForm(request.POST, request.FILES)
            if csv_form.is_valid():
                pairs = csv_form.cleaned_data['csv_file']
                level = csv_form.cleaned_data['level']
                category = csv_form.cleaned_data['category']
                count = _save_imported_pairs(pairs, level, category, request.user.username)
                messages.success(request, f'Импортировано {count} карточек из CSV! 🌿')
                return redirect('card_list')

    return render(request, 'trainer/import.html', {
        'text_form': text_form,
        'csv_form': csv_form,
    })


def _save_imported_pairs(pairs, level, category, username):
    """Save a list of word/translation pairs as cards. Return count saved."""
    count = 0
    for pair in pairs:
        card = {
            'word': pair['word'],
            'translation': pair['translation'],
            'example': '',
            'level': level,
            'category': category,
            'owner': username,
            'drawing_svg': '',
        }
        storage.save_card(card)
        count += 1
    return count


@login_required
def study(request):
    """Page: flip-card study mode."""
    cards = storage.get_user_cards(request.user.username)
    if not cards:
        messages.info(request, 'Сначала добавьте хотя бы одну карточку.')
        return redirect('card_add')
    return render(request, 'trainer/study.html', {'cards_json': json.dumps(cards)})


@login_required
def quiz(request):
    """Page: multiple-choice quiz."""
    cards = storage.get_user_cards(request.user.username)
    if len(cards) < 4:
        messages.info(request, 'Для квиза нужно минимум 4 карточки.')
        return redirect('card_add')
    return render(request, 'trainer/quiz.html', {'cards_json': json.dumps(cards)})


@login_required
def stats(request):
    """Page: learning progress statistics."""
    user_stats = storage.get_stats(request.user.username)
    cards = storage.get_user_cards(request.user.username)
    progress = storage.get_user_progress(request.user.username)

    card_details = []
    for card in cards:
        prog = progress.get(card['id'], {'correct': 0, 'wrong': 0})
        total = prog['correct'] + prog['wrong']
        card_details.append({
            'word': card['word'],
            'translation': card['translation'],
            'correct': prog['correct'],
            'wrong': prog['wrong'],
            'accuracy': round(prog['correct'] / total * 100) if total else 0,
            'attempts': total,
        })
    card_details.sort(key=lambda x: x['accuracy'])

    return render(request, 'trainer/stats.html', {
        'stats': user_stats,
        'card_details': card_details,
    })


@login_required
@require_POST
def api_record_answer(request):
    """AJAX: record quiz or study answer."""
    try:
        data = json.loads(request.body)
        card_id = data['card_id']
        correct = bool(data['correct'])
        storage.record_answer(request.user.username, card_id, correct)
        return JsonResponse({'ok': True})
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'Invalid data'}, status=400)


@login_required
@require_POST
def api_save_drawing(request, card_id):
    """AJAX: save canvas drawing SVG data to card."""
    card = storage.get_card_by_id(card_id)
    if not card or card.get('owner') != request.user.username:
        return JsonResponse({'ok': False, 'error': 'Not found'}, status=404)
    try:
        data = json.loads(request.body)
        card['drawing_svg'] = data.get('svg_data', '')
        storage.save_card(card)
        return JsonResponse({'ok': True})
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'error': 'Invalid data'}, status=400)
