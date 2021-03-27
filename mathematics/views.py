from django.shortcuts import render


# Create your views here.
def math_view(request):
    return render(request, "mathematics.html", {})
