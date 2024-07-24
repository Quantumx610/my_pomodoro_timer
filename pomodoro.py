import tkinter as tk
from tkinter import messagebox, filedialog
from plyer import notification
import pygame
import pyttsx3
import os
import sys
class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("650x600")  # Increased window size for higher resolution
        self.root.config(bg="#1E1E2E")

        self.checkmark = 0
        self.total_work_time = 0
        self.total_break_time = 0
        self.pomodoro_count = 0
        self.running = False
        self.paused = False
        self.remaining_time = 0

        # Initialize pygame mixer
        pygame.mixer.init()

        # Initialize pyttsx3
        self.engine = pyttsx3.init()

       # Custom Fonts
        self.font_large = ("Segoe UI", 72)
        self.font_medium = ("Segoe UI", 14)
        self.font_small = ("Segoe UI", 12) 

        # Task Label and Entry
        self.task_label = tk.Label(root, text="Task:", font=("Helvetica", 14), bg="#1E1E2E", fg="#D8DEE9")
        self.task_label.pack(pady=(20, 5))
        self.task_entry = tk.Entry(root, width=25, font=("Helvetica", 14), bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.task_entry.pack(pady=(0, 7))

        # Button to Set Task
        self.set_task_button = tk.Button(root, text="Set Task", command=self.set_task, font=("Helvetica", 14), bg="#FFC125", fg="#1E1E2E")
        self.set_task_button.pack(pady=(0, 7))

        # Current Task Display
        self.current_task_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#1E1E2E", fg="#D8DEE9")
        self.current_task_label.pack(pady=(3, 3))

        # Timer Label
        self.timer_label = tk.Label(root, text="25:00", font=("Helvetica", 72), bg="#1E1E2E", fg="#D8DEE9")
        self.timer_label.pack(pady=10)

        # Control Buttons
        self.button_frame = tk.Frame(root, bg="#1E1E2E")
        self.button_frame.pack(pady=20)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, font=("Helvetica", 14), bg="#7FFF00", fg="#1E1E2E", width=10)
        self.start_button.grid(row=0, column=0, padx=10)
        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_timer, font=("Helvetica", 14), bg="#FFA500", fg="#1E1E2E", width=10)
        self.pause_button.grid(row=0, column=1, padx=10)
        # self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_timer, font=("Helvetica", 14), bg="#BF616A", fg="#1E1E2E", width=10)
        # self.stop_button.grid(row=0, column=2, padx=10)
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, font=("Helvetica", 14), bg="#5E81AC", fg="#1E1E2E", width=10)
        self.reset_button.grid(row=0, column=2, padx=15)

        # Music Selection Button
        self.music_button = tk.Button(root, text="Select Music", command=self.load_music, font=("Helvetica", 14), bg="#A3BE8C", fg="#1E1E2E")
        self.music_button.pack(pady=10)

        # Custom Time Inputs
        self.custom_time_frame = tk.Frame(root, bg="#1E1E2E")
        self.custom_time_frame.pack(pady=5)

        self.work_time_label = tk.Label(self.custom_time_frame, text="Work Duration (min):", font=("Helvetica", 12), bg="#1E1E2E", fg="#D8DEE9")
        self.work_time_label.grid(row=0, column=0, padx=5)
        self.work_time_entry = tk.Entry(self.custom_time_frame, width=5, font=("Helvetica", 12), bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.work_time_entry.grid(row=0, column=1, padx=5)
        self.work_time_entry.insert(0, "25")

        self.break_time_label = tk.Label(self.custom_time_frame, text="Break Duration (min):", font=("Helvetica", 12), bg="#1E1E2E", fg="#D8DEE9")
        self.break_time_label.grid(row=0, column=2, padx=5)
        self.break_time_entry = tk.Entry(self.custom_time_frame, width=5, font=("Helvetica", 12), bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.break_time_entry.grid(row=0, column=3, padx=5)
        self.break_time_entry.insert(0, "5")

        # Statistics
        self.stats_label = tk.Label(root, text="Pomodoros Completed: 0\nTotal Work Time: 0 mins\nTotal Break Time: 0 mins", font=("Helvetica", 12), bg="#1E1E2E", fg="#D8DEE9")
        self.stats_label.pack(pady=10)

        # Custom Message Label
        self.custom_message_label = tk.Label(root, text="Made with <3, by Rajat!", font=self.font_small, bg="#1E1E2E", fg="#F8F8F2")
        self.custom_message_label.pack(pady=10)

        # Initial music file
        self.music_file = None

    def set_task(self):
        self.task = self.task_entry.get()
        self.task_entry.config(state='disabled')
        self.set_task_button.config(state='disabled')
        self.current_task_label.config(text=f"Current Task: {self.task}")

    def start_timer(self):
        if not self.running and not self.paused and self.task_entry.get() != "":
            self.running = True
            self.work_duration = int(self.work_time_entry.get()) * 60
            self.break_duration = int(self.break_time_entry.get()) * 60
            self.countdown(self.work_duration)
        elif self.paused:
            self.running = True
            self.paused = False
            self.countdown(self.remaining_time)
        elif not self.running:
            messagebox.showwarning("Warning", "Please set a task before starting the timer.")

    def pause_timer(self):
        if self.running:
            self.running = False
            self.paused = True

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.timer_label.config(text="25:00")
        self.task_entry.config(state='normal')
        self.set_task_button.config(state='normal')
        self.current_task_label.config(text="")
        self.update_stats(0, 0, 0, 0, True)

    def countdown(self, count):
        mins, secs = divmod(count, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        self.timer_label.config(text=time_format)
        self.remaining_time = count

        if self.running:
            if count > 0:
                self.root.after(1000, self.countdown, count-1)
            else:
                self.complete_task()

    def complete_task(self):
        self.checkmark += 1
        self.total_work_time += int(self.work_time_entry.get())
        self.pomodoro_count += 1
        self.engine.say(f"Task {self.task} completed. Take a break.")
        self.engine.runAndWait()
        notification.notify(
            title="Pomodoro Timer",
            message="Work session completed. Time for a break!",
            timeout=5
        )
        self.update_stats(self.total_work_time, self.total_break_time, self.pomodoro_count, 0)
        self.start_break()

    def start_break(self):
        if self.music_file:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(loops=-1)

        self.countdown_break(self.break_duration)

    def countdown_break(self, count):
        mins, secs = divmod(count, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        self.timer_label.config(text=time_format)
        self.remaining_time = count

        if self.running:
            if count > 0:
                self.root.after(1000, self.countdown_break, count-1)
            else:
                self.end_break()

    def end_break(self):
        self.stop_music()
        self.total_break_time += int(self.break_time_entry.get())
        self.engine.say("Break is over. Start focusing.")
        self.engine.runAndWait()
        notification.notify(
            title="Pomodoro Timer",
            message="Break is over. Time to focus!",
            timeout=5
        )
        self.update_stats(self.total_work_time, self.total_break_time, self.pomodoro_count, 0)
        self.running = False
        self.start_timer()  # Automatically start the next work session

    def load_music(self):
        self.music_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])

    def stop_music(self):
        pygame.mixer.music.stop()

    def update_stats(self, work_time, break_time, pomodoros, completed, reset=False):
        if reset:
            self.total_work_time = 0
            self.total_break_time = 0
            self.pomodoro_count = 0
        stats_text = f"Pomodoros Completed: {self.pomodoro_count}\nTotal Work Time: {self.total_work_time} mins\nTotal Break Time: {self.total_break_time} mins"
        self.stats_label.config(text=stats_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
