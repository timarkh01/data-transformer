from tkinter import *
from tkinter import ttk
import csv
import pandas as pd
import os
import json
from fileinput import close
import sqlite3 as sl
import webbrowser

FILE_TYPES = ["txt", "csv", "json", "xlsx", "sql"]
GITHUB_URL = "https://github.com/timarkh01/data-transformer/tree/main"

class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.master = master
        self.grid(sticky="nsew")


        self.locate_file_get = ''
        self.type_of_file_get = ''
        self.info_get = []
        
        self.new_name_file = ''
        self.locate_file_save = ''
        self.type_of_file_save = ''
        self.type_mode_save = ''

        self.output_text = ''

        self.create_widgets()

    # Создание всех виджетов
    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        settings_frame = ttk.Frame(self)
        settings_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.create_separator(settings_frame, 'h', 0, 0, 5)
        self.create_separator(settings_frame, 'v', 0, 0, 7)
        self.gost_information(settings_frame)
        self.create_separator(settings_frame, 'h', 1, 2, 3)
        self.get_data(settings_frame)
        self.create_separator(settings_frame, 'h', 1, 4, 2)
        self.save_data(settings_frame)
        self.create_separator(settings_frame, 'h', 1, 6, 3)
        self.create_separator(settings_frame, 'v', 2, 3, 4) #col, row, sp
        self.output(settings_frame)
        self.create_separator(settings_frame, 'v', 5, 1, 5)

    # Виджет для вывода ошибок/успешного завершения работы
    def output(self, parent):
        output_frame = Frame(parent)
        output_frame.grid(row=3, column=3, sticky='nsew')

        self.output_str = Label(output_frame, text='Вывод:') 
        self.output_str.grid(row=0, column=0)

        self.output_window = Label(output_frame, text=self.output_text, width=30)
        self.output_window.grid(row=1, column=0, rowspan=3)

    # Виджет с информацией для пользователя
    def gost_information(self, parent):
        text_fame = Frame(parent)
        text_fame.grid(row=1, column=1, columnspan=5, sticky='w')

        info_text = (
            "Трансформер - это конвертация данных между TXT, CSV, JSON, Excel и SQL.\n"
            "Укажите путь к файлу и его тип, чтобы загрузить данные, "
            "затем имя и папку для сохранения в нужном формате.\n"
            "Для более подробной информации насчет оформления данных можете"
            "перейти по сслыке:"
        )

        self.gost_info = Label(text_fame, text=info_text, wraplength=550, justify='left')
        self.gost_info.grid(row=0, column=0, sticky='w')

        self.gost_link = Label(
                               text_fame, text="https://github.com/timarkh01/data-transformer/tree/main",
                               fg="blue", cursor="hand2"
                               )
        self.gost_link.grid(row=1, column=0, sticky='w')
        self.gost_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

    # Виджет с сохранением данных
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
        
        self.get_data_btn = Button(save_frame, text='Конвертировать данные', command=self.command_save_data_btn) 
        self.get_data_btn.grid(row=4, column=1, columnspan=2, sticky='w', pady=10)

    # Описание работы при нажатии на кнопку "Конвертировать данные"
    def command_save_data_btn(self):
        self.new_name_file = self.entry_n_name.get().strip()
        raw_dir = self.entry_locate_save.get().strip()

        # Если путь к папке скопирован с ковычками, то удаляем их
        if len(raw_dir) >= 2 and raw_dir[0] == raw_dir[-1] and raw_dir[0] in ('"', "'"):
            raw_dir = raw_dir[1:-1]
        self.locate_file_save = raw_dir

        self.type_of_file_save = self.combo_type_of_file_save.get()
        self.type_mode_save = self.save_mode_var.get()

        if not os.path.exists(self.locate_file_save):
            self.output_text = errors('save_dir_not_found')
            self.create_widgets()
            return

        fullname = os.path.join(self.locate_file_save, self.new_name_file)
        full_path_with_ext = fullname + '.' + self.type_of_file_save

        try:
            if self.type_mode_save == 'new' and os.path.exists(full_path_with_ext):
                os.remove(full_path_with_ext)
            from_info_to_smth(fullname, self.info_get, self.type_of_file_save)
            self.output_text = 'Данные конвертированы'
        except Exception:
            self.output_text = errors('save_failed')

        self.create_widgets()

    # Виджет с полученнием данных
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

        self.get_data_btn = Button(get_frame, text='Загрузить данные', command=self.command_get_data_btn)
        self.get_data_btn.grid(row=2, column=1, columnspan=2, sticky='w', pady=10)

    # Описание работы при нажатии на кнопку "Загрузить данные"
    def command_get_data_btn(self):
        raw_path = self.entry_locate.get().strip()
        if len(raw_path) >= 2 and raw_path[0] == raw_path[-1] and raw_path[0] in ('"', "'"):
            raw_path = raw_path[1:-1]
        self.locate_file_get = raw_path
        self.type_of_file_get = self.combo_type_of_file_get.get()

        is_valid, error_key = check_exist_file(self.locate_file_get, self.type_of_file_get)
        if not is_valid:
            self.output_text = errors(error_key)
            self.info_get = []
        else:
            name_for_func, _ = os.path.splitext(self.locate_file_get)
            try:
                self.info_get = from_smth_to_info(name_for_func, self.type_of_file_get)
                self.output_text = 'Данные загружены'
            except Exception:
                self.info_get = []
                self.output_text = errors('get_failed')

        self.create_widgets()

    # Создание разделителей на экране интерфейса
    def create_separator(self, parent, way, column_ = 0, row_ = 0, span = 1):
        if way == 'v':
            separator = ttk.Separator(parent, orient='vertical')
            separator.grid(row=row_, column=column_, rowspan=span, sticky="ns")
        else:
            separator = ttk.Separator(parent, orient='horizontal')
            separator.grid(row=row_, column=column_, columnspan=span, sticky="ew")
            parent.grid_columnconfigure(0, weight=1)


