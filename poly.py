from getpass import getpass
from typing import List
from PBCourse import PBCourse
from PBSubject import PBSubject, PBSection, PBClassDays
import itertools
import numpy as np
from datetime import *

userID       = input("SSB Username: ")
userPassword = getpass("SSB Password: ")

from PBScraper import PBScraper

scraper = PBScraper(userID, userPassword, True)
scraper_login = scraper.login()
if scraper_login[0] == False:
    print(scraper_login[1])
    exit(1)

scraper_terms = scraper.get_terms()

scraper_courses = scraper.get_courses(scraper_terms[0])
print('_'*20)
for index, course in enumerate(scraper_courses):
    print(str(index), course.name)

selected_courses_indexes = [int(x) for x in input(f"Select a Courses (space-separated)[0-{len(scraper_courses)-1}]: ").split()]
print('_'*20)

selected_courses: List[PBCourse] = []
for index, course in enumerate(scraper_courses):
    if index in selected_courses_indexes:
        selected_courses.append(course)

scraper.get_subjects(selected_courses)

subjects_to_load: List[PBSubject] = []
for course in selected_courses:
    print(course.name)
    print('_'*20)
    for index, course_subject in enumerate(course.subjects):
        print(f'{index}|', course_subject.code, course_subject.name)
    selected_subjects_indexes = [int(x) for x in input(f"Select Subjects (space-separated)[0-{len(course.subjects)-1}]: ").split()]
    print('_'*20)
    for idx in selected_subjects_indexes:
        subjects_to_load.append(course.subjects[idx])

scraper.get_sections(subjects_to_load)

breakDays = [PBClassDays(x) for x in input("Enter Break days [U, M, T, W, R] (space-separated): ").split()]
start_hour = datetime.strptime(input('What time you want the classes to start at [H:MM (A/P)M]: '), '%I:%M %p')

filtered_subjects = subjects_to_load
for idx, subject in enumerate(subjects_to_load):
    to_remove = []
    for idy, section in enumerate(subject.sections):
        if section.on(breakDays) or section.before(start_hour):
            to_remove[:0] = [idy]
    for idy in to_remove:
        subjects_to_load[idx].sections.pop(idy)


sections_pool = [subject.sections for subject in filtered_subjects]

final_sections: List[tuple[PBSection]] = []
for sections_tuple in itertools.product(*sections_pool):
    # 144 10 minutes in a day by 5 days
    week_vectors = [np.zeros(144*5, dtype=bool) for _ in range(0, len(sections_tuple))]

    for idx in range(0, len(sections_tuple)):
        clss_ranges = sections_tuple[idx].ranges_in_week()
        for rng in clss_ranges:
            np.put(week_vectors[idx], rng, np.ones(len(rng), dtype=bool))
    
    mtrx = np.array(week_vectors)
    
    for x in mtrx:
        skipper = False
        for nested_x in mtrx:
            if np.array_equal(nested_x, x) : continue
            did_clash = np.sum(nested_x * x, dtype=bool)
            if did_clash:
                skipper = True
                break

        if skipper == False:
            final_sections.append(sections_tuple)
    


for idx, sctn_pool in enumerate(final_sections):
    print(f'Schedule #{idx} --', end=' ')
    for sctns in sctn_pool:
        print(f'[{sctns.section}] {sctns.code} {sctns.name}', end=' --- ')
    print('\n')
