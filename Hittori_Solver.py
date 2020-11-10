import numpy as np
import sys

#sys.setrecursionlimit()

'''
Short code description:
This code solves any N sized Hitori board. It does this through utilization of three boards.
Example: the main hitori board.
conflict_space: Board containing only numbers that are in conflict with others
safespace: Binary board containing information regarding if a node is safe to be crossed or not.

it also works in three different modes. The initial mode applies one time only functions as a starter
The second mode is a continous loop that switches between different functions as long as at least one of them is making 
progress per iterations. If the program exhausts it's option using these methods and no solution is reached,
it switches to the third mode. This mode is a depth first search that attempts to make applicable guesses based on 
remaining conflicts, utilizing mode two rulesets to limit search and make progress with as limited guesswork as possible.
NB: This mode intended as a last resort only in order to guarantee a solution but can increase execution time up to
several minutes. '''

example = np.matrix([   [7,	4,	8,	3,	6,	2,	7,	6,	4],
                        [2,	8,	1,	4,	5,	6,	8,	4,	7],
                        [2,	9,	7,	2,	1,	4,	2,	1,	6],
                        [3,	2,	8,	8,	7,	3,	5,	9,	1],
                        [4,	8,	5,	1,	2,	9,	3,	3,	7],
                        [7,	3,	5,	5,	4,	8,	1,	2,	6],
                        [8,	7,	6,	2,	3,	6,	2,	5,	1],
                        [9,	5,	8,	1,	1,	3,	6,	7,	8],
                        [1 ,4,	3,	7,	6,	5,	3,	8,	3]])

example = np.matrix([[4,	1,	7,	5,	8,	4,	1,	5],
[6,	3,	2,	7,	5,	2,	1,	2],
[3,	6,	1,	8,	2,	7,	5,	5],
[5,	4,	3,	6,	4,	1,	5,	8],
[5,	2,	3,	1,	1,	6,	8,	7],
[1,	7,	1,	5,	6,	5,	3,	1],
[7,	8,	2,	1,	4,	5,	4,	3],
[4,	5,	8,	4,	7,	1,	4,	6]])

example = np.matrix([[6,	3,	5,	2,	2,	6],
[2,	5,	2,	3,	4,	6],
[3,	3,	6,	4,	4,	2],
[5,	6,	4,	2,	3,	5],
[2,	3,	1,	2,	6,	3],
[4,	2,	4,	6,	1,	4]])
example = np.matrix([[4,	1,	7,	5,	8,	4,	1,	5],
[6,	3,	2,	7,	5,	2,	1,	2],
[3,	6,	1,	8,	2,	7,	5,	5],
[5,	4,	3,	6,	4,	1,	5,	8],
[5,	2,	3,	1,	1,	6,	8,	7],
[1,	7,	1,	5,	6,	5,	3,	1],
[7,	8,	2,	1,	4,	5,	4,	3],
[4,	5,	8,	4,	7,	1,	4,	6]])

example = np.matrix([[3,	1,	3,	5,	4],
[1,	1,	2,	4,	4],
[3,	2,	1,	1,	5],
[4,	3,	5,	3,	1],
 [2,	5,	1,	3,	2]])
"""initial vari"""
#example = np.matrix([[5,2,1,6,2,5],[3,1,4,2,6,6],[4,2,3,4,6,3],[4,5,6,3,2,2],[2,4,3,3,4,5],[6,4,6,5,3,3]])  # Stacc

"""initial variables"""
mShape = example.shape
shape = mShape[0]
conflict_space = np.zeros(mShape)
safeboard = np.zeros(mShape)


"""Functions. Organized chronologically in terms of references in code."""


def main()-> None:
    """main method, shifts between the three modes and rules to utilize depending on context and feedback."""
    print("Mode One - One time rules")
    conflict_check()
    init_safeboard()
    corner_init_check()
    squeeze_rules()
    progress_handler(False, True)
    print("Mode Two - iterative rules")
    while progress_handler():
        progress_handler(False, False)
        mark_check()
        if victory_checker():
            completion(True)
            break
        print(progress_handler())
        if not progress_handler():  # if progress halts, attempts more complex rules and special scenario solvers
            special_corner()
            if not progress_handler():
                separation_crawler(True)
                if not progress_handler():
                    print_debug("test")
                    occam_razor()  # starts guessing and activates mode three if necessary
        if not progress_handler():
            completion(victory_checker())


