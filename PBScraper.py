import httpx
from bs4 import BeautifulSoup
from typing import Tuple, Optional, List
from PBTerm import PBTerm
from PBCourse import PBCourse
from PBSubject import PBSubject, PBSection, PBClass, PBClassDays
from re import search
from datetime import *

class PBScraper:
    def __init__(self, userID: str, userPassword: str, debug = False) -> None:
        self.userID       = userID
        self.userPassword = userPassword
        self.session      = httpx.Client(follow_redirects=True, verify=False, headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'})
        self.baseURL      = 'https://selfservice.polytechnic.bh/PROD'
        self.debug        = debug

    def start(self):
        attempt_login = self.login()
        if attempt_login[0] == False:
            print(attempt_login[1])
            return
        print(f"Logged in as {self.userID}!")

    def login(self) -> Tuple[bool, Optional[str]]:
        '''
        (True, None) When a log in is successful,\n
        (False, str) When Login Failed with a reason message.
        '''

        login_page = self.session.get('https://selfservice.polytechnic.bh/PROD/twbkwbis.P_WWWLogin')
        if login_page.status_code != 200:
            reason = f"Failed to open Login Page [{login_page.status_code}]"
            return (False, reason + f"\n{login_page.text}" if self.debug else reason)

        login_page_soap        = BeautifulSoup(login_page.text, 'html.parser')
        login_page_form        = login_page_soap.find('form', id='fm1')

        login_page_form_action = login_page_form.get('action')
        login_page_form_lt     = login_page_form.find('input', {'name':'lt'}).get('value')

        if login_page_form_action == None:
            reason = "Failed to get login Action"
            return (False, reason  + f"\n{login_page.text}" if self.debug else reason)
        if login_page_form_lt == None or login_page_form_lt.startswith('LT') == False:
            reason = "Failed to get LT Token"
            return (False, reason + f"\n{login_page.text}" if self.debug else reason)
        
        login_payload = {
            'username' : self.userID,
            'password' : self.userPassword,
            'lt'       : login_page_form_lt,
            'execution': 'e1s1',
            '_eventId' : 'submit',
            'submit'   : 'LOGIN'
        }
        form_url      = 'https://bancas.polytechnic.bh:8443' + login_page_form_action

        login_request = self.session.post(form_url, data=login_payload)
        login_confirm = self.session.get(self.baseURL + '/xwskattr.p_view_calc')

        if self.userID not in login_confirm.text:
            reason = "Failed to login, wrong credentials"
            return (False, reason + f"\n{login_request.text}" if self.debug else reason)

        return (True, None)

    def get_terms(self) -> List[PBTerm]:
        '''
        [PBTerm] of the found terms,
        or a Reason string of the error if any happened.
        '''

        term_page = self.session.get(self.baseURL + '/bwskfcls.p_sel_crse_search')

        term_page_soap                 = BeautifulSoup(term_page.text, 'html.parser')
        term_page_form                 = term_page_soap.find_all('form')[1]
        term_page_form_terms_drop_menu = term_page_form.find('select', {'name':'p_term'})

        terms = []
        for option in term_page_form_terms_drop_menu.find_all('option'):
            if option.get('value') != '':
                term_text = option.text
                term_name = term_text.split('.')[0][:-2]
                terms.append(PBTerm(term_name, option.get('value')))
        return terms

    def get_courses(self, term: PBTerm) -> List[PBCourse]:
        '''
        Returns an array of courses for a given term,\n
        Any course that does not meet the criteria is not added.
        '''
        term_payload = {
            'p_calling_proc': 'P_CrseSearch',
            'p_term'        : term.term_code,
            'p_by_date'     : 'Y',
            'p_from_date'   : '',
            'p_to_date'     : ''
        }

        courses_page = self.session.post(self.baseURL + '/bwckgens.p_proc_term_date', data=term_payload)

        course_page_soap             = BeautifulSoup(courses_page.text, 'html.parser')
        course_page_form             = course_page_soap.find_all('form')[1]
        course_page_form_course_item = course_page_form.find('select', {'name':'sel_subj'})

        
        options = course_page_form_course_item.find('option')
        # Option section is broken so we take over manually
        options_str = str(options).splitlines()[:-1]
        courses     = []
        for option_str in options_str:
            course_name = option_str.split('">')[1]
            course_code = search('value="(\w+)"', option_str).group(1)
            if course_name and course_code != None or '':
                courses.append(PBCourse(course_name, course_code, term, []))

        return courses

    def get_subjects(self, courses: list[PBCourse]) -> None:
        '''
        Passed Courses will be updated with the subjects.
        '''
        subjects_payload = {
            "rsts": "dummy",
            "crn": "dummy",
            "term_in": courses[0].term.term_code,
            "sel_subj": [
                "dummy"
            ],
            "sel_day": "dummy",
            "sel_schd": "dummy",
            "sel_insm": "dummy",
            "sel_camp": "dummy",
            "sel_levl": "dummy",
            "sel_sess": "dummy",
            "sel_instr": "dummy",
            "sel_ptrm": [
                "dummy",
                "%"
            ],
            "sel_attr": "dummy",
            "sel_crse": "",
            "sel_title": "",
            "sel_from_cred": "",
            "sel_to_cred": "",
            "begin_hh": "0",
            "begin_mi": "0",
            "end_hh": "0",
            "end_mi": "0",
            "begin_ap": "x",
            "end_ap": "y",
            "path": "1",
            "SUB_BTN": "Course Search"
        }

        for course in courses:
            subjects_payload["sel_subj"].append(course.code)
        
        subjects_page             = self.session.post(self.baseURL+'/bwskfcls.P_GetCrse', data=subjects_payload)
        subjects_page_soap        = BeautifulSoup(subjects_page.text, 'html.parser')
        subjects_page_data_tables = subjects_page_soap.find_all('table', {'class': 'datadisplaytable'}, limit=len(courses)+1)[1:] #first table empty

        for subjects_page_data_table in subjects_page_data_tables:
            for item in subjects_page_data_table.find_all('td'):
                if item.find('form') != None:
                    subject_name, subject_code = [x.text for x in item.find_previous_siblings('td', limit=2)]
                    course_code = item.find_all('input', {'name':'sel_subj'}, limit=2)[1].get('value') # first item will be empty
                    subject = PBSubject(subject_name, subject_code, course_code, courses[0].term, [])
                    for course in courses:
                        if course.code == course_code:
                            course.subjects.append(subject)

    @staticmethod
    def _is_main_row(row) -> bool:
        first_3_td = row.find_all('td', limit=3)
        for td in first_3_td:
            if td.text.strip() == '':
                return False
        return True

    @staticmethod
    def _unwrap_main_row(row) -> Tuple:
        tds = [td.text for td in row.find_all('td')]
        #       crn, code, section, name, day1, raw_time, avail_seats, registered_seats, remaining_seats, instructor, location
        return (tds[1], tds[3], tds[4], tds[7], PBClassDays(tds[8]), tds[9], tds[10], tds[11], tds[12], tds[13], tds[15])

    @staticmethod
    def _unwrap_sub_row(row) -> Tuple:
        tds = [td.text for td in row.find_all('td')]
        #       day(n), raw_time, instructor, location
        return (PBClassDays(tds[8]), tds[9], tds[13], tds[15])

    def get_sections(self, subjects: List[PBSubject]) -> None:
        '''
        Any subject you don't need should be removed from the array.
        '''
        for subject in subjects:
            if self.debug: print(f'Loading sections for {subject.name}')
            sections_payload = {
                "term_in": subject.term.term_code,
                "sel_subj": [
                    "dummy",
                    subject.course
                ],
                "SEL_CRSE": subject.code,
                "SEL_TITLE": "",
                "BEGIN_HH": "0",
                "BEGIN_MI": "0",
                "BEGIN_AP": "a",
                "SEL_DAY": "dummy",
                "SEL_PTRM": "dummy",
                "END_HH": "0",
                "END_MI": "0",
                "END_AP": "a",
                "SEL_CAMP": "dummy",
                "SEL_SCHD": "dummy",
                "SEL_SESS": "dummy",
                "SEL_INSTR": [
                    "dummy",
                    "%"
                ],
                "SEL_ATTR": [
                    "dummy",
                    "%"
                ],
                "SEL_LEVL": [
                    "dummy",
                    "%"
                ],
                "SEL_INSM": "dummy",
                "sel_dunt_code": "",
                "sel_dunt_unit": "",
                "call_value_in": "",
                "rsts": "dummy",
                "crn": "dummy",
                "path": "1",
                "SUB_BTN": "View Sections"
            }

            subject_page       = self.session.post(self.baseURL + '/bwskfcls.P_GetCrse', data=sections_payload)
            if self.debug: print(f'Page loaded for {subject.name}')
            subject_page_soap  = BeautifulSoup(subject_page.text, 'html.parser')
            subject_page_table = subject_page_soap.find('table', {'class': 'datadisplaytable'})
            table_trs          = subject_page_table.find_all('tr')[2:]

            for idx, table_tr in enumerate(table_trs):
                if self._is_main_row(table_tr):
                    (crn, code, section, name, day1, raw_time,
                        avail_seats, registered_seats, remaining_seats,
                        instructor, location) = self._unwrap_main_row(table_tr)
                    

                    start_end = [datetime.strptime(x, '%I:%M %p') for x in raw_time.split('-')]
                    section_to_add = PBSection(
                        crn, code, section, name,
                        avail_seats, registered_seats,
                        remaining_seats, instructor, [PBClass(day1, *start_end, location)])
                    # find subrows after the current row
                    for sub_table_tr in table_trs[idx+1:]:
                        if self._is_main_row(sub_table_tr): break
                        (day1, raw_time, instructor, location) = self._unwrap_sub_row(sub_table_tr)
                        start_end = [datetime.strptime(x, '%I:%M %p') for x in raw_time.split('-')]
                        section_to_add.classes.append(PBClass(day1, *start_end, location))
                    
                    subject.sections.append(section_to_add)

                else:
                    continue
            
            if self.debug: print(f'Loaded sections for {subject.name}')

