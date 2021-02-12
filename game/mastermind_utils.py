import math, random

valid_colors = ['yellow', 'green', 'white', 'black', 'red', 'blue']

def get_random_pin_combination():
    return [valid_colors[random.randint(0, len(valid_colors) - 1)] for e in range(4)]


def get_response_from_code(main_list, submitted_list):
    result = validate_user_response(tuple(main_list), tuple(submitted_list))
    return result


def validate_user_response(main_tuple, submitted_tuple, rcp=None, rcwp=None):
    if rcp is not None and rcwp is not None:
        if rcp == 4 and main_tuple != submitted_tuple:
            return False, None
        if rcp != 4 and main_tuple == submitted_tuple:
            return False, None
        if rcp == 3 and rcwp == 1:
            return False, None

    calculated_rcp = 0
    calculated_rcwp = 0
    rcwp_user_check_list = list(main_tuple).copy()
    rcwp_ai_check_list = list(submitted_tuple).copy()

    for i in range(len(main_tuple)):
        # print(f'{ai_code}\n{user_code}')
        ai_pin_rcp = submitted_tuple[i]
        user_pin = main_tuple[i]
        # print(f'\nRCP: Checking if {ai_pin_rcp} == {user_pin} with index: {i}')
        if ai_pin_rcp == user_pin:
            # print(f'RCP: {rcwp_user_check_list} {rcwp_ai_check_list} Deleting index: {i-calculated_rcp}')
            del rcwp_user_check_list[i - calculated_rcp]
            del rcwp_ai_check_list[i - calculated_rcp]
            calculated_rcp += 1

    # print(f'\nList after RCP: {rcwp_user_check_list} {rcwp_ai_check_list}')
    if rcp is not None and rcwp is not None:
        if calculated_rcp != rcp:
            # print(f'Calculated rcp = {calculated_rcp}, user rcp = {rcp}')
            return None

    iterator_rcwp = 0
    while iterator_rcwp != len(rcwp_user_check_list):
        # print(f'User: {rcwp_user_check_list}')
        # print(f'AI:   {rcwp_ai_check_list}')
        ai_pin_rcwp = rcwp_ai_check_list[iterator_rcwp]
        # print(f'Checking if {ai_pin_rcwp} is in {rcwp_user_check_list} with index {iterator_rcwp}')
        if ai_pin_rcwp in rcwp_user_check_list:
            del rcwp_ai_check_list[iterator_rcwp]
            rcwp_user_check_list.remove(ai_pin_rcwp)
            iterator_rcwp = 0
            calculated_rcwp += 1
        else:
            iterator_rcwp += 1

    # print(f'List after RCWP: {rcwp_user_check_list} {rcwp_ai_check_list}')
    if rcp is not None and rcwp is not None:
        if calculated_rcwp != rcwp:
            # print(f'Calculated rcwp = {calculated_rcwp}, user rcwp = {rcwp}')
            return None

    result = {
        'rcp': calculated_rcp,
        'rcwp': calculated_rcwp
    }

    return result


def get_all_combinations():
    color_set = [valid_colors[0]] * 4
    combinations = []
    for i in range(len(valid_colors)):
        color_set[3] = valid_colors[i]
        for j in range(len(valid_colors)):
            color_set[2] = valid_colors[j]
            for k in range(len(valid_colors)):
                color_set[1] = valid_colors[k]
                for l in range(len(valid_colors)):
                    color_set[0] = valid_colors[l]
                    combinations.append(color_set.copy())
    return sorted(combinations)


def get_comb_simple_strategy(all_combinations, previous_code, previous_code_result):
    accepted_codes = []
    for code in all_combinations:
        result = get_response_from_code(tuple(code), tuple(previous_code))
        if int(previous_code_result['rcp']) == int(result['rcp']) and \
                int(previous_code_result['rcwp']) == int(result['rcwp']):
            accepted_codes.append(code)

    return accepted_codes[random.randint(0, len(accepted_codes)-1)]

def score(self, other):
    first = len([speg for speg, opeg in zip(self, other) if speg == opeg])
    return first, sum([min(self.count(j), other.count(j)) for j in valid_colors]) - first

