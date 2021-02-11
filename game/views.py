from django.shortcuts import render, HttpResponse
from game import mastermind_utils
import json, ast
from django.http import JsonResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')


def player_vs_ai(request):
    ai_combination = mastermind_utils.get_random_pin_combination()
    return render(request, 'player_vs_ai.html', {
        'ai_combination': json.dumps(ai_combination),
    })


def ai_vs_player(request):
    return render(request, 'ai_vs_player.html')


def submit_colors(request, ronde, colors):
    request.session['all_combinations'] = mastermind_utils.get_all_combinations()
    user_colors = tuple(str(colors).replace('&quot;', "'").split(','))
    ai_code = mastermind_utils.get_random_logical_start()
    hasAiWon = tuple(ai_code) == tuple(user_colors)
    isGameCompleted = ronde == 8
    validated, result = mastermind_utils.get_response_from_code(tuple(ai_code), tuple(user_colors), isUser=False)
    print(f'USER: {user_colors}\nAI: {ai_code}')

    context = {
        'round': int(ronde) + 1,
        'user_colors': colors,
        'ai_code': ai_code,
        'hasAiWon': hasAiWon,
        'isGameCompleted': isGameCompleted,
        'rcp': result['rcp'],
        'rcwp': result['rcwp'],
    }
    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')


def submit_feedback(request, round, colors, previous_code, rcp, rcwp):
    user_colors = tuple(str(colors).replace('&quot;', "'").split(','))
    previous_colors = tuple(str(previous_code).replace('&quot;', "'").split(','))
    # new_ai_code = mastermind_utils.get_random_pin_combination()
    ai_code = None
    result = {'rcp': None, 'rcwp': None}
    hasAiWon = tuple(previous_colors) == tuple(user_colors)
    isGameCompleted = round == 8
    gamestatusText = ''
    if hasAiWon:
        isGameCompleted = True
        gamestatusText = 'Helaas!<br>De AI heeft uw code geraden!'
    elif isGameCompleted:
        gamestatusText = 'Gefeliciteerd!<br>De AI kon u niet verslaan!'
    elif not isGameCompleted:
        guessList = mastermind_utils.get_worst_case_strategy(request.session['all_combinations'], user_colors, previous_code, rcp, rcwp)
        print(f'GuessList: {guessList}')
        # ai_code = mastermind_utils.get_comb_simple_strategy(request.session['all_combinations'], tuple(previous_colors), {
        #     'rcp': rcp,
        #     'rcwp': rcwp
        # })
        # new_all_comb = request.session['all_combinations']
        # new_all_comb.remove(ai_code)
        # request.session['all_combinations'] = new_all_comb
        validated, result = mastermind_utils.get_response_from_code(tuple(user_colors), tuple(ai_code), isUser=False)


    context = {
        'round': int(round) + 1,
        'new_ai_colors': ai_code,
        'hasAiWon': hasAiWon,
        'isGameCompleted': isGameCompleted,
        'gamestatusText': gamestatusText,
        'rcp': result['rcp'],
        'rcwp': result['rcwp']
    }

    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')


def check_colors(request, ronde, ai_comb, colors):
    if int(ronde) < 8:
        ai_comb = tuple(ast.literal_eval(str(ai_comb).replace('&quot;', "'")))
        user_comb = tuple(colors.split(','))
        print(f'AI: {ai_comb}\nME: {user_comb}')
        context = {
            'isGameCompleted': False,
            'isWon': False,
            'round': int(ronde) + 1,
        }
        # if tuple(ai_comb) != tuple(user_comb):
        validated, result = mastermind_utils.get_response_from_code(tuple(ai_comb), tuple(user_comb), isUser=False)
        context['rcp'] = result['rcp']
        context['rcwp'] = result['rcwp']
        # else:
        if tuple(ai_comb) == tuple(user_comb):
            context['isGameCompleted'] = True
            context['isWon'] = True
            context['gamestatusText'] = 'Gefeliciteerd!<br>Je hebt de juiste combinatie geraden!'

    else:
        context = {
            'isGameCompleted': True,
            'isWon': False,
            'gamestatusText': 'Helaas!<br>Je hebt in 8 rondes de combinatie niet geraden.<br>De juiste combinatie was:'
        }

    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')
