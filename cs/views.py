from django.shortcuts import render
from django.http import HttpResponse
from cs import db_reader
from cs.models import Question
import json
from xmemo import settings


# Create your views here.
def set_cookie(response, key, value):
    response.set_cookie(key, value)


def get_cookie(request, key):
    value = request.COOKIES.get(key)
    return value


def home_view(request):
    theme = get_cookie(request, "theme")
    if theme is None:
        theme = "light"
    return render(request, "index.html", {"theme": theme})


def display_by_date(request):
    theme = get_cookie(request, "theme")
    if theme is None:
        theme = "light"
    query = request.GET.get('q', '')
    if is_valid_date(query):
        html = {
            "html_string": db_reader.get_html_by_date(query),
            "theme": theme
        }
        return render(request, "questions_base.html", html)
    else:
        html = {
            "html_string": f'<p class="main-text" style="margin-bottom: 85vh;"> '
                           '<bold>{query}</bold> is not a valid date, (only 2020 and 2021 are accepted years) '
                           'try again. </p>',
            "theme": theme
        }
        return render(request, "questions_base.html", html)


def display_by_key(request):
    theme = get_cookie(request, "theme")
    if theme is None:
        theme = "light"
    query = request.GET.get('q', '')
    html = {
        "html_string": db_reader.get_html_by_key(query),
        "theme": theme
    }
    return render(request, "questions_base.html", html)


def update_question_review(request):
    question = request.POST.get("question", '')
    unique_id = request.POST.get("unique_id", '')
    val_type = request.POST.get("val_type", '')

    q_obj = Question.objects.filter(question=question)[0]

    answer_list = json.loads(q_obj.answer)

    for answer in answer_list:
        if answer["unique_id"] == f"c{unique_id}":
            answer[val_type] += 1

    q_obj.answer = json.dumps(answer_list)

    q_obj.save()

    return HttpResponse(status=200)


def switch_theme(request):
    # get post request's parameters
    mode = request.POST.get("theme", '').split("/")[-1].replace(".css", "")
    mode = mode.split("-")[0]
    # set cookie and return response
    response = HttpResponse(f"Setting Theme Cookie to {mode}")
    set_cookie(response, "theme", mode)
    return response


def is_valid_date(date):
    validity = False
    params = date.split(" ")
    try:
        if len(params) == 3:
            if not 1 <= int(params[0]) <= 31:
                return validity
            elif not params[1].lower() in [
                'january',
                'february',
                'march',
                'april',
                'may',
                'june',
                'july',
                'august',
                'september',
                'october',
                'november',
                'december'
            ]:
                return validity
            elif not params[2] in ["2020", "2021"]:
                return validity
            else:
                validity = True
                return validity
        else:
            return validity
    except (TypeError, ValueError):
        return validity
