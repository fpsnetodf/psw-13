from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from .models import Navigators, Mentorados, DisponibilidadeHorarios, Reuniao
from django.contrib.messages import add_message, constants
from .auth import valida_token

# Create your views here.

def mentorados(request):
    if request.method == 'GET':
        navigators = Navigators.objects.filter(user=request.user)
        mentorados = Mentorados.objects.filter(user=request.user)
        
        estagios_flat = [i[1] for i in Mentorados.estagio_choices]
        qtd_estagios = []

        for i, j in Mentorados.estagio_choices:
            qtd_estagios.append(Mentorados.objects.filter(estagio=i).count())

    
        return render(request, 'mentorados/mentorados.html', {'estagios': Mentorados.estagio_choices, 'navigators': navigators, 'mentorados': mentorados, 'estagios_flat': estagios_flat, 'qtd_estagios': qtd_estagios})
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

def reunioes(request):
    if request.method == 'GET':
        reuniao = Reuniao.objects.all()
        return render(request, 'mentorados/reunioes.html', {"reunioes": reuniao})
    else:
        data = request.POST.get('data')

        data = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        disponibilidade = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=(data - timedelta(minutes=50)),
            data_inicial__lte=(data + timedelta(minutes=50))
        )

        if disponibilidade.exists():
            add_message(request, constants.ERROR, 'Você já possui uma reunião em aberto.')
            return redirect('reunioes')

        disponibilidade = DisponibilidadeHorarios(
            data_inicial=data,
            mentor=request.user

        )
        disponibilidade.save()

        add_message(request, constants.SUCCESS, 'Horário disponibilizado com sucesso.')
        return redirect('reunioes')
    
    
def auth(request):
    if request.method == 'GET':
        return render(request, 'mentorados/auth_mentorado.html')
    else:
        token = request.POST.get('token')

        if not Mentorados.objects.filter(token=token).exists():
            add_message(request, constants.ERROR, 'Token inválido')
            return redirect('auth_mentorado')
        
        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=3600)
        return response
    



    
def escolher_dia(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    if request.method == 'GET':
        mentorado = valida_token(request.COOKIES.get('auth_token'))
        disponibilidades = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False,
            mentor = mentorado.user
           
        ).values_list('data_inicial', flat=True)
        horarios = []
        for i in disponibilidades:
            horarios.append(i.date())               
        return render(request, 'mentorados/escolher_dia.html', {'horarios': list(set(horarios))})


def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    mentorado = valida_token(request.COOKIES.get('auth_token'))

    # TODO validar se o horario agendado é realmente de um mentor do mentorado
    if request.method == 'GET':   
        data = request.GET.get("data")
        if data is None:
            data = "01-01-2025"  # Substitua por uma data padrão válida
            data = datetime.strptime(data, "%d-%m-%Y")
            

        if isinstance(data, str):
            data = datetime.strptime(data, "%d-%m-%Y")
        elif isinstance(data, datetime):
            # Se `data` já for um objeto `datetime`, não precisa fazer nada
            pass
        else:
            return HttpResponse("Erro: Tipo inesperado para data.", status=400)


        print("minha captura de horario pelo get: ", data)
        # data = datetime.strptime(data, "%d-%m-%Y")
        mentorado = mentorado
        horarios = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False,
            mentor=mentorado.user
        )    
    
        return render(request, 'mentorados/agendar_reuniao.html', {'horarios': horarios, 'tags': Reuniao.tag_choices})
    else : 
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get('descricao')
        
        reuniao = Reuniao(
            data_id=horario_id,
            mentorado=mentorado,
            tag=tag,
            descricao=descricao
            
        )
        reuniao.save()
        horario = DisponibilidadeHorarios.objects.get(id=horario_id)
        horario.agendado = True
        horario.save()
        add_message(request, constants.SUCCESS, "Reunião agendada com sucesso.  ")
        return redirect("escolher_dia/?data={{ horario }}")
        