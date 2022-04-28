from django.shortcuts import render, redirect


def engine_page(request):
    return render(request, 'engine_form.html')


def add_engine(request):
    # TODO: process the POST request
    return redirect('/engine_results')


def engine_results(request):
    return render(request, 'engine_results.html', {'vibration':63})