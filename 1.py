import tkinter as tk
import json
import requests
import time

class ChatInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Interface")
        self.root.geometry("600x400")

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(side="top", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.chat_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.chat_widget = tk.Text(self.chat_frame, yscrollcommand=self.scrollbar.set)
        self.chat_widget.pack(side="left", fill="both", expand=True)

        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(side="bottom", fill="x")

        self.entry_widget = tk.Entry(self.entry_frame)
        self.entry_widget.pack(side="left", fill="x", expand=True)

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right")

        # Initialize local server client
        self.client = requests.Session()
        self.client.base_url = "http://localhost:1234/v1"

        # Initialize chat history
        self.history = [
            {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
        ]

        # Initialize log
        self.log = []

    def send_message(self):
        user_message = self.entry_widget.get()
        self.chat_widget.insert("end", f"You: {user_message}\n")
        self.entry_widget.delete(0, "end")

        # Add user message to chat history
        self.history.append({"role": "user", "content": user_message})

        # Add user message to log
        self.log.append({"role": "user", "content": user_message})

        # Send request to local server
        completion = self.client.post(
            "chat/completions",
            json={
                "model": "local-model",
                "messages": self.history,
                "temperature": 0.7,
                "stream": True,
            },
            stream=True,
        )

        # Process response from local server
        new_message = {"role": "assistant", "content": ""}
        for chunk in completion.iter_lines():
            if chunk:
                data = json.loads(chunk)
                if data["choices"][0]["delta"].get("content"):
                    self.chat_widget.insert("end", data["choices"][0]["delta"]["content"], end="")
                    new_message["content"] += data["choices"][0]["delta"]["content"]

        # Add assistant message to chat history
        self.history.append(new_message)

        # Add assistant message to log
        self.log.append(new_message)

        # Add newline to chat widget
        self.chat_widget.insert("end", "\n")

        # If the assistant's response ends with a question mark, automatically respond
        if new_message["content"].endswith("?"):
            self.send_message()

    def view_log(self):
        log_text = json.dumps(self.log, indent=2)
        log_window = tk.Toplevel(self.root)
        log_window.title("Chat Log")
        log_window.geometry("800x600")

        log_widget = tk.Text(log_window)
        log_widget.pack(side="left", fill="both", expand=True)
        log_widget.insert("end", log_text)

root = tk.Tk()
chat_interface = ChatInterface(root)
root.mainloop()
