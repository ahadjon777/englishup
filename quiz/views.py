from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Quiz, Question, Choice, QuizAttempt


def quiz_list(request):
    quizzes = Quiz.objects.all()
    # foydalanuvchi qaysi quizlarni yechganini belgilaymiz
    done_ids = set()
    if request.user.is_authenticated:
        done_ids = set(
            QuizAttempt.objects.filter(user=request.user).values_list('quiz_id', flat=True)
        )
    return render(request, 'quiz/quiz_list.html', {
        'quizzes': quizzes,
        'done_ids': done_ids,
    })


@login_required
def quiz_take(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        score = 0
        total = questions.count()
        results = []
        for question in questions:
            selected_id = request.POST.get(f'question_{question.id}')
            correct_choice = question.choices.filter(is_correct=True).first()
            is_correct = False
            if selected_id and correct_choice and str(correct_choice.id) == selected_id:
                score += 1
                is_correct = True
            results.append({
                'question': question,
                'selected_id': int(selected_id) if selected_id else None,
                'correct_id': correct_choice.id if correct_choice else None,
                'is_correct': is_correct,
            })

        # Coin: faqat birinchi urinishda beriladi
        already = QuizAttempt.objects.filter(user=request.user, quiz=quiz).exists()
        coins_awarded = 0
        if not already and total > 0:
            # natijaga mutanosib coin (to'liq to'g'ri = to'liq mukofot)
            coins_awarded = round(quiz.coin_reward * score / total)
            if coins_awarded > 0:
                request.user.profile.add_coins(coins_awarded, f"Quiz: {quiz.title} ✅")

        QuizAttempt.objects.create(
            user=request.user, quiz=quiz, score=score, total=total, coins_awarded=coins_awarded
        )

        return render(request, 'quiz/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'percentage': round((score / total) * 100) if total else 0,
            'coins_awarded': coins_awarded,
            'first_time': not already,
            'results': results,
        })

    return render(request, 'quiz/quiz_take.html', {
        'quiz': quiz,
        'questions': questions,
    })
