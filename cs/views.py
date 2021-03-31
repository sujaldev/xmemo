from django.shortcuts import render
from django.http import HttpResponse
from cs import db_reader
from cs.models import Question
import json


# Create your views here.
def home_view(request):
    return render(request, "index.html", {})


def display_by_date(request):
    query = request.GET.get('q', '')
    if is_valid_date(query):
        html = {"html_string": db_reader.get_html_by_date(query)}
        return render(request, "questions_base.html", html)
    else:
        html = {
            "html_string": f'<p class="main-text"> <bold>{query}</bold> is not a valid date, (only 2020 and 2021 '
                           f'are accepted years) try again. </p>'
        }
        return render(request, "questions_base.html", html)


def display_by_key(request):
    query = request.GET.get('q', '')
    html = {
        "html_string": db_reader.get_html_by_key(query)
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
