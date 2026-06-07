from django.shortcuts import render

def times_table(request):
    return render(request, 'games/times_table.html')

def fractions(request):
    return render(request, 'games/fractions.html')

def mental_maths(request):
    return render(request, 'games/mental_maths.html')

def human_body(request):
    return render(request, 'games/human_body.html')

def chemistry(request):
    return render(request, 'games/chemistry.html')

def solar_system(request):
    return render(request, 'games/solar_system.html')

def physics(request):
    return render(request, 'games/physics.html')

def spelling_bee(request):
    return render(request, 'games/spelling_bee.html')

def grammar(request):
    return render(request, 'games/grammar.html')

def vocabulary(request):
    return render(request, 'games/vocabulary.html')

def nigeria(request):
    return render(request, 'games/nigeria.html')

def africa(request):
    return render(request, 'games/africa.html')