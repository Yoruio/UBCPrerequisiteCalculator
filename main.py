from selenium import webdriver
import re
import time
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from selenium.webdriver.chrome.options import Options


def find(numbers, match):
    for i in numbers:
        if i == match:
            return True
    return False


def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def parsereqs(req_str):
    req_list = req_str.split(' and ')
    for i in range(len(req_list)):
        if req_list[i].lower().startswith("one of"):
            req_list[i] = req_list[i].lower().split('one of')[1].split(", ")
            for j in range(len(req_list[i])):
                req_list[i][j] = req_list[i][j].strip()
                if req_list[i][j].startswith("or "):
                    req_list[i][j] = req_list[i][j].split("or ")[1]
                if req_list[i][j].startswith("("):
                    req_list[i][j] = req_list[i][j][4:]
                if req_list[i][j].endswith("."):
                    req_list[i][j] = req_list[i][j][:-1]
                #is a course?
                if len(req_list[i][j].split(' ')) == 2 and isint(req_list[i][j].split(' ')[1]):
                    req_list[i][j] = Course(req_list[i][j].split(' ')[0],req_list[i][j].split(' ')[1])

    return req_list


def printreqs(req_list, indent):
    for prereq in req_list:
        for i in range(indent):
            print("\t", end='')
        print(prereq)
    print('\n')


class CourseInfo:
    def __init__(self, course_name='unset', course_code='unset', course_number='unset', course_credit=None,
                 course_description='unset', course_prereqs=None, course_coreqs=None):
        if course_coreqs is None:
            course_coreqs = []
        if course_prereqs is None:
            course_prereqs = []
        if course_credit is None:
            course_credit = 404
        self.name = course_name
        self.credits = course_credit
        self.prereqs = course_prereqs
        self.coreqs = course_coreqs
        self.code = course_code
        self.number = course_number
        self.description = course_description

    def __str__(self):
        # general info
        returnstr = "%s %s - %s:\n\tCredits: %s\n" % (self.code, self.number, self.name,
                                                      'unset' if self.credits == 404 else str(self.credits))

        # prerequisites
        returnstr += "\tPrerequisites:\n"
        if len(self.prereqs) == 0:
            returnstr += "\t\tNone\n"
        else:
            for prereq in self.prereqs:
                returnstr += "\t\t%s\n" % prereq

        # corequisites
        returnstr += "\tCorequisites:\n"
        if len(self.coreqs) == 0:
            returnstr += "\t\tNone\n"
        else:
            for coreq in self.coreqs:
                returnstr += "\t\t%s\n" % coreq

        return returnstr


class Course:
    def __init__(self, code, number):
        self.code = str(code).upper()
        self.number = str(number).upper()

    def __str__(self):
        return "%s %s" % (self.code.upper(), self.number)

    def __repr__(self):
        return "%s %s" % (self.code.upper(), self.number)


class CourseList:
    def __init__(self):
        self.list = []

    def add(self, course):
        found = False
        for c in self.list:
            if c[0] == course.code:
                if not find(c[1], course.number):
                    c[1].append(course.number)
                found = True
        if not found:
            self.list.append((course.code, [course.number]))


'''
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')

chrome_options = Options()

chrome_options.add_argument('--headless')

chrome_options.add_argument('log-level=2')
'''

courses = CourseList()
CC = input('Enter course code (Ex. MATH 100) leave blank to continue: ')
while CC != "":
    courses.add(Course(CC.split()[0], CC.split()[1]))
    CC = input('Enter course code (Ex. MATH 100) leave blank to continue: ')
print(courses.list)

browser = webdriver.Chrome(ChromeDriverManager().install())
info_list = []
# populate info_list
for course in courses.list:
    code = course[0]
    browser.get("http://www.calendar.ubc.ca/vancouver/courses.cfm?page=code&code=%s" % code)
    if browser.current_url.endswith('index.cfm'):
        print('WARNING: Could not find course code %s' % code)
    else:
        for number in course[1]:

            # find corresponding course name and page element
            element = browser.find_elements_by_xpath('//*[@name="%s"]/parent::dt/following-sibling::dd[1]' % number)
            if len(element) == 0:
                print('WARNING: Could not find course %s %s' % (code, number))
            elif len(element) > 1:
                print('WARNING: Duplicate course %s %s?' % (code, number))
            else:
                name = browser.find_elements_by_xpath('//*[@name="%s"]/parent::dt' % number)
                name = name[0].text
                credit = name[name.find('(') + 1:name.find(')')]

                info = CourseInfo()
                info.name = name.split(') ', 1)[1]
                info.code = code
                info.number = number
                info.credits = int(credit)

                element = element[0]

                # find prerequisites and corequisites
                for paragraph in element.text.split('\n'):
                    if paragraph.lower().startswith('prerequisite'):
                        prereqs = paragraph.split(': ', 1)[1]
                        info.prereqs = parsereqs(prereqs)

                    if paragraph.lower().startswith('corequisite'):
                        coreqs = paragraph.split(': ', 1)[1]
                        info.coreqs = parsereqs(coreqs)
                info_list.append(info)


for course in info_list:
    # print(course)
    print(course.code + " " + course.number + ": ")
    print(course.prereqs)

browser.quit()
