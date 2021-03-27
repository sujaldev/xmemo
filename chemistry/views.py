from django.shortcuts import render


# Create your views here.
def chem_view(request):
    return render(request, "chemistry.html", {})
