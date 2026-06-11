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

# ---------------------------------------------------------------------------
# A1 GRAMMAR — 13 ta mavzu (dars)
# ---------------------------------------------------------------------------
A1_GRAMMAR = [
    {
        'title': 'To be (am, is, are)',
        'desc': "\"Bo'lmoq\" fe'li: am / is / are.",
        'grammar': (
            "'to be' fe'li shaxsga qarab o'zgaradi:\n"
            "I + am | He/She/It + is | You/We/They + are\n\n"
            "Tasdiq: I am a student.\n"
            "Inkor: She is not (isn't) happy.\n"
            "Savol: Are you ready?"
        ),
        'examples': "I am a teacher.\nShe is my friend.\nThey are students.\nIt is cold today.\nAre you from Uzbekistan?",
    },
    {
        'title': 'Subject pronouns',
        'desc': "Shaxs olmoshlari: I, you, he, she, it, we, they.",
        'grammar': (
            "Shaxs olmoshlari gap egasi bo'lib keladi:\n"
            "I (men), you (sen/siz), he (u - erkak), she (u - ayol),\n"
            "it (u - narsa/hayvon), we (biz), they (ular)."
        ),
        'examples': "I am happy.\nYou are kind.\nHe is tall.\nShe is a doctor.\nWe are friends.\nThey are here.",
    },
    {
        'title': 'Possessive adjectives',
        'desc': "Egalik sifatlari: my, your, his, her, its, our, their.",
        'grammar': (
            "Egalik sifatlari kimningligini bildiradi:\n"
            "I - my | you - your | he - his | she - her |\n"
            "it - its | we - our | they - their"
        ),
        'examples': "This is my book.\nWhat is your name?\nHis car is new.\nHer dress is red.\nOur house is big.\nTheir dog is small.",
    },
    {
        'title': 'Articles (a, an, the)',
        'desc': "Aniq va noaniq artikllar.",
        'grammar': (
            "'a' / 'an' - noaniq artikl (bitta, noma'lum narsa).\n"
            "'a' undosh tovushdan oldin: a book, a car.\n"
            "'an' unli tovushdan oldin: an apple, an hour.\n"
            "'the' - aniq artikl (ma'lum narsa): the sun, the book on the table."
        ),
        'examples': "I have a pen.\nShe is an engineer.\nThe moon is bright.\nHe bought an umbrella.\nThe car is fast.",
    },
    {
        'title': 'Singular va plural nouns',
        'desc': "Birlik va ko'plik otlar.",
        'grammar': (
            "Ko'plik odatda -s qo'shiladi: book -> books.\n"
            "-s, -ss, -sh, -ch, -x -> -es: box -> boxes.\n"
            "Tartibsiz: man -> men, child -> children, foot -> feet."
        ),
        'examples': "one book - two books\na box - three boxes\none man - two men\na child - many children\none foot - two feet",
    },
    {
        'title': 'There is / There are',
        'desc': "Mavjudlikni bildirish.",
        'grammar': (
            "There is - birlik uchun: There is a book.\n"
            "There are - ko'plik uchun: There are five books.\n"
            "Inkor: There isn't / There aren't.\n"
            "Savol: Is there...? / Are there...?"
        ),
        'examples': "There is a cat in the room.\nThere are three windows.\nThere isn't any milk.\nAre there any students?\nThere is a park near my house.",
    },
    {
        'title': 'Present Simple',
        'desc': "Hozirgi oddiy zamon: kundalik harakatlar.",
        'grammar': (
            "Kundalik, takrorlanuvchi harakatlar va haqiqatlar uchun.\n"
            "I/You/We/They + verb | He/She/It + verb + s/es\n"
            "Inkor: don't / doesn't + verb.\n"
            "Savol: Do / Does + subject + verb?"
        ),
        'examples': "I work every day.\nShe likes coffee.\nThey play football.\nHe doesn't eat meat.\nDo you speak English?",
    },
    {
        'title': 'Have got / Has got',
        'desc': "Egalikni bildirish (Britaniya uslubi).",
        'grammar': (
            "I/You/We/They + have got\n"
            "He/She/It + has got\n"
            "Inkor: haven't got / hasn't got.\n"
            "Savol: Have you got...? / Has she got...?"
        ),
        'examples': "I have got a bike.\nShe has got two sisters.\nThey have got a big house.\nHe hasn't got a car.\nHave you got a pen?",
    },
    {
        'title': "Can / Can't",
        'desc': "Qobiliyat va imkoniyat.",
        'grammar': (
            "can - qila olmoq (qobiliyat/ruxsat).\n"
            "can't (cannot) - qila olmaslik.\n"
            "Tuzilma: subject + can + verb (asosiy shakl).\n"
            "Savol: Can you swim?"
        ),
        'examples': "I can swim.\nShe can speak three languages.\nThey can't come today.\nCan you help me?\nHe can play the guitar.",
    },
    {
        'title': 'Prepositions of place',
        'desc': "O'rin ko'makchilari: in, on, under, next to...",
        'grammar': (
            "in - ichida | on - ustida | under - ostida\n"
            "next to - yonida | behind - orqasida | in front of - oldida\n"
            "between - orasida | near - yaqinida"
        ),
        'examples': "The book is on the table.\nThe cat is under the chair.\nThe bag is in the room.\nThe shop is next to the bank.\nThe car is behind the house.",
    },
    {
        'title': 'Some / Any',
        'desc': "Noaniq miqdor.",
        'grammar': (
            "some - tasdiq gaplarda: I have some money.\n"
            "any - inkor va savol gaplarda:\n"
            "I don't have any money. Do you have any money?"
        ),
        'examples': "There is some water.\nI have some friends.\nThere isn't any bread.\nDo you have any questions?\nWe need some help.",
    },
    {
        'title': 'Countable va uncountable nouns',
        'desc': "Sanaladigan va sanalmaydigan otlar.",
        'grammar': (
            "Sanaladigan: a book, two books (ko'plik bor).\n"
            "Sanalmaydigan: water, rice, money (ko'plik yo'q).\n"
            "much - sanalmaydigan, many - sanaladigan bilan ishlatiladi."
        ),
        'examples': "I have two apples. (countable)\nThere is some water. (uncountable)\nHow many books? \nHow much money?\nWe need some rice.",
    },
    {
        'title': 'Imperatives',
        'desc': "Buyruq gaplar.",
        'grammar': (
            "Buyruq gap fe'lning asosiy shakli bilan boshlanadi:\n"
            "Open the door. Sit down.\n"
            "Inkor: Don't + verb: Don't run!"
        ),
        'examples': "Open your books.\nClose the door, please.\nDon't be late.\nListen carefully.\nDon't touch that!",
    },
]

