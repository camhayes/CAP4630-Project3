from pysat.formula import CNF
from pysat.solvers import Solver
from rich.console import Console
from rich.table import Table
import random
import os
from math import isinf

def main():
    attributes_file = get_valid_filename("Enter attributes file name: ")
    constraints_file = get_valid_filename("\nEnter hard constraints file name: ")
    
    # testing purposes
    # attributes_file = "../TestCase/attributes.txt"
    # constraints_file = "../TestCase/constraints.txt"
    
    object_dict = create_objects_dict(attributes_file)
    encoded_set = encode_objects(object_dict)
    constraints_set = create_constraints_set(object_dict, constraints_file)
    feasible_set = create_feasible_set(encoded_set, constraints_set)

    preference_logic_menu(encoded_set, object_dict, constraints_set, feasible_set)


def reasoning_task_menu(logic_choice, encoded_set, object_dict, constraints_set, feasible_set, preferences_file):
    # perform the processing method
    processed_set = process_preference(logic_choice, preferences_file, feasible_set, object_dict)

    while(True):
        print("\nChoose the reasoning task to perform")
        print("1. Encoding")
        print("2. Feasibility Checking")
        print("3. Show the Table")
        print("4. Exemplification")
        print("5. Omni-optimization")
        print("6. Back to previous menu\n")
        choice = input("Your Choice: ").strip()
        if choice == "6":
            preference_logic_menu(encoded_set, object_dict, constraints_set, feasible_set)
        elif choice == "5":
            if logic_choice == 1:
                feasible_omni_optimization(processed_set, feasible_set)
            elif logic_choice == 2:
                qualitative_omni_optimization(processed_set)
        elif choice == "4":
            if logic_choice == 1:
                exemplify_penalty(feasible_set, processed_set)
            elif logic_choice == 2:
                exemplify_qualitative(processed_set)
        elif choice == "3":
            if logic_choice == 1:
                print_table_penalty(preferences_file, processed_set, feasible_set)
            elif logic_choice == 2:
                print_table_qualitative(preferences_file, processed_set)
        elif choice == "2":
            print_feasibility(feasible_set)
        elif choice == "1":
            print_encoded_set(encoded_set, object_dict)
        else:
            print("Invalid choice. Please try again.\n")


def preference_logic_menu(encoded_set, object_dict, constraints_set, feasible_set):
    looping = True
    while(looping):
        print("\nChoose a preference logic:")
        print("1. Penalty Logic")
        print("2. Qualitative Choice Logic")
        print("3. Exit\n")
        choice = input("Your Choice: ").strip()
        if choice == "3": 
            print("Goodbye!")
            exit()
        elif choice == "2":
            print("You picked Qualitative Choice Logic")
            looping = False
            choice = 2
        elif choice == "1":
            print("You picked Penalty Logic")
            looping = False
            choice = 1
        else:
            print("Invalid choice. Please try again.")
    preferences_file = get_valid_filename("\nEnter hard preferences file name: ")
    # preferences_file = "../TestCase/penaltylogic.txt"
    reasoning_task_menu(choice, encoded_set, object_dict, constraints_set, feasible_set, preferences_file)

def print_encoded_set(encoded_set, object_dict):
    for i, obj_ids in enumerate(encoded_set):
        line = f"o{i} - " + ", ".join(str(object_dict.get(obj_id)) for obj_id in obj_ids)
        print(line)

def encode_objects(object_dict):
    encoded_set = []
    num_attributes = len(object_dict) // 2

    for i in range(2 ** num_attributes):
        binary_digits = bin(i)[2:].zfill(num_attributes)
        encoded_obj = [j if digit == '1' else -j for j, digit in enumerate(binary_digits, start=1)]
        encoded_set.append(encoded_obj)

    return encoded_set

def create_objects_dict(attributes_file):

    object_dict = {}

    with open(attributes_file, "r") as file:
        for x_count, line in enumerate(file, start=1):
            _, values_set = line.split(":")
            values = [v.strip() for v in values_set.split(",")]

            if len(values) != 2:
                raise ValueError(f"Line {x_count} does not contain exactly 2 values: {line}")

            object_dict[x_count] = values[0]
            object_dict[-x_count] = values[1]

    return object_dict

def create_constraints_set(object_dict, constraints_file):
    constraints_set = []

    with open(constraints_file, "r") as file:
        for line in file:
            constraint = []
            parts = line.strip().split("OR")

            for part in parts:
                part = part.strip()
                if part.startswith("NOT"):
                    name = part[3:].strip()
                    constraint.append(-find_in_dict(object_dict, name))
                else:
                    constraint.append(find_in_dict(object_dict, part))

            constraints_set.append(constraint)

    return constraints_set

