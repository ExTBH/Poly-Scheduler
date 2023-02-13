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
print(f'{len(filtered_subjects[0].sections)} : {len(filtered_subjects[1].sections)}')
for idx, subject in enumerate(subjects_to_load):
    for section in subject.sections:
        if section.on(breakDays) or section.before(start_hour):
            filtered_subjects[idx].sections.remove(section)

print(f'{len(filtered_subjects[0].sections)} : {len(filtered_subjects[1].sections)}')

sections_pool = []
for subject in filtered_subjects:
    sections_pool.append(subject.sections)

for pool in itertools.product(*sections_pool):
    print('Schedule 2:', end=' ')
    for idx in range(0, len(filtered_subjects)):
        print (f'[{pool[idx].section}] {pool[idx].name}', end=' ')
    print('\n')
