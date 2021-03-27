from django.shortcuts import render


# Create your views here.
def phy_view(request):
    return render(request, "physics.html", {})
