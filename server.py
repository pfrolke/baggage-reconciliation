from flask import Flask, request
import tkinter as tk
from tkinter import ttk
import threading
import params

app = Flask(__name__)


class BagStatus:
    ON_BELT = 'On belt'
    OFF_BELT = 'Off belt'
    LOADED = 'Loaded'


off_belt = []


# Create a Tkinter window
window = tk.Tk()
window.title("BagInfo v0.0.1")
COLUMNS = ("BagId", "Class", "Status", "ULD")
table = ttk.Treeview(window, columns=COLUMNS)


@app.route('/scan', methods=['POST'])
def scan():
    content = request.get_json()
    cartid = content['cart']

    if not off_belt:
        return 'No bags', 400

    bagId = off_belt.pop()

    res = update_bag_status(bagId, BagStatus.LOADED, cartid)
    if res[1] != 200:
        return res

    return 'SUCCESS', 200


@app.route('/bag', methods=['POST'])
def bag():
    content = request.get_json()
    bagId = content['bagId']
    action = content['action']

    if action == 'on-belt':
        bag_type = content['bag_type']
        table.insert("", "end", values=(
            bagId, bag_type, BagStatus.ON_BELT, ''))
        return 'OK', 200

    elif action == 'off-belt':
        res = update_bag_status(bagId, BagStatus.OFF_BELT)
        if res[1] == 200:
            off_belt.append(bagId)
        return res

    return 'Invalid action', 400


def update_bag_status(bagId, bag_status, ULD=''):
    for row in table.get_children():
        values = table.item(row, 'values')

        if int(values[0]) == bagId:
            table.item(row, values=(
                values[0], values[1], bag_status, ULD))
            return 'OK', 200
    return 'Bag not found', 400


def run_server():
    app.run(host='0.0.0.0', port=params.SERVER_PORT)


server_thread = threading.Thread(target=run_server)
server_thread.start()

for i, col in enumerate(COLUMNS):
    table.heading('#' + str(i + 1), text=col)
    table.column('#' + str(i + 1), anchor="center")

table.pack()

window.mainloop()

server_thread.join()
