from django.shortcuts import render

def index(request):
    return render(request, 'homepage/index.html')
    
def vanilla(request):
    return render(request, 'homepage/vanilla.html')

