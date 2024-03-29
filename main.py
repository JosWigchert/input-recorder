import tkinter as tk
from tkinter import filedialog as fd
import time
import threading
import json
from pynput import mouse, keyboard


class RecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Recorder App")

        self.record_button = tk.Button(
            master, text="Record", command=self.start_recording
        )
        self.record_button.pack()

        self.run_button = tk.Button(
            master, text="Run", command=self.run_recorded_actions
        )
        self.run_button.pack()

        self.start_time = time.time()
        self.ctlr_pressed = False
        self.shift_pressed = False
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recorded_actions = []

    def start_recording(self):
        self.start_time = time.time()
        self.recorded_actions = []
        self.record_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.DISABLED)
        self.record_button.config(
            text="Recording... (Press Esc to stop)", command=self.stop_recording
        )

        self.record_thread = threading.Thread(target=self.record_actions)
        self.record_thread.start()

    def stop_recording(self):
        self.record_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        self.record_button.config(text="Record", command=self.start_recording)

        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        # Prompt for filename and save recorded actions to a JSON file
        filename = fd.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
        )
        if filename:
            with open(filename, "w") as f:
                json.dump(self.recorded_actions, f, indent=4)

    def record_actions(self):
        with mouse.Listener(
            on_click=self.on_click,
        ) as self.mouse_listener, keyboard.Listener(
            on_press=self.on_key_press, on_release=self.on_key_release
        ) as self.keyboard_listener:
            self.mouse_listener.join()
            self.keyboard_listener.join()

    def on_click(self, x, y, button, pressed):
        if hasattr(button, "name"):
            current_time = time.time()
            self.recorded_actions.append(
                {
                    "device": "mouse",
                    "time": current_time - self.start_time,
                    "data": {
                        "button": button.name,
                        "pressed": pressed,
                        "x": x,
                        "y": y,
                    },
                },
            )
            self.start_time = current_time
            print(self.recorded_actions[-1])

    def on_key_press(self, key):
        if key == keyboard.Key.esc:
            self.stop_recording()
            return
        elif hasattr(key, "value") and hasattr(key.value, "vk"):
            self.add_key_press(key.value.vk, "down")
        elif hasattr(key, "vk"):
            self.add_key_press(key.vk, "down")
        else:
            print("Unknown keypress: ", key)
            return
        print(self.recorded_actions[-1])

    def on_key_release(self, key):
        if hasattr(key, "value") and hasattr(key.value, "vk"):
            self.add_key_press(key.value.vk, "up")
        elif hasattr(key, "vk"):
            self.add_key_press(key.vk, "up")
        else:
            print("Unknown keypress: ", key)
            return
        print(self.recorded_actions[-1])

    def add_key_press(self, key, action: ["down", "up"]):
        current_time = time.time()
        self.recorded_actions.append(
            {
                "device": "keyboard",
                "time": current_time - self.start_time,
                "data": {
                    "key": key,
                    "action": action,
                },
            }
        )
        self.start_time = current_time

    def run_recorded_actions(self):
        filename = fd.askopenfilename(
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
        )
        if not filename:
            return

        with open(filename, "r") as f:
            loaded_actions = json.load(f)

            self.record_button.config(state=tk.DISABLED)
            self.run_button.config(state=tk.DISABLED)

            keyboard_controller = keyboard.Controller()
            mouse_controller = mouse.Controller()

            print("Running commands in ", end="")
            print("3 ", end="")
            time.sleep(1)
            print("2 ", end="")
            time.sleep(1)
            print("1 ", end="")
            time.sleep(1)
            for i in range(20):
                for action in loaded_actions:
                    time.sleep(action["time"])
                    data = action["data"]
                    print(data)
                    if action["device"] == "mouse":
                        button = None
                        if hasattr(mouse.Button, data["button"]):
                            button = getattr(mouse.Button, data["button"])

                        if button is not None:
                            if data["pressed"]:
                                mouse_controller.position = (data["x"], data["y"])
                                mouse_controller.press(button)
                            elif not data["pressed"]:
                                mouse_controller.position = (data["x"], data["y"])
                                mouse_controller.release(button)
                        else:
                            print("Button not found? (", action["button"], ")", sep="")
                    elif action["device"] == "keyboard":
                        key = data["key"]
                        action = data["action"]

                        if action == "down":
                            keyboard_controller.press(keyboard.KeyCode.from_vk(key))
                        elif action == "up":
                            keyboard_controller.release(keyboard.KeyCode.from_vk(key))
                        else:
                            print("Unknown error")

            self.record_button.config(state=tk.NORMAL)
            self.run_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()
