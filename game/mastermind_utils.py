import random

valid_colors = ['yellow', 'green', 'white', 'black', 'red', 'blue']


# Return random pin combination (used only for the gamemode where the AI picks a color-combination
def get_random_pin_combination():
    return [valid_colors[random.randint(0, len(valid_colors) - 1)] for e in range(4)]


# Returns a dictionary with 2 elements. These are:
#     - RCP: Right color and place (white pins). Also known as the 1 in (1, 0)
#     - RCWP: Right color wrong place (red pins). Also known as the 0 in (1, 0)
# These values are returned in a dictionary because this will be easier to translate to JSON and then to JavaScript
# which happens a lot in DJango
def get_response_from_code(main_list, submitted_list):
    result = validate_user_response(tuple(main_list), tuple(submitted_list))
    return result


def validate_user_response(main_tuple, submitted_tuple):
    # Declare vars
    counted_rcp = 0
    counted_rcwp = 0
    rcwp_main_list = list(main_tuple).copy()
    rcwp_submitted_list = list(submitted_tuple).copy()
    iterator_rcwp = 0

    # This counts the RCP aka the Pins in the right place with the right color (white pins)
    for i in range(len(main_tuple)):
        # get a pin from the given submitted combination with the same index
        ai_pin_rcp = submitted_tuple[i]
        user_pin = main_tuple[i]
        # now we can compare the 2 pins with eachother
        if ai_pin_rcp == user_pin:
            # if they math: update score and remove pins from list as we dont need these anymore
            del rcwp_main_list[i - counted_rcp]
            del rcwp_submitted_list[i - counted_rcp]
            counted_rcp += 1

    # This counts the rcwp (red pins)
    while iterator_rcwp != len(rcwp_main_list):
        # get pin from list
        submitted_pin_rcwp = rcwp_submitted_list[iterator_rcwp]

        # Check if this pin is seen in the list with the correct pin-combination
        if submitted_pin_rcwp in rcwp_main_list:
            # Remove pin from list as we dont need to check this anymore
            del rcwp_submitted_list[iterator_rcwp]
            rcwp_main_list.remove(submitted_pin_rcwp)
            # reset iterator and update counter
            iterator_rcwp = 0
            counted_rcwp += 1
        else:
            iterator_rcwp += 1

    # return results
    result = {
        'rcp': counted_rcp,
        'rcwp': counted_rcwp
    }

    return result


def get_all_combinations():
    # create a combination (color set) with 4 placeholder colors
    color_set = [valid_colors[0]] * 4
    # empty list to add all the color combinations to
    combinations = []
    # Loop through all valid colors (6 in the standard case)
    # (6^1)
    for i in range(len(valid_colors)):
        # assign the fourth color to a new one
        color_set[3] = valid_colors[i]
        # Loop again (6^2)
        for j in range(len(valid_colors)):
            # assign the third color to a new one
            color_set[2] = valid_colors[j]
            # loop again (6^3)
            for k in range(len(valid_colors)):
                # Assign the second color to a new one
                color_set[1] = valid_colors[k]
                # Loop again (6^4) which equals = 1296 aka the max amount of unique combinations
                for l in range(len(valid_colors)):
                    color_set[0] = valid_colors[l]
                    # add color_set to list as atleast one value has been updated every iteration (obviously)
                    combinations.append(color_set.copy())

    # I know this function could've been implemented a lot shorter (and more efficient)
    # But I wanted to show how I filled the list with the unqiue values using 6 to the power of 4

    # return the list sorted. This is also stated in the paper
    return sorted(combinations)


# Code for the simple strategy
def get_simple_strategy(all_combinations, previous_code, previous_code_result):
    # we return a random one from the list
    accepted_codes = get_same_values_results(all_combinations, previous_code, previous_code_result)
    return accepted_codes[random.randint(0, len(accepted_codes) - 1)]

