from django.shortcuts import render


# Create your views here.
def eng_view(request):
    return render(request, "english.html", {})
