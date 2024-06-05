from bs4 import BeautifulSoup
import requests
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

LINKS_TO_INFO_ABOUT_THE_VALUE_OF_ASSETS = {
    'ecd_names': [
        'https://ecd.rs/',
        'span',
        'name'
        ],
    'ecd_prices': [
        'https://ecd.rs/',
        'div',
        'price'
        ],
    'google_USDT_RUB': [
        'https://www.google.com/finance/quote/USDT-RUB?hl=sr',
        'div',
        'YMlKec fxKbKc'
    ]
}

COMMISSION_FOR_ADDING_MONEY_TO_WALLET = 0.01
COMMISSION_FOR_PURCHASE_OF_USDT = 0.02
COMMISSUON_FOR_TRANSFER_TO_ANOTHER_WALLET = 1  # USDT


def url_parser_to_list(url, tag, class_name):
    '''Выводит списов значений соответствующих тегам и классам указаного url'''
    response = requests.get(url)
    bs = BeautifulSoup(response.text, 'lxml')
    items = bs.find_all(tag, class_name)
    items_converted_to_text = [item.text for item in items]
    return items_converted_to_text


def url_parser_to_dict(url, tag, class_name):
    '''Выводит списов значений соответствующих тегам и классам указаного url'''
    response = requests.get(url)
    bs = BeautifulSoup(response.text, 'lxml')
    items = bs.find_all(tag, class_name)
    items_converted_to_text = [item.text for item in items]
    items_converted_to_float_rsd = []
    items_converted_to_float_eur = []
    for element in items_converted_to_text:
        new_elements = element.split()
        new_prices = float(new_elements[0].replace('.', '').replace(',', '.'))
        if new_elements[1] == 'RSD':
            items_converted_to_float_rsd.append(new_prices)
        else:
            items_converted_to_float_eur.append(new_prices)

    price_currency = dict(
        zip(
            url_parser_to_list(*LINKS_TO_INFO_ABOUT_THE_VALUE_OF_ASSETS[
                'ecd_names'
            ]),
            zip(items_converted_to_float_rsd, items_converted_to_float_eur)
        )
    )
    return price_currency


def url_parser_to_list_of_toupels(url, tag, class_name):
    '''
    Выводит коллекцию кортежей имени валюты, стоимости в rsd
    и eur соответствующих тегам и классам указаного url
    '''
    response = requests.get(url)
    bs = BeautifulSoup(response.text, 'lxml')
    items = bs.find_all(tag, class_name)
    items_converted_to_text = [item.text for item in items]
    items_converted_to_float_rsd = []
    items_converted_to_float_eur = []
    for element in items_converted_to_text:
        new_elements = element.split()
        new_prices = float(new_elements[0].replace('.', '').replace(',', '.'))
        if new_elements[1] == 'RSD':
            items_converted_to_float_rsd.append(new_prices)
        else:
            items_converted_to_float_eur.append(new_prices)

    price_currency_for_table = (
        zip(
            url_parser_to_list(*LINKS_TO_INFO_ABOUT_THE_VALUE_OF_ASSETS[
                'ecd_names'
            ]),
            items_converted_to_float_rsd, items_converted_to_float_eur)
    )
    return price_currency_for_table


def rsd_to_rub(rsd_send):
    '''Перевод из Сербии в РФ'''
    din_to_usdt = url_parser_to_dict(*LINKS_TO_INFO_ABOUT_THE_VALUE_OF_ASSETS[
                'ecd_prices'
        ])['Tether'][0]
    rub_collect = (
        (
            rsd_send
            * (1 - COMMISSION_FOR_ADDING_MONEY_TO_WALLET)
            * (1 - COMMISSION_FOR_PURCHASE_OF_USDT)
            - din_to_usdt
        )
        / din_to_usdt
        * [float(i.replace(',', '.')) for i in url_parser_to_list(
            *LINKS_TO_INFO_ABOUT_THE_VALUE_OF_ASSETS['google_USDT_RUB']
        )][0]
    )
    return rub_collect


def calculate():
    label['text'] = f'''
You`ll get {rsd_to_rub(float(entry.get())):.2f} RUB
If send {float(entry.get()):.2f} RSD
'''


root = Tk()
root.geometry('600x400')
root.title('Calculate your transfer 0.1')


def on_closing():
    # показываем диалоговое окно с кнопкой
    if messagebox.askokcancel("", "Закрыть программу?"):
        # удаляем окно и освобождаем память
        root.destroy()


# сообщаем системе о том, что делать, когда окно закрывается
root.protocol("WM_DELETE_WINDOW", on_closing)

entry = ttk.Entry()
entry.pack(anchor=NW, padx=6, pady=6)

btn = ttk.Button(text='Calculate', command=calculate)
btn.pack(anchor=NW, padx=6, pady=6)

label = ttk.Label()
label.pack(anchor=NW, padx=6, pady=6)

columns = ("name", "RSD", "EUR")

tree = ttk.Treeview(columns=columns, show="headings")
tree.pack(fill=BOTH, expand=1)

# определяем заголовки
tree.heading("name", text="Name")
tree.heading("RSD", text="RSD")
tree.heading("EUR", text="EUR")

# превратим словарь с кортежами в значениях в список с кортежами

for i in url_parser_to_list_of_toupels(*LINKS_TO_INFO_ABOUT_THE_VALUE_OF_ASSETS[
                'ecd_prices'
        ]):
    tree.insert("", END, values=i)

root.mainloop()
