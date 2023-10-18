from flask import Flask, request
import tkinter as tk
from tkinter import ttk
import threading
import params

app = Flask(__name__)


class BagStatus:
    ON_BELT = "On belt"
    OFF_BELT = "Off belt"
    LOADED = "Loaded"


off_belt = []


# Create a Tkinter window
window = tk.Tk()
window.title("BagInfo v0.0.1")
COLUMNS = ("BagId", "Class", "Status", "ULD")
table = ttk.Treeview(window, columns=COLUMNS)
uld_closing = {"one": 0, "two": 0}


@app.route("/scan", methods=["POST"])
def scan():
    content = request.get_json()
    cartid = content["cart"]

    if not off_belt:
        uld_closing[cartid] += 1
        if uld_closing[cartid] < 3:
            return f"Closing {uld_closing[cartid]}/3", 200

        uld_closing[cartid] = 0
        update_uld_status(cartid, "ULD closed")
        return "ULD closed", 200

    uld_closing[cartid] = 0

    bagId = off_belt.pop()

    res = get_bag_row(bagId)
    if res is None:
        return "Bag not found", 400

    row, values = res

    if values[1] not in params.SEGREGATION[cartid]:
        return "ERRROR", 400

    table.item(row, values=(values[0], values[1], BagStatus.LOADED, cartid))

    return "SUCCESS", 200


@app.route("/bag", methods=["POST"])
def bag():
    content = request.get_json()
    bagId = content["bagId"]
    action = content["action"]

    if action == "on-belt":
        bag_type = content["bag_type"]
        table.insert("", "end", values=(bagId, bag_type, BagStatus.ON_BELT, ""))
        return "OK", 200

    elif action == "off-belt":
        ret = get_bag_row(bagId)

        if ret is None:
            return "Bag not found", 400

        row, values = ret

        table.item(row, values=(values[0], values[1], BagStatus.OFF_BELT, values[3]))
        return "OK", 200

    return "Invalid action", 400


def get_bag_row(bagId):
    for row in table.get_children():
        values = table.item(row, "values")

        if int(values[0]) == bagId:
            return row, values

    return None


def update_uld_status(ULD, status):
    for row in table.get_children():
        values = table.item(row, "values")

        if int(values[3]) == ULD:
            table.item(row, values=(values[0], values[1], status, ULD))


def run_server():
    app.run(host="0.0.0.0", port=params.SERVER_PORT, threaded=True)


server_thread = threading.Thread(target=run_server)
server_thread.start()

for i, col in enumerate(COLUMNS):
    table.heading("#" + str(i + 1), text=col)
    table.column("#" + str(i + 1), anchor="center")

table.pack()

window.mainloop()

server_thread.join()
