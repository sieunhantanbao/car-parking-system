from datetime import datetime, timedelta
from decimal import Decimal
from models.constants import DATE_TIME_FORMAT, DATE_TIME_NEEDED_FORMAT
from objects.car_parking import CarParking
from objects.parking_history import ParkingHistory
from objects.payment_balance import PaymentBalance
from ultils.colors import RED, RESET, GREEN, YELLOW
from services import parking_service as _parking_service

def handle_parking() -> None:
    """ Hanlde car parking
    """
    print("Welcome to CAR PARKING. Please provide information as below (Ctrl + C to quit)")
    while True:
        try:
            car_identity = input("> Please input car identity (ex: 59C-12345): ")
            arrival_time = input("> Please input arrival time (ex: 2023-06-18 18:30): ")
            frequent_parking_number = input("> Please input frequent parking number if any (ex: 12345): ")
            if car_identity is not None and car_identity != "":
                # Check car_parking existence
                exist_car_parking = _parking_service.get_car_parking(car_identity)
                if exist_car_parking:
                    print(RED + "Invalid parking. Your car has already parked" + RESET)
                    break
                car_parking = CarParking(f"{arrival_time}:00", car_identity, frequent_parking_number)
                if car_parking and len(car_parking.errors) > 0:
                    for error in car_parking.errors:
                        print(RED + error + RESET)
                        
                    car_parking.errors.clear()
                else:    
                    _parking_service.save_car_parking(car_parking)
                    print(GREEN + "Your car is successfully parked" + RESET)
                    break
            else:
                print(RED + "Car identity is empty" + RESET)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(RED + e + RESET)


def handle_pickup() -> None:
    """ Hanlde car picking up
    """
    print("Welcome to CAR PICKUP. Please provide information as below (Ctrl + C to quit)")
    while True:
        try:
            car_identity = input("> Please input car identity (ex: 59C-12345): ")
            if car_identity is not None and car_identity != "":
                # Check car_parking existence
                parked_car = _parking_service.get_car_parking(car_identity)
                if not parked_car:
                    print(RED + "Invalid car identity or your car is not in parking lot." + RESET)
                    continue
                # Calculate the parking fee
                leaving_time = datetime.now()
                temp_leaving_time = input("> Leaving time - example 2023-06-18 18:30 - (optional). Blank or invalid input to use current datetime: ")
                try:
                    temp_leaving_time = datetime.strptime(f"{temp_leaving_time}:00", DATE_TIME_FORMAT)
                    leaving_time = temp_leaving_time
                except ValueError:
                    print(YELLOW + f"Invalid or not input leaving time, use current datetime: {leaving_time.strftime(DATE_TIME_NEEDED_FORMAT)}" + RESET)
                
                payment_fee = __calculate_payment_fee(parked_car, leaving_time)
                if payment_fee is None:
                    continue
                print(f"=> Your parking fee is: ${payment_fee}")
                # Get available credit
                payment_balance = _parking_service.get_payment_balance(car_identity)
                available_credit = Decimal("0.00")
                if payment_balance:
                    available_credit = Decimal(payment_balance.available_credit)
                # Pay the parking feed
                payment_amount_input = __input_and_validate_payment_amount(payment_fee, available_credit)
                final_available_credit = payment_amount_input + available_credit - payment_fee
                # Save the data to the parking_histories
                parking_history = ParkingHistory(parked_car.car_identity,
                                                 parked_car.arrival_time, leaving_time.strftime(DATE_TIME_FORMAT),
                                                 parked_car.frequent_parking_number if parked_car.frequent_parking_number != 'None' else 'NULL',
                                                 parked_car.is_valid_fpn, payment_fee)
                _parking_service.save_parking_history(parking_history)
                # Save the data to the payment_balances
                if payment_balance: # update
                    payment_balance = PaymentBalance(car_identity, final_available_credit)
                    _ = _parking_service.update_payment_balance(payment_balance)
                else: # add new
                    new_balance = PaymentBalance(car_identity, final_available_credit)
                    _ = _parking_service.save_payment_balance(new_balance)
                
                # Remove the parked_car from the car_parkings table
                _parking_service.remove_car_parking(car_identity)
                
                print(GREEN + "Your car is successfully pickup" + RESET)
                break
            else:
                print(RED + "Car identity is empty" + RESET)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(RED + e + RESET)

