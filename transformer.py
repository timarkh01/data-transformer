'''txt, csv (для excel лучше DictReader и DictWriter), json, excel, sql
имя, адрес, телефон, дата рождения
основной формат: [{name: ...; address: ...; ...}, ...]
можно добавить: логи, дату создания
нужно сделать: независимость от кол-ва колонок, названия и т.д.
пока что начальный файл с данными будет в txt
{
name: Timofey
address: abc str.
phone_number: +7123
date_of_birth: 12.12.2012
}

sql через опрос: название1,название2,...; тип1,тип2,...
выбор: дописать существующий, создать новый (если файл с таким названием существует, то он будет перезаписан)
sql смотреть через DB Browser
проверка на одинаковые колонки везде
куда сохранять файл
'''

from tkinter import *
from tkinter import ttk
import csv
import pandas as pd
import os
import json
from fileinput import close
import sqlite3 as sl

FILE_TYPES = ["txt", "csv", "json", "xlsx", "sql"]

class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.master = master
        self.grid(sticky="nsew")

        # настроить grid для master и self

        self.locate_file_get = ''
        self.type_of_file_get = ''
        self.info_get = []
        
        self.new_name_file = ''
        self.locate_file_save = ''
        self.type_of_file_save = ''
        self.type_mode_save = ''

        self.output_text = ''

        self.create_widgets()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        settings_frame = ttk.Frame(self)
        settings_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.create_separator(settings_frame, 'h', 0, 0, 5)
        self.create_separator(settings_frame, 'v', 0, 0, 5)
        self.gost_information(settings_frame)
        self.create_separator(settings_frame, 'h', 1, 2, 3)
        self.get_data(settings_frame)
        self.create_separator(settings_frame, 'h', 1, 4, 2)
        self.save_data(settings_frame)
        self.create_separator(settings_frame, 'h', 1, 6, 3)
        self.create_separator(settings_frame, 'v', 2, 3, 4) #col, row, sp
        self.output(settings_frame)
        self.create_separator(settings_frame, 'v', 5, 1, 5)

    def output(self, parent):
        output_frame = Frame(parent)
        output_frame.grid(row=3, column=3, sticky='nsew')

        self.output_str = Label(output_frame, text='Вывод:') 
        self.output_str.grid(row=0, column=0)

        self.output_window = Label(output_frame, text=self.output_text, width=30)
        self.output_window.grid(row=1, column=0, rowspan=3)

    def gost_information(self, parent):
        text_fame = Frame(parent)
        text_fame.grid(row=1, column=1, columnspan=5, sticky='nsew')

        self.gost_text = Label(text_fame, text='путь к файлу с ковычками, txt ...,' \
        ' .... При нажатии туда сюда .... При ошибке будет ...')
        self.gost_text.grid(row=0, column=0, pady=10)

    def save_data(self, parent):
        save_frame = Frame(parent)
        save_frame.grid(row=5, column=1, sticky='nsew')

        self.n_name = Label(save_frame, text='Имя нового файла:')
        self.n_name.grid(row=0, column=0, sticky='w', pady=5)
        
        self.entry_n_name = Entry(save_frame, width=20)
        self.entry_n_name.grid(row=0, column=1, sticky='w')

        self.locate_save = Label(save_frame, text='Куда сохранять файл:')
        self.locate_save.grid(row=1, column=0, sticky='w', pady=5)
        
        self.entry_locate_save = Entry(save_frame, width=20)
        self.entry_locate_save.grid(row=1, column=1, sticky='w')

        self.type_save = Label(save_frame, text='Тип файла')
        self.type_save.grid(row=2, column=0, sticky='w', pady=5)

        self.combo_type_of_file_save = ttk.Combobox(
        save_frame, values=FILE_TYPES, state='readonly', width=17)
        self.combo_type_of_file_save.grid(row=2, column=1, sticky='w')
        self.combo_type_of_file_save.current(0)

        self.save_mode_var = StringVar(save_frame, value='append')

        self.save_mode_label = Label(save_frame, text='Режим записи')
        self.save_mode_label.grid(row=3, column=0, sticky='w')

        mode_frame = Frame(save_frame)
        mode_frame.grid(row=3, column=1, sticky='w')

        self.radio_append = Radiobutton(mode_frame, text='Дописать',
                                        variable=self.save_mode_var, value='append')
        self.radio_append.grid(row=0, column=0, sticky='w')

        self.radio_append = Radiobutton(mode_frame, text='Создать новый',
                                                variable=self.save_mode_var, value='new')
        self.radio_append.grid(row=0, column=1, sticky='w')
        
        self.get_data_btn = Button(save_frame, text='Конвертировать данные', command=self.command_save_data_btn) #дописать 
        self.get_data_btn.grid(row=4, column=1, columnspan=2, sticky='w', pady=10)

    def command_save_data_btn(self):
        self.new_name_file = self.entry_n_name.get()
        self.locate_file_save = self.entry_locate_save.get()[1:-1]
        self.type_of_file_save = self.combo_type_of_file_save.get()
        self.type_mode_save = self.save_mode_var.get()

        if os.path.exists(self.locate_file_save):
            fullname = self.locate_file_save + '\\' + self.new_name_file
            if self.type_mode_save == 'new' and os.path.exists(fullname):
                os.remove(self.locate_file_save + self.new_name_file)
            from_info_to_smth(fullname, self.info_get, self.type_of_file_save)
            self.output_text = 'Данные конвертированы'
        else:
            self.output_text = errors('get')

        self.create_widgets()

    def get_data(self, parent):
        get_frame = Frame(parent)
        get_frame.grid(row=3, column=1, sticky='nsew')

        self.locate = Label(get_frame, text='Расположение файла:')
        self.locate.grid(row=0, column=0, pady=5)

        self.entry_locate = Entry(get_frame, width=20)
        self.entry_locate.grid(row=0, column=1, pady=5, sticky='w')

        self.type_of_file = Label(get_frame, text='Выберите тип файла') 
        self.type_of_file.grid(row=1, column=0, sticky='w', pady=5)

        self.combo_type_of_file_get = ttk.Combobox(
        get_frame, values=FILE_TYPES, state='readonly', width=17)
        self.combo_type_of_file_get.grid(row=1, column=1)
        self.combo_type_of_file_get.current(0)

        self.get_data_btn = Button(get_frame, text='Загрузить данные', 
                                   command=self.command_get_data_btn) #дописать 
        self.get_data_btn.grid(row=2, column=1, columnspan=2, sticky='w', pady=10)

    def command_get_data_btn(self):
        self.locate_file_get = self.entry_locate.get()[1:-1]
        self.type_of_file_get = self.combo_type_of_file_get.get()

        if not check_exist_file(self.locate_file_get, self.type_of_file_get):
            self.output_text = errors('save')
            self.info_get = []
        else:
            name_for_func = self.locate_file_get.split('.')[0]
            self.info_get = from_smth_to_info(name_for_func, self.type_of_file_get)
            self.output_text = 'Данные загружены'

        self.create_widgets()

    def create_separator(self, parent, way, column_ = 0, row_ = 0, span = 1):
        if way == 'v':
            separator = ttk.Separator(parent, orient='vertical')
            separator.grid(row=row_, column=column_, rowspan=span, sticky="ns")
        else:
            separator = ttk.Separator(parent, orient='horizontal')
            separator.grid(row=row_, column=column_, columnspan=span, sticky="ew")
            parent.grid_columnconfigure(0, weight=1)