# ---------------------------------------------------------------------------
# A1 VOCABULARY — 12 toifa
# ---------------------------------------------------------------------------
A1_VOCAB = {
    'Salomlashish': [
        ('hello', 'salom', 'Hello! How are you?', '👋'),
        ('goodbye', 'xayr', 'Goodbye, see you tomorrow.', '👋'),
        ('please', 'iltimos', 'Help me, please.', '🙏'),
        ('thank you', 'rahmat', 'Thank you very much.', '🙏'),
        ('sorry', 'kechirasiz', 'Sorry, I am late.', '😔'),
        ('welcome', 'xush kelibsiz', 'Welcome to our school!', '🎉'),
        ('good morning', 'xayrli tong', 'Good morning, teacher!', '🌅'),
        ('nice to meet you', 'tanishganimdan xursandman', 'Nice to meet you!', '🤝'),
    ],
    'Oila': [
        ('mother', 'ona', 'My mother is kind.', '👩'),
        ('father', 'ota', 'My father works hard.', '👨'),
        ('sister', 'opa/singil', 'I have one sister.', '👧'),
        ('brother', 'aka/uka', 'His brother is tall.', '👦'),
        ('grandmother', 'buvi', 'My grandmother tells stories.', '👵'),
        ('grandfather', 'bobo', 'My grandfather is old.', '👴'),
        ('son', "o'g'il", 'They have one son.', '👶'),
        ('daughter', 'qiz', 'Her daughter is clever.', '👧'),
    ],
    'Kasblar': [
        ('teacher', "o'qituvchi", 'She is a teacher.', '👩‍🏫'),
        ('doctor', 'shifokor', 'The doctor is busy.', '👨‍⚕️'),
        ('driver', 'haydovchi', 'He is a bus driver.', '🚕'),
        ('cook', 'oshpaz', 'The cook makes pizza.', '👨‍🍳'),
        ('engineer', 'muhandis', 'My uncle is an engineer.', '👷'),
        ('police officer', 'politsiyachi', 'The police officer helps people.', '👮'),
        ('farmer', 'fermer', 'The farmer grows wheat.', '🧑‍🌾'),
        ('pilot', 'uchuvchi', 'The pilot flies a plane.', '👨‍✈️'),
    ],
    'Raqamlar': [
        ('one', 'bir', 'I have one pen.', '1️⃣'),
        ('two', 'ikki', 'There are two cats.', '2️⃣'),
        ('three', 'uch', 'I see three birds.', '3️⃣'),
        ('four', "to'rt", 'Four students are here.', '4️⃣'),
        ('five', 'besh', 'Give me five apples.', '5️⃣'),
        ('ten', "o'n", 'I have ten fingers.', '🔟'),
        ('hundred', 'yuz', 'One hundred people came.', '💯'),
        ('zero', 'nol', 'The score is zero.', '0️⃣'),
    ],
    'Ranglar': [
        ('red', 'qizil', 'The apple is red.', '🔴'),
        ('blue', "ko'k", 'The sky is blue.', '🔵'),
        ('green', 'yashil', 'The grass is green.', '🟢'),
        ('yellow', 'sariq', 'The sun is yellow.', '🟡'),
        ('black', 'qora', 'My cat is black.', '⚫'),
        ('white', 'oq', 'Snow is white.', '⚪'),
        ('orange', "to'q sariq", 'I like orange juice.', '🟠'),
        ('purple', 'binafsha', 'Her dress is purple.', '🟣'),
    ],
    'Kunlar va oylar': [
        ('Monday', 'dushanba', 'I study on Monday.', '📅'),
        ('Friday', 'juma', 'Friday is my favourite day.', '📅'),
        ('Sunday', 'yakshanba', 'We rest on Sunday.', '📅'),
        ('January', 'yanvar', 'My birthday is in January.', '🗓️'),
        ('June', 'iyun', 'Summer starts in June.', '🗓️'),
        ('December', 'dekabr', 'It is cold in December.', '🗓️'),
        ('week', 'hafta', 'There are seven days in a week.', '📆'),
        ('month', 'oy', 'There are twelve months.', '📆'),
    ],
    'Vaqt': [
        ('hour', 'soat', 'An hour has sixty minutes.', '⏰'),
        ('minute', 'daqiqa', 'Wait a minute, please.', '⏱️'),
        ('morning', 'ertalab', 'I run in the morning.', '🌅'),
        ('afternoon', 'tushdan keyin', 'We meet in the afternoon.', '🌤️'),
        ('evening', 'kechqurun', 'I read in the evening.', '🌆'),
        ('night', 'tun', 'Good night!', '🌙'),
        ('today', 'bugun', 'Today is sunny.', '📍'),
        ('tomorrow', 'ertaga', 'See you tomorrow.', '➡️'),
    ],
    'Uy va xonalar': [
        ('house', 'uy', 'This is my house.', '🏠'),
        ('kitchen', 'oshxona', 'We cook in the kitchen.', '🍳'),
        ('bedroom', 'yotoqxona', 'I sleep in the bedroom.', '🛏️'),
        ('bathroom', 'hammom', 'The bathroom is clean.', '🛁'),
        ('door', 'eshik', 'Close the door, please.', '🚪'),
        ('window', 'deraza', 'Open the window.', '🪟'),
        ('table', 'stol', 'The book is on the table.', '🪑'),
        ('chair', 'stul', 'Sit on the chair.', '🪑'),
    ],
    'Oziq-ovqat': [
        ('bread', 'non', 'I eat bread for breakfast.', '🍞'),
        ('water', 'suv', 'I drink water.', '💧'),
        ('apple', 'olma', 'An apple a day is good.', '🍎'),
        ('milk', 'sut', 'Children drink milk.', '🥛'),
        ('rice', 'guruch', 'We cook rice.', '🍚'),
        ('meat', "go'sht", 'He likes meat.', '🍖'),
        ('egg', 'tuxum', 'I eat an egg.', '🥚'),
        ('tea', 'choy', 'She drinks tea.', '🍵'),
    ],
    'Kiyimlar': [
        ('shirt', 'ko\'ylak', 'He wears a white shirt.', '👔'),
        ('shoes', 'oyoq kiyim', 'My shoes are new.', '👟'),
        ('hat', 'shapka', 'She has a red hat.', '🧢'),
        ('dress', 'libos', 'Her dress is beautiful.', '👗'),
        ('trousers', 'shim', 'These trousers are black.', '👖'),
        ('jacket', 'kurtka', 'Wear a jacket, it is cold.', '🧥'),
        ('socks', 'paypoq', 'I need clean socks.', '🧦'),
        ('coat', 'palto', 'My coat is warm.', '🧥'),
    ],
    'Hayvonlar': [
        ('dog', 'it', 'The dog is friendly.', '🐶'),
        ('cat', 'mushuk', 'The cat sleeps a lot.', '🐱'),
        ('horse', 'ot', 'The horse runs fast.', '🐴'),
        ('cow', 'sigir', 'The cow gives milk.', '🐄'),
        ('bird', 'qush', 'The bird sings.', '🐦'),
        ('fish', 'baliq', 'Fish live in water.', '🐟'),
        ('sheep', "qo'y", 'The sheep is white.', '🐑'),
        ('chicken', 'tovuq', 'The chicken lays eggs.', '🐔'),
    ],
    'Maktab buyumlari': [
        ('book', 'kitob', 'Open your book.', '📖'),
        ('pen', 'ruchka', 'I write with a pen.', '🖊️'),
        ('pencil', 'qalam', 'Draw with a pencil.', '✏️'),
        ('bag', 'sumka', 'My bag is heavy.', '🎒'),
        ('notebook', 'daftar', 'Write in your notebook.', '📓'),
        ('ruler', 'chizg\'ich', 'Use a ruler to draw a line.', '📏'),
        ('eraser', "o'chirg'ich", 'I need an eraser.', '🧽'),
        ('board', 'doska', 'The teacher writes on the board.', '📋'),
    ],
}

