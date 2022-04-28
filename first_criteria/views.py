from django.shortcuts import render, redirect
from first_criteria.models import Engine
from first_criteria.data_processing.vibrations import refreshBaseEngines

import pandas as pd


def engine_page(request):
    return render(request, 'engine_form.html')


def add_engine(request):
    # TODO: process the POST request
    Engine.objects.create(name=request.POST['name'], nu=request.POST['nu'])
    return redirect('/engine_results')


def engine_results(request):
    return render(request, 'engine_results.html')


def all_engines_page(request):
    engines = Engine.objects.all()
    return render(request, 'all_engines.html', {'engines': engines})