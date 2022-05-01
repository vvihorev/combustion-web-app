from django.shortcuts import render, redirect
from first_criteria.models import Engine
import first_criteria.data_processing.vibrations as process_data

import pandas as pd


def engine_page(request):
    return render(request, 'engine_form.html')


def add_engine(request):
    engine = Engine.objects.create(
        name=request.POST['name'],
        N_e=request.POST['N_e'],
        nu=request.POST['nu'],
        pe=request.POST['pe'],
        pz=request.POST['pz'],
        N_max=request.POST['N_max'],
        delta=request.POST['delta'],
        D_czvt=request.POST['D_czvt'],
        D_czb=request.POST['D_czb'],
        group=process_data.assignGroup(request.POST['nu']),
        S_n=request.POST['S_n'],
    )
    return redirect(f'/engine_results/{engine.id}')


def engine_results(request, engine_id):
    engine = Engine.objects.get(id=engine_id)
    process_data.getVibrations(engine.__dict__)
    results = process_data._calculate_frequency_b_d(engine.nu)
    
    df = results['df']
    context = {
        'engine': engine,
        'results': results,
        'df': df.to_html(),
        'df_dict': df.to_dict(),
        'df_rec': df.to_dict(orient='records')
    }
    return render(request, 'engine_results.html', context)


def delete_engine(request, engine_id):
    engine = Engine.objects.get(id=engine_id)
    engine.delete()
    return redirect('/all_engines')


def all_engines_page(request):
    engines = Engine.objects.order_by('nu')
    return render(request, 'all_engines.html', {'engines': engines})


def theory(request):
    return render(request, 'theory.html')


def upload_base_engines(request):
    process_data._refreshBaseEngines()
    return redirect('/all_engines')
