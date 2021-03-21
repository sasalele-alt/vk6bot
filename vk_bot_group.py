from homework_lesson import text_converter, homework_compleater, all_hw, lessons, homework_write, lesson_compleater, status, les, one_hw
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
import vk_api, os, time, requests

# Класс бот с набором основных методов
class Group_bot():

    # Иницализация основных параметров
    def __init__(self, vk_session, upload, longpoll):
        self.vk_session = vk_session
        self.upload = upload
        self.longpoll = longpoll
        self.users_list = {}
        self.hw_start = True # Начальное меню
        self.hw_check = False # Просмотр домашки
        self.hw_chwrite = False # Изменение домашки
        self.hw_enter = False # Ввод текста
        self.pub_1 = False
        self.pub_2_a = False
        self.pub_2_d = False
        self.date = False
        self.choice = False
        self.id_g = -199643651
        self.hw = []

    # Основной цикл
    def loop(self):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.__check_usr(event)
                
    # ----------------------------------------------------------------------------------------------------------------------------
    # Ввыод расписания
    def __timetable(self, event):
        if status():
            self.msg(text_converter(), event.user_id)
        else:
            self.msg('Возникли проблемы с получением расписания, попробуйте позже.\nВыберете другой пункт меню.', 133867067)
            
    # ----------------------------------------------------------------------------------------------------------------------------
    # Список домашнего задания
    # 1 часть
    def __hw_list(self, event):
        self.msg('Выберите один из предложенных пунктов.', event.user_id, open('/app/Keyboards/Key_HW_Choice.json', 'r', encoding='UTF-8').read())

    # 2 часть
    def __hw_list_today(self, event):
        if status():
            self.msg(homework_compleater(), event.user_id, open('/app/Keyboards/Key_Admin_Menu.json', 'r', encoding='UTF-8').read())
        else:
            self.msg('Возникли проблемы с получением расписания, из-за этого не получается получить информацию по дз на завтра.\nПопробуйте позже.', event.user_id, open(os.getcwd() + 'Keyboards\Key_Admin_Menu.json', 'r', encoding='UTF-8').read())

    # 3 часть
    def __hw_list_all(self, event):
        if status():
            self.msg(all_hw(), event.user_id, open('/app/Keyboards/Key_Admin_Menu.json', 'r', encoding='UTF-8').read())
        else:
            self.msg('Возникли проблемы с получением расписания, из-за этого не получается получить информацию по дз на завтра.\nПопробуйте позже.', event.user_id, open(os.getcwd() + 'Keyboards\Key_Admin_Menu.json', 'r', encoding='UTF-8').read())

    # ----------------------------------------------------------------------------------------------------------------------------
    # Изменение домашнего задания
    def __hw_change(self, event):
        self.msg('Часть 1', event.user_id, open('/app/Keyboards/Key_Subject_List_1.json', 'r', encoding='UTF-8').read())
        self.msg('Часть 2', event.user_id, open('/app/Keyboards/Key_Subject_List_2.json', 'r', encoding='UTF-8').read())
        self.msg('Часть 3', event.user_id, open('/app/Keyboards/Key_Subject_List_3.json', 'r', encoding='UTF-8').read())
        if self.pub_2_a == True:
            self.msg('Выберите нужный предмет.', event.user_id, open('/app/Keyboards/Key_Move_vr2.json', 'r', encoding='UTF-8').read())
        else:
            self.msg('Выберите нужный предмет.', event.user_id, open('/app/Keyboards/ey_Move.json', 'r', encoding='UTF-8').read())

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
        print(attach)
        b = os.getcwd()
        if not os.path.isdir(os.getcwd() + '\\Subject\\' + previous):
            a = os.getcwd().replace('\\','/') + '/Subject/'
            os.chdir(a)
            os.mkdir(previous)
            os.chdir(b)

        a = os.getcwd().replace('\\','/') + '/Subject/' + previous
        cd = os.listdir(a)

        for _ in cd:
            os.remove(a + '/' + _)
        cd = []

        os.chdir(a)
        self.msg('Загрузка началась подождите 2-3 минуты.', event.user_id)
        time.sleep(120)

        #try:
        url_origin = self.vk_session.method('messages.getHistoryAttachments', {'peer_id': event.user_id, 'media_type': 'photo', 'count': 15, 'photo_sizes': 1})

        # Извелечение из 'atachments' ссылки на изображение
        for i in range(len(attach)//2):
            print(url_origin['items'])
            url = url_origin['items'][i]
            print(url)
            print('\n')
            url = url['attachment']
            print(url)
            print('\n')
            url = url['photo']
            print(url)
            print('\n')
            url = url['sizes']
            
            
            size_list = []
            for _ in range(len(url)):
                size_list.append(url[_]['height'])
            pos = max(size_list)
            pos = size_list.index(pos)
                
            url = url[pos]
            print(url)
            print('\n')
            url = url['url']
            print(url)
            print('\n')

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
            w = open(previous, 'wb')
            w.write(p.content)
            w.close()

        os.chdir(b)
        self.msg('Загрузка почти закончилась.', event.user_id, open('/app/Keyboards/Key_Move.json', 'r', encoding='UTF-8').read())
        #except:
            #self.msg('Произошла ошибка. Фото не сохранилось.', event.user_id, open('Keyboards\Key_Move.json', 'r', encoding='UTF-8').read())
        #finally:
        self.msg('Загрузка прошла успешно', event.user_id, open('/app/Keyboards/Key_Move.json', 'r', encoding='UTF-8').read())
        
    # ----------------------------------------------------------------------------------------------------------------------------
    # Авторизация
    def __auth(self):
        toka = os.environ.get('BOT_TOKEN_USER')
        self.vk = vk_api.VkApi(token = toka)
        self.ses = self.vk.get_api()
        self.upload = VkUpload(self.vk)

    # Отправка текста
    def __post(self, message):
        post_id = self.vk.method('wall.post', {'message': message, 'owner_id' : self.id_g,'from_group' : 1})
        post_id = post_id['post_id']
        return post_id

    # Отправка фотографий
    def __photo_post(self, subject):
        try:
            for x in subject:
                if not os.path.isdir(os.getcwd() + '\\Subject\\' + x): #Если папки нет, то пропуск
                    continue

                # Смена директории
                b = os.getcwd()
                print(b)
                a = os.getcwd() + '/Subject/' + x
                os.chdir(a)
            
                files = os.listdir(a)
                print(files)
                count = len(files)
                attachments = []

                # Цикл, публикующий по 2 фото в комментарии за раз ( ограничение вк )
                for _ in files:
                    link = a + '/' + _
                    upload_image = self.upload.photo_wall(photos = link, group_id = 199643651)[0]
                    attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))

                    if len(attachments) == 2 or _ == files[-1]:
                        self.vk.method('wall.createComment', {'owner_id': self.id_g,'post_id': self.post_id, 'attachments': ','.join(attachments)})
                        attachments = []
                os.chdir(b)
        except:
            os.chdir(b)

    # Отправка дз в группу (auto)
    def publish(self, event):
        if status():
            self.__auth()
            self.post_id = self.__post(text_converter() + homework_compleater())
            self.__photo_post(les(lessons()))
            self.msg('Публикация дз закончена.', event.user_id, open('/app/Keyboards/Key_Admin_Menu.json', 'r', encoding='UTF-8').read())
            
    # ----------------------------------------------------------------------------------------------------------------------------
    # Расписание
    def __hand(self):
        list_l = []
        print(self.hw)
        for i in range(0, len(self.hw), 2):
            for _ in range(int(self.hw[i+1])):
                list_l.append(self.hw[i])
        print(list_l)
        self.hw = list_l

    # Публикация
    def publish_hand(self, event):
        self.__hand()
        self.__auth()
        self.post_id = self.__post(text_converter(self.d, self.hw) + homework_compleater(lesson_compleater(self.hw)))
        self.__photo_post(lesson_compleater(self.hw))
        
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
        a = os.getcwd() + '\\Subject\\' + subject
        
        if os.path.isdir(a) and os.listdir(a): #Если папки нет, то пропуск
            file = os.listdir(a)
            attachments = []
            for _ in file:
                upload_image = upload.photo_messages(photos = a + '\\' + _)[0]
                attachments.append('photo{}_{}'.format(upload_image['owner_id'], upload_image['id']))
            self.vk_session.method('messages.send', {'user_id': event.user_id, 'attachment': ','.join(attachments), 'random_id' : get_random_id()})
            
        
    # Регистрация пользователь, одновременно польлзующихся ботом
    def __check_usr(self, event):
        if not event.user_id in self.users_list:
            self.msg('Бот начал работу', event.user_id, open('/app/Keyboards/Key_Admin_Menu.json', 'r', encoding='UTF-8').read())
            self.users_list[event.user_id] = [True, False, False, False, False, False, False, False, False], '', []
        else:
            self.setting_setup(event.user_id)
            # Основной цикл работ с пользователями
            previous = self.users_list[event.user_id][-2]

            if event.text.capitalize() == 'Расписание' and self.hw_start == True:
                print('1')
                header = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36', 
