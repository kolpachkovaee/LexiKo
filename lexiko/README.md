# 🌸 LexiKo — тренажёр английских слов

**Автор:** Елизавета Колпачкова  
**Стек:** Python 3.10+, Django 4.2, JSON-хранилище

Веб-приложение для изучения английских слов с рисованием ассоциаций.  
К каждой карточке можно нарисовать образ прямо в браузере.  
Импорт слов — как в Quizlet: вставь текст или загрузи CSV.

## Страницы

| URL | Что делает |
|-----|-----------|
| `/` | Главная |
| `/cards/` | Список карточек |
| `/cards/add/` | Добавить карточку |
| `/cards/import/` | Импорт как в Quizlet |
| `/cards/<id>/` | Карточка + холст для рисования |
| `/study/` | Режим перелистывания |
| `/quiz/` | Квиз с вариантами ответа |
| `/stats/` | Статистика прогресса |

## Запуск локально

```bash
git clone https://github.com/kolpachkovaee/LexiKo.git
cd LexiKo
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python seed_data.py
python manage.py runserver
```

Открой: **http://127.0.0.1:8000**  
Зарегистрируйся с логином `demo` чтобы увидеть тестовые карточки.
