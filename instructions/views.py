from django.shortcuts import render


# Create your views here.
def get_cookie(request, key):
    value = request.COOKIES.get(key)
    return value


def instructions_view(request):
    theme = get_cookie(request, "theme")
    if theme is None:
        theme = "light"

    context = {
        "theme": theme
    }
    return render(request, "instructions.html", context)