'upgrade-insecure-requests': '1', 
'cookie': 'mos_id=CllGxlx+PS20pAxcIuDnAgA=; session-cookie=158b36ec3ea4f5484054ad1fd21407333c874ef0fa4f0c8e34387efd5464a1e9500e2277b0367d71a273e5b46fa0869a; NSC_WBS-QUBG-jo-nptsv-WT-443=ffffffff0951e23245525d5f4f58455e445a4a423660; rheftjdd=rheftjddVal; _ym_uid=1552395093355938562; _ym_d=1552395093; _ym_isad=2' 
}
                p = requests.get('http://p11505.edu35.ru/gmraspisanie/izmeneniya', timeout = 5, headers = header, proxies = {'http': '212.68.227.166'})
                if p.status_code == '200':
                    print('success')
                        
                print(p.status_code)
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
                self.msg('Вы вышли из меню редактирования домашнего задания.', event.user_id, open('/app/Keyboards/Key_Admin_Menu.json', 'r', encoding='UTF-8').read())

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
                self.msg('Публикация дз закончена.', event.user_id, open('/app/Keyboards/Key_Admin_Menu.json', 'r', encoding='UTF-8').read())

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
                                
            else:
                self.msg('Была введена неизвестная команда.', event.user_id)

        
        self.users_list[event.user_id] = [self.hw_start, self.hw_check, self.hw_chwrite, self.hw_enter, self.pub_1, self.pub_2_a, self.pub_2_d, self.date, self.choice], event.text, [self.hw]
        print(self.users_list)
        
    # Метод отправки сообщений
    def msg(self, text, user_id, keyboard = None):
        self.vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id' : get_random_id(), 'keyboard':  keyboard, 'random_id': get_random_id()})


def bot_auth():
    pass

sub = ('Русский язык', 'Литература', 'Иностранный язык',
       'История', 'Физическая культура', 'Обж', 'Астрономия',
       'Химия', 'Математика', 'Информатика', 'Физика', 'Обществознание')

tok = os.environ.get('BOT_TOKEN_GROUP')
session = vk_api.VkApi(token=tok)
longpoll = VkLongPoll(session)
upload = VkUpload(session)

bot = Group_bot(session, upload, longpoll)
bot.loop()
