from django.shortcuts import render, redirect
from first_criteria.models import Engine


def engine_page(request):
    return render(request, 'engine_form.html')


def add_engine(request):
    # TODO: process the POST request
    Engine.objects.create(name=request.POST['name'], nu=request.POST['nu'])
    return redirect('/engine_results')


def engine_results(request):
    engine = Engine.objects.last()
    vibration = engine.nu * 2
    return render(request, 'engine_results.html', {'vibration':vibration})