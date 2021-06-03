from bs4 import BeautifulSoup
import requests
import shelve
import os

# 'tr' - строка, 'td' - ячейка таблицы
URL = 'http://p11505.edu35.ru/gmraspisanie/izmeneniya'
NUM = '41/2020'

def status():
    page = requests.get('http://p11505.edu35.ru/gmraspisanie/izmeneniya')
    if page.status_code != 200:
        return
    else:
        return 1
    
# Получение расписания с сайта колледжа
def lessons():
    
    # Инициализация работы с сайтом
    if not status():
        return
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    date = soup.find_all('tr')[1].text 
    groups = soup.find_all('tr')

    # Опрделение позиции
    for _ in range(len(groups)):
        if NUM in groups[_].text:
            pos = _
            for x in groups[_ + 1 : -1]:
                if 'Расписание звонков' in x.text:
                    break
                pos += 1
            position = (_ + 2, pos + 1, groups[_].text.split().index(NUM) - 1)  # (Верхняя граница, нижняя граница, Позиция по горизонтали)
            break

    time_t = []
    c = 0
    i = 0
    timetable = []    
    for _ in groups[position[0] : position[1]]:
        if i:
            c *= 2
            i = 0

        if not c:
            c = _.text.split().count('практика')
            i = 1
        
        if 'Обед' in _.text:
            time_t.append(_.text.split()[0])
            continue
        
        time_t.append(_.text.split()[0])
        timetable.append(_.find_all('td')[position[-1] * 2 - 2 - c].text)

    while True:
        if timetable[-1] == '\xa0':
            timetable.pop()
        else:
            break
        
    while len(time_t) != len(timetable) + 1:
        time_t.pop()           
    return date, timetable, time_t


# Создание файлов для записи туда текст дз
def file_maker():
    if not os.path.isdir(os.getcwd() + '/Homework'): #Если папки нет, то она создаётся
        os.mkdir(os.getcwd() + '/Homework')
        s = shelve.open(os.getcwd() +'/Homework/homework_list')
        s['Русский язык'] = ['Ничего не задано.']
        s['Литература'] = ['Ничего не задано.']
        s['Немецкий язык'] = ['Ничего не задано.']
        s['Английский язык'] = ['Ничего не задано.']
        s['История'] = ['Ничего не задано.']
        s['Физическая культура'] = ['Ничего не задано.']
        s['Обж'] = ['Ничего не задано.']
        s['Астрономия'] = ['Ничего не задано.']
        s['Химия'] = ['Ничего не задано.']
        s['Математика'] = ['Ничего не задано.']
        s['Информатика'] = ['Ничего не задано.']
        s['Физика'] = ['Ничего не задано.']
        s['Обществознание'] = ['Ничего не задано.']
        s['Дата'] = []
        s.sync()
        s.close()

def one_hw(subject):
    file_maker()
    s = shelve.open(os.getcwd() + '/Homework/homework_list')
    d = s[subject][0]
    s.close()    
    return d

# Запись дз в файл
def homework_write(subject, home_text):
    print('7')
    print(subject, home_text)
    file_maker()    
    s = shelve.open(os.getcwd() + '/Homework/homework_list')

    # Запись дз в определёную ячейку файла
    if subject == 'Русский язык':
        s['Русский язык'] = [home_text]
    elif subject == 'Литература':
        s['Литература'] = [home_text]
    elif subject == 'Немецкий язык':
        s['Немецкий язык'] = [home_text]
    elif subject == 'Английский язык':
        s['Английский язык'] = [home_text]
    elif subject == 'История':
        s['История'] = [home_text]
    elif subject == 'Физическая культура':
        s['Физическая культура'] = [home_text]
    elif subject == 'Обж':
        s['Обж'] = [home_text]
    elif subject == 'Астрономия':
        s['Астрономия'] = [home_text]
    elif subject == 'Химия':
        s['Химия'] = [home_text]
    elif subject == 'Математика':
        s['Математика'] = [home_text]
    elif subject == 'Информатика':
        s['Информатика'] = [home_text]
    elif subject == 'Физика':
        s['Физика'] = [home_text]
    elif subject == 'Обществознание':
        s['Обществознание'] = [home_text]
    else:
        print('4444')
        return
    s.sync()
    s.close()


