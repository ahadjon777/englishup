from django.core.management.base import BaseCommand

from lessons.models import Level, Lesson
from vocabulary.models import Word
from quiz.models import Quiz, Question, Choice
from users.models import Sticker


LEVELS = [
    ('A1', 'Beginner A1', 'Boshlang\'ich daraja', 1, '🌱'),
    ('A2', 'Elementary A2', 'Elementar daraja', 2, '🌿'),
    ('B1', 'Pre-Intermediate B1', 'O\'rta oldi daraja', 3, '🌳'),
    ('B2', 'Intermediate B2', 'O\'rta daraja', 4, '⭐'),
    ('C1', 'Upper-Intermediate C1', 'Yuqori o\'rta daraja', 5, '🚀'),
    ('C2', 'Advanced C2', 'Yuqori daraja', 6, '🏆'),
]

A1_WORDS = [
    ('apple', 'olma', 'I eat an apple every day.', '🍎'),
    ('book', 'kitob', 'She reads a book.', '📖'),
    ('water', 'suv', 'I drink water.', '💧'),
    ('house', 'uy', 'This is my house.', '🏠'),
    ('friend', 'do\'st', 'He is my best friend.', '🧑‍🤝‍🧑'),
    ('school', 'maktab', 'I go to school.', '🏫'),
    ('teacher', 'o\'qituvchi', 'My teacher is kind.', '👩‍🏫'),
    ('happy', 'baxtli', 'I am happy today.', '😊'),
    ('car', 'mashina', 'My father has a car.', '🚗'),
    ('food', 'ovqat', 'The food is delicious.', '🍽️'),
    ('dog', 'it', 'The dog is running.', '🐶'),
    ('cat', 'mushuk', 'The cat is sleeping.', '🐱'),
    ('day', 'kun', 'Have a nice day!', '☀️'),
    ('night', 'tun', 'Good night!', '🌙'),
    ('family', 'oila', 'I love my family.', '👨‍👩‍👧‍👦'),
]

A2_WORDS = [
    ('travel', 'sayohat qilmoq', 'I like to travel.', '✈️'),
    ('weather', 'ob-havo', 'The weather is nice.', '🌤️'),
    ('money', 'pul', 'I need some money.', '💰'),
    ('language', 'til', 'English is a global language.', '🗣️'),
    ('important', 'muhim', 'This is very important.', '❗'),
    ('beautiful', 'chiroyli', 'What a beautiful view!', '🌸'),
    ('difficult', 'qiyin', 'This task is difficult.', '🧩'),
    ('remember', 'eslamoq', 'I remember you.', '🧠'),
]

QUIZZES = [
    {
        'title': 'Present Simple Basics',
        'level': 'A1',
        'reward': 20,
        'questions': [
            ('She ___ to school every day.', ['go', 'goes', 'going', 'gone'], 'goes'),
            ('I ___ coffee in the morning.', ['drinks', 'drinking', 'drink', 'drank'], 'drink'),
            ('They ___ football on Sundays.', ['plays', 'play', 'playing', 'played'], 'play'),
            ('He ___ not like fish.', ['do', 'does', 'is', 'are'], 'does'),
            ('___ you speak English?', ['Does', 'Is', 'Do', 'Are'], 'Do'),
            ('My sister ___ in London.', ['live', 'lives', 'living', 'lived'], 'lives'),
            ('We ___ TV in the evening.', ['watches', 'watching', 'watch', 'watched'], 'watch'),
            ('The sun ___ in the east.', ['rise', 'rises', 'rising', 'rose'], 'rises'),
        ],
    },
    {
        'title': 'Articles: a / an / the',
        'level': 'A1',
        'reward': 20,
        'questions': [
            ('I have ___ apple.', ['a', 'an', 'the', '-'], 'an'),
            ('She is ___ teacher.', ['an', 'the', 'a', '-'], 'a'),
            ('___ sun is very bright today.', ['A', 'An', 'The', '-'], 'The'),
            ('He bought ___ umbrella.', ['a', 'an', 'the', '-'], 'an'),
            ('This is ___ best film ever.', ['a', 'an', 'the', '-'], 'the'),
            ('I need ___ pen to write.', ['a', 'an', 'the', '-'], 'a'),
        ],
    },
    {
        'title': 'Past Simple',
        'level': 'A2',
        'reward': 25,
        'questions': [
            ('I ___ to the cinema yesterday.', ['go', 'went', 'gone', 'going'], 'went'),
            ('She ___ her homework last night.', ['do', 'did', 'does', 'done'], 'did'),
            ('They ___ happy at the party.', ['was', 'were', 'are', 'is'], 'were'),
            ('We ___ a great movie.', ['watch', 'watches', 'watched', 'watching'], 'watched'),
            ('He ___ not come to school.', ['do', 'did', 'does', 'is'], 'did'),
            ('I ___ born in 2005.', ['was', 'were', 'am', 'is'], 'was'),
        ],
    },
]

