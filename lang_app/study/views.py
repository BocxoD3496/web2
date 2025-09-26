import json
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Lessons data with one real test (lesson id "2" = Numbers)
LESSONS = [
    {"id": "1", "title": "Alphabet Basics", "content": "Learn the alphabet A-Z."},
    {"id": "2", "title": "Numbers", "content": "Short test about numbers.",
     "questions": [
         {
             "id": "q1",
             "text": "How do you say '1' in English?",
             "options": ["one", "two", "three"],
             "answer": "one"
         },
         {
             "id": "q2",
             "text": "How do you say '3' in English?",
             "options": ["five", "three", "seven"],
             "answer": "three"
         }
     ]
    },
    {"id": "3", "title": "Greetings", "content": "Learn common greetings."},
]

COOKIE_NAME_SETTINGS = "ls_settings"
COOKIE_NAME_PROGRESS = "ls_progress"


def _load_cookie_json(request, name, default):
    raw = request.COOKIES.get(name)
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def index(request):
    # load settings and progress from cookies
    settings = _load_cookie_json(request, COOKIE_NAME_SETTINGS, {"language": "en"})
    progress = _load_cookie_json(request, COOKIE_NAME_PROGRESS, {})

    # build lessons list with completed flag
    lessons = []
    for l in LESSONS:
        l_copy = l.copy()
        l_copy["completed"] = bool(progress.get(str(l["id"]), False))
        lessons.append(l_copy)

    context = {
        "lessons": lessons,
        "progress": progress,
        "settings": settings,
    }
    return render(request, "study/index.html", context)


def lesson_detail(request, lesson_id):
    settings = _load_cookie_json(request, COOKIE_NAME_SETTINGS, {"language": "en"})
    progress = _load_cookie_json(request, COOKIE_NAME_PROGRESS, {})

    lesson = next((l for l in LESSONS if str(l["id"]) == str(lesson_id)), None)
    if not lesson:
        return HttpResponse("Lesson not found", status=404)

    completed = bool(progress.get(str(lesson_id), False))
    passed = request.GET.get("passed")  # '1' or '0' or None
    message = None
    if passed == "1":
        message = "Test passed! Lesson marked as completed."
    elif passed == "0":
        message = "Some answers are incorrect. Try again."

    return render(request, "study/lesson.html", {
        "lesson": lesson,
        "completed": completed,
        "settings": settings,
        "message": message,
    })


def submit_test(request, lesson_id):
    # Handles quiz submission for lessons that have 'questions'
    if request.method != "POST":
        return redirect("study:lesson_detail", lesson_id=lesson_id)

    lesson = next((l for l in LESSONS if str(l["id"]) == str(lesson_id)), None)
    if not lesson:
        return HttpResponse("Lesson not found", status=404)

    questions = lesson.get("questions")
    if not questions:
        # Not a quiz lesson — redirect to lesson page
        return redirect("study:lesson_detail", lesson_id=lesson_id)

    # Collect answers from POST and compare
    all_correct = True
    for q in questions:
        qname = q["id"]
        user_ans = request.POST.get(qname, "")
        if user_ans != q["answer"]:
            all_correct = False
            break

    # Prepare response redirect and update cookies accordingly
    next_url = request.POST.get("next", request.path)
    response = redirect(next_url if next_url else f"/lesson/{lesson_id}/")

    progress = _load_cookie_json(request, COOKIE_NAME_PROGRESS, {})

    if all_correct:
        progress[str(lesson_id)] = True
        response.set_cookie(COOKIE_NAME_PROGRESS, json.dumps(progress), max_age=30*24*3600, path="/")
        # redirect with passed=1 to show success message
        response['Location'] = f"{next_url}?passed=1" if next_url else f"/lesson/{lesson_id}/?passed=1"
    else:
        # don't mark completed, redirect with passed=0
        response['Location'] = f"{next_url}?passed=0" if next_url else f"/lesson/{lesson_id}/?passed=0"

    return response


def save_progress(request):
    # keep handler for settings and simple checkbox progress (non-quiz lessons)
    if request.method != "POST":
        return redirect("study:index")

    next_url = request.POST.get("next", "/")
    response = redirect(next_url)

    # load current progress
    progress = _load_cookie_json(request, COOKIE_NAME_PROGRESS, {})

    # update progress (checkbox may be absent when unchecked)
    if "lesson_id" in request.POST:
        lesson_id = str(request.POST.get("lesson_id"))
        # Checkbox handling: present means checked
        completed = "completed" in request.POST
        progress[lesson_id] = bool(completed)
        response.set_cookie(COOKIE_NAME_PROGRESS, json.dumps(progress), max_age=30*24*3600, path="/")

    # update settings (language)
    if "language" in request.POST:
        language = request.POST.get("language", "en")
        settings = {"language": language}
        response.set_cookie(COOKIE_NAME_SETTINGS, json.dumps(settings), max_age=365*24*3600, path="/")

    return response


def reset_progress(request):
    # clear the cookies by setting empty values / deleting
    response = redirect("study:index")
    response.delete_cookie(COOKIE_NAME_PROGRESS, path="/")
    response.delete_cookie(COOKIE_NAME_SETTINGS, path="/")
    return response