def create_preference_set(preference_file, logic_choice, object_dict):
    if logic_choice == 1:
        return create_penalty_logic_set(preference_file, object_dict)
    else:
        return create_qualitative_choice_set(preference_file, object_dict)

def create_penalty_logic_set(preference_file, object_dict):

    # clauseA OR clauseB AND clauseC = [clauseA, clauseB], [clauseC] where AND is the delimeter and OR joins clauses

    penalty_set = []
    file = open(preference_file, "r")
    for line in file:
        penalty_logic = line.split(",")[0].split("AND")
        penalty_logic = [conj.strip() for conj in penalty_logic]
        penalty_cost = line.split(",")[1].strip()
        conjunction_set = []
        disjunction_set = []
        penalty_rule = []
        for rule in penalty_logic:
            if "OR" in rule:
                rule = rule.split("OR")
                rule = [i.strip() for i in rule]
                for disjunction in rule:
                    if "NOT" in disjunction:
                        disjunction = disjunction.split("NOT")[1].strip()
                        disjunction_set.append(find_in_dict(object_dict, disjunction) * -1)
                    else:
                        disjunction_set.append(find_in_dict(object_dict, disjunction))
            else:
                if "NOT" in rule:
                    rule = rule.split("NOT")[1].strip()
                    conjunction_set.append([find_in_dict(object_dict, rule) * -1])
                else:
                    conjunction_set.append([find_in_dict(object_dict, rule)])
        
        if len(disjunction_set) > 0:
            penalty_rule.append(disjunction_set)
        if len(conjunction_set) > 0:
            for x in conjunction_set:
                penalty_rule.append(x)
        penalty_rule.append(int(penalty_cost))
        penalty_set.append(penalty_rule)
    return penalty_set

# TODO: Implement this

def create_qualitative_choice_set(preference_file, object_dict):
    """
    Parses qualitative choice rules from a preference file.
    Syntax supports:
      - IF: separates the main preference from its condition
      - BT: separates sequential preferences or steps
      - AND: separates required attributes within a preference
      - OR: provides alternatives within a clause
      - NOT: negates a specific attribute
    Output structure:
      [
        [ [[a], [b, c]], [[-d]], [[e]] ],  # One rule: BT-separated parts
        ...
      ]
    """
    # TODO: Clean this up?

    choice_sets = []
    file = open(preference_file, "r")
    
    for line in file:
        line_set = []

        for condition in line.split("IF"):
            condition_set = []
            
            for preferences in condition.split("BT"):
                prefs_set = []
                for clauses in preferences.split("AND"):
                    clause_set = []
                    if "OR" in clauses:
                        for attribute in clauses.split("OR"):
                            if "NOT" in attribute:
                                clause_set.append(-find_in_dict(object_dict, (attribute.split("NOT")[1].strip())))
                            else:   
                                clause_set.append(find_in_dict(object_dict, attribute.strip()))
                    else:
                        if "NOT" in clauses:
                            prefs_set.append([-find_in_dict(object_dict, clauses.split("NOT")[1].strip())])
                        else:
                            prefs_set.append([find_in_dict(object_dict, clauses.strip())])
                    if len(clause_set) > 0:
                        prefs_set.append(clause_set)
                line_set.append(prefs_set)
        choice_sets.append(line_set)
    return choice_sets

def find_in_dict(object_dict, token):
    for key in object_dict:
        if object_dict.get(key) == token:
            return key

def create_feasible_set(encoded_set, constraints_set):
    feasible_set = []

    for index, obj in enumerate(encoded_set):
        # Combine constraints and object as unit clauses
        clauses = constraints_set + [[literal] for literal in obj]

        cnf = CNF(from_clauses=clauses)
        with Solver(bootstrap_with=cnf) as solver:
            if solver.solve():
                feasible_set.append([index, solver.get_model()])

    return feasible_set

def print_feasibility(feasible_set):
    count = len(feasible_set)
    if count > 0:
        print(f"Yes, there are {count} feasible objects.")
    else:
        print("There are no feasible objects.")


def process_preference(logic_choice, preferences_file, feasible_set, object_dict):
    preference_set = create_preference_set(preferences_file, logic_choice, object_dict)

    if logic_choice == 1:
        return process_penalty_logic(preference_set, feasible_set)
    else:
        return process_qualitative_choice(preference_set, feasible_set)


