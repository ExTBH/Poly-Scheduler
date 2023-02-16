from getpass import getpass
from typing import List
from PBCourse import PBCourse
from PBSubject import PBSubject, PBSection, PBClassDays
import itertools
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
    for section in subject.sections:
        if section.on(breakDays) or section.before(start_hour):
            filtered_subjects[idx].sections.remove(section)


sections_pool = []
for subject in filtered_subjects:
    sections_pool.append(subject.sections)

final_sections: List[tuple[PBSection]] = []
# Tuple of PBSection
for outer_pool in itertools.product(*sections_pool):
    #loop over tuple
    for outer_itm in outer_pool:
        #loop again
        no_clash = True
        for inner_itm in outer_pool:
            # skip to next item in inner loop if same
            if outer_itm == inner_itm:
                continue
            # break inner in class and go to next
            if outer_itm._clashes(inner_itm):
                no_clash = False
                break
        if no_clash: final_sections.append(outer_pool)

print(len(final_sections))

for tup in final_sections:
    print('Stream:', end=' ')
    for sec in tup:
        print (f'[{sec.section}] {sec.name}', end=' ')
    print('\n')