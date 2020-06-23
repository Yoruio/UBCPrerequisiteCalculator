from selenium import webdriver
import re
import time
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from selenium.webdriver.chrome.options import Options
from helper import *


'''
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')

chrome_options = Options()

chrome_options.add_argument('--headless')

chrome_options.add_argument('log-level=2')
'''

courses = collectcourses()
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
                info.credits = credit

                element = element[0]

                # find prerequisites and corequisites
                for paragraph in element.text.split('\n'):
                    if paragraph.lower().startswith('prerequisite'):
                        prereqs = paragraph.split(': ', 1)[1]
                        info.prereqs = parsereqs(prereqs)

                    if paragraph.lower().startswith('corequisite'):
                        coreqs = paragraph.split(': ', 1)[1]
                        info.coreqs = parsereqs(coreqs)

                    if paragraph.lower().startswith('equivalency'):
                        equivs = paragraph.split(': ', 1)[1]
                        info.equivalency = parsereqs(equivs)
                info_list.append(info)

for course in info_list:
    # print(course)
    print(course)

browser.quit()