STICKERS = [
    ('Yulduzcha', '⭐', 'Yorqin yulduz', 50),
    ('Olov', '🔥', 'Streak ramzi', 80),
    ('Toj', '👑', 'Chempion toji', 150),
    ('Raketa', '🚀', 'Tez o\'sish', 120),
    ('Brilliant', '💎', 'Noyob stiker', 300),
    ('Trofey', '🏆', 'G\'olib uchun', 250),
    ('Kamalak', '🌈', 'Rang-barang', 90),
    ('Yurak', '❤️', 'Sevimli', 60),
]


class Command(BaseCommand):
    help = "EnglishUp uchun namunaviy ma'lumotlar (daraja, dars, so'z, quiz, stiker) qo'shadi"

    def handle(self, *args, **options):
        # Levels
        levels = {}
        for code, name, desc, order, icon in LEVELS:
            level, _ = Level.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': desc, 'order': order, 'icon': icon},
            )
            levels[code] = level
        self.stdout.write(self.style.SUCCESS(f"Darajalar: {len(levels)} ta tayyor"))

        # Lessons (A1 namuna)
        a1 = levels['A1']
        lesson, _ = Lesson.objects.get_or_create(
            level=a1, title='Present Simple Tense',
            defaults={
                'description': 'Hozirgi oddiy zamon: kundalik harakatlar uchun.',
                'grammar_explanation': (
                    "Present Simple kundalik, takrorlanuvchi harakatlar va umumiy haqiqatlar uchun ishlatiladi.\n\n"
                    "Tasdiq: I/You/We/They + verb | He/She/It + verb + s/es\n"
                    "Inkor: don't / doesn't + verb\n"
                    "Savol: Do / Does + subject + verb?"
                ),
                'examples': 'I work every day.\nShe likes coffee.\nThey play football.\nHe does not eat meat.\nDo you speak English?',
                'youtube_url': 'https://www.youtube.com/watch?v=hSU3lUg8Z2g',
                'order': 1,
            },
        )
        Lesson.objects.get_or_create(
            level=a1, title='Articles: a, an, the',
            defaults={
                'description': 'Aniq va noaniq artikllar.',
                'grammar_explanation': (
                    "'a' va 'an' - noaniq artikllar (bitta narsa).\n"
                    "'a' undosh tovush oldidan, 'an' unli tovush oldidan keladi.\n"
                    "'the' - aniq artikl (ma'lum narsa)."
                ),
                'examples': 'I have a book.\nShe is an engineer.\nThe sun is hot.',
                'order': 2,
            },
        )
        self.stdout.write(self.style.SUCCESS("A1 darslar tayyor"))

        # Words
        word_count = 0
        for eng, uz, ex, emoji in A1_WORDS:
            _, created = Word.objects.get_or_create(
                english=eng, defaults={'uzbek': uz, 'example': ex, 'emoji': emoji, 'level': levels['A1']}
            )
            word_count += 1 if created else 0
        for eng, uz, ex, emoji in A2_WORDS:
            _, created = Word.objects.get_or_create(
                english=eng, defaults={'uzbek': uz, 'example': ex, 'emoji': emoji, 'level': levels['A2']}
            )
            word_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"So'zlar: {word_count} ta yangi qo'shildi"))

        # Quizzes
        quiz_count = 0
        for qz in QUIZZES:
            if Quiz.objects.filter(title=qz['title']).exists():
                continue
            quiz = Quiz.objects.create(
                title=qz['title'],
                description=f"{qz['title']} bo'yicha test",
                level=levels.get(qz['level']),
                coin_reward=qz['reward'],
            )
            for i, (text, options, answer) in enumerate(qz['questions']):
                question = Question.objects.create(quiz=quiz, text=text, order=i)
                for opt in options:
                    Choice.objects.create(question=question, text=opt, is_correct=(opt == answer))
            quiz_count += 1
        self.stdout.write(self.style.SUCCESS(f"Quizlar: {quiz_count} ta yangi qo'shildi"))

        # Stickers
        sticker_count = 0
        for i, (name, emoji, desc, price) in enumerate(STICKERS):
            _, created = Sticker.objects.get_or_create(
                name=name, defaults={'emoji': emoji, 'description': desc, 'price': price, 'order': i}
            )
            sticker_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"Stikerlar: {sticker_count} ta yangi qo'shildi"))

        self.stdout.write(self.style.SUCCESS("\nTayyor! Namunaviy ma'lumotlar muvaffaqiyatli qo'shildi."))