# Описание ошибок
def errors(name_error):
    match name_error:
        case 'get_extension':
            return 'Расширение файла не совпадает с выбранным типом'
        case 'get_not_found':
            return 'Файл не найден по указанному пути'
        case 'get_failed':
            return 'Не удалось прочитать файл, проверьте формат данных'
        case 'save_dir_not_found':
            return 'Указанная папка для сохранения не найдена'
        case 'save_failed':
            return 'Не удалось сохранить файл'
        case _:
            return 'Неизвестная ошибка'

# Проверка на существование файла
def check_exist_file(filename, type_of_file_user):
    if not os.path.exists(filename):
        return False, 'get_not_found'
    type_of_file_prog = filename.split('.')[-1]
    if type_of_file_prog != type_of_file_user:
        return False, 'get_extension'
    return True, None


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
    fin_name = name + '.xlsx'                   
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
    for values in res['data']:                # Преобразовывал под "ГОСТ" инфы
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
    key_tuple_str = '' # Т.к. в команде ключи должны быть без кавычек, то нужно создать свою строку
    question_str = ''
    for key in fieldnames:
        key_tuple_str += f'{key}, '
        question_str += f'?, '
        table_command += f'{key} TEXT,\n'
    table_command = table_command[:-2]
    key_tuple_str = key_tuple_str[:-2] # Убираю пробел и запятую в конце
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
        list_value = list(value)[1:] # Убрал id
        for i, key in enumerate(headers):
            info_line[key] = list_value[i]
        info.append(info_line)

    con.commit()
    con.close()

    return info



#endregion

#filename = 'info'
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

if __name__ == "__main__":
    root = Tk()
    root.geometry("560x400")
    root.title('Трансформер')
    app = Application(root)
    root.mainloop()