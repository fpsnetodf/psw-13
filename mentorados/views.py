from django.shortcuts import render, redirect
from .models import Navigators, Mentorados
from django.contrib.messages import add_message, constants

# Create your views here.
def mentorados(request):
    if request.method == 'GET':
        navigators = Navigators.objects.filter(user=request.user)
        return render(request, 'mentorados/mentorados.html', {'estagios': Mentorados.estagio_choices, 'navigators': navigators})
    else:
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')
        estagio = request.POST.get("estagio")
        navigator = request.POST.get('navigator')

        mentorado = Mentorados(
            nome=nome,
            foto=foto,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user
        )

        mentorado.save()

        add_message(request, constants.SUCCESS, 'Mentorado cadastrado com sucesso.')
        return redirect('mentorados')