def errors(name_error):
    error = ''
    match name_error:
        case 'save':
            error = 'save'
        case 'get':
            error = 'get'
    return error

def check_exist_file(filename, type_of_file_user):
    type_of_file_prog = filename.split('.')[-1]
    if type_of_file_prog == type_of_file_user:
        return True
    return False

def from_info_to_smth(filename, info, type_of_file):
    match type_of_file:
        case 'txt':
            from_info_to_txt(filename, info)
        case 'csv':
            from_info_to_csv(filename, info)
        case 'json':
            from_info_to_json(filename, info)
        case 'xlsx':
            from_info_to_xlsx(filename, info)
        case 'sql':
            from_info_to_sql(filename, info)

def from_smth_to_info(filename, type_of_file):
    cur_info = []
    match type_of_file:
        case 'txt':
            cur_info = from_txt_to_info(filename)
        case 'csv':
            cur_info = from_csv_to_info(filename)
        case 'json':
            cur_info = from_json_to_info(filename) 
        case 'xlsx':
            cur_info = from_xlsx_to_info(filename)
        case 'sql':
            cur_info = from_sql_to_info(filename)
    return cur_info

#region txt

def from_info_to_txt(name, info):
    name = name + '.txt'
    with open(name, 'a', encoding='utf-8') as txt_file:
        for line in info:
            txt_file.write('{\n')
            for key, value in line.items():
                txt_file.write('  ' + key + ': ' + value + '\n')
            txt_file.write('}\n\n')
    close()

