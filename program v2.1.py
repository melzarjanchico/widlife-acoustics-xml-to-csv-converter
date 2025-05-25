import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from bs4 import BeautifulSoup
from tkinter.ttk import Progressbar

def process_files(input_folder, output_folder, status_label, progress_bar, progress_label, start_button):
    def task():
        status_label.config(text="Processing...", fg="blue")
        start_button.config(state=tk.DISABLED)
        progress_bar.config(value=0)
        progress_label.config(text="")
        root.update_idletasks()

        final_list = []
        file_list = os.listdir(input_folder)
        total_files = len(file_list)

        if total_files == 0:
            status_label.config(text="No files found in the folder!", fg="red")
            start_button.config(state=tk.NORMAL)
            return

        progress_bar.config(maximum=total_files)
        progress_bar.pack(pady=5)
        progress_label.pack(pady=5)

        for index, filename in enumerate(file_list, start=1):
            filepath = os.path.join(input_folder, filename)
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception as e:
                continue  # Skip unreadable files
                
            soup = BeautifulSoup(file_content, "xml")

            temp_raw = soup.find("TEMPERATURE")
            try:
                temp = float(temp_raw.text) / 100
            except:
                temp = "No Temp in XML"

            datetime_raw = soup.find("WavFileHandler", {"SamplingStartTimeLocal": True})
            try:
                datetime_string = datetime_raw["SamplingStartTimeLocal"].split("T")
                date, time = datetime_string[0], datetime_string[1]
            except:
                date, time = "No Date in XML", "No Time in XML"

            if temp == "No Temp in XML" and date == "No Date in XML" and time == "No Time in XML":
                continue

            try:
                filename_date = re.search(r'\.(.+?)\.log', filename).group(1)
            except:
                filename_date = "n/a"

            temp_list = [filename, filename_date, temp, date, time]
            final_list.append(temp_list)

            progress_bar.config(value=index)
            progress_percentage = (index / total_files) * 100
            progress_label.config(text=f"{progress_percentage:.2f}% completed")
            root.update_idletasks()

        if final_list:
            df = pd.DataFrame(final_list, columns=["FILENAME", "FILENAME_DATETIME", "TEMPERATURE", "SAMPLE_START_DATE", "SAMPLE_START_TIME"])
            extract_foldername = os.path.basename(input_folder)
            output_filename = os.path.join(output_folder, f"{extract_foldername}.csv")

            df.to_csv(output_filename, index=False)
            status_label.config(text="Processing complete!", fg="green")
            messagebox.showinfo("Success", f"Processing complete! File saved as {output_filename}")
        else:
            status_label.config(text="No valid data found!", fg="red")
        
        start_button.config(state=tk.NORMAL)
    
    threading.Thread(target=task, daemon=True).start()

def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_folder_var.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder_var.set(folder)

def start_processing():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Please select both input and output folders!")
        return

    process_files(input_folder, output_folder, status_label, progress_bar, progress_label, start_button)

# GUI setup
root = tk.Tk()
root.title("XML to CSV Converter")
root.geometry("500x400")

tk.Label(root, text="Input Folder:").pack(pady=5)
input_folder_var = tk.StringVar()
tk.Entry(root, textvariable=input_folder_var, width=50).pack()
tk.Button(root, text="Browse", command=select_input_folder).pack(pady=5)

tk.Label(root, text="Output Folder:").pack(pady=5)
output_folder_var = tk.StringVar()
tk.Entry(root, textvariable=output_folder_var, width=50).pack()
tk.Button(root, text="Browse", command=select_output_folder).pack(pady=5)

start_button = tk.Button(root, text="Start Processing", command=start_processing)
start_button.pack(pady=20)

progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress_label = tk.Label(root, text="", fg="black")
status_label = tk.Label(root, text="", fg="black")

status_label.pack(pady=5)

root.mainloop()