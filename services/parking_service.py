from datetime import datetime
import sqlite3
from models.constants import DATE_TIME_FORMAT
from objects.car_parking import CarParking
from objects.parking_history import ParkingHistory
from objects.payment_balance import PaymentBalance
conn = sqlite3.connect("database/my_database.db")

def get_car_parking(car_identity) -> CarParking:
    query = "SELECT arrival_time, car_identity, frequent_parking_number, is_valid_fpn FROM car_parkings WHERE car_identity = ?"
    result = conn.execute(query, (car_identity,)).fetchone()
    if result is not None:
        car_parking = CarParking(result[0], result[1], str(result[2]))
        car_parking.is_valid_fpn = result[3]
        return car_parking
    return None

def save_car_parking(car_parking: CarParking) -> bool:
    conn.execute(f"INSERT INTO car_parkings (car_identity, arrival_time,frequent_parking_number , is_valid_fpn) \
      VALUES ('{car_parking.car_identity}', '{car_parking.arrival_time}', {car_parking.frequent_parking_number if car_parking.frequent_parking_number else 'NULL'}, '{car_parking.is_valid_fpn}')")
    conn.commit()
    return True

def remove_car_parking(car_identity) -> bool:
    query = "DELETE FROM car_parkings WHERE car_identity = ?"
    conn.execute(query, (car_identity,))
    conn.commit()
    return True

def save_parking_history(parking_history: ParkingHistory) -> bool:
    conn.execute(f"INSERT INTO parking_histories (car_identity, arrival_time, leaving_time, frequent_parking_number, is_valid_fpn, parking_fee) \
      VALUES ('{parking_history.car_identity}', '{parking_history.arrival_time}', '{parking_history.leaving_time}',{parking_history.frequent_parking_number}, '{parking_history.is_valid_fpn}', {parking_history.parking_fee})")
    conn.commit()
    return True

def get_parking_histories(car_identity) -> list[ParkingHistory]:
    query = "SELECT car_identity, arrival_time, leaving_time, frequent_parking_number, is_valid_fpn, parking_fee FROM parking_histories WHERE car_identity = ? ORDER BY arrival_time DESC"
    results = conn.execute(query, (car_identity,)).fetchall()
    parking_histories: list[ParkingHistory] = []
    if results is not None:
        for result in results:
            parking_histories.append(ParkingHistory(result[0], datetime.strptime(result[1], DATE_TIME_FORMAT), datetime.strptime(result[2], DATE_TIME_FORMAT), result[3], result[4], result[5]))
        return parking_histories
    return None



def save_payment_balance(payment_balance: PaymentBalance) -> bool:
    conn.execute(f"INSERT INTO payment_balances (car_identity, available_credit) \
      VALUES ('{payment_balance.car_identity}', {payment_balance.available_credit})")
    conn.commit()
    return True


def get_payment_balance(car_identity) -> PaymentBalance:
    query = "SELECT car_identity, available_credit FROM payment_balances WHERE car_identity = ?"
    result = conn.execute(query, (car_identity,)).fetchone()
    if result is not None:
        return PaymentBalance(car_identity=result[0], available_credit=result[1])
    return None

def update_payment_balance(payment_balance: PaymentBalance) -> bool:
    conn.execute(f"UPDATE payment_balances SET available_credit={payment_balance.available_credit} WHERE car_identity ='{payment_balance.car_identity}'")
    conn.commit()
    return True