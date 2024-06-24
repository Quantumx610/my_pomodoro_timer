import tkinter as tk
from tkinter import messagebox, filedialog
from plyer import notification
import pygame
import pyttsx3

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("900x650")  # Increased window size for higher resolution
        self.root.config(bg="#1E1E2E")  # Background color

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
        self.task_label = tk.Label(root, text="Task:", font=self.font_medium, bg="#1E1E2E", fg="#F8F8F2")
        self.task_label.pack(pady=(20, 5))
        self.task_entry = tk.Entry(root, width=50, font=self.font_medium, bg="#2E2E3E", fg="#F8F8F2", insertbackground="#F8F8F2", relief="flat")
        self.task_entry.pack(pady=(0, 7))

        # Button to Set Task
        self.set_task_button = tk.Button(root, text="Set Task", command=self.set_task, font=self.font_medium, bg="#6272A4", fg="#1E1E2E", relief="flat", bd=0, activebackground="#44475A", activeforeground="#F8F8F2")
        self.set_task_button.pack(pady=(0, 7))

        # Current Task Display
        self.current_task_label = tk.Label(root, text="", font=self.font_medium, bg="#1E1E2E", fg="#F8F8F2")
        self.current_task_label.pack(pady=(3, 3))

        # Timer Label
        self.timer_label = tk.Label(root, text="25:00", font=self.font_large, bg="#1E1E2E", fg="#F8F8F2")
        self.timer_label.pack(pady=10)   

        # Control Buttons
        self.button_frame = tk.Frame(root, bg="#1E1E2E")
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, font=self.font_medium, bg="#50FA7B", fg="#1E1E2E", width=10, relief="flat", bd=0, activebackground="#282A36", activeforeground="#F8F8F2")
        self.start_button.grid(row=0, column=0, padx=10)
        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_timer, font=self.font_medium, bg="#FFB86C", fg="#1E1E2E", width=10, relief="flat", bd=0, activebackground="#282A36", activeforeground="#F8F8F2")
        self.pause_button.grid(row=0, column=1, padx=10)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_timer, font=self.font_medium, bg="#FF5555", fg="#1E1E2E", width=10, relief="flat", bd=0, activebackground="#282A36", activeforeground="#F8F8F2")
        self.stop_button.grid(row=0, column=2, padx=10)
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, font=self.font_medium, bg="#BD93F9", fg="#1E1E2E", width=10, relief="flat", bd=0, activebackground="#282A36", activeforeground="#F8F8F2")
        self.reset_button.grid(row=0, column=3, padx=10)

        # Music Selection Button
        self.music_button = tk.Button(root, text="Select Music", command=self.load_music, font=self.font_medium, bg="#6272A4", fg="#1E1E2E", relief="flat", bd=0, activebackground="#44475A", activeforeground="#F8F8F2")
        self.music_button.pack(pady=10)

        # Custom Time Inputs
        self.custom_time_frame = tk.Frame(root, bg="#1E1E2E")
        self.custom_time_frame.pack(pady=5)

        self.work_time_label = tk.Label(self.custom_time_frame, text="Work Duration (min):", font=self.font_small, bg="#1E1E2E", fg="#F8F8F2")
        self.work_time_label.grid(row=0, column=0, padx=5)
        self.work_time_entry = tk.Entry(self.custom_time_frame, width=5, font=self.font_small, bg="#2E2E3E", fg="#F8F8F2", insertbackground="#F8F8F2", relief="flat")
        self.work_time_entry.grid(row=0, column=1, padx=5)
        self.work_time_entry.insert(0, "25")

        self.break_time_label = tk.Label(self.custom_time_frame, text="Break Duration (min):", font=self.font_small, bg="#1E1E2E", fg="#F8F8F2")
        self.break_time_label.grid(row=0, column=2, padx=5)
        self.break_time_entry = tk.Entry(self.custom_time_frame, width=5, font=self.font_small, bg="#2E2E3E", fg="#F8F8F2", insertbackground="#F8F8F2", relief="flat")
        self.break_time_entry.grid(row=0, column=3, padx=5)
        self.break_time_entry.insert(0, "5")

        # Statistics
        self.stats_label = tk.Label(root, text="Pomodoros Completed: 0\nTotal Work Time: 0 mins\nTotal Break Time: 0 mins", font=self.font_small, bg="#1E1E2E", fg="#F8F8F2")
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
        self.running = False
        self.paused = False
        self.checkmark += 1

        if self.checkmark % 2 != 0:
            self.pomodoro_count += 1
            self.total_work_time += int(self.work_time_entry.get())
            self.update_stats(self.total_work_time, self.total_break_time, self.pomodoro_count)
            notification.notify(
                title="Pomodoro Timer",
                message="Time for a break!",
                timeout=10
            )
            if self.music_file:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(loops=0)
            self.root.after(1000, self.countdown, self.break_duration)
        else:
            self.total_break_time += int(self.break_time_entry.get())
            self.update_stats(self.total_work_time, self.total_break_time, self.pomodoro_count)
            notification.notify(
                title="Pomodoro Timer",
                message="Break is over. Time to work!",
                timeout=10
            )
            if self.music_file:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(loops=0)
            self.root.after(1000, self.countdown, self.work_duration)

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