def get_worst_case_strategy(all_combinations, user_code, previous_code, rcp, rcwp):
    allAnswers = list(all_combinations).copy()
    print(allAnswers)
    bestGuess = False
    bestScore = math.pow(6, 4)
    for guess in allAnswers:
        results = {}
        for posAnswer in allAnswers:
            # print(f'Pos: {posAnswer}')
            # print(f'Guess: {guess}')
            result = get_response_from_code(posAnswer, guess)
            results[(result['rcp'], result['rcwp'])] = 1 + results[((result['rcp'], result['rcwp']), 0)]
        score = max(results.values())
        if score < bestScore:
            bestGuess = guess
            bestScore = score
    return bestGuess

    # allAnswers = list(all_combinations).copy()
    # print(allAnswers)
    # worstGuess = False
    # worstScore = 0
    # worstResults = {}
    # for guess in allAnswers:
    #     results = {}
    #     for posAnswer in allAnswers:
    #         # print(f'Pos: {posAnswer}')
    #         # print(f'Guess: {guess}')
    #         val, res = get_response_from_code(posAnswer, guess, isUser=False)
    #         results[(res['rcp'], res['rcwp'])] = 1 + results.get((res['rcp'], res['rcwp']), 0)
    #     score = max(results.values())
    #     if score > worstScore:
    #         worstGuess = guess
    #         worstScore = score
    #         worstResults = results
    # return (worstGuess, lambda: len(allAnswers))

    # S = all_combinations.copy()
    #
    # allstemp = []
    # for i in range(5):
    #     for j in range(0, 4-i+1):
    #         allstemp.append((i, j))
    # allScore = allstemp[:len(allstemp)-2]+allstemp[len(allstemp)-1:]
    #
    # guessList = [previous_code]
    # rcp, rcwp = rcp, rcwp
    # while(rcp, rcwp) != (4, 0):
    #     temp = []
    #     cScore = []*len(all_combinations)
    #
    #     for code in S:
    #         validated, result = get_response_from_code(tuple(user_code), tuple(code), isUser=False)
    #         if int(rcp) == int(result['rcp']) and \
    #                 int(rcwp) == int(result['rcwp']):
    #             temp.append(code)
    #
    #     S = temp[:]
    #
    #     for code in all_combinations:
    #         if code not in guessList:
    #             hitCount = [0]*len(allScore)
    #             for s in S:
    #                 validated, result = get_response_from_code(tuple(user_code), tuple(code), isUser=False)
    #                 hitCount[allScore.index((result['rcp'], result['rcwp']))] += 1
    #             cScore.append(len(S)-max(hitCount))
    #         else:
    #             cScore.append(0)
    #
    #     maxScore = max(cScore)
    #
    #     indices = [i for i, x in enumerate(cScore) if x == maxScore]
    #     change = False
    #
    #     for i in range(len(indices)):
    #         if all_combinations[indices[i]] in S:
    #             guess = all_combinations[i]
    #             change = True
    #             break
    #     if change == False:
    #         guess = all_combinations[indices[0]]
    #     guessList.append(guess)
    #     validated, result = get_response_from_code(tuple(user_code), tuple(guess), isUser=False)
    #     rcp, rcwp = result['rcp'], result['rcwp']
    #
    # return guessList
    # results = [(right, wrong) for right in range(5) for wrong in range(5 - right) if not (right == 3 and wrong == 1)]
    # if len(all_combinations) == 1:
    #     ai_code = all_combinations.pop()
    # else:
    #     ai_code = max(get_all_combinations(), key=lambda x: min(sum(1 for p in all_combinations if score(p, x) != res) for res in results))
    #
    # sc = score(user_code, ai_code)
    #
    # set(all_combinations).difference_update(set(p for p in all_combinations if score(p, ai_code) != sc))
    #
    # return ai_code, all_combinations

def get_safe_input_int(question, exception_text):
    answer = None
    while answer is None:
        try:
            answer = int(input(question))
            return answer
        except ValueError:
            print(exception_text)

def get_random_logical_start():
    colors = (valid_colors.copy())
    code = [colors[random.randint(0, len(colors) - 1)]] * 2
    colors.remove(code[0])
    code += [colors[random.randint(0, len(colors) - 1)]] * 2
    return code