# ---------------------------------------------------------------------------
# A1 HOMEWORK (Quiz) — namunaviy grammatika testlari
# ---------------------------------------------------------------------------
A1_QUIZZES = [
    {
        'title': 'To be (am/is/are)', 'reward': 20,
        'questions': [
            ('I ___ a student.', ['am', 'is', 'are', 'be'], 'am'),
            ('She ___ my friend.', ['am', 'are', 'is', 'be'], 'is'),
            ('They ___ from Uzbekistan.', ['is', 'am', 'are', 'be'], 'are'),
            ('It ___ cold today.', ['are', 'is', 'am', 'be'], 'is'),
            ('We ___ happy.', ['is', 'am', 'are', 'be'], 'are'),
            ('___ you a teacher?', ['Is', 'Am', 'Are', 'Be'], 'Are'),
        ],
    },
    {
        'title': 'Articles (a/an/the)', 'reward': 20,
        'questions': [
            ('I have ___ apple.', ['a', 'an', 'the', '-'], 'an'),
            ('She is ___ teacher.', ['an', 'the', 'a', '-'], 'a'),
            ('___ sun is bright.', ['A', 'An', 'The', '-'], 'The'),
            ('He bought ___ umbrella.', ['a', 'an', 'the', '-'], 'an'),
            ('This is ___ best day.', ['a', 'an', 'the', '-'], 'the'),
            ('I need ___ pen.', ['a', 'an', 'the', '-'], 'a'),
        ],
    },
    {
        'title': 'Present Simple', 'reward': 20,
        'questions': [
            ('She ___ to school every day.', ['go', 'goes', 'going', 'gone'], 'goes'),
            ('I ___ coffee in the morning.', ['drinks', 'drinking', 'drink', 'drank'], 'drink'),
            ('They ___ football.', ['plays', 'play', 'playing', 'played'], 'play'),
            ('He ___ not like fish.', ['do', 'does', 'is', 'are'], 'does'),
            ('___ you speak English?', ['Does', 'Is', 'Do', 'Are'], 'Do'),
            ('The sun ___ in the east.', ['rise', 'rises', 'rising', 'rose'], 'rises'),
        ],
    },
    {
        'title': "Can / Can't", 'reward': 20,
        'questions': [
            ('I ___ swim very well.', ['can', 'cans', 'caning', 'to can'], 'can'),
            ('She can ___ three languages.', ['speaks', 'speak', 'speaking', 'spoke'], 'speak'),
            ('They ___ come today. (negative)', ["can't", 'can', 'cans', "don't can"], "can't"),
            ('___ you help me?', ['Can', 'Do', 'Are', 'Is'], 'Can'),
            ('He can ___ the guitar.', ['plays', 'playing', 'play', 'played'], 'play'),
            ('We can ___ English.', ['to read', 'reads', 'read', 'reading'], 'read'),
        ],
    },
    {
        'title': 'There is / There are', 'reward': 20,
        'questions': [
            ('___ a cat in the room.', ['There are', 'There is', 'There be', 'It is'], 'There is'),
            ('___ five books on the table.', ['There is', 'There are', 'There be', 'It are'], 'There are'),
            ('There ___ any milk.', ["isn't", "aren't", 'is', 'are'], "isn't"),
            ('___ there any students?', ['Is', 'Are', 'Be', 'Do'], 'Are'),
            ('There ___ a park near my house.', ['are', 'is', 'be', 'am'], 'is'),
            ('There ___ three windows.', ['is', 'am', 'are', 'be'], 'are'),
        ],
    },
]

