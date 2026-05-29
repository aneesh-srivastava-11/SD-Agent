import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os
import json
import time

class ShadowDragonGUI:
    def __init__(self, assistant):
        self.assistant = assistant
        self.root = tk.Tk()
        self.root.title("🐲 ShadowDragon Control Center")
        self.root.geometry("800x600")
        self.root.configure(bg="#121214")

        # Custom Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure Colors
        self.style.configure("TFrame", background="#121214")
        self.style.configure("TLabel", background="#121214", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.configure("TButton", background="#1f1f23", foreground="#00f0ff", bordercolor="#00f0ff", font=("Segoe UI", 10, "bold"))
        self.style.map("TButton",
            background=[("active", "#00f0ff"), ("pressed", "#008b99")],
            foreground=[("active", "#121214")]
        )

        self._build_ui()
        self.refresh_memory()
        
        # Set self in assistant so it can update status and logs
        self.assistant.gui = self

    def _build_ui(self):
        # Main Layout: Two Columns (Left: Status & Logs, Right: Memory & Controls)
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, width=280, padx=(5, 0))

        # --- Left Column: Status & Logs ---
        status_container = ttk.Frame(left_frame)
        status_container.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(status_container, text="System Status:", font=("Segoe UI", 12, "bold"), foreground="#8f9099").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_container, text="System Online (Idle)", font=("Segoe UI", 12, "bold"), foreground="#00f0ff")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Log View
        ttk.Label(left_frame, text="Conversation Logs", font=("Segoe UI", 11, "bold"), foreground="#00f0ff").pack(anchor=tk.W, pady=(0, 5))
        self.log_text = scrolledtext.ScrolledText(
            left_frame, 
            bg="#1c1c1f", 
            fg="#e3e3e6", 
            insertbackground="#00f0ff",
            font=("Consolas", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground="#2d2d30",
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # --- Right Column: Memory & Controls ---
        # Memory View
        ttk.Label(right_frame, text="Persistent Memory Store", font=("Segoe UI", 11, "bold"), foreground="#00f0ff").pack(anchor=tk.W, pady=(0, 5))
        self.memory_text = scrolledtext.ScrolledText(
            right_frame,
            bg="#1c1c1f",
            fg="#a9a9b3",
            font=("Consolas", 9),
            bd=0,
            highlightthickness=1,
            highlightbackground="#2d2d30",
            width=35,
            height=20,
            state=tk.DISABLED
        )
        self.memory_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Controls Panel
        controls_label = ttk.Label(right_frame, text="Controls & Shortcut", font=("Segoe UI", 11, "bold"), foreground="#00f0ff")
        controls_label.pack(anchor=tk.W, pady=(10, 5))

        shortcut_info = ttk.Label(right_frame, text="Global hotkey: Alt+Shift+S\nto trigger manual listening.", justify=tk.LEFT, foreground="#8f9099")
        shortcut_info.pack(anchor=tk.W, pady=(0, 10))

        btn_trigger = ttk.Button(right_frame, text="🎙️ Trigger Listen", command=self.trigger_listen)
        btn_trigger.pack(fill=tk.X, pady=5)

        btn_clear = ttk.Button(right_frame, text="🗑️ Clear Logs", command=self.clear_logs)
        btn_clear.pack(fill=tk.X, pady=5)

        btn_exit = ttk.Button(right_frame, text="❌ Shutdown Agent", command=self.shutdown_agent)
        btn_exit.pack(fill=tk.X, pady=(15, 0))

    def update_status(self, text, color="#00f0ff"):
        def _update():
            self.status_label.config(text=text, foreground=color)
        self.root.after(0, _update)

    def add_log(self, role, text):
        def _add():
            self.log_text.config(state=tk.NORMAL)
            timestamp = time.strftime("%H:%M:%S")
            prefix = "👤 User: " if role.lower() == "user" else "🐲 Agent: "
            color = "#00f0ff" if role.lower() == "agent" else "#ffffff"
            
            # Insert log turn with customized formatting
            self.log_text.insert(tk.END, f"[{timestamp}] ")
            self.log_text.insert(tk.END, prefix)
            self.log_text.insert(tk.END, f"{text}\n\n")
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)
        self.root.after(0, _add)

    def refresh_memory(self):
        def _refresh():
            self.memory_text.config(state=tk.NORMAL)
            self.memory_text.delete("1.0", tk.END)
            try:
                memory_data = self.assistant.memory.get_memory()
                formatted_json = json.dumps(memory_data, indent=2)
                self.memory_text.insert(tk.END, formatted_json)
            except Exception as e:
                self.memory_text.insert(tk.END, f"Error loading memory: {e}")
            self.memory_text.config(state=tk.DISABLED)
        self.root.after(0, _refresh)

    def trigger_listen(self):
        self.assistant.hotkey_triggered = True
        self.add_log("System", "Manual listen triggered.")

    def clear_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def shutdown_agent(self):
        self.assistant.running = False
        self.root.destroy()
        os._exit(0)

    def run(self):
        self.root.mainloop()
