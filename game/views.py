from django.shortcuts import render, HttpResponse
from game import mastermind_utils
import json, ast


# Loads the index page (homepage)
def index(request):
    return render(request, 'index.html')


# Loads the page to the gamemode player vs ai
def player_vs_ai(request):
    # get a random combination. This is code the user has to guess.
    ai_combination = mastermind_utils.get_random_pin_combination()
    # return to template with the added data
    return render(request, 'player_vs_ai.html', {
        'ai_combination': json.dumps(ai_combination),
    })


# Load page with gamemode ai vs player
def ai_vs_player(request):
    return render(request, 'ai_vs_player.html')


# This runs when the player submits color for the ai to guess. This only runs once in a game of ai vs player
def submit_colors(request, ronde, colors):
    # Add a list with all possible combinations to the session (kindoff like a mini-database)
    request.session['all_combinations'] = mastermind_utils.get_all_combinations()
    # convert the user_colors to a python tuple. The data is given from Javascript so there are some quotation issues..
    user_colors = tuple(str(colors).replace('&quot;', "'").split(','))

    # get a combination like AABB to start with
    ai_code = mastermind_utils.get_random_logical_start()

    # Gather some data
    hasAiWon = tuple(ai_code) == tuple(user_colors)
    isGameCompleted = ronde == 8

    # get result. This is a dict because it is easier to parse though to JavaScript.
    result = mastermind_utils.get_response_from_code(ai_code, user_colors)

    # place all values in a dict
    context = {
        'round': int(ronde) + 1,
        'user_colors': colors,
        'ai_code': ai_code,
        'hasAiWon': hasAiWon,
        'isGameCompleted': isGameCompleted,
        'rcp': result['rcp'],
        'rcwp': result['rcwp'],
    }

    # convert to JSON
    data = json.dumps(context)
    # return JSON back to the template. This function was called via Ajax which is why the page doesnt reload. its async!
    return HttpResponse(data, content_type='application/json')


# This will run every time the user has submitted its feedback on the ai
def submit_feedback(request, round, colors, previous_code, alg_type):
    user_code = tuple(str(colors).replace('&quot;', "'").split(','))
    previous_code = tuple(previous_code.split(","))

    # default values for if the game is over, these cannot be assigned
    ai_code = None
    result = {'rcp': None, 'rcwp': None}

    # check game status
    hasAiWon = previous_code == user_code
    isGameCompleted = round == 8
    gamestatusText = ''

    # if the game is over, see what text should be displayed
    if hasAiWon:
        isGameCompleted = True
        gamestatusText = 'Helaas!<br>De AI heeft uw code geraden!'
    elif isGameCompleted:
        gamestatusText = 'Gefeliciteerd!<br>De AI kon u niet verslaan!'

    elif not isGameCompleted:
        # if the game is not over, check to see which algorithm should be used
        if alg_type == 'simple':
            print('Simple')
            ai_code = get_ai_code(0, request, user_code, previous_code, round)

        elif alg_type == 'worst-case':
            print('Worst-case')
            ai_code = get_ai_code(1, request, user_code, previous_code, round)

        else:
            print('Cliffhanger')
            ai_code = get_ai_code(2, request, user_code, previous_code, round)

        print(f'Returning new code to temlate: {ai_code}')
        result = mastermind_utils.get_response_from_code(user_code, ai_code)

    # create a dict with all the values
    context = {
        'round': int(round) + 1,
        'new_ai_colors': ai_code,
        'hasAiWon': hasAiWon,
        'isGameCompleted': isGameCompleted,
        'gamestatusText': gamestatusText,
        'rcp': result['rcp'],
        'rcwp': result['rcwp']
    }

    # convert to JSON
    data = json.dumps(context)
    # return data to template
    return HttpResponse(data, content_type='application/json')


# Check the colors. This function is called from the player vs ai gamemode
def check_colors(request, ronde, ai_comb, colors):
    # if the game still has rounds leftover
    if int(ronde) < 8:
        # convert the ai combination into a python-tuple
        ai_comb = tuple(ast.literal_eval(str(ai_comb).replace('&quot;', "'")))
        # same for user_combination..
        user_comb = tuple(colors.split(','))

        # create a dict with value we will passon later
        context = {
            'isGameCompleted': False,
            'isWon': False,
            'round': int(ronde) + 1,
        }

        # get result (dict with the amound of white and red pins) from this combination
        result = mastermind_utils.get_response_from_code(ai_comb, user_comb)

        # add these to the 'main dict'
        context['rcp'] = result['rcp']
        context['rcwp'] = result['rcwp']

        # checking gamestate
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
    # convert to json and return to template
    data = json.dumps(context)
    return HttpResponse(data, content_type='application/json')


# little function to return the ai code in the gamemode ai vs player
def get_ai_code(alg_type, request, user_code, previous_code, round):
    if alg_type == 0:
        # SIMPLE

        ai_code = mastermind_utils.get_simple_strategy(request.session['all_combinations'], previous_code, user_code)
        # gather list from session, remove the current guess so we dont get duplicates, and store back
        new_all_comb = request.session['all_combinations']
        new_all_comb.remove(ai_code)
        request.session['all_combinations'] = new_all_comb

        return ai_code
    elif alg_type == 1:
        # KNUTH, WORST-CASE
        try:
            # get list from session
            knuth_list = request.session['knuth_list']
            if len(knuth_list) == 0 or round == 1:
                # if this is a new game we cant use a list from an older session we raise an error to create a new list
                raise KeyError
        except KeyError:
            # get a new list
            knuth_list = mastermind_utils.get_knuth_strategy(user_code, previous_code)
        # remove current element from list and store it back in the session
        # if we already have a list in the session we dont bother calculating the ai moves again. We just take the next move
        # When we generate a list we generate all the moves at once to save up on runtime
        ai_code = knuth_list.pop(0)
        request.session['knuth_list'] = knuth_list
        return ai_code
    elif alg_type == 2:
        # CLIFFHANGER
        # This algorithm which I though of myself always uses all the gameround. It is designed to make the user think it has won
        # and right when the last round is upon the user the algoprithm pulls out the right guess!
        try:
            # get list from session
            codes = request.session['cliffhanger_codes']
            if len(codes) == 0 or round == 1:
                print('raising error')
                # if this is a new game we cant use a list from an older session we raise an error to create a new list
                raise KeyError
        except KeyError:
            codes = mastermind_utils.cliffhanger_strategy(user_code, previous_code)
        # remove current element from list and store it back in the session
        # if we already have a list in the session we dont bother calculating the ai moves again. We just take the next move
        # When we generate a list we generate all the moves at once to save up on runtime
        ai_code = codes.pop(0)
        request.session['cliffhanger_codes'] = codes
        return ai_code
