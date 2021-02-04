from random import randint

valid_colors = ['yellow', 'green', 'white', 'black', 'red', 'blue']

def isValidOpstelling(opstelling):
    try:
        pins = str(opstelling).split(',')
        if len(pins) != 4:
            return False
        for pin in pins:
            if pin.lower().strip() not in valid_colors:
                return False
        return True
    except ValueError:
        return False


def opstellingValidation():
    isValid = False
    while not isValid:
        print('\nKies uw opstelling. U heeft de keuze uit de kleuren: Blauw, Geel, Groen, Rood, Wit, Zwart.')
        print('Voorbeeld: Rood, Wit, Zwart, Zwart\n')
        opstelling = input('Opstelling: ')
        isValid = isValidOpstelling(opstelling)
        if not isValid:
            print("U heeft geen geldige opstellen ingevoerd. Denk aan de comma's!")
        else:
            return opstelling

def get_tuple_from_string(opstelling):
    pin_list = []
    for pin in opstelling.split(','):
        pin_list.append(pin.lower().strip())
    return tuple(pin_list)

def get_code_user():
    keuzes = opstellingValidation()
    return get_tuple_from_string(keuzes)

def get_random_pin_combination():
    # TODO: Implement logic! (Algorithm from study?)
    return [valid_colors[randint(0, len(valid_colors)-1)] for e in range(4)]

def get_response_from_code(user_code, ai_code, isUser=True):
    validated, result = False, None
    while not validated:
        if isUser:
            right_color_place = get_safe_input_int('\nHoeveel pins zitten op de juiste plek én hebben de juiste kleur? ', 'Alleen een nummer invoeren aub.')
            right_color_wrong_place = get_safe_input_int('Hoeveel pins hebben de juiste kleur maar zitten op de verkeerde plek? ', 'Alleen een nummer invoeren aub.')
            validated, result = validate_user_response(user_code, ai_code, rcp=right_color_place, rcwp=right_color_wrong_place)
        else:
            validated, result = validate_user_response(user_code, ai_code)
        if not validated:
            print('Iets lijkt niet te kloppen. Kijk aub nog eens goed!')
    return validated, result

def validate_user_response(user_code, ai_code, rcp=None, rcwp=None):
    if rcp is not None and rcwp is not None:
        if rcp == 4 and user_code != ai_code:
            # print(1)
            return False, None
        if rcp != 4 and user_code == ai_code:
            # print(2)
            return False, None
        if rcp == 3 and rcwp == 1:
            # print(3)
            return False, None

    calculated_rcp = 0
    calculated_rcwp = 0
    rcwp_user_check_list = list(user_code).copy()
    rcwp_ai_check_list = list(ai_code).copy()

    for i in range(len(user_code)):
        print(f'{ai_code}\n{user_code}')
        ai_pin_rcp = ai_code[i]
        user_pin = user_code[i]
        # print(f'\nRCP: Checking if {ai_pin_rcp} == {user_pin} with index: {i}')
        if ai_pin_rcp == user_pin:
            # print(f'RCP: {rcwp_user_check_list} {rcwp_ai_check_list} Deleting index: {i-calculated_rcp}')
            del rcwp_user_check_list[i-calculated_rcp]
            del rcwp_ai_check_list[i-calculated_rcp]
            calculated_rcp += 1

    # print(f'\nList after RCP: {rcwp_user_check_list} {rcwp_ai_check_list}')
    if rcp is not None and rcwp is not None:
        if calculated_rcp != rcp:
            # print(f'Calculated rcp = {calculated_rcp}, user rcp = {rcp}')
            # print(4)
            return False, None

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
            return False, None

    result = {
        'rcp': calculated_rcp,
        'rcwp': calculated_rcwp
    }

    return True, result

def get_safe_input_int(question, exception_text):
    answer = None
    while answer is None:
        try:
            answer = int(input(question))
            return answer
        except ValueError:
            print(exception_text)
