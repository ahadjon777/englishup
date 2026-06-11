import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from groq import Groq

from quiz.models import Quiz, Question, Choice
from lessons.models import Lesson


# Har bir darsga yaratiladigan mashqlar to'plami (Englify uslubi)
EXERCISE_SET = [
    ('Grammar', "multiple-choice grammar questions", 6),
    ('Grammar', "fill-in-the-blank grammar questions (choose the correct word)", 6),
    ('Reading', "a SHORT reading passage (3-5 simple sentences) with comprehension questions", 5),
    ('Vocabulary', "vocabulary questions: word meaning, synonym or the correct word for the sentence", 5),
    ('Writing', "sentence-building questions: choose the correctly written sentence", 5),
]


class Command(BaseCommand):
    help = "AI yordamida har bir darsga turli mashqlar (Grammar x2, Reading, Vocabulary, Writing) yaratadi"

    def add_arguments(self, parser):
        parser.add_argument('--lesson', type=int, default=None, help="Bitta lesson ID")
        parser.add_argument('--level', default='A1', help="Daraja kodi (default A1)")
        parser.add_argument('--reward', type=int, default=15, help="Har mashq uchun coin")

    def handle(self, *args, **options):
        if options['lesson']:
            lessons = Lesson.objects.filter(pk=options['lesson'])
        else:
            lessons = Lesson.objects.filter(level__code=options['level']).order_by('order')
        if not lessons:
            raise CommandError("Dars topilmadi. Avval seed_content ishlating.")

        client = Groq(api_key=settings.GROQ_API_KEY)
        total = 0
        for lesson in lessons:
            self.stdout.write(f"\n{lesson.title}:")
            for idx, (category, desc, count) in enumerate(EXERCISE_SET):
                title = f"{lesson.title} - {category} {idx + 1}"
                if Quiz.objects.filter(title=title).exists():
                    self.stdout.write(f"  - {title} (mavjud)")
                    continue
                level_code = lesson.level.code if lesson.level else 'A1'
                try:
                    data = self._generate(client, lesson.title, level_code, category, desc, count)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  - {title}: xato ({e})"))
                    continue

                questions = data.get('questions', [])
                if not questions:
                    continue
                quiz = Quiz.objects.create(
                    title=title,
                    description=data.get('passage', ''),
                    category=category,
                    level=lesson.level,
                    lesson=lesson,
                    coin_reward=options['reward'],
                    order=idx,
                )
                for qi, q in enumerate(questions):
                    question = Question.objects.create(quiz=quiz, text=q['question'], order=qi)
                    ans = q.get('answer', '').strip()
                    for opt in q.get('options', []):
                        Choice.objects.create(question=question, text=opt, is_correct=(opt.strip() == ans))
                total += 1
                self.stdout.write(self.style.SUCCESS(f"  + {title} ({len(questions)} savol)"))

        self.stdout.write(self.style.SUCCESS(f"\nJami {total} ta yangi mashq yaratildi."))

    def _generate(self, client, topic, level_code, category, desc, count):
        if category == 'Reading':
            instruction = (
                f"Create {desc} for CEFR {level_code} English learners. "
                f"The passage theme may relate to '{topic}'. "
                f"Provide exactly {count} multiple-choice questions about the passage, each with 4 options. "
                'Return ONLY JSON: {"passage": "...", "questions": '
                '[{"question":"...","options":["..","..","..",".."],"answer":"correct option text"}]}'
            )
        else:
            instruction = (
                f"Create exactly {count} {desc} about '{topic}' for CEFR {level_code} English learners. "
                "Each question must have 4 options and one correct answer. "
                'Return ONLY JSON: {"questions": '
                '[{"question":"...","options":["..","..","..",".."],"answer":"correct option text"}]}'
            )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an English teacher. Return valid JSON only."},
                {"role": "user", "content": instruction},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)