def handle_history() -> None:
    """ Hanlde car history query
    """
    print("Welcome to CAR HISTORY QUERY. Please provide information as below (Ctrl + C to quit)")
    while True:
        try:
            car_identity = input("> Please input car identity (ex: 59C-12345): ")
            if car_identity is not None and car_identity != "":
                # Get parking history
                parking_histories = _parking_service.get_parking_histories(car_identity)
                if not parking_histories:
                    print(RED+ "The provided car identity is not found or invalid" + RESET)
                    continue
                # Get payment balance
                payment_balance = _parking_service.get_payment_balance(car_identity)
                # Display result to console
                __show_payment_history_to_console(car_identity, payment_balance, parking_histories)
                # Save the result to file
                __write_payment_history_to_file(car_identity, payment_balance, parking_histories)
                print(GREEN + f"The result has been saved to file: {car_identity}.txt" + RESET)
                break
            else:
                print(RED + "Car identity is empty" + RESET)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(RED + e + RESET)

def __calculate_payment_fee(parked_car: CarParking, leaving_time: datetime) -> Decimal:
    if leaving_time < parked_car.arrival_time:
        print(RED + "Leaving time could not be less than arrival time!!!" + RESET)
        return None
    calculated_time_periods = __calculate_hours_between(parked_car.arrival_time, leaving_time)
    parking_fee = Decimal("0.00")
    discount_afternoon = Decimal("1.00") if parked_car.is_valid_fpn == 'False' else Decimal("0.90")
    discount_morning_or_evening = Decimal("1.00") if parked_car.is_valid_fpn == 'False' else Decimal("0.50")
    
    for calculated_time_period in calculated_time_periods:
        match calculated_time_period.get("dayOfWeek"):
            case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":
                # Calculate fee for hours_from_08h_to_17h
                if 2 >= calculated_time_period.get("hours_from_08h_to_17h") > 0:
                    parking_fee += calculated_time_period.get("hours_from_08h_to_17h")*Decimal("10.00")*discount_afternoon
                else:
                    parking_fee += 2*Decimal("10.00")*discount_afternoon
                    remaining_hours = calculated_time_period.get("hours_from_08h_to_17h") - 2
                    parking_fee += remaining_hours*Decimal("10.00")*2*discount_afternoon
                
                parking_fee += __calculate_fee_morning_and_evening(calculated_time_period.get("hours_from_00h_to_08h"), 
                                                  calculated_time_period.get("hours_from_17h_to_00h"), 
                                                  discount_morning_or_evening)
                
            case "Sunday":
                # Calculate fee for hours_from_08h_to_17h
                if 8 >= calculated_time_period.get("hours_from_08h_to_17h") > 0:
                    parking_fee += calculated_time_period.get("hours_from_08h_to_17h")*Decimal("2.00")*discount_afternoon
                else:
                    parking_fee += 8*Decimal("2.00")*discount_afternoon
                    remaining_hours = calculated_time_period.get("hours_from_08h_to_17h") - 8
                    parking_fee += remaining_hours*Decimal("2.00")*2*discount_afternoon
                    
                parking_fee += __calculate_fee_morning_and_evening(calculated_time_period.get("hours_from_00h_to_08h"), 
                                                  calculated_time_period.get("hours_from_17h_to_00h"), 
                                                  discount_morning_or_evening)
            case "Saturday":
                # Calculate fee for hours_from_08h_to_17h
                if 4 >= calculated_time_period.get("hours_from_08h_to_17h") > 0:
                    parking_fee += calculated_time_period.get("hours_from_08h_to_17h")*Decimal("3.00")*discount_afternoon
                else:
                    parking_fee += 4*Decimal("3.00")*discount_afternoon
                    remaining_hours = calculated_time_period.get("hours_from_08h_to_17h") - 4
                    parking_fee += remaining_hours*Decimal("3.00")*2*discount_afternoon
                
                parking_fee += __calculate_fee_morning_and_evening(calculated_time_period.get("hours_from_00h_to_08h"), 
                                                  calculated_time_period.get("hours_from_17h_to_00h"), 
                                                  discount_morning_or_evening)
                
    #round up to 2-decimal format            
    return round(parking_fee, 2)

