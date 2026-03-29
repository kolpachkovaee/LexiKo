"""Forms for LexiKo application."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

LEVEL_CHOICES = [
    ('', '— уровень —'),
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),
    ('C1', 'C1'),
    ('C2', 'C2'),
]

CATEGORY_CHOICES = [
    ('', '— категория —'),
    ('adjectives', 'Прилагательные'),
    ('nouns', 'Существительные'),
    ('verbs', 'Глаголы'),
    ('phrases', 'Фразы'),
    ('other', 'Другое'),
]


class CardForm(forms.Form):
    """Form for adding or editing a single flashcard."""

    word = forms.CharField(
        label='Английское слово',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Например: resilient',
            'autocomplete': 'off',
        }),
        error_messages={'required': 'Введите английское слово.'},
    )
    translation = forms.CharField(
        label='Перевод',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Например: стойкий',
        }),
        error_messages={'required': 'Введите перевод.'},
    )
    example = forms.CharField(
        label='Пример предложения',
        max_length=400,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 2,
            'placeholder': 'Необязательно: She is very resilient.',
        }),
    )
    level = forms.ChoiceField(
        label='Уровень',
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        error_messages={'required': 'Выберите уровень.'},
    )
    category = forms.ChoiceField(
        label='Категория',
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        error_messages={'required': 'Выберите категорию.'},
    )

    def clean_word(self):
        """Validate that word contains only Latin characters."""
        word = self.cleaned_data['word'].strip()
        if not word:
            raise forms.ValidationError('Слово не может быть пустым.')
        if not all(c.isalpha() or c in " -'" for c in word):
            raise forms.ValidationError(
                'Слово должно содержать только латинские буквы.'
            )
        return word.lower()

    def clean_level(self):
        """Validate level is selected."""
        level = self.cleaned_data['level']
        if not level:
            raise forms.ValidationError('Выберите уровень сложности.')
        return level

    def clean_category(self):
        """Validate category is selected."""
        category = self.cleaned_data['category']
        if not category:
            raise forms.ValidationError('Выберите категорию.')
        return category


class ImportTextForm(forms.Form):
    """Form for bulk import via pasted text (Quizlet-style)."""

    text = forms.CharField(
        label='Вставьте слова',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 10,
            'placeholder': (
                'resilient\tстойкий\n'
                'eloquent\tкрасноречивый\n'
                'candor\tискренность\n\n'
                'Формат: слово [Tab] перевод, каждая пара на новой строке.'
            ),
        }),
        error_messages={'required': 'Вставьте хотя бы одну пару слов.'},
    )
    level = forms.ChoiceField(
        label='Уровень для всех слов',
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
    category = forms.ChoiceField(
        label='Категория для всех слов',
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    def clean_text(self):
        """Parse and validate pasted text into word/translation pairs."""
        raw = self.cleaned_data['text'].strip()
        if not raw:
            raise forms.ValidationError('Вставьте хотя бы одну пару слов.')

        pairs = []
        errors = []
        for i, line in enumerate(raw.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                parts = line.split('  ')
            if len(parts) < 2:
                errors.append(f'Строка {i}: нет разделителя (Tab) между словом и переводом.')
                continue
            word = parts[0].strip().lower()
            translation = parts[1].strip()
            if not word or not translation:
                errors.append(f'Строка {i}: слово или перевод пустые.')
                continue
            pairs.append({'word': word, 'translation': translation})

        if errors:
            raise forms.ValidationError(errors)
        if not pairs:
            raise forms.ValidationError('Не удалось распознать ни одной пары.')
        return pairs

    def clean_level(self):
        """Validate level is selected."""
        level = self.cleaned_data['level']
        if not level:
            raise forms.ValidationError('Выберите уровень.')
        return level

    def clean_category(self):
        """Validate category is selected."""
        category = self.cleaned_data['category']
        if not category:
            raise forms.ValidationError('Выберите категорию.')
        return category


class ImportCsvForm(forms.Form):
    """Form for bulk import via CSV file upload."""

    csv_file = forms.FileField(
        label='CSV-файл',
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.csv'}),
        error_messages={'required': 'Выберите CSV-файл.'},
    )
    level = forms.ChoiceField(
        label='Уровень для всех слов',
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
    category = forms.ChoiceField(
        label='Категория для всех слов',
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    def clean_csv_file(self):
        """Validate and parse uploaded CSV file."""
        f = self.cleaned_data['csv_file']
        if not f.name.endswith('.csv'):
            raise forms.ValidationError('Файл должен быть в формате .csv')
        try:
            content = f.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            raise forms.ValidationError('Не удалось прочитать файл. Убедитесь, что кодировка UTF-8.')

        pairs = []
        errors = []
        for i, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) < 2:
                errors.append(f'Строка {i}: нет запятой между словом и переводом.')
                continue
            word = parts[0].strip().strip('"').lower()
            translation = parts[1].strip().strip('"')
            if not word or not translation:
                continue
            pairs.append({'word': word, 'translation': translation})

        if errors:
            raise forms.ValidationError(errors)
        if not pairs:
            raise forms.ValidationError('В файле не найдено ни одной пары слов.')
        return pairs

    def clean_level(self):
        """Validate level is selected."""
        level = self.cleaned_data['level']
        if not level:
            raise forms.ValidationError('Выберите уровень.')
        return level

    def clean_category(self):
        """Validate category is selected."""
        category = self.cleaned_data['category']
        if not category:
            raise forms.ValidationError('Выберите категорию.')
        return category


class RegisterForm(UserCreationForm):
    """Extended registration form with email."""

    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com',
        }),
        error_messages={
            'required': 'Введите email.',
            'invalid': 'Введите корректный email.',
        },
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """Attach CSS classes to auth fields."""
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Придумайте логин',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Пароль (минимум 8 символов)',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Повторите пароль',
        })

    def clean_email(self):
        """Check email is not already registered."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован.')
        return email
