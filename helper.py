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


def formator(req_str):
    if req_str.lower().startswith("either"):
        req_str = req_str[6:]
    elif req_str.lower().startswith("one of"):
        req_str = req_str[6:]
    else:
        req_list = req_str
        if req_list.startswith('or '):
            req_list = req_list[3:]
        if req_list.endswith('or'):
            req_list = req_list[:-2]
        req_list = req_list.strip(',. ')
        return req_list
    req_str = req_str.strip()
    req_list = re.split('\\([a-z]\\)', req_str.lower())[1:]
    if len(req_list) == 0:
        req_list = re.split(',|or ', req_str.lower())[1:]
    for j in range(len(req_list)):
        req_list[j] = req_list[j].strip()
        if req_list[j].startswith('a score of'):
            req_list[j] = formatminscore(req_list[j])
        elif req_list[j].startswith('one of') or req_str.lower().startswith("either"):
            req_list[j] = formator(req_list[j])
        else:
            req_list[j] = req_list[j].strip()
            if req_list[j].startswith('or '):
                req_list[j] = req_list[j][3:]
            if req_list[j].endswith('or'):
                req_list[j] = req_list[j][:-2]
            req_list[j] = req_list[j].strip(' .')
            # is a course?
            if len(req_list[j].split(' ')) == 2 and isint(req_list[j].split(' ')[1]):
                req_list[j] = Course(req_list[j].split(' ')[0], req_list[j].split(' ')[1])

    return req_list


def formatminscore(req_str):
    if req_str.lower().startswith('a score of'):
        req_str = req_str.lower().split('a score of ')[1]
        try:
            return_tup = (int(req_str.split('%')[0]), formator(req_str.split('or higher in ')[1]))
        except ValueError:
            return_tup = (404, ["error parsing min score sentence"])
        return return_tup


def parsereqs(req_str):
    #req_list = req_str.split(' and ')
    req_list = re.split(' and |\\. ', req_str.lower())
    pop_list = []
    for i in range(len(req_list)):
        req_list[i] = req_list[i].strip(' .,')
        if req_list[i].lower().strip().startswith('either') or req_list[i].lower().strip().startswith('one of'):
            req_list[i] = formator(req_list[i])
        elif req_list[i].lower().strip().startswith('a score of'):
            req_list[i] = formatminscore(req_list[i])
        elif req_list[i].strip == '':
            pop_list.append(i)
        elif len(req_list[i].split(' ')) == 2 and isint(req_list[i].split(' ')[1]):
            req_list[i] = Course(req_list[i].split(' ')[0], req_list[i].split(' ')[1])
    for i in pop_list:
        req_list.pop(i)

    return req_list


def printreqs(req_list, indent):
    for prereq in req_list:
        for i in range(indent):
            print("\t", end='')
        print(prereq)
    print('\n')


