import pathlib
from django.http import HttpResponse
from django.shortcuts import render

this_dir = pathlib.Path(__file__).resolve().parent

def home_page_view(request, *args, **kwargs):
    my_title = "My Title"  
    my_context = {
        "my_title": my_title,
    }
    html_template = "home.html"
    return render(request, "home.html", my_context)