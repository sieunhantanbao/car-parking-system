from datetime import datetime
from typing import Optional
import re
from models.constants import DATE_TIME_FORMAT
from ultils.ultils import calculate_modulo11_check_digit

class CarParking():
    """ Car Parking class

    Returns:
        _type_: _description_
    """
    _arrival_time: datetime
    _leaving_time: Optional[datetime] = None
    _car_identity: str
    _frequent_parking_number: Optional[int] = None
    is_valid_fpn: bool = False
    errors = []
    
    def __init__(self, at, ci: str, fpn: Optional[int] = None, lt: Optional[datetime] = None):
        self.arrival_time = at
        self.car_identity = ci
        self.frequent_parking_number = fpn
        self.leaving_time =lt
    
    def __repr__(self):
        return f"Car identity: {self.car_identity}. Arrival time: {self.arrival_time}. Frequent Parking Number: {self.frequent_parking_number}.Is valid frequent parking number: {self.is_valid_fpn}. Leaving time: {self.leaving_time}"

    @property
    def arrival_time(self):
        return self._arrival_time

    @arrival_time.setter
    def arrival_time(self, at):
        if not at:
            self.errors.append('Arrival time cannot be empty')
        try:
            date_obj = datetime.strptime(str(at), DATE_TIME_FORMAT)
            if date_obj > datetime.now():
                self.errors.append("Arrival time can't be greater than current datetime")
                return
            self._arrival_time = date_obj
        except ValueError:
            self.errors.append('Arrival time is invalid')
    
    @property
    def leaving_time(self):
        return self._leaving_time
    
    @leaving_time.setter
    def leaving_time(self, lt):
        if not lt:
            return
        try:
            date_obj = datetime.strptime(str(lt), DATE_TIME_FORMAT)
            self._leaving_time = date_obj
        except ValueError:
            self.errors.append('Leaving time is invalid')
        
        
    @property
    def car_identity(self):
        return self._car_identity

    @car_identity.setter
    def car_identity(self, ci):
        if not ci:
            self.errors.append('Car identity cannot be empty')
            return
        if not self.validate_car_identity(ci):
            self.errors.append('Invalid car identity format')
            return
        self._car_identity = ci
    
    def validate_car_identity(self, ci):
        pattern = r'^[0-9]{2}[A-Z]{1}-[0-9]{5}$'
        return re.match(pattern, ci) is not None
    
    @property
    def frequent_parking_number(self):
        return self._frequent_parking_number

    @frequent_parking_number.setter
    def frequent_parking_number(self, fpn):
        self.is_valid_fpn = False
        self._frequent_parking_number = fpn
        if not fpn or fpn == 'None':
            return
        if not self.validate_frequent_parking_number(fpn):
            self.errors.append('Invalid frequent parking number')
            return
        if calculate_modulo11_check_digit(fpn[:4]) == int(fpn[4:]):
            self.is_valid_fpn = True
                
    def validate_frequent_parking_number(self, fpn):
        pattern = r'^[0-9]{5}$'
        return re.match(pattern, fpn) is not None