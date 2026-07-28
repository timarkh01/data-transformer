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
'''

from tkinter import *
from tkinter import ttk
import csv
import pandas as pd
import os
import json
from fileinput import close
import sqlite3 as sl


class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.master = master
        self.grid(sticky="nsew")

        self.create_widgets()

    def create_widgets(self):
        settings_frame = ttk.Frame(self)
        settings_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.gost_information(settings_frame)
        self.create_separator(self, 1, 'h')

    def gost_information(self, parent):
        text_fame = Frame(parent)
        text_fame.grid(row=0, column=0, sticky='nsew')

        self.gost_text = Label(text_fame, text='ad')
        self.gost_text.grid(row=0, column=0, columnspan=2)

    def create_separator(self, parent, column_row, way):
        if way == 'v':
            separator = ttk.Separator(parent, orient='vertical')
            separator.grid(row=0, column=column_row, rowspan=1, sticky="ns")
        else:
            separator = ttk.Separator(parent, orient='horizontal')
            separator.grid(row=column_row, column=0, sticky="ew")
            parent.grid_columnconfigure(0, weight=1)

    def start_name(self, parent):
        text_fame = Frame(parent)
        text_fame.grid(row=2, column=0, sticky='nsew')


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

def from_info_to_excel(name, new_info):
    fin_name = name + '.xlsx'                    #fin_name - финальное название
    if os.path.exists(fin_name):
        old_info = from_excel_to_info(name)
        new_info = new_info + old_info
    df = pd.DataFrame(new_info)
    df.to_excel(fin_name, index=False)

def from_excel_to_info(name):
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
info = from_txt_to_info(filename)
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

# root = Tk()
# root.geometry("1170x600")
# root.title('Трансформатор')
# app = Application(root)
# root.mainloop()