def from_txt_to_info(name):
    info = []
    name = name + '.txt'
    with open(name, 'r', encoding='utf-8') as txt_file:
        lines = txt_file.readlines()
        one_info = {}
        for line in lines:
            line = line.strip()
            if '{' not in line and '}' not in line and '' != line:
                info_line = line.split(': ')
                one_info[info_line[0]] = info_line[1]
            elif '}' in line:
                info.append(one_info)
                one_info = {}
    close()
    return info

#endregion

#region csv

def from_info_to_csv(name, info):
    new_name = name + '.csv'
    if os.path.exists(new_name):
        data = []
        for line in info:
            info_line = list(line.values())
            data.append(info_line)

        with open(new_name, 'a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(data)

    else:
        with open(new_name, 'w', encoding='utf-8', newline='') as csv_file:
            fieldnames = info[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(info)
    close()

def from_csv_to_info(name):
    info = []
    name = name + '.csv'
    with open(name, 'r', encoding='utf-8', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            info.append(line)
    close()
    return info

#endregion

#region json

def from_info_to_json(name, new_info):
    fin_name = name + '.json'
    if os.path.exists(fin_name):
        old_info = from_json_to_info(name)
        new_info = old_info + new_info
    with open(fin_name, 'w', encoding='utf-8') as json_file:
        json.dump(new_info, json_file, ensure_ascii=False, indent=2)
    close()

def from_json_to_info(name):
    info = []
    name = name + '.json'
    with open(name, 'r', encoding='utf-8') as json_file:
        json_reader = json.load(json_file)
        for line in json_reader:
            info.append(line)
    close()
    return info

#endregion

#region excel

def from_info_to_xlsx(name, new_info):
    fin_name = name + '.xlsx'                    #fin_name - финальное название
    if os.path.exists(fin_name):
        old_info = from_xlsx_to_info(name)
        new_info = new_info + old_info
    df = pd.DataFrame(new_info)
    df.to_excel(fin_name, index=False)

def from_xlsx_to_info(name):
    info = []
    name = name + '.xlsx'
    df = pd.read_excel(name)
    res = df.to_dict(orient='split')
    for values in res['data']:                # преобразовывал под "ГОСТ" инфы
        info_line = {}
        for i, key in enumerate(res['columns']):
            info_line[key] = values[i]
        info.append(info_line)
    return info

#endregion

#region sql

def from_info_to_sql(name, info):
    new_name = name + '.sql'
    name_table = name.capitalize()
    con = sl.connect(new_name)
    cursor = con.cursor()

    fieldnames = info[0].keys()
    table_command = f'''CREATE TABLE IF NOT EXISTS {name_table} (
id INTEGER PRIMARY KEY,
'''
    key_tuple_str = '' # т.к. в команде ключи должны быть без кавычек, то нужно создать свою строку
    question_str = ''
    for key in fieldnames:
        key_tuple_str += f'{key}, '
        question_str += f'?, '
        table_command += f'{key} TEXT,\n'
    table_command = table_command[:-2]
    key_tuple_str = key_tuple_str[:-2] # убираю пробел и запятую в конце
    question_str = question_str[:-2]
    table_command += ''')'''

    cursor.execute(table_command)

    info_command = f'INSERT INTO {name_table} ({key_tuple_str}) VALUES ({question_str})'
    for info_line in info:
        info_tuple = tuple(info_line.values())
        cursor.execute(info_command, info_tuple)

    con.commit()
    con.close()

def from_sql_to_info(name):
    info = []
    new_name = name + '.sql'
    name_table = name.capitalize()
    con = sl.connect(new_name)
    cursor = con.cursor()

    cursor.execute(f'SELECT * FROM {name_table}')
    res = cursor.fetchall()
    headers = [description[0] for description in cursor.description][1:] # убрал id

    for value in res:
        info_line = {}
        list_value = list(value)[1:] # убрал id
        for i, key in enumerate(headers):
            info_line[key] = list_value[i]
        info.append(info_line)

    con.commit()
    con.close()

    return info



#endregion

filename = 'info'
# info = [{'name':'ab'}]
# info = from_txt_to_info(filename)
# from_info_to_txt(filename, info)
# from_info_to_csv(filename, info)
# info = from_csv_to_info(filename)
# info = from_json_to_info(filename)
# from_info_to_json(filename, info)
# from_info_to_excel(filename, info)
# from_info_to_sql(filename, info)
# info = from_excel_to_info(filename)
# info = from_sql_to_info(filename)
# print(info)

root = Tk()
root.geometry("560x350")
root.title('Трансформер')
app = Application(root)
root.mainloop() 