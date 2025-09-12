from django.shortcuts import render, redirect
from .models import Progress
from .forms import AnswerForm

def home(request):
    all_words = list(Progress.objects.all().order_by("id"))
    if not all_words:
        return render(request, "study/home.html", {"error": "⚠ Нет слов в базе."})

    session_index = request.session.get("word_index", 0)
    show_stats = request.session.get("show_stats", False)

    # Если нужно показать статистику — делаем редирект один раз
    if show_stats:
        request.session["show_stats"] = False
        request.session.modified = True
        return redirect("stats")

    word = all_words[session_index % len(all_words)]
    result = None

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer'].strip().lower()
            if user_answer == word.word_ru:
                result = "Правильно!"
                word.correct_answers += 1
            else:
                result = f"Неправильно. Правильный ответ: {word.word_ru}"
                word.wrong_answers += 1
            word.save()

            # увеличиваем индекс
            session_index += 1
            request.session["word_index"] = session_index

            # если прошло 10 слов — ставим флаг для stats
            if session_index % 10 == 0:
                request.session["show_stats"] = True

            request.session.modified = True
            return redirect("home")
    else:
        form = AnswerForm()

    return render(request, "study/home.html", {
        "word": word,
        "form": form,
        "result": result,
        "progress": word,
        "index": session_index + 1,
        "total": len(all_words)
    })


def stats(request):
    all_words = list(Progress.objects.all().order_by("id"))
    session_index = request.session.get("word_index", 0)

    # Берём последние 10 слов
    start = max(0, session_index - 10)
    words = all_words[start:session_index]

    # сброс после 30 слов
    if session_index >= len(all_words):
        request.session["word_index"] = 0
        request.session.modified = True

    return render(request, "study/stats.html", {"words": words})
