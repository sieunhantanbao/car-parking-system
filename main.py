from ultils.colors import RED, RESET, GREEN
from handle_options import handle_parking, handle_pickup, handle_history
        
while True:
    try:
        print("========WELCOME YOU TO OUR CAR PARKING SERVICE========")
        option = int(input("Please select an option: \n\
                    1: Park \n\
                    2: Pickup \n\
                    3: History \n\
                    0: Exit/Quit \n\
> Your selection: "))
        match option:
            case 0:
                print(GREEN + "Goodbye! Nice to serve you!" + RESET)
                break
            case 1:
                handle_parking()
            case 2:
                handle_pickup()
            case 3:
                handle_history()
            case _:
                print(RED + "Invalid option. Please select option again." + RESET)
    except KeyboardInterrupt:
        print(GREEN + "\nGoodbye! Nice to serve you!" + RESET)
        break
    except ValueError:
        print(RED + "Invalid option. Please select option again." + RESET)
    
    
    
    

    
    