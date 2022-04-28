from django.shortcuts import render, redirect
from first_criteria.models import Engine
from first_criteria.data_processing.vibrations import refreshBaseEngines, assignGroup

import pandas as pd


def engine_page(request):
    return render(request, 'engine_form.html')


def add_engine(request):
    Engine.objects.create(
        name=request.POST['name'],
        N_e=request.POST['N_e'],
        nu=request.POST['nu'],
        pe=request.POST['pe'],
        pz=request.POST['pz'],
        N_max=request.POST['N_max'],
        delta=request.POST['delta'],
        D_czvt=request.POST['D_czvt'],
        D_czb=request.POST['D_czb'],
        group=assignGroup(request.POST['nu']),
        S_n=request.POST['S_n'],
    )
    return redirect('/engine_results')


def engine_results(request):
    return render(request, 'engine_results.html')


def all_engines_page(request):
    engines = Engine.objects.all()
    return render(request, 'all_engines.html', {'engines': engines})