def conflict_check() ->None:
    """Copies all conflicts from the main board. Also used for updating the board and verify victory condition"""
    global conflict_space
    conflict_space = np.zeros(mShape)
    for x in range(shape):
        for y in range(shape):
            for z in range(y+1, shape):
                if example[x, y] == example[x, z]:
                    conflict_space[x, y] = example[x, y]
                    conflict_space[x, z] = example[x, z]
                if example[y, x] == example[z, x]:
                    conflict_space[y, x] = example[y, x]
                    conflict_space[z, x] = example[z, x]


def init_safeboard() ->None:
    """Binary copy of conflict space"""
    for x in range(shape):
        for y in range(shape):
            if conflict_space[x, y] != 0:
                safeboard[x, y] = 1


def corner_init_check():
    """Checks for marking according to two marking rules.
    First rule checks if three identical values are in a corner and marks the corner if True
    Second rule check for these type of situations in corners: [1,2][1,2] (in any permutation). Marks corner and inner
    corner"""
    """Rule One"""
    z = shape-1
    if example[0, 0] == example[0, 1] and example[0, 0] == example[1, 0] and example[0, 0] != 0:  # NE
        example[0, 0] = 0
        shade_neighbours(0, 0)
        print("RULE 1 NW")
    if example[0, z] == example[0, z-1] and example[0, z] == example[1, z] and example[0, z] != 0:  # NW
        example[0, z] = 0
        shade_neighbours(0, z)
        print("RULE 1 NE")
    if example[z, z] == example[z, z-1] and example[z, z] == example[z-1, z] and example[z, z] != 0:  # SE
        example[z, z] = 0
        shade_neighbours(z, z)
        print("RULE 1 SE")
    if example[z, 0] == example[z, 1] and example[z, 0] == example[z-1, 0] and example[z, 0] != 0:  # SW
        example[z, 0] = 0
        shade_neighbours(z, 0)
        print("RuLE 1 SW")

    """Rule Two"""
    if (example[0, 0] == example[0, 1] or example[0, 0] == example[1, 0]) \
        and (example[1, 1] == example[0, 1] or example[1, 1] == example[1, 0])\
            and (example[0, 0] != example[1, 1]):  # NE
        example[0, 0] = 0
        example[1, 1] = 0
        shade_neighbours(1, 1)
        print("RULE 2 NW")
    if (example[0, z] == example[0, z-1] or example[0, z] == example[1, z]) \
        and (example[1, z-1] == example[0, z-1] or example[1, z-1] == example[1, z]) \
            and (example[0, z] != example[1, z-1]):  # NW
        example[0, z] = 0
        example[1, z-1] = 0
        shade_neighbours(1, z - 1)
        print("RULE 2 NE")
    if (example[z, z] == example[z, z-1] or example[z, z] == example[z-1, z]) \
        and (example[z-1, z-1] == example[z-1, z] or example[z-1, z-1] == example[z, z-1]) \
            and (example[z, z] != example[z-1, z-1]):  # SE
        example[z, z] = 0
        example[z-1, z-1] = 0
        shade_neighbours(z - 1, z - 1)
        print("RULE 2 SE")
    if (example[z, 0] == example[z, 1] or example[z, 0] == example[z-1, 0]) \
        and (example[z-1, 1] == example[z, 1] or example[z-1, 1] == example[z-1, 0]) \
            and (example[z, 0] != example[z-1, 1]):  # SW
        example[z, 0] = 0
        example[z-1, 1] = 0
        shade_neighbours(z - 1, 1)
        print("RULE 2 SW")
    conflict_check()


