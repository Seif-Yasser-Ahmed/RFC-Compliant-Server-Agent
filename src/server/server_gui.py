import sys
from threading import Thread
import time
from server import Server
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import customtkinter as ctk
from tkinter import messagebox
# from customtkinter import
import tkinter.ttk as ttk

from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
import os


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("server_logs.txt"):
            self.callback()


class DHCPServerGUI:

    def __init__(self, root):
        self.ip_list = []  # Stores the IP addresses in the table
        self.root = root
        self.root.title("DHCP Server GUI")
        self.root.geometry("600x600")

        self.server_started = False  # Flag to track if the server is running
        self.observer = None  # File system observer

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview",
                             background="#333333",
                             foreground="lightgreen",
                             fieldbackground="black",
                             font=("Arial", 10))
        self.style.configure("Treeview.Heading",
                             background="#333333",
                             foreground="green",
                             font=("Arial", 10, "bold"))
        self.style.map("Treeview",
                       background=[("selected", "green")])
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        center_frame = ctk.CTkFrame(self.main_frame)
        center_frame.pack(expand=True)

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "server.png")
            self.server_image = Image.open(image_path)

            self.server_image = self.server_image.resize((215, 215))

            self.server_image = ImageTk.PhotoImage(self.server_image)

            self.image_label = ctk.CTkLabel(
                center_frame, image=self.server_image, text="")
            self.image_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading image: {e}")

        self.modify_button = ctk.CTkButton(
            center_frame, text="Modify Server", font=("Helvetica", 18, "bold"), fg_color="#4CAF50", text_color="white",
            command=self.show_modify_window
        )
        self.modify_button.pack(pady=10)

        self.modify_frame = ctk.CTkFrame(self.root)
        self.table = None
        self.add_button = None
        self.delete_button = None
        self.back_button = None
        self.start_button = None
        self.view_ip_button = None

    def on_closing(self):
        os._exit(0)

    def show_modify_window(self):
        self.main_frame.pack_forget()
        self.modify_frame.pack(fill="both", expand=True)

        if self.table is None:
            self.table = ttk.Treeview(self.modify_frame, columns=(
                "#", "IP Address"), show="headings")
            self.table.heading("#", text="#")
            self.table.heading("IP Address", text="IP Address")
            self.table.column("#", width=40, anchor="center")
            self.table.column("IP Address", width=150, anchor="w")
            default_ips = Server.load_ip_pool(os.path.join(
                os.getcwd(), "src/server/ip_pool.txt"))
            for idx, ip in enumerate(default_ips, start=1):
                self.table.insert("", "end", values=(idx, ip))
                self.ip_list.append(ip)
            self.table.pack(fill="both", expand=True, padx=10, pady=10)

        if self.add_button is None:
            button_frame = ctk.CTkFrame(self.modify_frame)
            button_frame.pack(pady=10)

            self.add_button = ctk.CTkButton(
                button_frame, text="+", font=("Helvetica", 14), command=self.add_ip, width=4, fg_color="#4CAF50", text_color="white")
            self.add_button.pack(side="left", padx=5)

            self.delete_button = ctk.CTkButton(
                button_frame, text="-", font=("Helvetica", 14), command=self.delete_ip, width=4, fg_color="#4CAF50", text_color="white")
            self.delete_button.pack(side="left", padx=5)

            self.back_button = ctk.CTkButton(button_frame, text="Back", font=(
                "Helvetica", 15), command=self.show_main_window, width=5, fg_color="#4CAF50", text_color="white")
            self.back_button.pack(side="left", padx=5)

            self.start_button = ctk.CTkButton(
                self.modify_frame, text="Start Server", font=("Helvetica", 14, "bold"),
                command=self.start_server, width=20, fg_color="#4CAF50", text_color="white"
            )
            self.start_button.pack(pady=10)

    def update_log_display(self):
        """Update the log display when file changes are detected."""
        try:
            log_file_path = os.path.join(os.getcwd(), "output/log.log")
            if not os.path.exists(log_file_path):
                print("Log file does not exist yet.")
                return

            with open(log_file_path, "r") as log_file:
                content = log_file.read()

            if hasattr(self, 'log_text'):
                self.log_text.configure(state="normal")
                self.log_text.delete(1.0, "end")
                self.log_text.insert("end", content)
                self.log_text.see("end")
                self.log_text.configure(state="disabled")

        except Exception as e:
            print(f"Error updating log display: {e}")

    def start_server(self):
        self.log_cleaner()
        Server.write_ip_pool(os.path.join(
            os.getcwd(), "src/server/ip_pool.txt"), self.ip_list)

        if self.table is None or len(self.table.get_children()) == 0:
            messagebox.showerror(
                "Error", "Cannot start server. No IPs are present.")
            return

        Thread(target=Server.main).start()
        self.server_started = True
        # print(f"Server started: {self.server_started}")

        self.start_button.configure(
            text="Terminate Server", fg_color="red", command=self.terminate_server)

        self.log_window = ctk.CTkToplevel(self.root)
        self.log_window.title("DHCP Server Logs")
        self.log_window.geometry("800x400")

        log_frame = ctk.CTkFrame(self.log_window)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = ctk.CTkTextbox(log_frame, wrap="word",
                                       height=750, width=800, fg_color="black", text_color="white")
        self.log_text.pack(side="left", fill="both", expand=True)

        self.log_window.protocol("WM_DELETE_WINDOW", self.terminate_server)

        self.log_text.configure(state="disabled")

        self.observer = Observer()
        log_dir = os.path.dirname(os.path.join(
            os.getcwd(), "output/log.log"))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)  # Create directory if it doesn't exist
        event_handler = LogFileHandler(self.update_log_display)
        self.observer.schedule(event_handler, path=log_dir, recursive=False)
        self.observer.start()

        self.update_log_display()

        def continuous_log_update():
            while self.server_started:
                self.update_log_display()
                time.sleep(1)  # Update every second

        Thread(target=continuous_log_update, daemon=True).start()

        def display_ip_table():
            """Open a new window to display Server.IP_GUI dictionary."""
            if not hasattr(Server, 'IP_GUI') or not Server.IP_GUI:
                messagebox.showerror(
                    "Error", "No IP data available to display.")
                return

            ip_table_window = ctk.CTkToplevel(self.root)
            ip_table_window.title("IP Address Table")
            ip_table_window.geometry("600x400")

            table_frame = ctk.CTkFrame(ip_table_window)
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)

            columns = ("IP Address", "Value", "Time")
            ip_tree = ttk.Treeview(
                table_frame, columns=columns, show="headings")
            ip_tree.heading("IP Address", text="IP Address")
            ip_tree.heading("Value", text="Value")
            ip_tree.heading("Time", text="Time")
            ip_tree.pack(fill="both", expand=True, padx=10, pady=10)

            # print(Server.IP_GUI)

            def insert_ip_data():
                for ip, (value, time) in Server.IP_GUI.items():
                    found = False
                    for row in ip_tree.get_children():
                        if ip_tree.item(row, "values")[0] == ip:
                            ip_tree.item(row, values=(ip, value, time))
                            found = True
                            break
                    if not found:
                        ip_tree.insert("", "end", values=(ip, value, time))
                ip_tree.after(1000, insert_ip_data)

            insert_ip_data()

            scroll_bar = ttk.Scrollbar(
                table_frame, orient="vertical", command=ip_tree.yview)
            ip_tree.configure(yscrollcommand=scroll_bar.set)
            scroll_bar.pack(side="right", fill="y")

        if self.view_ip_button is None:
            self.view_ip_button = ctk.CTkButton(
                self.modify_frame,
                text="View IP Table",
                command=display_ip_table
            )
            self.view_ip_button.pack(pady=10)

    def log_cleaner(self):
        log_file_path = os.path.join(os.getcwd(), "output/log.log")
        backup_log_file_path = os.path.join(
            os.getcwd(), "output/log_history.log")

        with open(log_file_path, "r") as log_file:
            content = log_file.read()

        with open(backup_log_file_path, "w") as backup_log_file:
            backup_log_file.write(content)

        with open(log_file_path, "w") as log_file:
            log_file.write("")

    def terminate_server(self):
        self.server_started = False
        # print(f"Server terminated: {self.server_started}")

        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        self.start_button.configure(
            text="Start Server", fg_color="#008CBA", command=self.start_server)

        if hasattr(self, 'log_window') and self.log_window.winfo_exists():
            self.log_window.destroy()

    def delete_ip(self):
        selected_item = self.table.selection()
        if selected_item:
            ip_to_remove = self.table.item(selected_item, "values")[1]
            self.table.delete(selected_item)
            if ip_to_remove in self.ip_list:
                self.ip_list.remove(ip_to_remove)
            self.update_indexes()
            Server.write_ip_pool(os.path.join(
                os.getcwd(), "src/server/ip_pool.txt"), self.ip_list)
            print("IP List Updated:", self.ip_list)
        else:
            messagebox.showwarning(
                "No Selection", "Please select an IP to delete.")

    def update_indexes(self):
        for idx, item in enumerate(self.table.get_children(), start=1):
            values = self.table.item(item, "values")
            self.table.item(item, values=(idx, values[1]))

    def show_main_window(self):
        self.modify_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

    def add_ip(self):
        ip = askstring("Add IP", "Enter IP Address:")
        if ip and self.is_valid_ip(ip):
            existing_ips = [self.table.item(
                item)["values"][1] for item in self.table.get_children()]
            if ip in existing_ips:
                messagebox.showwarning("Duplicate IP", f"The IP address {
                                       ip} already exists.")
                return
            current_row_count = len(self.table.get_children())
            self.table.insert("", "end", values=(current_row_count + 1, ip))
            self.ip_list.append(ip)
            Server.write_ip_pool(os.path.join(
                os.getcwd(), "src/server/ip_pool.txt"), self.ip_list)
            print("IP List Updated:", self.ip_list)

    def is_valid_ip(self, ip):
        parts = ip.split(".")
        if len(parts) != 4:
            messagebox.showerror(
                "Invalid Entry", "Invalid IP format! IP should be in the format: xxx.xxx.xxx.xxx")
            return False

        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                messagebox.showerror(
                    "Invalid Entry", "Invalid IP format! Each octet should be a number between 0 and 255.")
                return False

        if sum(int(part) for part in parts) == 0:
            messagebox.showerror(
                "Reserved IP", "Can't use reserved IP addresses like 0.0.0.0 or 255.255.255.255.")
            return False

        reserved_ips = ["0.0.0.0", "255.255.255.255",
                        "00.00.00.00", "000.000.000.000"]
        if ip in reserved_ips:
            messagebox.showerror(
                "Reserved IP", "Can't use reserved IP addresses like 0.0.0.0 or 255.255.255.255.")
            return False

        return True


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = DHCPServerGUI(root)
    root.mainloop()
