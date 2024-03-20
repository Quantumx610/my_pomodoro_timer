import pygame
import os
from time import sleep
import pyttsx3

checkmark = 0
total_mins = 0

# Initialize pygame
pygame.init()

# Set up a minimal display (1x1 pixels)
pygame.display.set_mode((1, 1))

# Initialize pygame mixer for audio
pygame.mixer.init()

# Hardcoded path to the directory containing the music files
music_directory = "E:\pomodoro\music"

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()

def tasks(task):
    global checkmark
    global total_mins
    mins = 0
    focus_time = 25
    print('Timer for',task,'is',focus_time,'mins.')
    while mins < focus_time:
        sleep(60)
        mins += 1
        total_mins += 1
        print(mins,"minutes work completed.")
    checkmark += 1
    print('Total cycles of pomodoro completed:', checkmark)

def load_music_files(directory):
    music_files = []
    for file in os.listdir(directory):
        if file.endswith(".mp3") or file.endswith(".wav") or file.endswith(".opus") or file.endswith(".m4a"):
            music_files.append(os.path.join(directory, file))
    return music_files

def select_music(available_music_files):
    print("Available music files:")
    for idx, file in enumerate(available_music_files):
        print(f"{idx + 1}. {os.path.basename(file)}")

    while True:
        try:
            selection = int(input("Enter the number corresponding to the music file you want to play: "))
            if 1 <= selection <= len(available_music_files):
                return available_music_files[selection - 1]
            else:
                print("Invalid selection. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def breaks(selected_music_file):
    global checkmark
    mins = 0
    pygame.mixer.music.load(selected_music_file)
    pygame.mixer.music.play(loops=-1)  # Play the music on loop
    
    # Set an event for music end
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)

    if checkmark < 6:
        print('Take a short break.')
        while mins < 5:
            sleep(60)
            mins += 1
            print(mins,"minutes break completed.")
            
            # Check if the music end event is triggered
            for event in pygame.event.get():
                if event.type == MUSIC_END:
                    pygame.mixer.music.play(loops=-1)  # Play the music again if it ends
        print('Break over')
    elif checkmark >= 6:
        print('Take a long break.')
        while mins < 15:
            sleep(60)
            mins += 1
            print(mins, " minutes break completed.")
            
            # Check if the music end event is triggered
            for event in pygame.event.get():
                if event.type == MUSIC_END:
                    pygame.mixer.music.play(loops=-1)  # Play the music again if it ends
        checkmark = 0
        print('Your long Break is over.')
        
    pygame.mixer.music.stop()
    engine.say('Your break has been ended. Start focusing.')
    engine.runAndWait()

def main():
    global total_mins
    engine.say('Welcome to my Pomodoro Timer. What task do you want to work on?')
    engine.runAndWait()
    task = input('Welcome to Pomodoro Timer\nWhat task do you want to work on? ')

    available_music_files = load_music_files(music_directory)
    selected_music_file = select_music(available_music_files)
    
    while checkmark<7:
        tasks(task)
        breaks(selected_music_file)

    print(f"End of task {task}.\nTotal time worked was {total_mins} minutes.")

if __name__ == '__main__':
    main()