def process_penalty_logic(preference_set, feasible_set):
    processed_set = []
    # processed_set = [[problem, [objectNumber, object, cost], ...], ...]
    # for each preference, test each object once
    for preference in preference_set:
        # print(preference)
        penalty_cost = preference[len(preference) - 1]
        clauses = []
        for i in range(len(preference) - 1):
            clauses.append(preference[i])
        problem_set = [clauses]
        for feasible_object in feasible_set:
            cnf_test = clauses.copy()
            for x in feasible_object[1]:
                cnf_test.append([x])
            # print(cnf_test)
            cnf = CNF(from_clauses=cnf_test)
            # test the current preference problem with each model
            with Solver(bootstrap_with=cnf) as solver:
                 if solver.solve():
                    # solves the problem, so doesn't incur a penalty
                    parsed = [feasible_object[0], feasible_object[1], 0]
                    problem_set.append(parsed)
                 else:
                     # incurs the penalty
                     parsed = [feasible_object[0], feasible_object[1], penalty_cost]
                     problem_set.append(parsed)
        processed_set.append(problem_set)
    return processed_set

def print_table_penalty(preferences_file, processed_set, feasible_set):
    headings = define_table_headings(preferences_file)
    table = Table(title="Penalty Logic Table")

    table.add_column("Encoding")
    for col in headings:
        table.add_column(col)
    table.add_column("Total Cost")

    table_rows = [["o" + str(obj_index)] for obj_index, _ in feasible_set]

    # Add cost entries for each rule
    for rule_index, problem in enumerate(processed_set):
        for row_index, (_, _, cost) in enumerate(problem[1:]):
            table_rows[row_index].append(str(cost))

    # Calculate total cost per object
    for row in table_rows:
        costs = [int(value) for value in row[1:]]
        total = sum(costs)
        row.append(str(total))

    # Print the table
    for row in table_rows:
        table.add_row(*row)

    console = Console()
    console.print(table)


def exemplify_penalty(feasible_set, processed_set):
    # A is strictly preferred over B if totalCost(A) < totalCost(B)
    # A and B are equal if totalCost(A) == totalCost(B) AND the same rules are violated
    # A and B are incomparable if totalCost(A) == totalCost(B) AND different rules are violated
    if len(feasible_set) == 1:
        print("There is only one feasible set. The set is o" + str(feasible_set[0][0]) )
        return
    elif len(feasible_set) == 0:
        print("There are no feasible sets.")
        return
    object_index = [[item[0]] for item in feasible_set]
    random_sets = random.sample(object_index, 2)
    for sets in processed_set:
        for i in range(1, len(sets)):
            if sets[i][0] == random_sets[0][0]:
                random_sets[0].append(sets[i][len(sets[i]) - 1])
                # random_sets[0][1] += sets[i][len(sets[i]) - 1]
            elif sets[i][0] == random_sets[1][0]:
                random_sets[1].append(sets[i][len(sets[i]) - 1])
    for set in random_sets:
        sum = 0
        for values in range(1, len(set)):
            sum += set[values]
        set.append(sum)
    
    print("Two randomly selected feasible objects are o" + str(random_sets[0][0]) + " and o" + str(random_sets[1][0]))
    if random_sets[0][len(random_sets[0]) - 1] < random_sets[1][len(random_sets[1]) - 1]:
        print("o" + str(random_sets[0][0]) + " is strictly preferred over o" + str(random_sets[1][0]))
    elif random_sets[1][len(random_sets[1]) - 1] < random_sets[0][len(random_sets[0]) - 1]:
        print("o" + str(random_sets[1][0]) + " is strictly preferred over o" + str(random_sets[0][0]))
    else: # total cost is the same
        print("o" + str(random_sets[0][0]) + " and o" + str(random_sets[1][0]) + " are equivalent")
    return

def feasible_omni_optimization(processed_set, feasible_set):
    optimized_set = []
    summed_set = []
    for sets in feasible_set:
        summed_set.append([sets[0], 0])

    for sets in processed_set:
        for i in range(1,len(sets)):
            summed_set[i-1][1] += sets[i][len(sets[i]) - 1]

    min_sum = summed_set[0][1]
    optimized_set.append(summed_set[0][0])
    
    for i in range(1, len(summed_set)):
        if summed_set[i][1] < min_sum:
            optimized_set = [summed_set[i][0]]
            min_sum = summed_set[i][1]
        elif summed_set[i][1] == min_sum:
            optimized_set.append(summed_set[i][0])
    print("All optimal objects:", ', '.join(("o" + str(obj)) for obj in optimized_set))

    return


