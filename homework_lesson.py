from bs4 import BeautifulSoup
import requests
import shelve
import os

# 'tr' - строка, 'td' - ячейка таблицы


def status():
    page = requests.get('http://p11505.edu35.ru/gmraspisanie/izmeneniya', timeout = 5)
    print(page.status_code)
    if page.status_code != 200:
        return
    else:
        return 1
    
# Получение расписания с сайта колледжа
def lessons():
    # Создание переменных
    groups = []
    first_p = []
    x = 0
    pos = 0
    num_group = '41/2020'
    url = 'http://p11505.edu35.ru/gmraspisanie/izmeneniya'
    l = []
    l_text = []

    # Инициализация работы с сайтом
    page = requests.get(url)

    # На случай, если сайт упадёт
    if page.status_code != 200:
        return

    # Продолжение работы с сайтом
    soup = BeautifulSoup(page.text, 'html.parser')
    groups = soup.find_all('tr',style = 'height: 13.5pt;')[0]

    # Поиск даты занятий
    date = soup.find('tr',style = 'height: 23.25pt;').text
    
    # Опредиление позиции номера группы 1 смена
    try:
        for i in range(3):
            position = 0
            groups = soup.find_all('tr',style = 'height: 13.5pt;')[x]
            for _ in groups.find_all('td'):
                if _.text.strip() == '':
                    position -= 1
                if _.text == num_group:
                    smena = 1
                    pos = position
                    les_v = x
                    break
                position += 1
            x += 2
    except:
        print('!')

    # Опредиление позиции номера группы 2 смена
    if pos == 0:
        x = 0
        for i in range(2):
            position = 0
            groups = soup.find_all('tr',style = 'height: 12pt;')[x]
            for _ in groups.find_all('td'):
                if _.text.strip() == '':
                    position -= 1
                if _.text == num_group:
                    smena = 2
                    pos = position
                    les_v = x
                    break
                position += 1
            x += 2

    # Опредиление позиции расписания группы
    if pos == 2:
        pos_l = 2
    elif pos == 3:
        pos_l = 4
    elif pos == 4:
        pos_l = 6
    elif pos == 5:
        pos_l = 8
    elif pos == 6:
        pos_l = 10
    elif pos == 7:
        pos_l = 12
    elif pos == 8:
        pos_l = 14
    else:
        pos_l = 16

    # Опредиление кол-ва циклов
    if les_v == 0:
        count = 1
    elif les_v == 2:
        count = 2
    elif les_v == 4:
        count = 3

    # Выбор нижней или верхней таблицы
    if smena == 1:
        st = 'height: 11.25pt;'
    else:
        st = 'padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: Calibri, sans-serif; vertical-align: middle; white-space: nowrap; height: 11.25pt;'

    # Опредиление кол-ва уроков       
    lesson_count = 0 
    for _ in range(count):
        start_position = lesson_count
        while True:
            lesson_count += 1
            try:
                p = soup.find_all('tr',style = st)[lesson_count]
            except:
                break
            if '1' in p.find_all('td')[1].text:
                break

    # Добавление и изменение переменных для составления расписания
    i = 1
    pos_cut = 0
    tr = 2
    lesson_count = lesson_count - start_position
    x = 0

    print(lesson_count)
    # Кол-во циклов зависит от кол-ва уроков
    for _ in range(lesson_count):
        print(_)
        print(l)
        first_p = soup.find_all('tr',style = st)[_+start_position]

        # Проверка первой строки, используется только один раз
        if tr == 2:
            for a in range(pos_l):

                # Если в строке имеется что-то из этого, то строка смещается на 1 вправо
                if first_p.find_all('td')[a].text == 'Производственная практика' or first_p.find_all('td')[a].text == 'Учебная практика':#Опредиление кол-ва практик и расчёт коэфициента
                    pos_cut += 1
            tr = 0

        # Если встречается обед, то идёт проверка на наличие учебной практики
        if first_p.find_all('td')[2].text == 'Обед':
            correct = soup.find_all('tr',style = st)[_+start_position+1]
            for a in range(pos_l):

                # Если есть, то строка смещается на 1 влево,т. к. практика встречается два раза
                try:
                    if correct.find_all('td')[a].text == 'Учебная практика':
                        pos_cut -= 1
                except:
                    print('skip')
            i = 0
            x = 1
            continue

        # Если встречается '', то происходит замена на '-'
        if (first_p.find_all('td')[pos_l - pos_cut].text.strip()) == '':
            l.append('-')

        # Если они встречаются в строке, то их добавляем
        if first_p.find_all('td')[pos_l - pos_cut].text == 'Производственная практика' or first_p.find_all('td')[pos_l - pos_cut].text == 'Учебная практика':
            l.append(first_p.find_all('td')[pos_l].text)
            break

        # Добавление уроков
        if (first_p.find_all('td')[pos_l - pos_cut].text.strip()) != '':
            l.append(first_p.find_all('td')[pos_l - pos_cut].text)

        # Повторный расчёт смещения, используется только один раз
        if tr == 0 or x == 1:
            for a in range(pos_l):
                try:
                    if first_p.find_all('td')[a].text == 'Производственная практика' or first_p.find_all('td')[a].text == 'Учебная практика':#Опредиление кол-ва практик и расчёт коэфициента
                        pos_cut += 1
                except:
                    print('skip')
            tr = 1
            x = 0
    return date, l


