from django.shortcuts import render
from menus.models import Menu

def portfolio_view(request, *args, **kwargs):
    obj = Menu.objects.all().order_by('iOrder')

    context = {
        'menu_list': obj,
    }

    return render(request, "portfolio.html", context)
