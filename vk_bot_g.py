from homework_lesson import text_converter, homework_compleater, all_hw, lessons, homework_write, lesson_compleater, status, les, one_hw
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from datetime import datetime
import vk_api, os, time, requests, threading, shelve

# Класс бот с набором основных методов
class Group_bot():

    # Иницализация основных параметров
    def __init__(self, vk_session, upload, longpoll):
        self.vk_session = vk_session
        self.upload = upload
        self.longpoll = longpoll
        self.users_list = {} # Действия пользователя и доступные флаги
        self.hw_start = True # Начальное меню
        self.hw_check = False # Просмотр домашки
        self.hw_chwrite = False # Изменение домашки
        self.hw_enter = False # Ввод текста
        self.pub_1 = False
        self.pub_2_a = False
        self.pub_2_d = False
        self.date = False
        self.choice = False
        self.id_g = -198339321 # id группы
        self.timer_1 = True # Состояние таймера
        self.hw = []
        self.t = None # Переменная таймера
        self.subj = None
        self.main_keyboard = '/app/Keyboards/Key_Admin_Menu_Positive.json' # Основная клавиатура

    # Основной цикл
    def loop(self):
        while True:
            #try:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        self.__check_usr(event)
            #except:
                #continue
                
    # ----------------------------------------------------------------------------------------------------------------------------
    # Ввыод расписания
    def __timetable(self, event):
        if status():
            self.msg(text_converter(), event.user_id)
        else:
            self.msg('Возникли проблемы с получением расписания, попробуйте позже.\nВыберете другой пункт меню.', event.user_id)
            
    # ----------------------------------------------------------------------------------------------------------------------------
    # Список домашнего задания
    # 1 часть
    def __hw_list(self, event):
        self.msg('Выберите один из предложенных пунктов.', event.user_id, open('/app/Keyboards/Key_HW_Choice.json', 'r', encoding='UTF-8').read())

    # 2 часть
    def __hw_list_today(self, event):
        if status():
            self.msg(homework_compleater(), event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
        else:
            self.msg('Возникли проблемы с получением расписания, из-за этого не получается получить информацию по дз на завтра.\nПопробуйте позже.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())

    # 3 часть
    def __hw_list_all(self, event):
        if status():
            self.msg(all_hw(), event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
        else:
            self.msg('Возникли проблемы с получением расписания, из-за этого не получается получить информацию по дз на завтра.\nПопробуйте позже.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())

    # ----------------------------------------------------------------------------------------------------------------------------
    # Изменение домашнего задания
    def __hw_change(self, event):
        self.msg('Часть 1', event.user_id, open('/app/Keyboards/Key_Subject_List_1.json', 'r', encoding='UTF-8').read())
        self.msg('Часть 2', event.user_id, open('/app/Keyboards/Key_Subject_List_2.json', 'r', encoding='UTF-8').read())
        self.msg('Часть 3', event.user_id, open('/app/Keyboards/Key_Subject_List_3.json', 'r', encoding='UTF-8').read())
        if self.pub_2_a == True:
            self.msg('Выберите нужный предмет.', event.user_id, open('/app/Keyboards/Key_Move_vr2.json', 'r', encoding='UTF-8').read())
        else:
            self.msg('Выберите нужный предмет.', event.user_id, open('/app/Keyboards/Key_Move.json', 'r', encoding='UTF-8').read())

    # Ввод дз
    def __hw_ent(self, event, previous):
        if event.attachments:
            photo = event.attachments
            self.__get_photo(event, event.attachments, photo, previous)

        if not (event.attachments and event.text == ''):
            homework_write(previous.capitalize(), event.text)
        self.__hw_change(event)

    # Скачивание фото
    def __get_photo(self, event, attach, photo, previous):
        if not os.path.isdir(os.getcwd() + '/Subject/' + previous):
            os.mkdir(os.getcwd() + '/Subject/' + previous)

        a = os.getcwd() + '/Subject/' + previous
        g = previous
        cd = os.listdir(a)
        
        self.msg('Загрузка началась подождите 2-3 минуты.', event.user_id, open('/app/Keyboards/Key_Empty.json', 'r', encoding='UTF-8').read())
        time.sleep(120)
        url_origin = self.vk_session.method('messages.getHistoryAttachments', {'peer_id': event.user_id, 'media_type': 'photo', 'count': 15, 'photo_sizes': 1})

        # Извелечение из 'atachments' ссылки на изображение
        for i in range(len(attach)//2):
            url = url_origin['items'][i]
            url = url['attachment']
            url = url['photo']
            url = url['sizes']                        
            size_list = []
            for _ in range(len(url)):
                size_list.append(url[_]['height'])
            pos = max(size_list)
            pos = size_list.index(pos)                
            url = url[pos]
            url = url['url']

            p = requests.get(url)

                # Подбор уникального имени файлу, дабы избежать прерзапись существующего файла
            v = i
            while True:
                previous = str(v) + '.jpg'
                if previous in cd:
                    v += 1
                else:
                    break

                # Скачивание фото
            w = open(os.getcwd() + '/Subject/' + g + '/' + previous, 'wb')
            w.write(p.content)
            w.close()

        self.msg('Загрузка почти закончилась.', event.user_id, open('/app/Keyboards/Key_Empty.json', 'r', encoding='UTF-8').read())
        self.msg('Загрузка прошла успешно', event.user_id, open('/app/Keyboards/Key_Move.json', 'r', encoding='UTF-8').read())
        
    # ----------------------------------------------------------------------------------------------------------------------------
    # Авторизация
    def __auth(self):
        self.vk = vk_api.VkApi(token = '389a203f6dbba52e2e0fe4f28d8a283c97169ba0fa138848abd23722ff628984ae0780613c9ed4260fa16')
        self.ses = self.vk.get_api()
        self.upload = VkUpload(self.vk)

    # Отправка текста
    def __post(self, message):
        post_id = self.vk.method('wall.post', {'message': message, 'owner_id' : self.id_g,'from_group' : 1})
        post_id = post_id['post_id']
        return post_id

    # Отправка фотографий
    def __photo_post(self, subject, event):
        for x in subject:
            if not os.path.isdir(os.getcwd() + '/Subject/' + x): #Если папки нет, то пропуск
                continue

            # Смена директории
            a = os.getcwd() + '/Subject/' + x            
            files = os.listdir(a)
            print(files)
            count = len(files)
            attachments = []

            # Цикл, публикующий по 2 фото в комментарии за раз ( ограничение вк )
            for _ in files:
                link = a + '/' + _
                upload_image = self.upload.photo_wall(photos = link, group_id = 198339321)[0]
                attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))

                if len(attachments) == 2 or _ == files[-1]:
                    self.vk.method('wall.createComment', {'owner_id': self.id_g,'post_id': self.post_id, 'attachments': ','.join(attachments)})
                    attachments = []

            for _ in files:
                os.remove(a + '/' + _)
        self.msg('Фотографиии были опубликованы, а после удалены.', event.user_id)
        

    # Отправка дз в группу (auto)
    def publish(self, event, auto = None):
        while True:            
            if status():
                if auto:
                    s = shelve.open(os.getcwd() +'/Homework/homework_list')
                    if not s['Дата'] == lessons()[0]:
                        self.t = threading.Timer(self.time_set(TIME_STEP), self.publish, args = (event, ))
                        self.t.start()
                        s.close()
                        self.msg('Расписание на сайте не обновилось, дз не выложено.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
                        continue
                    else:
                        self.t = threading.Timer(self.time_set(TIME, True), self.publish, args = (event, True, ))
                        self.t.start()
                    
                self.__auth()
                self.post_id = self.__post(text_converter() + homework_compleater())
                self.__photo_post(les(lessons()), event)
                
                s = shelve.open(os.getcwd() +'/Homework/homework_list')
                s['Дата'] = lessons()[0]
                s.sync()
                s.close()
                
                self.msg('Публикация дз закончена.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
                break
            
    # ----------------------------------------------------------------------------------------------------------------------------
    # Расписание
    def __hand(self):
        list_l = []
        for i in range(0, len(self.hw), 2):
            for _ in range(int(self.hw[i+1])):
                list_l.append(self.hw[i])
        self.hw = list_l

    # Публикация
    def publish_hand(self, event):
        self.__hand()
        self.__auth()
        
        if 'Обед' in self.hw:
            t = timeе[0:(len(self.hw))]
            t = t[0:self.hw.index('Обед')] + ('Обед',) + t[self.hw.index('Обед'):-1]
            self.hw.pop(self.hw.index('Обед'))

        self.post_id = self.__post(text_converter(self.d, self.hw, t) + homework_compleater(lesson_compleater(self.hw)))
        self.__photo_post(lesson_compleater(self.hw), event)
        self.t = threading.Timer(self.time_set(TIME, True), self.publish, args = (event, True, ))
        self.t.start()
        s = shelve.open(os.getcwd() +'/Homework/homework_list')
        s['Дата'] = self.d
        s.sync()
        s.close()
        
    # ----------------------------------------------------------------------------------------------------------------------------
    # Методы для работы с таймером
    # Установка времени
    def time_set(self, tt, skip = None):
        current_time = datetime.now().time()
        add_par = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second)

        if skip:
            value_timer = 86400 - add_par + tt
            return float(value_timer)
        
        # Сколько секунд осталось до нужного времени
        if add_par >= tt:
            value_timer = 86400 - add_par + tt        
        else:
            value_timer = tt - add_par
        return float(value_timer)

    # ----------------------------------------------------------------------------------------------------------------------------
    # Подгон настроек пользователя
    def setting_setup(self, user):
        print(self.users_list[user])
        self.hw_start = self.users_list[user][0][0]
        self.hw_check = self.users_list[user][0][1]
        self.hw_write = self.users_list[user][0][2]
        self.hw_enter = self.users_list[user][0][3]
        self.pub_1 = self.users_list[user][0][4]
        self.pub_2_a = self.users_list[user][0][5]
        self.pub_2_d = self.users_list[user][0][6]
        self.date = self.users_list[user][0][7]
        self.choice = self.users_list[user][0][8]
        self.timer_1 = self.users_list[user][0][9]

    # Выставление начальных настроек
    def default_setting(self):
        self.hw_start = True
        self.hw_check = False
        self.hw_chwrite = False
        self.hw_enter = False
        self.pub_1 = False
        self.pub_2_a = False
        self.pub_2_d = False
        self.date = False
        self.choice = False
        self.subj = None
        self.hw = []

    # ----------------------------------------------------------------------------------------------------------------------------
    # Отправка фото пользователю
    def photo_send(self, subject, event):
        a = os.getcwd() + '/Subject/' + subject        
        if os.path.isdir(a) and os.listdir(a): #Если папки нет, то пропуск
            file = os.listdir(a)
            attachments = []
            for _ in file:
                upload_image = upload.photo_messages(photos = a + '/' + _)[0]
                attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
            self.vk_session.method('messages.send', {'user_id': event.user_id, 'attachment': ','.join(attachments), 'random_id' : get_random_id()})
            
        
    # Регистрация пользователь, одновременно польлзующихся ботом
    def __check_usr(self, event):
        if not event.user_id in self.users_list:
            self.msg('Бот начал работу', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
            self.users_list[event.user_id] = [True, False, False, False, False, False, False, False, False, True], '', []
            self.t = threading.Timer(self.time_set(TIME), self.publish, args = (event, True, ))
            self.t.start()
        else:
            self.setting_setup(event.user_id)
            # Основной цикл работ с пользователями
            previous = self.users_list[event.user_id][-2]

            if event.text.capitalize() == 'Расписание' and self.hw_start == True:
                self.__timetable(event)
                self.default_setting()
                
            elif event.text.capitalize() == 'Домашнее задание' and self.hw_start == True:
                self.hw_start = False
                self.hw_check = True
                self.hw_chwrite = False
                self.hw_enter = False
                self.__hw_list(event)
                
            elif event.text.capitalize() == 'Дз на учебный день' and self.hw_check == True:
                self.__hw_list_today(event)
                self.default_setting()
                
            elif event.text.capitalize() == 'Полный список дз' and self.hw_check == True:
                self.__hw_list_all(event)
                self.default_setting()
                
            elif event.text.capitalize() == 'Изменение домашнего задания' and self.hw_start == True:
                self.hw_start = False
                self.hw_check = False
                self.hw_chwrite = True
                self.hw_enter = False
                self.__hw_change(event)
                
            elif (event.text.capitalize() in sub) and self.hw_chwrite == True:
                self.choice = True
                self.subj = event.text
                self.msg('Вот что было задано по этому предмету:\n\n' + one_hw(event.text.capitalize()), event.user_id, open('/app/Keyboards/Key_Empty.json', 'r', encoding='UTF-8').read())
                self.photo_send(event.text.capitalize(), event)
                self.msg('Вы хотите произвести изменения?', event.user_id, open('/app/Keyboards/Key_Choice.json', 'r', encoding='UTF-8').read())

            elif event.text.capitalize() == 'Да' and self.choice == True:
                self.hw_enter = True
                self.choice = False
                self.msg('Введите текст домашнего задания.', event.user_id, open('/app/Keyboards/Key_HW_Enter.json', 'r', encoding='UTF-8').read())

            elif event.text.capitalize() == 'Нет' and self.choice == True:
                self.choice = False
                self.__hw_change(event)
                 
            elif event.text.capitalize() == 'Назад' and self.hw_start == False:
                self.default_setting()
                self.msg('Вы вышли из меню редактирования домашнего задания.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())

            elif event.text.capitalize() == 'Публикация' and self.hw_start == True:
                self.pub_1 = True
                self.hw_start = False
                self.msg('Выберите нужный пункт меню.', event.user_id, open('/app/Keyboards/Key_Pub_Choice.json', 'r', encoding='UTF-8').read())

            elif event.text.capitalize() == 'Автоматическая публикация' and self.pub_1 == True:
                self.publish(event)
                self.default_setting()

            elif event.text.capitalize() == 'Ручная публикация' and self.pub_1 == True:
                self.date = True
                self.pub_1 = False
                self.msg('Введите дату.', event.user_id, open('/app/Keyboards/Key_Empty.json', 'r', encoding='UTF-8').read())

            elif self.date == True:
                self.date = False
                self.pub_2_a = True
                self.d = event.text
                self.__hw_change(event)

            elif self.pub_2_a == True and event.text.capitalize() == 'Завершить' and self.hw:
                self.publish_hand(event)
                self.default_setting()
                self.msg('Публикация дз закончена.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())

            elif self.pub_2_a == True:
                self.hw.append(event.text)
                self.pub_2_a = False
                self.pub_2_d = True
                self.msg('Выберите количество уроков по этому предмету.', event.user_id, open('/app/Keyboards/Key_Count_Lessons.json', 'r', encoding='UTF-8').read())    

            elif self.pub_2_d == True:
                if event.text.isdigit():
                    self.hw.append(event.text)
                    self.pub_2_a = True
                    self.pub_2_d = False
                    self.__hw_change(event)
                else:
                    self.msg('Некоректное значение.', event.user_id, open('/app/Keyboards/Key_Count_Lessons.json', 'r', encoding='UTF-8').read())

            elif (self.subj in sub) and self.hw_enter == True:
                self.__hw_ent(event, self.subj)
                self.hw_enter = False
                self.subj = None

            elif event.text.capitalize() == 'Авто' and self.hw_start == True:
                if self.timer_1:
                    self.timer_1 = False
                    self.t.cancel()
                    self.main_keyboard = '/app/Keyboards/Key_Admin_Menu.json'
                    self.msg('Таймер был выключен.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
                else:
                    self.timer_1 = True
                    self.t = threading.Timer(self.time_set(TIME), self.publish, args = (event, True, ))
                    self.t.start()
                    self.main_keyboard = '/app/Keyboards/Key_Admin_Menu_Positive.json'
                    self.msg('Таймер был включен.', event.user_id, open(self.main_keyboard, 'r', encoding='UTF-8').read())
                                
            else:
                self.msg('Была введена неизвестная команда.', event.user_id)

        
        self.users_list[event.user_id] = [self.hw_start, self.hw_check, self.hw_chwrite, self.hw_enter, self.pub_1, self.pub_2_a, self.pub_2_d, self.date, self.choice, self.timer_1], event.text, [self.hw]
        print(self.users_list)
        
    # Метод отправки сообщений
    def msg(self, text, user_id, keyboard = None):
        self.vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id' : get_random_id(), 'keyboard':  keyboard, 'random_id': get_random_id()})


def bot_auth():
    pass

TIME = 61320 # Таймер на 15:00
TIME_STEP = 1800 # Шаг таймера 30 минут
sub = ('Русский язык', 'Литература', 'Немецкий язык', 'Английский язык',
       'История', 'Физическая культура', 'Обж', 'Астрономия',
       'Химия', 'Математика', 'Информатика', 'Физика', 'Обществознание')

timeе = ('08:00-08:45', '08:50-09:35', '09:45-10:30', '10:35-11:20', '11:40-12:25', '12:30-13:15', '13:20-14:05', '14:10-14:55')

session = vk_api.VkApi(token='178314e04810da6851aad5ce17cca518835d5f1f5b330ef42fa0f7179a44f8a4c2d5d224fd95777b0ae1e')
longpoll = VkLongPoll(session)
upload = VkUpload(session)

bot = Group_bot(session, upload, longpoll)
bot.loop()
