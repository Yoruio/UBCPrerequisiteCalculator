from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from selenium.webdriver.chrome.options import Options


class Course:
    def __init__(self, code, number):
        self.code = str(code).upper()
        self.number = str(number).upper()

    def __str__(self):
        return "%s %s" % (self.code.upper(), self.number)


def find(numbers, match):
    for i in numbers:
        if i == match:
            return True
    return False


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
CC = input('Enter Course Code (Ex. MATH 100): ')
while CC != "":
    courses.add(Course(CC.split()[0],CC.split()[1]))
    CC = input('Enter Course Code (Ex. MATH 100): ')
print(courses.list)

browser = webdriver.Chrome(ChromeDriverManager().install())

for i in courses.list:
    browser.get("http://www.calendar.ubc.ca/vancouver/courses.cfm?page=code&code=%s" % (i[0]))
    elements = browser.find_elements_by_xpath('//*[@name="%s"]/parent::dt/following-sibling::dd[1]' % (i[1][0]))
    print(elements)
    for element in elements:
        print(element.text)


'''
    browser.get("https://www.bcgreengames.ca/project/zero-waste3634")
    time.sleep(sleepTime)

    likeButton = browser.find_element_by_id('lb-like-0')
    # time.sleep(sleepTime)

    likeButton.click()
    # time.sleep(sleepTime)

    voteCount = browser.find_element_by_class_name('lb-count');
    print("votes: " + voteCount.get_attribute('data-count'))

    time.sleep(voteTime + randint(0, randTime))
'''
browser.quit()