def squeeze_rules() -> None:
    """Checks for squeezed variables (4_2_4), which signify a safe mark in the middle
     and rule of three (4_4_4), which signifies a crossing of edge values. Updates conflict_board when done."""
    for x in range(shape):
        for y in range(1, shape-1):
            # Vertical check
            if conflict_space[x, y+1] == conflict_space[x, y-1] and conflict_space[x, y+1] != 0:
                if conflict_space[x, y] == conflict_space[x, y+1]:
                    example[x, y + 1] = 0
                    shade_neighbours(x, y + 1)
                    example[x, y - 1] = 0
                    shade_neighbours(x, y - 1)
                else:
                    safeboard[x, y] = 0
            # Horizontal check
            if conflict_space[y+1, x] == conflict_space[y-1, x] and conflict_space[y+1, x] != 0:
                if conflict_space[y, x] == conflict_space[y+1, x]:
                    example[y+1, x] = 0
                    shade_neighbours(y + 1, x)
                    example[y-1, x] = 0
                    shade_neighbours(y - 1, x)
                else:
                    safeboard[y, x] = 0
    conflict_check()


def progress_handler(operation: bool = True, setstate: bool = False) -> bool:
    """Progress value is used to determine if program need to switch ruleset or determine progress.
    operation defines read if true, write if false. Setstate defines what to write.
    Used by most function to indicate that it has done an operation"""
    global progress
    if operation:
        return progress
    else:
        if setstate:
            progress = True
        else:
            progress = False
    return progress


def mark_check() -> None:
    """First level iterative checker. Iterates through whole conflict_space and checks for each cell. If the value of
    the cell is not marked as safe (i.e. cannot me crossed,1), and it is only in conflict with one other cell then
    it marks itself. Includes horizontal and vertical check."""
    for i in range(shape):
        y = i
        can_mark = False
        conflict_counter = 0

        # Horizontal Check
        for j in range(shape):
            x = j
            for z in range(shape):
                if conflict_space[x, y] == conflict_space[z, y] and x != z and conflict_space[x, y] != 0:
                    if safeboard[z, y] == 0:
                        can_mark = True
                        conflict_counter += 1
                    else:
                        conflict_counter += 1
            if can_mark and conflict_counter < 2 and safeboard[x, y] != 0 and no_neighbour(x, y):
                print("Horizontal: conflict_counter at", conflict_counter, "so it is going to mark ", x, ",", y)
                example[x, y] = 0
                conflict_space[x, y] = 0
                shade_neighbours(x, y)
                conflict_check()
                progress_handler(False, True)
            conflict_counter = 0
            can_mark = False

        # Vertical Check
        x = i
        for j in range(shape):
            y = j
            for z in range(shape):
                if conflict_space[x, y] == conflict_space[x, z] and y != z and conflict_space[x, y] != 0:
                    if safeboard[x, z] == 0:
                        can_mark = True
                        conflict_counter += 1
                    else:
                        conflict_counter += 1
            if can_mark and conflict_counter < 2 and safeboard[x, y] != 0 and no_neighbour(x, y):
                print("Vertical: conflict_counter at", conflict_counter, "so it is going to mark ", x, ",", y)
                example[x, y] = 0
                conflict_space[x, y] = 0
                shade_neighbours(x, y)
                conflict_check()
                progress_handler(False, True)
            conflict_counter = 0
            can_mark = False


def no_neighbour(x: int, y: int) -> bool:
    """Checks if neighbours to cell is crossed. Return False if neighbour, True if not."""
    if not wall_check(x, y-1, False):
        if example[x, y-1] == 0:
            return False
    if not wall_check(x, y+1, False):
        if example[x, y+1] == 0:
            return False
    if not wall_check(x+1, y, False):
        if example[x+1, y] == 0:
            return False
    if not wall_check(x-1, y, False):
        if example[x-1, y] == 0:
            return False
    return True


def wall_check(x: int, y: int, state: bool) -> bool:
    """Check where a cell(x,y). State defines mode.
    State(T): Checks cell is at a wall
    State(F): Checks if cell would be outside shape. Nullpoint exception checker in other words."""
    if state:
        if x == 0 or x == shape-1 or y == 0 or y == shape-1:
            return True
    else:
        if x < 0 or x >= shape or y < 0 or y >= shape:
            return True
    return False


def shade_neighbours(x: int, y: int) -> None:
    """ Based on input coords, mark surrounding cells and itself as safe in the safe_board """
    if x > 0:
        safeboard[x-1, y] = 0
    if x < shape-1:
        safeboard[x+1, y] = 0
    if y > 0:
        safeboard[x, y-1] = 0
    if y < shape-1:
        safeboard[x, y+1] = 0
    safeboard[x, y] = 0


