from flask import Flask, request, json
import tkinter as tk
from tkinter import ttk
import threading

app = Flask(__name__)


class BagStatus:
    ON_BELT = 'On belt'
    OFF_BELT = 'Off belt'
    LOADED = 'Loaded'


off_belt = []


# Create a Tkinter window
window = tk.Tk()
window.title("BagInfo v0.0.1")
table = ttk.Treeview(window, columns=("BagId", "Class", "Status", "ULD"))


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
    bag_type = content['bag_type']

    if action == 'on-belt':
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

        if values[0] == bagId:
            table.item(row, values=(
                values[0], values[1], bag_status, ULD))
            return 'OK', 200
    return 'Bag not found', 400


def run_server():
    app.run(host='0.0.0.0', port=6969)


server_thread = threading.Thread(target=run_server)
server_thread.start()

table.heading("#1", text="BagId")
table.heading("#2", text="Class")
table.heading("#3", text="Status")
table.heading("#4", text="ULD")

# Pack the table to display it
table.pack()

window.mainloop()

server_thread.join()
