# A General A* Function and its Application to Slide Puzzles
# CS 470/670 at UMass Boston

import numpy as np
from collections import deque
import bisect

example_1_start = np.array([[2, 8, 3],
                           [1, 6, 4],
                           [7, 0, 5]])

example_1_goal = np.array([[1, 2, 3],
                           [8, 0, 4],
                           [7, 6, 5]])

example_2_start = np.array([[ 2,  6,  4,  8],
                            [ 5, 11,  3, 12],
                            [ 7,  0,  1, 15],
                            [10,  9, 13, 14]])

example_2_goal = np.array([[ 1,  2,  3,  4],
                           [ 5,  6,  7,  8],
                           [ 9, 10, 11, 12],
                           [13, 14, 15,  0]])

# For a given current state, move, and goal, compute the new state and its h'-score and return them as a pair. 
def make_node(state, row_from, col_from, row_to, col_to, goal):
    # Create the new state that results from playing the current move. 
    (height, width) = state.shape
    new_state = np.copy(state)
    new_state[row_to, col_to] = new_state[row_from, col_from]
    new_state[row_from, col_from] = 0
    
    # Count the mismatched numbers and use this value as the h'-score (estimated number of moves needed to reach the goal).
    mismatch_count = 0
    for i in range(height):
        for j in range(width):
            if new_state[i, j] > 0 and new_state[i, j] != goal[i, j]:
                mismatch_count += 1
   
    return (new_state, mismatch_count)

# For given current state and goal state, create all states that can be reached from the current state
# (i.e., expand the current node in the search tree) and return a list that contains a pair (state, h'-score)
# for each of these states.   
def slide_expand(state, goal):
    node_list = []
    (height, width) = state.shape
    (empty_row, empty_col) = np.argwhere(state == 0)[0]     # Find the position of the empty tile
    
    # Based on the position of the empty tile, find all possible moves and add a pair (new_state, h'-score)
    # for each of them.
    if empty_row > 0:
        node_list.append(make_node(state, empty_row - 1, empty_col, empty_row, empty_col, goal))
    if empty_row < height - 1:
        node_list.append(make_node(state, empty_row + 1, empty_col, empty_row, empty_col, goal))
    if empty_col > 0:
        node_list.append(make_node(state, empty_row, empty_col - 1, empty_row, empty_col, goal))
    if empty_col < width - 1:
        node_list.append(make_node(state, empty_row, empty_col + 1, empty_row, empty_col, goal))
    
    return node_list
  
# TO DO: Return either the solution as a list of states from start to goal or [] if there is no solution.               
def a_star(start, goal, expand):
    currentState = start
    openCycle, closedCycle, resultState, fcount, misplacedCount = [], [], [], 0, 0  # initialize
    height, width = start.shape
    for i in range(height):
        for j in range(width):
            if currentState[i, j] > 0 and currentState[i, j] != goal[i, j]:
                indexSol = np.argwhere(goal == currentState[i,j])
                distCount=abs(indexSol[0][0]-i) + abs(indexSol[0][1]-j)     # manhattan distance
                misplacedCount += distCount
    closedCycle.append((start, misplacedCount))
    minCount = misplacedCount  
    while minCount:  # loop till misplaced tile count is 0
        possibilities = expand(currentState, goal)  # store children (possibilities) for current node
        if openCycle:
            closedCycle = openCycle
        fcount += 1 
        lenOfPossibilities = len(possibilities)
        possibleSolutions = []
        for i in range(lenOfPossibilities):
            poss = list(possibilities[i])
            poss[1] += fcount
            possibleSolutions.append(poss)
        openCycle = possibleSolutions  # append all possible states to open 
        lenOfPossibileSoln = len(possibleSolutions)
        hscore = []
        for i in range(lenOfPossibileSoln):
            hscore.append(possibleSolutions[i][1])  # match h score to each possible state
        minVal = min(hscore)
        lenPrev = len(closedCycle)
        fscore = []
        for i in range(lenPrev):
            fscore.append(closedCycle[i][1])  # match f score
        minF = min(fscore)
        if minF <= minVal:
            k = hscore.index(min(hscore))
            currentState = possibleSolutions[k][0]
        else:
            k = fscore.index(min(fscore))
            currentState = closedCycle[k][0]
            fcount -= 1
        minCount = possibilities[k][1]
        resultState.append(currentState)  
    return resultState

# Find and print a solution for a given slide puzzle, i.e., the states we need to go through 
# in order to get from the start state to the goal state.
def slide_puzzle_solver(start, goal):
    solution = a_star(start, goal, slide_expand)
    if len(solution) == 0:
        print('This puzzle has no solution. Please stop trying to fool me.')
        return
        
    (height, width) = start.shape
    if height * width >= 10:            # If numbers can have two digits, more space is needed for printing
        digits = 2
    else:
        digits = 1
    horizLine = ('+' + '-' * (digits + 2)) * width + '+'
    for step in range(len(solution)):
        state = solution[step]
        for row in range(height):
            print(horizLine)
            for col in range(width):
                print('| %*d'%(digits, state[row, col]), end=' ')
            print('|')
        print(horizLine)
        if step < len(solution) - 1:
            space = ' ' * (width * (digits + 3) // 2)
            print(space + '|)
            print(space + 'V')

slide_puzzle_solver(example_1_start, example_1_goal)       # Find solution to example_1


