from dataclasses import dataclass
from typing import List
from PBSubject import PBSubject
from PBTerm import PBTerm

@dataclass
class PBCourse:
    name    : str
    code    : str
    term    : PBTerm
    subjects: List[PBSubject]