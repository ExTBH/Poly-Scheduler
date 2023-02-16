from dataclasses import dataclass
from typing import List
from enum import Enum
from PBTerm import PBTerm
from datetime import *
import numpy as np

class PBClassDays(Enum):
    sunday    = 'U'
    monday    = 'M'
    tuesday   = 'T'
    wednesday = 'W'
    thursday  = 'R'


@dataclass
class PBClass:
    day     : PBClassDays
    start   : datetime
    end     : datetime
    location: str

    def _range_in_week(self) -> List[int]:
        muliplier = 0
        match self.day:
            case PBClassDays.sunday:
                muliplier = 1
            case PBClassDays.monday:
                muliplier = 2
            case PBClassDays.tuesday:
                muliplier = 3
            case PBClassDays.wednesday:
                muliplier = 4
            case PBClassDays.thursday:
                muliplier = 5

        st_float = (self.start.hour * 60 + self.start.minute) / 10
        en_float = (self.end.hour * 60 + self.end.minute) / 10
        #round minutes to next group, i.e 9:01 > 9:10, 9:00 > 9:00
        st = int(st_float if st_float.is_integer() else np.ceil(st_float))
        en = int(en_float if en_float.is_integer() else np.ceil(en_float))
        return (
            list(
                range(st * muliplier, (en * muliplier) + 1)
            )
        )
@dataclass
class PBSection:
    crn             : int
    code            : str
    section         : int
    name            : str
    available_seats : int
    registered_seats: int
    remaining_seats : int
    instructor      : str
    classes         : List[PBClass]

    def on(self, days: List[PBClassDays]) -> bool:
        '''
        Checks if a section have a class on the given days.
        '''
        for clazz in self.classes:
            if clazz.day in days:
                return True
        return False

    def before(self, time: datetime) -> bool:
        '''
        Checks if a section have a class before a given hour.
        '''
        for clazz in self.classes:
            if time > clazz.start:
                return True
        return False
    
    def ranges_in_week(self) -> List[List[int]]:
        '''
        Convenice method.
        '''
        return [clazz._range_in_week() for clazz in self.classes]





@dataclass
class PBSubject:
    name    : str
    code    : str
    course  : str
    term    : PBTerm
    sections: List[PBSection]
    # add subject comparison
