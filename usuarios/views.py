from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.messages import add_message, constants
from django.contrib import auth
from django.contrib.auth import authenticate
# Create your views here.

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro/cadastro.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        if not senha == confirmar_senha:
            return redirect('/usuarios/cadastro')
        
        if len(senha) == 6:
            return redirect('/usuarios/cadastro')
        users = User.objects.filter(username=username)
        if users.exists():
            return redirect('/usuarios/cadastro')
        
        User.objects.create_user(
            username=username,
            password=senha
        )       
        return redirect('/usuarios/login')


def login(request):
    if request.method == 'GET':
        return render(request, 'cadastro/login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            return redirect('/mentorados/')
        
        add_message(request, constants.ERROR, 'Username ou senha inválidos')
        return redirect('login')