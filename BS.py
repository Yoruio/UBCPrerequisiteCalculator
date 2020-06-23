from helper import *
from requests import get
from bs4 import BeautifulSoup, element


courses = collectcourses()
print(courses.list)

for i in courses.list:
    code = i[0]
    html = get("http://www.calendar.ubc.ca/vancouver/courses.cfm?page=code&code=%s" % code).text
    bs = BeautifulSoup(html, 'html.parser')
    for number in i[1]:
        info = CourseInfo()
        name = bs.find("a", {"name": str(number)})
        if name is None:
            print("could not find course: %s %s" % (code, number))
            continue
        name = name.findParent("dt")
        print(name.text)
        description = name.findNext('dd')
        name = name.text
        print(description.get_text(separator='\n'))
        ptype = 0
        pnum = 0

        info.credits = name[name.find('(') + 1:name.find(')')]
        info.name = name[name.find(')')+2:]
        info.code = code
        info.number = number

        for paragraph in description.get_text(separator='\n---\n').split('\n---\n'):
            paragraph = paragraph.strip()
            if ptype == 0:
                if pnum == 0:
                    info.description = paragraph
                elif paragraph.lower().startswith('prerequisite'):
                    ptype = 1
                elif paragraph.lower().startswith('corequisite'):
                    ptype = 2
                elif paragraph.lower().startswith('equivalency'):
                    ptype = 3
                elif 'this course is not eligible for credit/d/fail grading' in paragraph:  #cr/d/f
                    info.cdf = False
                elif re.search(r'\[[0-9]-[0-9]-[0-9]\*?\]', paragraph): #hours required
                    pass
            elif ptype == 1:
                info.prereqs = parsereqs(paragraph.strip())
                ptype = 0
            elif ptype == 2:
                info.coreqs = parsereqs(paragraph.strip())
                ptype = 0
            elif ptype == 3:
                info.equivalency = parsereqs(paragraph.strip())
                ptype = 0
            pnum += 1

        print(info)