class CourseInfo:
    def __init__(self, course_name='unset', course_code='unset', course_number='unset', course_credit=None,
                 course_description='unset', course_prereqs=None, course_coreqs=None, course_equivalency=None,
                 course_cdf=True):
        if course_coreqs is None:
            course_coreqs = []
        if course_prereqs is None:
            course_prereqs = []
        if course_credit is None:
            course_credit = 404
        if course_equivalency is None:
            course_equivalency = []
        self.name = course_name
        self.credits = course_credit
        self.prereqs = course_prereqs
        self.coreqs = course_coreqs
        self.code = course_code
        self.number = course_number
        self.description = course_description
        self.equivalency = course_equivalency
        self.cdf = course_cdf

    def __str__(self):
        # general info
        returnstr = "%s %s - %s:\n\tCredits: %s\n" % (self.code, self.number, self.name,
                                                      'unset' if self.credits == 404 else self.credits)

        # prerequisites
        returnstr += "\tPrerequisites:\n"
        if len(self.prereqs) == 0:
            returnstr += "\t\tNone\n"
        else:
            for prereq in self.prereqs:
                returnstr += "\t\t"
                if isinstance(prereq, tuple):  # minimum in one of courses

                    if isinstance(prereq[1], list):
                        returnstr += "Minimum %d%% in one of\n:" % prereq[0]
                        for course in prereq[1]:
                            returnstr += "\t\t\t%s\n" % str(course)
                        returnstr = returnstr.strip()
                    elif isinstance(prereq[1], str):
                        returnstr += "Minimum %d%% in:" % prereq[0]
                        returnstr += " %s\n" % prereq[1]
                    elif isinstance(prereq[1], Course):
                        returnstr += "Minimum %d%% in:" % prereq[0]
                        returnstr += " %s\n" % str(prereq[1])

                elif isinstance(prereq, list):  # one of these courses\
                    returnstr += "One of:\n"
                    for oneof in prereq:
                        if isinstance(oneof, tuple):  # minimum average in courses

                            if isinstance(oneof[1], list):
                                returnstr += "\t\t\tMinimum %d%% in one of:\n" % oneof[0]
                                for course in oneof[1]:
                                    returnstr += "\t\t\t\t%s\n" % str(course)
                            elif isinstance(oneof[1], str):
                                returnstr += "\t\t\tMinimum %d%% in:" % oneof[0]
                                returnstr += " %s\n" % oneof[1]
                            elif isinstance(oneof[1], Course):
                                returnstr += "\t\t\tMinimum %d%% in:" % oneof[0]
                                returnstr += " %s\n" % str(oneof[1])

                        elif isinstance(oneof, str):    # non-parsable
                            returnstr += "\t\t\t%s\n" % oneof

                        elif isinstance(oneof, list):  # a bunch of courses
                            returnstr += "\t\t\tOne of:\n"
                            for course in oneof:
                                returnstr += "\t\t\t\t%s\n" % str(course)

                        elif isinstance(oneof, Course):  # Course
                            returnstr += "\t\t\t%s\n" % str(oneof)

                    returnstr = returnstr.strip(' ')

                elif isinstance(prereq, Course):  # a class
                    returnstr += str(prereq)
                    returnstr += "\n"

                elif isinstance(prereq, str):  # a class
                    returnstr += prereq
                    returnstr += "\n"


        # corequisites
        returnstr += "\tCorequisites:\n"
        if len(self.coreqs) == 0:
            returnstr += "\t\tNone\n"
        else:
            for coreq in self.coreqs:
                returnstr += "\t\t"
                if isinstance(coreq, tuple):  # minimum average in courses
                    returnstr += "Minimum %d%% in:\n" % coreq[0]
                    for course in coreq[1]:
                        returnstr += "\t\t\t%s\n" % str(course)
                    returnstr = returnstr.strip()

                elif isinstance(coreq, list):  # one of these courses\
                    returnstr += "One of:\n"
                    for oneof in coreq:
                        if isinstance(oneof, tuple):  # minimum average in courses
                            returnstr += "\t\t\tMinimum %d%% in one of:\n" % oneof[0]
                            for course in oneof[1]:
                                returnstr += "\t\t\t\t%s\n" % str(course)

                        elif isinstance(oneof, list):  # a bunch of courses
                            returnstr += "\t\t\tOne of:\n"
                            for course in oneof:
                                returnstr += "\t\t\t\t%s\n" % str(course)

                        elif isinstance(oneof, Course):  # Course
                            returnstr += "\t\t\t%s\n" % str(oneof)

                        elif isinstance(oneof, str):    # non-parsable
                            returnstr += "\t\t\t%s\n" % oneof
                    returnstr = returnstr.strip()

                elif isinstance(coreq, Course):  # a class
                    returnstr += str(coreq)
                    returnstr += "\n"

                elif isinstance(coreq, str):  # a class
                    returnstr += str
                    returnstr += "\n"
        if len(self.equivalency) > 0:
            returnstr += "\tEquivalency:\n"
            for equiv in self.equivalency:
                returnstr += "\t\t%s\n" % str(equiv)

        returnstr += "\tCr/D/F Eligibility: %s" % 'Eligible' if self.cdf else 'NOT eligible'

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


def collectcourses():
    courses = CourseList()
    cc = input('Enter course code (Ex. MATH 100) leave blank to continue: ')
    while cc != "":
        if cc == "/scan":
            break
        courses.add(Course(cc.split()[0], cc.split()[1]))
        cc = input('Enter course code (Ex. MATH 100) leave blank to continue: ')
    return courses