# get list filled with the same results as given
def get_same_values_results(combinations, secondary_code, main_code_result, swap_comparisons=False):
    codes = []
    main_rcp = int(main_code_result['rcp'])
    main_rcwp = int(main_code_result['rcwp'])
    for code in combinations:
        # get result (rcp and rcwp) from code in iteration of all_combinations
        if swap_comparisons:
            result = get_response_from_code(secondary_code, code)
        else:
            result = get_response_from_code(code, secondary_code)
        rcp = int(result['rcp'])
        rcwp = int(result['rcwp'])
        # if the results match, add them to the list
        if rcp == main_rcp and rcwp == main_rcwp:
            codes.append(code)
    # Now we have a list with all the unqiue combinations which give the same result as that my previous code got
    return codes

# fill list with all results from code-comparison
def fill_scores(all_combinations, logicalGuessesList, allValidScores, all_remaining_combinations, all_scores):
    for code_all_combinations in all_combinations:
        if code_all_combinations not in logicalGuessesList:

            # Keeps track the count of certain rcp and rcwp combinations
            counter = [0] * len(allValidScores)

            # for all guesses in all_remaining_combinations,
            # get its result if the unused guess is in the all_combinations list
            # Increase the counter by 1 on the position of its values.
            for code_remaining_combinations in all_remaining_combinations:
                inner_result = get_response_from_code(code_remaining_combinations, code_all_combinations)
                counter[allValidScores.index((int(inner_result['rcp']), int(inner_result['rcwp'])))] += 1
            # calculate the score for the current unused guess
            # fill list with all scores and the count of them
            all_scores.append(len(all_remaining_combinations) - max(counter))
        else:
            all_scores.append(0)

    return all_scores

# Worst case aka Knuth strategy
def get_knuth_strategy(user_code, previous_guess):
    # this is used to remove duplicates from final list later-on
    original_guess = tuple(list(previous_guess).copy())

    # create a list with only valid scores
    allScoresTemp = []
    for i in range(5):
        for j in range(0, 4 - i + 1):
            allScoresTemp.append((i, j))
    allValidScores = allScoresTemp[:len(allScoresTemp) - 2] + allScoresTemp[len(allScoresTemp) - 1:]

    # Create a list of all logical guesses. We first add our previous guess
    # (in the first instance it is the initial guess aka AABB)
    logicalGuessesList = [previous_guess]  # AABB

    # Get results. RCP and RCWP from previous guess
    result = get_response_from_code(user_code, previous_guess)
    rcp = result['rcp']

    # all the 1296 possible codes
    all_combinations = get_all_combinations()

    # the list contains all remaining possible solutions. This is copied instead for faster runtime
    all_remaining_combinations = all_combinations.copy()
    # while we dont have the right answer
    while rcp != 4:

        # temp is filled with unique answers with the same results
        same_results = get_same_values_results(all_remaining_combinations, previous_guess, result, swap_comparisons=True)
        all_remaining_combinations = same_results.copy()
        # all_scores is a list of scores for each guess in all_combinations
        all_scores = fill_scores(all_combinations, logicalGuessesList, allValidScores, all_remaining_combinations, [] * len(all_combinations))


        # find all indices with the max score
        # Get score which has the most occurrences
        maxScore = max(all_scores)

        # get index of max score, this will be used to slice list later on
        indices = [i for i, x in enumerate(all_scores) if x == maxScore]

        # if any guesses corresponds to the indices is in all_remaining_combinations,
        # use that as the next guess
        change = False
        for i in range(len(indices)):
            if all_combinations[indices[i]] in all_remaining_combinations:
                previous_guess = all_combinations[indices[i]]
                change = True
                break

        # else use the smallest guess as next guess
        if change == False:
            previous_guess = all_combinations[indices[0]]

        logicalGuessesList.append(previous_guess)
        result = get_response_from_code(user_code, previous_guess)
        rcp = result['rcp']

    # remove original guess from list so we dont ask again
    if original_guess in logicalGuessesList:
        logicalGuessesList.remove(original_guess)

    # return the list shuffled
    random.shuffle(logicalGuessesList)
    return logicalGuessesList


# Retrieve an AABB style code
def get_random_logical_start():
    colors = (valid_colors.copy())
    # Add 2 random colors from the validcolors list
    code = [colors[random.randint(0, len(colors) - 1)]] * 2
    # remove the previously added color (this prevents duplicates)
    colors.remove(code[0])
    # Add another 2 colors
    code += [colors[random.randint(0, len(colors) - 1)]] * 2
    return code
