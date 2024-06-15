import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import pyttsx3
import os

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("800x600")  # Increased window size for higher resolution
        self.root.config(bg="#2E3440")

        self.checkmark = 0
        self.total_mins = 0
        self.running = False

        # Initialize pygame mixer
        pygame.mixer.init()

        # Initialize pyttsx3
        self.engine = pyttsx3.init()

        # Task Label and Entry
        self.task_label = tk.Label(root, text="Task:", font=("Helvetica", 14), bg="#2E3440", fg="#D8DEE9")
        self.task_label.pack(pady=(30, 10))
        self.task_entry = tk.Entry(root, width=50, font=("Helvetica", 14), bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.task_entry.pack(pady=(0, 20))

        # Button to Set Task
        self.set_task_button = tk.Button(root, text="Set Task", command=self.set_task, font=("Helvetica", 14), bg="#A3BE8C", fg="#2E3440")
        self.set_task_button.pack(pady=(0, 20))

        # Current Task Display
        self.current_task_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#2E3440", fg="#D8DEE9")
        self.current_task_label.pack(pady=(0, 20))

        # Timer Label
        self.timer_label = tk.Label(root, text="25:00", font=("Helvetica", 72), bg="#2E3440", fg="#D8DEE9")
        self.timer_label.pack(pady=20)

        # Control Buttons
        self.button_frame = tk.Frame(root, bg="#2E3440")
        self.button_frame.pack(pady=20)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, font=("Helvetica", 14), bg="#88C0D0", fg="#2E3440", width=10)
        self.start_button.grid(row=0, column=0, padx=15)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_timer, font=("Helvetica", 14), bg="#BF616A", fg="#2E3440", width=10)
        self.stop_button.grid(row=0, column=1, padx=15)
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, font=("Helvetica", 14), bg="#5E81AC", fg="#2E3440", width=10)
        self.reset_button.grid(row=0, column=2, padx=15)

        # Music Selection Button
        self.music_button = tk.Button(root, text="Select Music", command=self.load_music, font=("Helvetica", 14), bg="#A3BE8C", fg="#2E3440")
        self.music_button.pack(pady=30)

        # Initial music file
        self.music_file = None

    def set_task(self):
        self.task = self.task_entry.get()
        self.task_entry.config(state='disabled')
        self.set_task_button.config(state='disabled')
        self.current_task_label.config(text=f"Current Task: {self.task}")

    def start_timer(self):
        if not self.running and self.task_entry.get() != "":
            self.running = True
            self.countdown(25 * 60)
        elif not self.running:
            messagebox.showwarning("Warning", "Please set a task before starting the timer.")

    def stop_timer(self):
        self.running = False

    def reset_timer(self):
        self.running = False
        self.timer_label.config(text="25:00")
        self.task_entry.config(state='normal')
        self.set_task_button.config(state='normal')
        self.current_task_label.config(text="")

    def countdown(self, count):
        mins, secs = divmod(count, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        self.timer_label.config(text=time_format)
        if self.running:
            if count > 0:
                self.root.after(1000, self.countdown, count-1)
            else:
                self.complete_task()

    def complete_task(self):
        self.checkmark += 1
        self.total_mins += 25
        self.engine.say(f"Task {self.task} completed. Take a break.")
        self.engine.runAndWait()
        self.start_break()

    def start_break(self):
        if self.music_file:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(loops=-1)

        if self.checkmark < 6:
            self.countdown_break(5 * 60)
        else:
            self.checkmark = 0
            self.countdown_break(15 * 60)

    def countdown_break(self, count):
        mins, secs = divmod(count, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        self.timer_label.config(text=time_format)
        if self.running:
            if count > 0:
                self.root.after(1000, self.countdown_break, count-1)
            else:
                self.end_break()

    def end_break(self):
        self.stop_music()
        self.engine.say("Break is over. Start focusing.")
        self.engine.runAndWait()
        self.reset_timer()

    def load_music(self):
        self.music_file = filedialog.askopenfilename(filetypes=(("Music Files", "*.mp3;*.wav;*.opus;*.m4a"),))

    def stop_music(self):
        pygame.mixer.music.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
