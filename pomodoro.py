import tkinter as tk
from tkinter import messagebox, filedialog
from plyer import notification
import pygame
import pyttsx3

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("600x610")  # Increased window size for higher resolution
        self.root.config(bg="#1E1E1E")  # Dark background to match Windows 11

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

        # Task Label and Entry
        self.task_label = tk.Label(root, text="Task:", font=("Segoe UI", 14), bg="#1E1E1E", fg="#FFFFFF")
        self.task_label.pack(pady=(20, 5))
        self.task_entry = tk.Entry(root, width=30, font=("Segoe UI", 13), bg="#3C3C3C", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.task_entry.pack(pady=(0, 10))

        # Button to Set Task
        self.set_task_button = tk.Button(root, text="Set Task", command=self.set_task, font=("Segoe UI", 12), bg="#0078D4", fg="#FFFFFF", relief='flat', overrelief='ridge')
        self.set_task_button.pack(pady=(0, 10))

        # Current Task Display
        self.current_task_label = tk.Label(root, text="", font=("Segoe UI", 12), bg="#1E1E1E", fg="#FFFFFF")
        self.current_task_label.pack(pady=(0, 7))

        # Timer Label
        self.timer_label = tk.Label(root, text="25:00", font=("Segoe UI", 65), bg="#1E1E1E", fg="#FFFFFF")
        self.timer_label.pack(pady=5)

        # Control Buttons
        self.button_frame = tk.Frame(root, bg="#1E1E1E")
        self.button_frame.pack(pady=10)

        button_style = {"font": ("Segoe UI", 12), "width": 10, "relief": "flat", "overrelief": "ridge"}

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, bg="#0078D4", fg="#FFFFFF", **button_style)
        self.start_button.grid(row=0, column=0, padx=10)
        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_timer, bg="#EBCB8B", fg="#1E1E1E", **button_style)
        self.pause_button.grid(row=0, column=1, padx=10)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_timer, bg="#BF616A", fg="#FFFFFF", **button_style)
        self.stop_button.grid(row=0, column=2, padx=10)
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, bg="#5E81AC", fg="#FFFFFF", **button_style)
        self.reset_button.grid(row=0, column=3, padx=10)

        # Music Selection Button
        self.music_button = tk.Button(root, text="Select Music", command=self.load_music, font=("Segoe UI", 12), bg="#800080", fg="#FFFFFF", relief='flat', overrelief='ridge')
        self.music_button.pack(pady=15)

        # Custom Time Inputs
        self.custom_time_frame = tk.Frame(root, bg="#1E1E1E")
        self.custom_time_frame.pack(pady=5)

        self.work_time_label = tk.Label(self.custom_time_frame, text="Work Duration (min):", font=("Segoe UI", 12), bg="#1E1E1E", fg="#FFFFFF")
        self.work_time_label.grid(row=0, column=0, padx=5)
        self.work_time_entry = tk.Entry(self.custom_time_frame, width=5, font=("Segoe UI", 12), bg="#3C3C3C", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.work_time_entry.grid(row=0, column=1, padx=5)
        self.work_time_entry.insert(0, "25")

        self.break_time_label = tk.Label(self.custom_time_frame, text="Break Duration (min):", font=("Segoe UI", 12), bg="#1E1E1E", fg="#FFFFFF")
        self.break_time_label.grid(row=0, column=2, padx=5)
        self.break_time_entry = tk.Entry(self.custom_time_frame, width=5, font=("Segoe UI", 12), bg="#3C3C3C", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.break_time_entry.grid(row=0, column=3, padx=5)
        self.break_time_entry.insert(0, "5")

        # Statistics
        self.stats_label = tk.Label(root, text="Pomodoros Completed: 0\nTotal Work Time: 0 mins\nTotal Break Time: 0 mins", font=("Segoe UI", 12), bg="#1E1E1E", fg="#FFFFFF")
        self.stats_label.pack(pady=15)

        # Custom Message Label
        self.custom_message_label = tk.Label(root, text="Made with <3, by Rajat", font=("Segoe UI", 8), bg="#1E1E1E", fg="#FFFFFF")
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

    def stop_timer(self):
        self.running = False
        self.paused = False
        self.timer_label.config(text="25:00")

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.timer_label.config(text="25:00")
        self.task_entry.config(state='normal')
        self.set_task_button.config(state='normal')
        self.current_task_label.config(text="")
        self.update_stats(0, 0, 0, 0, True)

        #stops music after reset
        self.stop_music()

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
        self.start_timer()

    def stop_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def load_music(self):
        self.music_file = filedialog.askopenfilename(title="Select Music File", filetypes=(("mp3 Files", "*.mp3"), ("wav Files", "*.wav")))

    def update_stats(self, work_time, break_time, pomodoros, reset=0, reset_all=False):
        if reset_all:
            self.checkmark = 0
            self.total_work_time = 0
            self.total_break_time = 0
            self.pomodoro_count = 0
        stats_text = f"Pomodoros Completed: {self.pomodoro_count}\nTotal Work Time: {self.total_work_time} mins\nTotal Break Time: {self.total_break_time} mins"
        self.stats_label.config(text=stats_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
