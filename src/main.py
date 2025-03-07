def main():
    global attributes_file
    global constraints_file
    preferences_file = ""
    attributes_file = input("Enter attributes file name: ")
    constraints_file = input("\nEnter hard contstraints file name: ")
    preference_logic_menu()
    

def reasoning_task_menu(preference_choice):
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
            preference_logic_menu()
        # TODO: Populate these selections
        # elif choice == "5":
        # elif choice == "4":
        # elif choice == "3":
        # elif choice == "2":
        # elif choice == "1":
        else:
            print("Invalid choice. Please try again.\n")
            

def preference_logic_menu():
    looping = True
    while(looping):
        print("\nChoose a preference logic:")
        print("1. Penalty Logic")
        print("2. Qualitative Choice Logic")
        print("3. Exit\n")
        choice = input("Your Choice: ")
        if choice == "3": 
            exit()
        elif choice == "2":
            print("You picked Qualitative Choice Logic")
            looping = False
            choice = 2
        elif choice == "1":
            print("Penalty Logic")
            looping = False
            choice = 1
        else:
            print("Invalid choice. Please try again.")
    global preferences_file
    preferences_file = input("\nEnter hard preferences file name: ")
    reasoning_task_menu(choice)

def encode_objects():
    

# TODO: Feasibility Checking
# TODO: Show the Table
# TODO: Exemplification
# TODO: Omni-optimization

# Enter
if __name__ == "__main__":
    main()