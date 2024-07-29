import requests
import time
import tkinter as tk
from tkinter import messagebox

token = 'Ваш токен'

def get_time_range():
    current_time_unix_ms = int(time.time() * 1000)
    if time_var.get() == 1:
        current_time_unix_ms -= 7200000
    elif time_var.get() == 2:
        current_time_unix_ms -= 1
    
    time_72_hours_ago_unix_ms = current_time_unix_ms - (72 * 60 * 60 * 1000)
    return current_time_unix_ms, time_72_hours_ago_unix_ms

def fetch_orders():
    current_time_unix_ms, time_72_hours_ago_unix_ms = get_time_range()
    
    params = {
        'page[number]': 0,
        'page[size]': 20,
        'filter[orders][state]': 'NEW',
        'filter[orders][creationDate][$ge]': time_72_hours_ago_unix_ms,
        'filter[orders][creationDate][$le]': current_time_unix_ms,
        'filter[orders][status]': 'APPROVED_BY_BANK',
        'filter[orders][deliveryType]': 'PICKUP',
        'filter[orders][signatureRequired]': 'false',
        'include[orders]': 'user'
    }

    headers = {
        'Content-Type': 'application/vnd.api+json',
        'X-Auth-Token': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36'
    }

    try:
        response = requests.get('https://kaspi.kz/shop/api/v2/orders', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        orders = [(order['id'], order['attributes']['code']) for order in data['data']]
        return orders
    except requests.exceptions.RequestException as e:
        messagebox.showerror('Error', f'Ошибка при выполнении запроса: {e}')
        return []

def accept_order(order_id, order_code):
    url = f'https://kaspi.kz/shop/api/v2/orders/{order_id}'
    payload = {
        "data": {
            "type": "orders",
            "id": order_id,
            "attributes": {
                "code": order_code,
                "status": "ACCEPTED_BY_MERCHANT"
            }
        }
    }

    headers = {
        'Content-Type': 'application/vnd.api+json',
        'X-Auth-Token': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36'
    }

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        messagebox.showinfo('Success', 'Заказ принят успешно!')
    except requests.exceptions.RequestException as e:
        messagebox.showerror('Error', f'Ошибка при выполнении запроса: {e}')

def auto_accept_orders():
    if auto_accept_var.get():
        orders = fetch_orders()
        for order_id, order_code in orders:
            accept_order(order_id, order_code)
    root.after(15000, auto_accept_orders)

def refresh_orders():
    orders = fetch_orders()
    listbox.delete(0, tk.END)
    for order_id, order_code in orders:
        listbox.insert(tk.END, f'{order_code} (ID: {order_id})')
    root.after(15000, refresh_orders)

def on_accept_order():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning('Warning', 'Выберите заказ для принятия.')
        return

    order_info = listbox.get(selected[0])
    order_id = order_info.split(' (ID: ')[1][:-1]
    order_code = order_info.split(' (ID: ')[0]
    accept_order(order_id, order_code)

root = tk.Tk()
root.title('Kaspi.kz Order Manager')

frame = tk.Frame(root)
frame.pack(pady=10)

listbox = tk.Listbox(frame, width=50, height=15)
listbox.pack(side=tk.LEFT, padx=10)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox.config(yscrollcommand=scrollbar.set)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

refresh_button = tk.Button(button_frame, text='Обновить заказы', command=refresh_orders)
refresh_button.pack(side=tk.LEFT, padx=5)

accept_button = tk.Button(button_frame, text='Принять заказ', command=on_accept_order)
accept_button.pack(side=tk.LEFT, padx=5)

auto_accept_var = tk.BooleanVar()
auto_accept_checkbox = tk.Checkbutton(root, text='Автопринятие заказов', variable=auto_accept_var)
auto_accept_checkbox.pack(pady=10)

time_var = tk.IntVar(value=1)
radio_frame = tk.Frame(root)
radio_frame.pack(pady=10)

radio1 = tk.Radiobutton(radio_frame, text='Заказы старше 90 минут', variable=time_var, value=1)
radio1.pack(side=tk.LEFT, padx=5)

radio2 = tk.Radiobutton(radio_frame, text='Все новые заказы', variable=time_var, value=2)
radio2.pack(side=tk.LEFT, padx=5)

refresh_orders()
auto_accept_orders()

root.mainloop()