# Выборка уроков для последующих операций
def lesson_compleater(lessons):
    common = []
        
    for _ in lessons:
        if _ in common:
            continue
        else:
            common.append(_)
    return common


def les(lessons):
    c = lesson_compleater(lessons)[1]
    a = []

    for _ in c:
        if _ in a or _ == '-':
            continue
        else:
            a.append(_)
    return a


# Форматирование и объединение даты и расписания под одной переменной
def text_converter(date = None, lesson = None, t = None):
    text_vk = ''
    i = 0

    if not lesson and not date:
        date, lesson, t = lessons()
        
    text_vk = text_vk + date + '\n'
    c = 1
    for _ in lesson:
        i += 1
        if t:
            if t[i - c] == 'Обед':
                text_vk += t[i - c] + '\n'
                c = 0
            
            text_vk = text_vk + str(i)+')' + t[i - c] + ' ' + _ + '\n'
        else:
            text_vk = text_vk + str(i)+')' + ' ' + _ + '\n'

    return text_vk


# Подбор дз по расписанию   
def homework_compleater(lesson = None):      
    file_maker()

    # Если расписание было получено с сайта
    if not lesson:
        date, lesson, t = lessons()
        
    s = shelve.open(os.getcwd() + '/Homework/homework_list')
    homework_c = ''
    i = 1

    # Добавление и форматирование текста дз
    lessons_list= lesson_compleater(lesson)
    for subject in lessons_list:
        subject = subject.split()[0]
        
        if subject.strip() == 'Русский':
            sub = ''.join(s['Русский язык'])
            homework_c = homework_c + str(i)+')' + subject + ' язык' + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Литература':
            sub = ''.join(s['Литература'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Немецкий':
            sub = ''.join(s['Немецкий язык'])
            homework_c = homework_c + str(i)+')' + subject + ' язык - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Английский':
            sub = ''.join(s['Английский язык'])
            homework_c = homework_c + str(i)+')' + subject + 'язык - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Иностранный':
            sub = ''.join(s['Немецкий язык'])
            sub1 = ''.join(s['Английский язык'])
            homework_c = homework_c + str(i)+')' + 'Немецкий язык - ' + sub + '\nАнглийский язык - ' + sub1 + '\n'
            i += 1

        elif subject.strip() == 'История':
            sub = ''.join(s['История'])
            
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Физическая':
            sub = ''.join(s['Физическая культура'])
            homework_c = homework_c + str(i)+')' + subject + ' культура' + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Обж':
            sub = ''.join(s['Обж'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Астрономия':
            sub = ''.join(s['Астрономия'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Химия':
            sub = ''.join(s['Химия'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Математика':
            sub = ''.join(s['Математика'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1
            
        elif subject == 'Информатика':
            sub = ''.join(s['Информатика'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Физика':
            sub = ''.join(s['Физика'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        elif subject.strip() == 'Обществознание':
            sub = ''.join(s['Обществознание'])
            homework_c = homework_c + str(i)+')' + subject + ' - ' + sub + '\n'
            i += 1

        else:
            continue

    homework_c = '\nДомашнее задание.\n' + homework_c

    s.close()
    
    return homework_c


# Отображение всего дз из файла
def all_hw():
    file_maker()    
    s = shelve.open(os.getcwd() + '/Homework/homework_list')
    hw = ('''
1) Русский язык - {}
2) Литература - {}
3) Немецкий язык - {}
4) Английский язык - {}
5) История - {}
6) Физическая культура - {}
7) ОБЖ - {}
8) Астрономия - {}
9) Химия - {}
10) Математика - {}
11)Информатика - {}
12)Физика - {}
13)Обществознание - {}
'''.format(''.join(s['Русский язык']),''.join(s['Литература']),''.join(s['Немецкий язык']),''.join(s['Английский язык']),''.join(s['История']),''.join(s['Физическая культура']),''.join(s['Обж']),''.join(s['Астрономия']),''.join(s['Химия']),''.join(s['Математика']),''.join(s['Информатика']),''.join(s['Физика']),''.join(s['Обществознание'])))

    return hw
