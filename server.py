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
closed = []
error_bag = None

# Create a Tkinter window
window = tk.Tk()
window.title("BagInfo v0.0.1")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{screen_width // 2}x{screen_height // 4}+{screen_width // 2}+0")
COLUMNS = ("BagId", "Class", "Status", "ULD")
table = ttk.Treeview(window, columns=COLUMNS)
uld_closing = {"one": 0, "two": 0}


@app.after_request
def log(response):
    print(response.get_data())
    return response


@app.route("/scan", methods=["POST"])
def scan():
    content = request.get_json()
    cartid = content["cart"]

    if cartid in closed:
        return "ULD closed", 200

    global uld_closing
    uld_closing = {id: 0 if id != cartid else uld_closing[cartid] for id in uld_closing}

    global error_bag
    if not error_bag and not off_belt:
        return "Bag not found", 400

    bagId = error_bag or off_belt.pop()
    row, values = get_row(bagId)

    table.item(row, values=(values[0], values[1], BagStatus.LOADED, cartid))

    if values[1] not in params.SEGREGATION[cartid]:
        table.item(row, tags=("error"))
        error_bag = bagId
        return "INCORRECT CART", 200

    table.item(row, tags=("success"))
    error_bag = None
    return "SUCCESS", 200


@app.route("/ULD", methods=["POST"])
def uld():
    content = request.get_json()
    cartid = content["cart"]

    if cartid in closed:
        return "ULD closed", 200

    global uld_closing
    uld_closing = {id: 0 if id != cartid else uld_closing[cartid] for id in uld_closing}

    uld_closing[cartid] += 1

    if uld_closing[cartid] < 3:
        return f"ULD closing {uld_closing[cartid]}/3", 200

    update_uld_status(cartid, "ULD closed")
    closed.append(cartid)
    return "ULD closed", 200


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
        global error_bag
        error_bag = None

        row, values = get_row(bagId)
        if row is None:
            return "Bag not found", 400

        table.item(row, values=(values[0], values[1], BagStatus.OFF_BELT, values[3]))
        off_belt.append(bagId)
        return "OK", 200

    return "Invalid action", 400


def get_row(bagId=None, uld=None):
    for row in table.get_children():
        values = table.item(row, "values")

        if bagId is not None and int(values[0]) != bagId:
            continue

        if uld is not None and values[3] != uld:
            continue

        return row, values

    return None, None


def update_uld_status(uld, status):
    for row in table.get_children():
        values = table.item(row, "values")

        if values[3] == uld:
            table.item(row, values=(values[0], values[1], status, uld))


def run_server():
    app.run(host="0.0.0.0", port=params.SERVER_PORT, threaded=True)


server_thread = threading.Thread(target=run_server)
server_thread.start()

for i, col in enumerate(COLUMNS):
    table.heading("#" + str(i + 1), text=col)
    table.column("#" + str(i + 1), anchor="center")

table.tag_configure("error", background="orange")
table.tag_configure("success", background="green")

# table.insert("", "end", values=(1, "ECO", BagStatus.OFF_BELT, ""))
# off_belt.append(1)

table.pack()

window.mainloop()

server_thread.join()
