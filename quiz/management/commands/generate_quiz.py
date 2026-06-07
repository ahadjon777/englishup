import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from groq import Groq

from quiz.models import Quiz, Question, Choice
from lessons.models import Level, Lesson


class Command(BaseCommand):
    help = "AI (Groq) yordamida mavzu bo'yicha quiz savollarini yaratadi"

    def add_arguments(self, parser):
        parser.add_argument('--topic', required=True, help="Mavzu, masalan: 'Present Simple'")
        parser.add_argument('--level', default=None, help="Daraja kodi: A1, A2, B1, B2, C1, C2")
        parser.add_argument('--count', type=int, default=10, help="Savollar soni (10 yoki 20)")
        parser.add_argument('--reward', type=int, default=20, help="Quiz uchun coin mukofoti")
        parser.add_argument('--lesson', type=int, default=None, help="Lesson ID (ixtiyoriy)")

    def handle(self, *args, **options):
        topic = options['topic']
        level_code = options['level']
        count = options['count']
        reward = options['reward']
        lesson_id = options['lesson']

        level = None
        if level_code:
            level = Level.objects.filter(code=level_code).first()
            if not level:
                raise CommandError(f"'{level_code}' kodli daraja topilmadi. Avval admin'da yarating.")

        lesson = None
        if lesson_id:
            lesson = Lesson.objects.filter(pk=lesson_id).first()

        self.stdout.write(f"AI '{topic}' mavzusi uchun {count} ta savol yaratmoqda...")

        client = Groq(api_key=settings.GROQ_API_KEY)
        level_text = f" for CEFR level {level_code}" if level_code else ""
        prompt = (
            f"Generate exactly {count} multiple-choice English learning questions "
            f"about the topic '{topic}'{level_text}. "
            "Each question must have exactly 4 options and one correct answer. "
            "Return ONLY valid JSON in this exact format: "
            '{"questions": [{"question": "...", "options": ["...","...","...","..."], '
            '"answer": "exact text of the correct option"}]}'
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an English teacher creating quiz questions. Always return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        raw = completion.choices[0].message.content
        try:
            data = json.loads(raw)
            questions = data["questions"]
        except (json.JSONDecodeError, KeyError) as e:
            raise CommandError(f"AI javobini o'qib bo'lmadi: {e}. Javob boshi: {raw[:300]}")

        quiz = Quiz.objects.create(
            title=topic,
            description=f"{topic} bo'yicha AI tomonidan yaratilgan test",
            level=level,
            lesson=lesson,
            coin_reward=reward,
        )

        created = 0
        for i, q in enumerate(questions):
            question = Question.objects.create(quiz=quiz, text=q["question"], order=i)
            answer = q.get("answer", "").strip()
            for opt in q["options"]:
                Choice.objects.create(
                    question=question,
                    text=opt,
                    is_correct=(opt.strip() == answer),
                )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"'{quiz.title}' quizi yaratildi - {created} ta savol. Quiz ID: {quiz.id}"
        ))
