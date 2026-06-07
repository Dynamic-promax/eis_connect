from django.urls import path
from . import views

urlpatterns = [
    path('times-table/', views.times_table, name='game_times_table'),
    path('fractions/', views.fractions, name='game_fractions'),
    path('mental-maths/', views.mental_maths, name='game_mental_maths'),
    path('human-body/', views.human_body, name='game_human_body'),
    path('chemistry/', views.chemistry, name='game_chemistry'),
    path('solar-system/', views.solar_system, name='game_solar_system'),
    path('physics/', views.physics, name='game_physics'),
    path('spelling-bee/', views.spelling_bee, name='game_spelling_bee'),
    path('grammar/', views.grammar, name='game_grammar'),
    path('vocabulary/', views.vocabulary, name='game_vocabulary'),
    path('nigeria/', views.nigeria, name='game_nigeria'),
    path('africa/', views.africa, name='game_africa'),
]