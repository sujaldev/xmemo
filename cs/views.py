from django.shortcuts import render
from django.http import HttpResponse
from cs import db_reader


# Create your views here.
def home_view(request):
    return render(request, "index.html", {})


def display_by_date(request):
    query = request.GET.get('q', '')
    if is_valid_date(query):
        try:
            html = {"html_string": db_reader.read_json(query)}
        except FileNotFoundError:
            html = {
                "html_string": '<p class="main-text" style="margin-bottom: 80vh;">No record for given date exists</p>'
            }
        return render(request, "questions_base.html", html)
    else:
        return HttpResponse(f"<p> {query} is not a valid date, try again </p>")


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
    except TypeError:
        return validity
