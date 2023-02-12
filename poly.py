from getpass import getpass
from typing import List
from PBCourse import PBCourse
from PBSubject import PBSubject

userID       = input("SSB Username: ")
userPassword = getpass("SSB Password: ")

from PBScraper import PBScraper

scraper = PBScraper(userID, userPassword)
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

for subject in subjects_to_load:
    print(subject, '\n\n')