# Создание файлов для записи туда текст дз
def file_maker():
    if not os.path.isdir(os.getcwd() + '\\' + 'Homework'): #Если папки нет, то она создаётся
        os.mkdir('Homework')

    b = os.getcwd()
    a = os.getcwd().replace('\\','/') + '/' + 'Homework'
    os.chdir(a)
    
    try: 
        s = shelve.open('homework_list.dat','w')

    # Если файла нет
    except: 
        s = shelve.open('homework_list.dat')
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
        s.sync()

    s.close()
    os.chdir(b)

def one_hw(subject):
    file_maker()
    
    b = os.getcwd()
    a = os.getcwd().replace('\\','/') + '/' + 'Homework'
    os.chdir(a)
    
    s = shelve.open('homework_list.dat')
    d = s[subject][0]
    s.close()
    os.chdir(b)
    
    return d

# Запись дз в файл
def homework_write(subject, home_text):
    file_maker()
    
    b = os.getcwd()
    a = os.getcwd().replace('\\','/') + '/' + 'Homework'
    os.chdir(a)
    
    s = shelve.open('homework_list.dat')

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
        return
    s.sync()
    s.close()
    os.chdir(b)


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
    c = lesson_compleater(lessons)[-1]
    print(c)
    a = []

    for _ in c:
        if _ in a or _ == '-':
            continue
        else:
            a.append(_)
    return a


# Форматирование и объединение даты и расписания под одной переменной
def text_converter(date = None, lesson = None):
    text_vk = ''
    i = 0

    if not lesson and not date:
        date, lesson = lessons()
        
    text_vk = text_vk + date + '\n'
    for _ in lesson:
        i += 1
        text_vk = text_vk + str(i)+')' + _ + '\n'

    return text_vk


# Подбор дз по расписанию   
def homework_compleater(lesson = None):      
    file_maker()

    b = os.getcwd()
    a = os.getcwd().replace('\\','/') + '/' + 'Homework'
    os.chdir(a)

    # Если расписание было получено с сайта
    if not lesson:
        date, lesson = lessons()
        
    s = shelve.open('homework_list.dat')
    homework_c = ''
    i = 1

    # Добавление и форматирование текста дз
    lessons_list= lesson_compleater(lesson)
    for subject in lessons_list:
        subject = subject.split()[0]
        print(subject)
        
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
    os.chdir(b)
    
    return homework_c


# Отображение всего дз из файла
def all_hw():
    file_maker()
    
    b = os.getcwd()
    a = os.getcwd().replace('\\','/') + '/' + 'Homework'
    os.chdir(a)
    
    s = shelve.open('homework_list.dat')
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
    os.chdir(b)

    return hw