def __calculate_fee_morning_and_evening(hours_from_00h_to_08h: int,
                                        hours_from_17h_to_00h: int,
                                        discount_morning_or_evening: Decimal) -> Decimal:
    parking_fee = Decimal("0.00")
    # Calculate fee for hours_from_17h_to_00h
    parking_fee += hours_from_17h_to_00h*Decimal("5.00")*discount_morning_or_evening
    # Calculate fee for hours_from_00h_to_08h
    if hours_from_00h_to_08h > 0:
        parking_fee += Decimal("20.00")*discount_morning_or_evening
    return parking_fee

def __calculate_hours_between(arrival_time, leaving_time):
    # Initialize the result list
    result = []
    # Define time periods
    time_periods = [
        ("hours_from_08h_to_17h", 8, 17),
        ("hours_from_17h_to_00h", 17, 0),
        ("hours_from_00h_to_08h", 0, 8)
    ]

    # Iterate through each day between arrival_time and leaving_time
    current_datetime = arrival_time
    while current_datetime < leaving_time:
        # Initialize dictionary to store hours for the current day
        day_hours = {
            "date": current_datetime.strftime("%Y-%m-%d"),
            "dayOfWeek": current_datetime.strftime("%A")
        }

        # Calculate hours for each time period
        for period_name, start_hour, end_hour in time_periods:
            # Calculate the start and end time for the current period
            start_time = current_datetime.replace(hour=start_hour, minute=0, second=0)
            end_time = current_datetime.replace(hour=end_hour, minute=0, second=0)
            
            # Adjust end_time for the next day if end_hour is 0
            if end_hour == 0:
                end_time += timedelta(days=1)
            
            # Clip the start and end times within the range of arrival_time and leaving_time
            start_time = max(start_time, arrival_time)
            end_time = min(end_time, leaving_time)
            
            # Calculate the duration in hours for the current period
            # Round the fractional hours to the nearest whole number by + 0.5 and convert it to int
            hours = int(max(0, (end_time - start_time).total_seconds() / 3600) + 0.5)
            day_hours[period_name] = hours

        # Add the calculated hours for the day to the result list
        result.append(day_hours)

        # Move to the next day
        current_datetime += timedelta(days=1)

    return result

def __input_and_validate_payment_amount(payment_fee: Decimal, available_credit: Decimal) -> Decimal:
    while True:
        try:
            # Validate payment amount input
            payment_amount = input("> Input your payment amount: ")
            if not payment_amount.replace(".", "", 1).isdigit():
                print(RED + "Invalid payment amount" + RESET)
                continue
            payment_amount_decimal = Decimal(payment_amount)
            if payment_amount_decimal + available_credit < payment_fee:
                print(RED + "Payment amount needs to be great or equal the payment fee" + RESET)
                continue
            return payment_amount_decimal
        except Exception as e:
            raise e
   
def __show_payment_history_to_console(car_identity, payment_balance, parking_histories) -> None:
    total_payment = sum([parking_history.parking_fee for parking_history in parking_histories])
    print(f"**************************PARKING HISTORY - {car_identity}*****************************")
    print(f"   Total payment: ${round(total_payment, 2)}")
    print(f"   Available credits: ${round(payment_balance.available_credit, 2) if payment_balance else '0'}")
    print("   Parked Dates:")
    for parking_history in parking_histories:
        print(f"        {parking_history.arrival_time.strftime(DATE_TIME_NEEDED_FORMAT)} - {parking_history.leaving_time.strftime(DATE_TIME_NEEDED_FORMAT)} ${parking_history.parking_fee}")
    print(f"**************************PARKING HISTORY - {car_identity}*****************************")


def __write_payment_history_to_file(car_identity, payment_balance, parking_histories) -> None:
    total_payment = sum([parking_history.parking_fee for parking_history in parking_histories])
    with open(f"exports/{car_identity}.txt", "w", encoding="utf-8") as file:
        file.write(f"Total payment: ${round(total_payment, 2)}\n")
        file.write(f"Available credits: ${round(payment_balance.available_credit, 2) if payment_balance else '0'}\n")
        file.write("Parked Dates:\n")
        for parking_history in parking_histories:
            file.write(f"\t{parking_history.arrival_time.strftime(DATE_TIME_NEEDED_FORMAT)} - {parking_history.leaving_time.strftime(DATE_TIME_NEEDED_FORMAT)} ${parking_history.parking_fee}\n")