def victory_checker() -> bool:
    """Verifies if victory is reached. Requires that conflict_space is empty and separation crawler to not find any
    divided partitions. Returns True if victory is reached, False if not"""
    conflict_check()
    for x in range(shape):
        for y in range(shape):
            if conflict_space[x, y] != 0:
                return False
    if separation_crawler(False):
        return False
    return True


def completion(state: bool) -> None:
    """Writes end output. state determines if solution(T) or failure(F) output. Ends program."""
    if state:
        print("Solution is reached. Zero represents marked nodes")
        print_debug("checkstate")
        print("Preferred output:")
        for y in range(shape):
            for x in range(shape):
                if example[y, x] == 0:
                    print("X", end='')
                else:
                    print(example[y, x], end='')
    else:
        print("I'm a big dumb dumb and this is where I am stuck.")
        print(example)
        print("Conflict Board state:")
        print(conflict_space)
        print("safeboard state:")
        print(safeboard)
    exit()


def special_corner() -> None:
    """Mode two rule, rarer situations. This one marks the corner if it is in conflict two direct spaces away and inner 
    corner is marked.Avoids getting blocked in."""
    if example[1, 1] == 0:  # NW
        if conflict_space[0, 0] == conflict_space[0, 2] and conflict_space[2, 0] == conflict_space[0, 0] \
                and conflict_space[0, 0] != 0:
            example[0, 0] = 0
            safeboard[0, 0] = 0
            progress_handler(False, True)
            
    if example[1, shape-2] == 0:  # NE
        if conflict_space[0, shape-1] == conflict_space[0, shape-3] and \
                conflict_space[2, shape-1] == conflict_space[0, shape-1] and conflict_space[0, shape-1] != 0:
            example[0, shape-1] = 0
            safeboard[0, shape-1] = 0
            progress_handler(False, True)
            
    if example[shape-2, shape-2] == 0:  # SE
        if conflict_space[shape-1, shape-1] == conflict_space[shape-1, shape-3] and \
                conflict_space[shape-1, shape-1] == conflict_space[shape-3, shape-1] \
                and conflict_space[shape-1, shape-1] != 0:
            example[shape-1, shape-1] = 0
            safeboard[shape-1, shape-1] = 0
            progress_handler(False, True)
            
    if example[shape-2, 1] == 0:  # SW
        if conflict_space[shape-1, 0] == conflict_space[shape-1, 2] and \
                conflict_space[shape-1, 0] == conflict_space[shape-3, 0] and conflict_space[shape-1, 0] != 0:
            example[shape-1, 0] = 0
            safeboard[shape-1, 0] = 0
            progress_handler(False, True)
    if progress_handler(True, False):
        conflict_check()


def separation_crawler(mode: bool) -> bool:
    """Crawler method for checking for blocked section. Mode determines function.
    Mode True: The code checks if crossing any conflict cell would wall off sections. Marks them safe if not
    Mode False: Verifies that solution is without separations. Returns True if it rejects solution"""
    for x in range(shape):
        for y in range(shape):
            if mode:
                if conflict_space[x, y] != 0 and safeboard[x, y] == 1:
                    if walled_in(x, y):
                        safeboard[x, y] = 0
                        print("Cell will create separation if marked. Marked safe:", x, ",", y)
                        progress_handler(False, True)
            else:
                if example[x, y] == 0:
                    if walled_in(x, y):
                        print("Solution Rejected, separated areas")
                        return True


def walled_in(x: int, y: int) -> bool:
    """Checks if cell(x,y) will get separated if it is crossed. Checks this searching diagonally for crossed cells
    uses markTravel() to go beyond initial state. Requires two different connections to fail. One if at a wall
    Returns True if it cell will result in separation. False if the cell does not find any blockage"""
    threshold = 2
    level = 0
    if wall_check(x, y, True):
        threshold = 1
    if not wall_check(x-1, y+1, False):
        if example[x-1, y+1] == 0:
            if mark_traveller(x-1, y+1, "SW"):
                level += 1
                if level >= threshold:
                    return True
    if not wall_check(x - 1, y - 1, False):
        if example[x - 1, y - 1] == 0:
            if mark_traveller(x - 1, y - 1, "SE"):
                level += 1
                if level >= threshold:
                    return True
    if not wall_check(x + 1, y - 1, False):
        if example[x + 1, y - 1] == 0:
            if mark_traveller(x + 1, y - 1, "NE"):
                level += 1
                if level >= threshold:
                    return True
    if not wall_check(x + 1, y + 1, False):
        if example[x + 1, y + 1] == 0:
            if mark_traveller(x + 1, y + 1, "NW"):
                level += 1
                if level >= threshold:
                    return True
    return False