STICKERS = [
    ('Yulduzcha', '⭐', 'Yorqin yulduz', 50),
    ('Olov', '🔥', 'Streak ramzi', 80),
    ('Toj', '👑', 'Chempion toji', 150),
    ('Raketa', '🚀', "Tez o'sish", 120),
    ('Brilliant', '💎', 'Noyob stiker', 300),
    ('Trofey', '🏆', "G'olib uchun", 250),
    ('Kamalak', '🌈', 'Rang-barang', 90),
    ('Yurak', '❤️', 'Sevimli', 60),
]


class Command(BaseCommand):
    help = "EnglishUp uchun to'liq A1 kontenti (grammar, vocabulary, homework, stiker)"

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

        a1 = levels['A1']

        # Grammar lessons
        lesson_count = 0
        for i, g in enumerate(A1_GRAMMAR):
            _, created = Lesson.objects.get_or_create(
                level=a1, title=g['title'],
                defaults={
                    'description': g['desc'],
                    'grammar_explanation': g['grammar'],
                    'examples': g['examples'],
                    'order': i,
                },
            )
            lesson_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"A1 grammar darslar: {lesson_count} ta yangi qo'shildi"))

        # Vocabulary
        word_count = 0
        for category, words in A1_VOCAB.items():
            for eng, uz, ex, emoji in words:
                _, created = Word.objects.get_or_create(
                    english=eng,
                    defaults={'uzbek': uz, 'example': ex, 'emoji': emoji, 'level': a1},
                )
                word_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"A1 so'zlar: {word_count} ta yangi qo'shildi"))

        # Homework (quizzes)
        quiz_count = 0
        for qz in A1_QUIZZES:
            if Quiz.objects.filter(title=qz['title']).exists():
                continue
            quiz = Quiz.objects.create(
                title=qz['title'],
                description=f"{qz['title']} bo'yicha grammatika testi",
                level=a1,
                coin_reward=qz['reward'],
            )
            for i, (text, options, answer) in enumerate(qz['questions']):
                question = Question.objects.create(quiz=quiz, text=text, order=i)
                for opt in options:
                    Choice.objects.create(question=question, text=opt, is_correct=(opt == answer))
            quiz_count += 1
        self.stdout.write(self.style.SUCCESS(f"A1 homework (quiz): {quiz_count} ta yangi qo'shildi"))

        # Stickers
        sticker_count = 0
        for i, (name, emoji, desc, price) in enumerate(STICKERS):
            _, created = Sticker.objects.get_or_create(
                name=name, defaults={'emoji': emoji, 'description': desc, 'price': price, 'order': i}
            )
            sticker_count += 1 if created else 0
        self.stdout.write(self.style.SUCCESS(f"Stikerlar: {sticker_count} ta yangi qo'shildi"))

        self.stdout.write(self.style.SUCCESS("\nTayyor! A1 kontenti to'liq yuklandi."))