# TODO: Implement this
def process_qualitative_choice(preference_set, feasible_set):
    # for each for object, test each condition
    # preference set is formatted [ [[3]], [[-3]], [[None]] ] -> fish BT beef IF 
    # return a set containing [o0, prefScore1, prefScore2, ...]
    processed_set = []
    for i in range(0, len(feasible_set)):
        processed_set.append([feasible_set[i][0]])
        for condition_set in preference_set:
            member_set = [[member] for member in feasible_set[i][1]]
            # @ objectI, testJ
            initial_condition = condition_set[len(condition_set) - 1][0]
            # test initial condition first, if it fails, then the value is inf
            if initial_condition == [None]:
                processed_set[i].append(match_rules(member_set, condition_set))
            else: # test if object passes the initial condition
                cnf_set = [initial_condition]
                cnf_set.extend(member_set)
                cnf = CNF(from_clauses=cnf_set)
                # print(cnf)
                with Solver(bootstrap_with=cnf) as solver:
                    # print(cnf_set)
                    if solver.solve(): # object passes intial condition, now determine which preference it has
                        processed_set[i].append(match_rules(member_set, condition_set))
                    else: # object failes initial condition, so it's inf
                        processed_set[i].append(float('inf'))
                        
    return processed_set

def match_rules(member_set, condition_set):
    min = float('inf')
    # start with infinity, if a solution is found, that's the new value
    for j in range(0, len(condition_set) - 1):
        test_set = condition_set[j].copy()
        test_set.extend(member_set)
        cnf_test = CNF(from_clauses=test_set)
        with Solver(bootstrap_with=cnf_test) as solver:
            if solver.solve():
                min = j+1
    return min

def print_table_qualitative(preferences_file, processed_set):
    headings = define_table_headings(preferences_file)
    table = Table(title="Qualitative Choice Table")

    table.add_column("encoding")
    for col in headings:
        table.add_column(col.strip())

    for row in processed_set:
        display_row = [f"o{row[0]}"] + [
            ", ".join(map(str, item)) if isinstance(item, (list, set, tuple)) else str(item)
            for item in row[1:]
        ]
        table.add_row(*display_row)

    Console().print(table)

def exemplify_qualitative(processed_set): 
    random_objects = random.sample(processed_set, 2)
    result = compare_objects(*random_objects)
    print("Two randomly selected feasible objects are o" + str(random_objects[0][0]) + " and o" + str(random_objects[1][0]))
    if result == 1:
        print("o" + str(random_objects[0][0]) + " is more optimal than " + "o" + str(random_objects[1][0])) # A is more optimal
    elif result == -1:
        print("o" + str(random_objects[1][0]) + " is more optimal than " + "o" + str(random_objects[0][0]))  # B is more optimal
    elif result == 0:
        print("o" + str(random_objects[0][0]) + " and " + "o" + str(random_objects[1][0]) + " are equivalent")  # equivalent
    elif result == None:
        print("o" + str(random_objects[0][0]) + " and " + "o" + str(random_objects[1][0]) + " are incomparable")  # incomparable

def qualitative_omni_optimization(processed_set):
    optimal_set = []

    for i, candidate in enumerate(processed_set):
        is_dominated = False

        for j, challenger in enumerate(processed_set):
            if i == j:
                continue

            result = compare_objects(candidate, challenger)

            if result == -1:  # challenger dominates candidate
                is_dominated = True
                break

        if not is_dominated:
            optimal_set.append(candidate)

    optimal_labels = [f"o{item[0]}" for item in optimal_set]
    print("The optimal sets are: " + ", ".join(optimal_labels))

    return optimal_set

def compare_objects(obj_a, obj_b):
    # Strip identifiers for comparison
    values_a = obj_a[1:]
    values_b = obj_b[1:]

    dominates_a = False
    dominates_b = False

    for a, b in zip(values_a, values_b):
        if a < b:
            dominates_a = True
        elif b < a:
            dominates_b = True

    if dominates_a and not dominates_b:
        return 1
    elif dominates_b and not dominates_a:
        return -1
    elif not dominates_a and not dominates_b:
        return 0
    else:
        return None 

def define_table_headings(preference_file):
    table_headings = []
    file = open(preference_file, "r")
    for line in file:
        if "," in line:
            line = line.split(",")[0]
        table_headings.append(line)
    return table_headings


def get_valid_filename(prompt):
    while True:
        try:
            file_name = input(prompt).strip()
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"File '{file_name}' does not exist.")
            return file_name
        except Exception as e:
            print(f"Error: {e}\nPlease try again.\n")

# Enter

if __name__ == "__main__":
    main()