def mark_traveller(x: int, y: int, origin: str) -> bool:
    """Recursive function that performs most of the search operations for the separation crawler.
    Uses cell information to search for next crossed out sell to investigate or if a wall is hit. Origin makes sure
    that it doesn't backtrack. Returns true if wall is found. False if not"""
    if "NE" not in origin:
        if wall_check(x - 1, y + 1, False):
            return True
        elif example[x-1, y+1] == 0:
            if mark_traveller(x-1, y+1, "SW"):
                return True
    if "NW" not in origin:
        if wall_check(x - 1, y - 1, False):
            return True
        elif example[x-1, y-1] == 0:
            if mark_traveller(x-1, y-1, "SE"):
                return True
    if "SW" not in origin:
        if wall_check(x + 1, y - 1, False):
            return True
        elif example[x+1, y-1] == 0:
            if mark_traveller(x+1, y-1, "NE"):
                return True
    if "SE" not in origin:
        if wall_check(x + 1, y + 1, False):
            return True
        elif example[x+1, y+1] == 0:
            if mark_traveller(x+1, y+1, "NW"):
                return True
    return False


def occam_razor() -> None:
    """This is mode three. The system has now determined that it cannot solve it with the rules available and needs
    to start guessing. Creates a list of all cells left in conflict and does one last test. If crossing one with the
    most conflicts doesn't solve it, it switches mode into a depth first search function that iterates over all
    possible solutions, using mode two rules when possible."""
    print("WARNING! Mode three activated. Time to complete may be several minutes")
    temp = []  # x-y-conflicts
    global example
    backup = example.copy()  # Backup so it can backtrack through solutions
    for x in range(shape):
        for y in range(shape):
            conflict_counter = 0
            for z in range(shape):
                if conflict_space[x, y] != 0:
                    if conflict_space[x, y] == conflict_space[x, z] and z != y:
                        conflict_counter += 1
                    if conflict_space[x, y] == conflict_space[z, y] and z != x:
                        conflict_counter += 1
            if conflict_counter > 0 and no_neighbour(x, y):
                temp.append([x, y, conflict_counter])
    threshold = [0, 0, 0]
    """Takes an educated guess on the node in most conflict in case it's one move away from being solved"""
    for x in range(len(temp)):
        if temp[x][2] > threshold[2]:
            threshold = temp[x]
    if threshold[2] > 0:
        example[threshold[0], threshold[1]] = 0
        shade_neighbours(threshold[0], threshold[1])
        if not victory_checker():
            """code now begins guessing"""
            for x in range(len(temp)):
                example = backup.copy()
                if no_neighbour(temp[x][0], temp[x][1]):
                    example[temp[x][0], temp[x][1]] = 0
                else:
                    continue
                progress_handler(False, True)
                while progress_handler(True, False):
                    print_debug("itteration")
                    progress_handler(False, False)
                    mark_check()
                    if victory_checker():
                        completion(True)
                    if not progress_handler(True, False):
                        special_corner()
                        if not progress_handler(True, False):
                            separation_crawler(True)
                            if not progress_handler(True, False):
                                occam_razor()  # Recursive
                    if not progress_handler(True, False):
                        if victory_checker():
                            completion(True)
                        else:
                            print("Searching...")
                            continue
        conflict_check()


def print_debug(context: str = "") -> None:
    """Writes out current state of the boards for debugging including context argument"""
    print(context)
    print("This is the current board")
    print(example)
    print("This is the conflict space")
    print(conflict_space)
    print("This is the safeboard")
    print(safeboard)


if __name__ == "__main__":
    main()
