from django.urls import path, re_path
from first_criteria import views as first_views

urlpatterns = [
    path('', first_views.engine_page),
    path('add_engine', first_views.add_engine),
    path('all_engines', first_views.all_engines_page),
    re_path(r'^engine_results/(\d+)/$', first_views.engine_results),
    re_path(r'^delete_engine/(\d+)/$', first_views.delete_engine),
    path('theory', first_views.theory),
    path('upload_base_engines', first_views.upload_base_engines)
]
