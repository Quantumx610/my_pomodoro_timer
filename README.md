# Pomodoro Timer

A focused productivity timer built with Python and Tkinter, designed around the Pomodoro Technique. Features dark-mode interface, audio playback during breaks, voice announcements, desktop notifications, and customizable intervals.

---

## Features

- **Dark Mode UI**: Minimalist aesthetic utilizing Nord-inspired colors.
- **Task Management**: Set and lock your current task during focus intervals.
- **Configurable Durations**: Customize work and break durations directly from the interface.
- **Audio for Breaks**: Load and play background music during break sessions.
- **Voice & Desktop Alerts**: Non-blocking voice announcements (`pyttsx3`) and native system desktop notifications (`plyer`).
- **Session Tracking**: Track completed pomodoro counts and total work/break minutes.
- **Cross-Platform**: Fully compatible with Linux (Pop!_OS, Ubuntu, Debian, Fedora, Arch) and Windows.

---

## Installation & Setup (Linux)

### 1. Install System Dependencies
On Ubuntu / Pop!_OS / Debian-based distributions, install the required packages for Tkinter, text-to-speech, and desktop notifications:

```bash
sudo apt update
sudo apt install -y python3-tk python3-venv espeak-ng libnotify-bin
```

*(On Fedora: `sudo dnf install python3-tkinter espeak-ng libnotify`)*  
*(On Arch: `sudo pacman -S tk espeak-ng libnotify`)*

### 2. Set Up Virtual Environment

```bash
# Clone the repository (if not already done)
git clone https://github.com/Quantumx610/my_pomodoro_timer.git
cd my_pomodoro_timer

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

With your virtual environment active, run:

```bash
python3 pomodoro.py
```

---

## Usage Guide

1. **Enter a Task**: Type your focus goal into the **Task** field and click **Set Task** (or click **Start** to auto-set).
2. **Adjust Intervals**: Default is 25 minutes of work and 5 minutes of break. Adjust durations in the input boxes if desired.
3. **Start Session**: Click **Start** to begin the timer.
4. **Pause / Reset**: Use **Pause** to hold the timer (resumes back into your current mode), or **Reset** to clear the session.
5. **Select Break Music**: Click **Select Music** to choose an MP3 or WAV file to automatically play during break sessions.

---

## Contributing

Contributions and feedback are welcome!
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## License & Acknowledgements

- The Pomodoro Technique was created by Francesco Cirillo.
- Color palette inspired by the [Nord](https://www.nordtheme.com/) theme.
