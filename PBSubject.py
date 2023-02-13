from dataclasses import dataclass
from typing import List
from enum import Enum
from PBTerm import PBTerm
from datetime import *

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

@dataclass
class PBSubject:
    name    : str
    code    : str
    course  : str
    term    : PBTerm
    sections: List[PBSection]
    # add subject comparison
