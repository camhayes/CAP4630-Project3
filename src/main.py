from pysat.formula import CNF
from pysat.solvers import Solver

def main():
    preferences_file = ""
    # TODO: Reestablish this file input at some point
    # attributes_file = input("Enter attributes file name: ")
    # constraints_file = input("\nEnter hard contstraints file name: ")

    # testing purposes
    attributes_file = "../ExampleTestCase/attributes.txt"
    constraints_file = "../ExampleTestCase/constraints.txt"
    object_dict = create_objects_dict(attributes_file)
    encoded_set = encode_objects(object_dict)
    constraints_set = create_constraints_set(object_dict, constraints_file)
    feasible_set = create_feasible_set(encoded_set, constraints_set)

    preference_logic_menu(encoded_set, object_dict, constraints_set, feasible_set)
    

def reasoning_task_menu(logic_choice, encoded_set, object_dict, constraints_set, feasible_set, preferences_file):
    # perform the processing method
    processed_sets = process_preference(logic_choice, preferences_file, object_dict)

    while(True):
        print("\nChoose the reasoning task to perform")
        print("1. Encoding")
        print("2. Feasibility Checking")
        print("3. Show the Table")
        print("4. Exemplification")
        print("5. Omni-optimization")
        print("6. Back to previous menu\n")
        choice = input("Your Choice: ")
        if choice == "6":
            preference_logic_menu(encoded_set, object_dict, constraints_set, feasible_set)
        # TODO: Populate these selections
        # elif choice == "5":
        # elif choice == "4":
        # elif choice == "3":
        elif choice == "2":
            print_feasiblity(feasible_set)
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
        choice = input("Your Choice: ")
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
    # preferences_file = input("\nEnter hard preferences file name: ")
    preferences_file = "../ExampleTestCase/penaltylogic.txt"
    reasoning_task_menu(choice, encoded_set, object_dict, constraints_set, feasible_set, preferences_file)

def print_encoded_set(encoded_set, object_dict):
    i = 0
    for x in encoded_set:
        line = "o" + str(i) + " - "
        for y in x:
            line += str(object_dict.get(y)) + ", "
        print(line)
        i += 1

def encode_objects(object_dict):
    # Creates a set of encoded objects as their binary representation.

    encoded_set = []
    i = 0
    attributes_num = int(len(object_dict) / 2)

    for i in range(2**attributes_num):
        encoded_obj = []
        binary_num = bin(i)[2:].zfill(attributes_num)
        j = 1
        
        for digit in str(binary_num):
            if digit == "0":
                encoded_obj.append(-j)
            else:
                encoded_obj.append(j)
            j += 1
        encoded_set.append(encoded_obj)
        
        i += 1
    return encoded_set

def create_objects_dict(attributes_file):
    # Creates a dictionary of all of my binary objects to simplify later operations.
    # The key the is the name of an object value and the value is some binary of n.

    file = open(attributes_file, "r")
    object_dict = {}
    x_count = 1

    for x in file:
        values_set = x.split(":")[1]
        values_delim = values_set.split(",")
        coin = 1
        
        
        for y in values_delim:
            
            object_dict.update({x_count if coin > 0 else -x_count:y.strip()})
            coin *= -1
            
        x_count += 1
    print(object_dict)
    file.close()
    return object_dict

def create_constraints_set(object_dict, constraints_file):
    file = open(constraints_file, "r")
    constraints_set = []
    for x in file:
        constraint = []
        y = x.split("OR")
        for z in y:
            z = z.strip()
            if "NOT" in z:
                z = z.split("NOT")[1].strip()
                # Negate the value to account for not
                constraint.append(find_in_dict(object_dict, z) * -1)
            else:
                constraint.append(find_in_dict(object_dict, z))
        constraints_set.append(constraint)
    return constraints_set

def create_preference_set(preference_file, logic_choice, object_dict):
    preference_set = []
    if logic_choice == 1: # penalty logic
        preference_set = create_penalty_logic_set(preference_file, object_dict)
    else: 
        preference_set = create_qualitative_choice_set(preference_file, object_dict)
    return preference_set

def create_penalty_logic_set(preference_file, object_dict):
    penalty_set = []
    file = open(preference_file, "r")
    for line in file:
        penalty_logic = line.split(",")[0].split("AND")
        penalty_logic = [conj.strip() for conj in penalty_logic]
        penalty_cost = line.split(",")[1].strip()
        conjunction_set = []
        disjunction_set = []
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
            penalty_rule = [disjunction_set, int(penalty_cost)]
            penalty_set.append(penalty_rule)
        elif len(conjunction_set) > 0:
            penalty_rule = []
            for x in conjunction_set:
                penalty_rule.append(x)
            penalty_rule.append(int(penalty_cost))
            penalty_set.append(penalty_rule)
    return penalty_set

def create_qualitative_choice_set(preference_file, object_dict):
    qualitative_set = []
    return qualitative_set

def find_in_dict(object_dict, token):
    for key in object_dict:
        if object_dict.get(key) == token:
            return key

def create_feasible_set(encoded_set, constraints_set):

    # for each object in encoded set... check if it is feasble. return a new set of all feasible sets
    # for x in feasible_set, x[0] is the original set number, x[1] is the set itself
    # feasible_set = [[0, [-1,-2,-3,-4]], [1, [-1,-2,-3,4]], [7, [1,2,3,4]]]
    
    feasible_set = []
    set_index = 0

    for set in encoded_set:
        clauses = []
        for i in constraints_set:
            clauses.append(i)
        for k in set:
            clauses.append([k])
        
        
        cnf = CNF(from_clauses=clauses)
        with Solver(bootstrap_with=cnf) as solver:
            if solver.solve():
                feasible_set.append([set_index, solver.get_model()])
        set_index += 1

    return feasible_set

def print_feasiblity(feasible_set):
    if len(feasible_set) > 0:
        print("Yes, there are " + str(len(feasible_set)) + " feasible objects.")
    else: 
        print("There are no feasible objects.")

def process_preference(logic_choice, preferences_file, object_dict):
    # create preference set
    processed_sets = []
    create_preference_set(preferences_file, logic_choice, object_dict)

    return processed_sets


# TODO: Show the Table
# this will just print out the processed_sets in a tabular format

# TODO: Exemplification
# TODO: Omni-optimization

# Enter

if __name__ == "__main__":
    main()