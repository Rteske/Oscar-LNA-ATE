import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
import datetime
from pa_module_level_test_manager import PaModuleTestManager
from logging_utils import configure_logging, log_message, log_queue
from mocked_test_class import MockedTest

class GUIHandler(logging.Handler):
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.log_widget.after(0, self.log_widget.update_log, log_entry)

class OscarPaModuleGUI:
    def __init__(self, root, sim_mode=False):
        self.root = root
        self.root.title("Oscar PA Module GUI")
        self.root.geometry("600x600")
        self.sim_mode = sim_mode

        # Notebook (Tabbed Interface)
        self.notebook = ttk.Notebook(root)
        self.main_frame = ttk.Frame(self.notebook)
        self.extra_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main Test")
        self.notebook.add(self.extra_tab, text="Tech Tools")
        self.notebook.pack(expand=True, fill="both")

        # Serial number entry
        tk.Label(self.main_frame, text="Enter Serial Number:").pack(pady=5)
        self.sn_entry = tk.Entry(self.main_frame)
        self.sn_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Enter Dir:").pack(pady=5)
        self.dir_entry = tk.Entry(self.main_frame)
        self.dir_entry.pack(pady=5)

        # Dropdown menu
        self.options = [
            "HIGH_BAND_PATH1 (Vertical)",
            "HIGH_BAND_PATH2 (Horizontal)",
            "LOW_BAND_PATH1 (Vertical)",
            "LOW_BAND_PATH2 (Horizontal)"
        ]
        self.dropdown_var = tk.StringVar(value=self.options[0])
        tk.Label(self.main_frame, text="Select an option:").pack(pady=5)
        self.dropdown_menu = ttk.Combobox(self.main_frame, textvariable=self.dropdown_var, values=self.options, state="readonly", width=40)
        self.dropdown_menu.pack(pady=5)

        # Checkboxes
        self.checkbox1_var = tk.BooleanVar()
        self.checkbox2_var = tk.BooleanVar()
        tk.Checkbutton(self.main_frame, text="CW & OQPSK SIGNAL ANALYZER", variable=self.checkbox1_var).pack(pady=5)
        tk.Checkbutton(self.main_frame, text="VSWR GAIN AND PHASE", variable=self.checkbox2_var).pack(pady=5)

        # Status label
        self.status_label = tk.Label(self.main_frame, text="Status: Idle", fg="blue")
        self.status_label.pack(pady=5)

        # Scrollable Logger display
        self.log_text = scrolledtext.ScrolledText(self.main_frame, height=10, width=60, state=tk.DISABLED)
        self.log_text.pack(pady=5)

        # Submit button
        self.run_button = tk.Button(self.main_frame, text="Run Tests", command=self.start_test_thread)
        self.run_button.pack(pady=10)

        # Extra Tab - Additional Controls
        tk.Label(self.extra_tab, text="Select Path:").pack(pady=5)
        self.filepath_var = tk.StringVar()
        self.filepath_dropdown = ttk.Combobox(self.extra_tab, textvariable=self.filepath_var, values=self.options, state="readonly")
        self.filepath_dropdown.pack(pady=5)
        
        tk.Label(self.extra_tab, text="Select Attenuation Setting:").pack(pady=5)
        self.gain_var = tk.StringVar()
        self.gain_dropdown = ttk.Combobox(self.extra_tab, textvariable=self.gain_var, values=[i for i in range(0, 32, 1)], state="readonly")
        self.gain_dropdown.pack(pady=5)
        
        tk.Label(self.extra_tab, text="Select Measurement Type:").pack(pady=5)
        self.measurement_var = tk.StringVar()
        self.measurement_dropdown = ttk.Combobox(self.extra_tab, textvariable=self.measurement_var, values=["S22", "S21", "S11"], state="readonly")
        self.measurement_dropdown.pack(pady=5)

        # Submit button
        self.run_tool_button = tk.Button(self.extra_tab, text="Swap to State", command=self.start_tool_thread)
        self.run_tool_button.pack(pady=10)

        self.turn_fetts_off_button = tk.Button(self.extra_tab, text="Turn FETTs Off", command=self.start_turn_fetts_off_thread)
        self.turn_fetts_off_button.pack(pady=10)

        self.turn_fetts_on_button = tk.Button(self.extra_tab, text="Turn FETTs On", command=self.start_turn_fetts_on_thread)
        self.turn_fetts_on_button.pack(pady=10)

        if sim_mode:
            self.mocked_test = MockedTest(42)
        else:
            self.pa_module_test_manager = PaModuleTestManager(sim=False)
        
        # Start log monitoring loop
        self.monitor_log_queue()

    def turn_fetts_off(self):
        self.pa_module_test_manager.daq.disable_rf()

    def start_turn_fetts_off_thread(self):
        turn_fetts_off_thread = threading.Thread(target=self.turn_fetts_off, daemon=True)
        turn_fetts_off_thread.start()

    def turn_fetts_on(self):
        self.pa_module_test_manager.daq.enable_rf()

    def start_turn_fetts_on_thread(self):
        turn_fetts_off_thread = threading.Thread(target=self.turn_fetts_on, daemon=True)
        turn_fetts_off_thread.start()

    def monitor_log_queue(self):
        """ Continuously checks the log queue and updates the GUI log """
        while not log_queue.empty():
            message = log_queue.get()
            self.update_log(message)
        self.root.after(100, self.monitor_log_queue)  # Run this method every 100ms

    def run_tests(self):
        self.notebook.tab(1, state="disabled")  # Disable Extra Tab

        serial_number = self.sn_entry.get().strip()
        if not serial_number:
            self.update_log("Error: Serial Number is required.")
            self.notebook.tab(1, state="normal")  # Re-enable Extra Tab if an error occurs
            return
        
        user_defined_dir = self.dir_entry.get().strip()
        if not user_defined_dir:
            self.update_log("Error: Directory is required.")
            self.notebook.tab(1, state="normal")

        configure_logging(serial_number)
        self.update_status("Running...", "red")
        selected_option = self.dropdown_var.get()
        bin = selected_option.split(" ")
        selected_option = bin[0]
        checkbox1_state = self.checkbox1_var.get()
        checkbox2_state = self.checkbox2_var.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"[{timestamp}] Running tests... SN: {serial_number}, Selected: {selected_option}, Checkbox 1: {checkbox1_state}, Checkbox 2: {checkbox2_state}"
        log_message(message)
        print(message)
        
        if self.sim_mode:
            self.mocked_test.run_tests()
        else:
            # THis is for the results path creation i wanted to see it first to make sure it was working
            self.pa_module_test_manager.scribe.new_sno(serial_number, user_defined_dir)
            self.pa_module_test_manager.run_and_process_tests(selected_option, sno=serial_number, sig_a_tests=checkbox1_state, na_tests=checkbox2_state)


        log_message("Tests completed.")
        self.update_status("Idle", "blue")
        self.notebook.tab(1, state="normal")  # Re-enable Extra Tab
        print("Tests completed.")

    def start_tool_thread(self):
        tool_thread = threading.Thread(target=self.run_tools, daemon=True)
        tool_thread.start()

    def run_tools(self):
        # This disables the tab state so that when the tool is running you cant run a test at  the same time
        self.notebook.tab(0, state="disabled")
        selected_option = self.filepath_var.get()
        bin = selected_option.split(" ")
        selected_option = bin[0]
        gain_setting = int(self.gain_var.get())
        measurement_type = self.measurement_var.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] Running tools... Selected: {selected_option}, Gain: {gain_setting}, Measurement: {measurement_type}"
        log_message(message)
        print(message)
        self.pa_module_test_manager.run_state_process(selected_option, gain_setting, measurement_type)
        # This reenables it
        self.notebook.tab(0, state="normal")

    def start_test_thread(self):
        self.test_thread = threading.Thread(target=self.run_tests, daemon=True)
        self.test_thread.start()

    def turn_fetts_off(self):
        self.pa_module_test_manager.daq.disable_rf()

    def start_turn_fetts_off_thread(self):
        turn_fetts_off_thread = threading.Thread(target=self.turn_fetts_off, daemon=True)
        turn_fetts_off_thread.start()

    def update_status(self, text, color):
        self.status_label.config(text=f"Status: {text}", fg=color)
    
    def update_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, str(message) + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

if __name__ == "__main__":
    import sys
    try:
        root = tk.Tk()
        app = OscarPaModuleGUI(root)
        root.mainloop()
    except Exception as e:
        root.destroy()
        sys.exit()
        print(e)
