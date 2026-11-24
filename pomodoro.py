import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
import threading
import time

# Suppress Pygame welcome banner
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

try:
    import pygame
except ImportError:
    pygame = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from plyer import notification
except ImportError:
    notification = None


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("650x640")  # Window size for resolution
        self.root.config(bg="#1E1E2E")

        self.checkmark = 0
        self.total_work_time = 0
        self.total_break_time = 0
        self.pomodoro_count = 0
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.end_time = 0.0
        self.after_id = None
        self.timer_mode = "work"  # Tracks 'work' or 'break' mode
        self.task = ""            # Default task name
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60

        # Initialize pygame mixer safely
        self.audio_available = False
        if pygame:
            try:
                pygame.mixer.init()
                self.audio_available = True
            except Exception as e:
                print(f"Warning: Audio mixer initialization failed ({e}). Running without audio.")

        # Initialize pyttsx3 safely
        self.tts_available = False
        self.engine = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.tts_available = True
            except Exception as e:
                print(f"Warning: TTS engine initialization failed ({e}). Voice alerts disabled.")

        # Determine best available font family for Linux/cross-platform
        base_font = "Helvetica"
        try:
            import tkinter.font as tkfont
            available_fonts = set(tkfont.families(self.root))
            for candidate in ("Ubuntu", "DejaVu Sans", "Fira Sans", "Segoe UI", "Helvetica", "Arial"):
                if candidate in available_fonts:
                    base_font = candidate
                    break
        except Exception:
            base_font = "Helvetica"

        # Fonts
        self.font_large = (base_font, 72, "bold")
        self.font_medium = (base_font, 14)
        self.font_small = (base_font, 12)

        # Task Label and Entry
        self.task_label = tk.Label(root, text="Task:", font=self.font_medium, bg="#1E1E2E", fg="#D8DEE9")
        self.task_label.pack(pady=(15, 5))
        self.task_entry = tk.Entry(root, width=25, font=self.font_medium, bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.task_entry.pack(pady=(0, 7))

        # Button to Set Task
        self.set_task_button = tk.Button(root, text="Set Task", command=self.set_task, font=self.font_medium, bg="#FFC125", fg="#1E1E2E")
        self.set_task_button.pack(pady=(0, 7))

        # Current Task Display
        self.current_task_label = tk.Label(root, text="", font=self.font_medium, bg="#1E1E2E", fg="#D8DEE9")
        self.current_task_label.pack(pady=(2, 2))

        # Timer Label
        self.timer_label = tk.Label(root, text="25:00", font=self.font_large, bg="#1E1E2E", fg="#D8DEE9")
        self.timer_label.pack(pady=5)

        # Control Buttons
        self.button_frame = tk.Frame(root, bg="#1E1E2E")
        self.button_frame.pack(pady=15)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, font=self.font_medium, bg="#7FFF00", fg="#1E1E2E", width=10)
        self.start_button.grid(row=0, column=0, padx=10)
        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_timer, font=self.font_medium, bg="#FFA500", fg="#1E1E2E", width=10)
        self.pause_button.grid(row=0, column=1, padx=10)
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, font=self.font_medium, bg="#5E81AC", fg="#1E1E2E", width=10)
        self.reset_button.grid(row=0, column=2, padx=10)

        # Music Selection & Controls
        self.music_file = None
        self.bundled_music = []
        music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
        if os.path.isdir(music_dir):
            for fname in sorted(os.listdir(music_dir)):
                if fname.lower().endswith((".mp3", ".wav")):
                    self.bundled_music.append(os.path.join(music_dir, fname))

        if self.bundled_music:
            self.music_file = self.bundled_music[0]

        self.music_frame = tk.Frame(root, bg="#1E1E2E")
        self.music_frame.pack(pady=5)

        self.music_button = tk.Button(self.music_frame, text="Select Music", command=self.load_music, font=self.font_medium, bg="#A3BE8C", fg="#1E1E2E")
        self.music_button.grid(row=0, column=0, padx=5)

        self.clear_music_button = tk.Button(self.music_frame, text="Clear Music", command=self.clear_music, font=self.font_medium, bg="#BF616A", fg="#ECEFF4")
        self.clear_music_button.grid(row=0, column=1, padx=5)

        initial_track = os.path.basename(self.music_file) if self.music_file else "None (Silent)"
        self.music_label = tk.Label(root, text=f"Track: {initial_track}", font=self.font_small, bg="#1E1E2E", fg="#A3BE8C")
        self.music_label.pack(pady=(0, 5))

        # Custom Time Inputs
        self.custom_time_frame = tk.Frame(root, bg="#1E1E2E")
        self.custom_time_frame.pack(pady=5)

        self.work_time_label = tk.Label(self.custom_time_frame, text="Work Duration (min):", font=self.font_small, bg="#1E1E2E", fg="#D8DEE9")
        self.work_time_label.grid(row=0, column=0, padx=5)
        self.work_time_entry = tk.Entry(self.custom_time_frame, width=5, font=self.font_small, bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.work_time_entry.grid(row=0, column=1, padx=5)
        self.work_time_entry.insert(0, "25")

        self.break_time_label = tk.Label(self.custom_time_frame, text="Break Duration (min):", font=self.font_small, bg="#1E1E2E", fg="#D8DEE9")
        self.break_time_label.grid(row=0, column=2, padx=5)
        self.break_time_entry = tk.Entry(self.custom_time_frame, width=5, font=self.font_small, bg="#4C566A", fg="#D8DEE9", insertbackground="#D8DEE9")
        self.break_time_entry.grid(row=0, column=3, padx=5)
        self.break_time_entry.insert(0, "5")

        # Statistics & Reset Stats
        self.stats_frame = tk.Frame(root, bg="#1E1E2E")
        self.stats_frame.pack(pady=5)

        self.stats_label = tk.Label(self.stats_frame, text="Pomodoros Completed: 0\nTotal Work Time: 0 mins\nTotal Break Time: 0 mins", font=self.font_small, bg="#1E1E2E", fg="#D8DEE9")
        self.stats_label.pack(pady=(0, 4))

        self.reset_stats_button = tk.Button(self.stats_frame, text="Reset Stats", command=self.reset_stats, font=self.font_small, bg="#4C566A", fg="#D8DEE9")
        self.reset_stats_button.pack()

        # Custom Message Label
        self.custom_message_label = tk.Label(root, text="Made with <3, by Rajat!", font=self.font_small, bg="#1E1E2E", fg="#F8F8F2")
        self.custom_message_label.pack(pady=10)

        # Clean cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def cancel_timer(self):
        """Cancels any pending after() scheduled callback to prevent race conditions."""
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def tick(self):
        """Precision tick driven by wall-clock time (time.time()) to eliminate clock drift."""
        if not self.running:
            return

        remaining = int(round(self.end_time - time.time()))
        if remaining < 0:
            remaining = 0
        self.remaining_time = remaining

        mins, secs = divmod(remaining, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        self.timer_label.config(text=time_format)

        if remaining <= 0:
            self.cancel_timer()
            if self.timer_mode == "work":
                self.complete_task()
            else:
                self.end_break()
        else:
            # Poll at 200ms intervals to guarantee accurate second updates without drift
            self.after_id = self.root.after(200, self.tick)

    def speak_async(self, text):
        """Speaks text in a non-blocking background daemon thread to prevent UI freezing."""
        if not self.tts_available or not self.engine:
            return

        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")

        threading.Thread(target=_speak, daemon=True).start()

    def send_notification(self, title, message):
        """Sends a desktop notification safely on Linux."""
        if not notification:
            return
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5
            )
        except Exception as e:
            print(f"Notification error: {e}")

    def set_task(self):
        task_input = self.task_entry.get().strip()
        if not task_input:
            messagebox.showwarning("Warning", "Task name cannot be empty.")
            return
        self.task = task_input
        self.task_entry.config(state='disabled')
        self.set_task_button.config(state='disabled')
        self.current_task_label.config(text=f"Current Task: {self.task}")

    def start_timer(self):
        if not self.running and not self.paused:
            # Auto-set task if user typed in entry but did not click 'Set Task'
            if not self.task:
                task_input = self.task_entry.get().strip()
                if task_input:
                    self.set_task()
                else:
                    messagebox.showwarning("Warning", "Please set a task before starting the timer.")
                    return

            try:
                self.work_duration = int(self.work_time_entry.get().strip()) * 60
                self.break_duration = int(self.break_time_entry.get().strip()) * 60
                if self.work_duration <= 0 or self.break_duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter positive integers for work and break durations.")
                return

            self.running = True
            self.timer_mode = "work"
            self.remaining_time = self.work_duration
            self.end_time = time.time() + self.remaining_time
            self.cancel_timer()
            self.tick()

        elif self.paused:
            self.running = True
            self.paused = False
            self.end_time = time.time() + self.remaining_time
            self.cancel_timer()
            self.tick()

    def pause_timer(self):
        if self.running:
            self.cancel_timer()
            self.remaining_time = max(0, int(round(self.end_time - time.time())))
            self.running = False
            self.paused = True

    def reset_timer(self):
        """Resets the active timer countdown without erasing lifetime stats."""
        self.cancel_timer()
        self.running = False
        self.paused = False
        self.timer_mode = "work"
        try:
            work_mins = int(self.work_time_entry.get().strip())
            self.work_duration = work_mins * 60
        except ValueError:
            work_mins = 25
            self.work_duration = 25 * 60

        self.remaining_time = self.work_duration
        self.timer_label.config(text=f"{work_mins:02d}:00")
        self.task = ""
        self.task_entry.config(state='normal')
        self.task_entry.delete(0, tk.END)
        self.set_task_button.config(state='normal')
        self.current_task_label.config(text="")
        self.stop_music()

    def reset_stats(self):
        """Explicitly resets lifetime pomodoro statistics."""
        self.update_stats(0, 0, 0, 0, reset=True)

    def countdown(self, count):
        """Maintains API compatibility while delegating to wall-clock tick()."""
        self.timer_mode = "work"
        self.remaining_time = count
        self.end_time = time.time() + count
        self.cancel_timer()
        self.tick()

    def countdown_break(self, count):
        """Maintains API compatibility while delegating to wall-clock tick()."""
        self.timer_mode = "break"
        self.remaining_time = count
        self.end_time = time.time() + count
        self.cancel_timer()
        self.tick()

    def complete_task(self):
        self.checkmark += 1
        try:
            self.total_work_time += int(self.work_time_entry.get().strip())
        except ValueError:
            self.total_work_time += 25
        self.pomodoro_count += 1

        self.speak_async(f"Task {self.task} completed. Take a break.")
        self.send_notification("Pomodoro Timer", "Work session completed. Time for a break!")
        self.update_stats(self.total_work_time, self.total_break_time, self.pomodoro_count, 0)
        self.start_break()

    def start_break(self):
        self.timer_mode = "break"
        if self.music_file and self.audio_available and pygame:
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(loops=-1)
            except Exception as e:
                print(f"Warning: Could not play music ({e})")

        self.countdown_break(self.break_duration)

    def end_break(self):
        self.stop_music()
        try:
            self.total_break_time += int(self.break_time_entry.get().strip())
        except ValueError:
            self.total_break_time += 5

        self.speak_async("Break is over. Start focusing.")
        self.send_notification("Pomodoro Timer", "Break is over. Time to focus!")
        self.update_stats(self.total_work_time, self.total_break_time, self.pomodoro_count, 0)
        self.running = False
        self.timer_mode = "work"
        self.start_timer()  # Automatically start next work session

    def load_music(self):
        music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
        initial_dir = music_dir if os.path.isdir(music_dir) else os.getcwd()
        selected = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        if selected:
            self.music_file = selected
            self.music_label.config(text=f"Track: {os.path.basename(selected)}")

    def clear_music(self):
        self.music_file = None
        self.stop_music()
        self.music_label.config(text="Track: None (Silent)")

    def stop_music(self):
        if self.audio_available and pygame:
            try:
                pygame.mixer.music.stop()
            except Exception as e:
                print(f"Warning: Could not stop music ({e})")

    def update_stats(self, work_time, break_time, pomodoros, completed=0, reset=False):
        if reset:
            self.total_work_time = 0
            self.total_break_time = 0
            self.pomodoro_count = 0
        stats_text = (
            f"Pomodoros Completed: {self.pomodoro_count}\n"
            f"Total Work Time: {self.total_work_time} mins\n"
            f"Total Break Time: {self.total_break_time} mins"
        )
        self.stats_label.config(text=stats_text)

    def on_close(self):
        self.running = False
        self.cancel_timer()
        self.stop_music()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
