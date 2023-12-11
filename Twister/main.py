import pygame
import time
import os
# os.environ['SDL_AUDIODRIVER'] = 'dsp'
import subprocess
import glob
from dataclasses import dataclass
from typing import Dict
from typing import List
import RPi.GPIO as GPIO
import multiprocessing
from random import shuffle, randrange

GPIO.setmode(GPIO.BOARD)
USERNAME = "midirasp03"

@dataclass
class Song:
    source_dir: str
    all_parts: list
    all_pygame_sounds: List[pygame.mixer.Sound]

BOUTON1 = 29#5
BOUTON2 = 22#6
BOUTON3 = 32#12
BOUTON4 = 13#16
LED1 = 11#17 
LED2 = 15#22 o 
LED3 = 16#23 o
LED4 = 18#24

all_boutons = [
    [BOUTON1, 0], [BOUTON2, 0], [BOUTON3, 0], 
    [BOUTON4, 0]]

bouton_led:Dict[int, int] = {
    BOUTON1: LED1,
    BOUTON2: LED2,
    BOUTON3: LED3,
    BOUTON4: LED4,
}

led_order = [LED1, LED2, LED3, LED4]
led_opposite = [LED4, LED3, LED2, LED1]

for bouton, led in bouton_led.items():
    GPIO.setup(bouton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(led, GPIO.OUT)

pygame.mixer.init(buffer=1024)
pygame.mixer.set_num_channels(50)

chan1 = pygame.mixer.Channel(0)

song_dir_simon:Dict[int, Song] = dict()
list_dir_simon = ['/home/' + USERNAME + '/TwisterSimon/Simon/*.mp3']
song_dir_simon[0] = Song(dir, ['/home/' + USERNAME + '/TwisterSimon/Simon/' + str(i)+".mp3" for i in range(1,9)], [])
print(song_dir_simon[0].all_parts)
for song_path in song_dir_simon[0].all_parts:
    print(song_path)
    song_dir_simon[0].all_pygame_sounds.append(pygame.mixer.Sound(song_path))
song_simon_win = pygame.mixer.Sound("/home/" + USERNAME + "/TwisterSimon/Simon/winner.mp3")
song_simon_wrong = pygame.mixer.Sound("/home/" + USERNAME + "/TwisterSimon/Simon/wrong.mp3")

for bouton, led in bouton_led.items():
    GPIO.output(led, 1)
    
time.sleep(1)

for bouton, led in bouton_led.items():
    GPIO.output(led, 0)

time.sleep(1)

def check_interrupt() -> bool:
    for bouton_i, bouton in enumerate(all_boutons):
        if GPIO.input(bouton[0]) == 1:
            print(bouton_i)
            return True
    return False

def sleep_custom(delay_sec):
    counter: int = 0
    while True:
        time.sleep(delay_sec / 100)
        if check_interrupt():
            return
        if counter >= delay_sec * 100:
            break
        counter += 1

def play_win():
    for led in led_order:
        sleep_custom(0.2)
        if check_interrupt():
            return
        GPIO.output(led, 1)
    for led in led_opposite:
        if check_interrupt():
            return
        sleep_custom(0.2)
        GPIO.output(led, 0)

def play_wrong():
    for i in range(0,3):
        for bouton, led in bouton_led.items():
            GPIO.output(led, 1) 
        time.sleep(0.3)
        for bouton, led in bouton_led.items():
            GPIO.output(led, 0)
        time.sleep(0.3)


def anim_waiting():
    while True:
        for led in led_order:
            sleep_custom(0.4)
            if check_interrupt():
                return
            GPIO.output(led, 1)
        for led in led_opposite:
            if check_interrupt():
                return
            sleep_custom(0.4)
            GPIO.output(led, 0)

def loop_simon():
    music_bouton:Dict[int, Tuple[int, pygame.mixer.Sound]] = dict()
    reset = True
    game_running = False
    while True:
        if reset:
            list_boutons:List[int] = [i for i in range(0, 4)]
            for i in range(0, 4):
                list_boutons.append(randrange(4))
            print(list_boutons)
            shuffle(list_boutons)
            print(list_boutons)
            for track_index, bouton in enumerate(list_boutons):
                music_bouton[track_index] = (all_boutons[bouton][0], song_dir_simon[0].all_pygame_sounds[track_index])
            reset = False
        
        # for bouton_i, bouton in enumerate(all_boutons):
        #     if GPIO.input(bouton[0]) == 1:
        anim_waiting()
        for bouton, led in bouton_led.items():
            GPIO.output(led, 0)
        game_running = True
        start_time = time.time()
        level = 0
        button_pointer = 0
        my_turn = True
        while game_running:
            if time.time() - start_time > 30:
                reset = True
                game_running = False
                break

            if my_turn:
                if level == 8:
                    print("YOU WON")
                    reset = True
                    game_running = False
                    chan1.play(song_simon_win)
                    
                    while chan1.get_busy():
                        play_win()
                    break
                time.sleep(0.5)
                for i in range(0,level+1):
                    print('play {0}'.format(i))
                    chan1.play(music_bouton[i][1])
                    GPIO.output(bouton_led[music_bouton[i][0]], 1)
                    while chan1.get_busy():
                        pass
                    GPIO.output(bouton_led[music_bouton[i][0]], 0)
                my_turn = False
                print("YOUR TURN")
                print(str(music_bouton[button_pointer][0]))

            if not my_turn:
                if button_pointer == level + 1:
                    my_turn = True
                    button_pointer = 0
                    level = level + 1
                    continue
                for bouton_i, bouton in enumerate(all_boutons):
                    if GPIO.input(bouton[0]) == 1 and bouton[0] == music_bouton[button_pointer][0]:
                        start_time = time.time()
                        print("pressed " + str(bouton[0]))
                        while GPIO.input(bouton[0]) == 1:
                            pass
                        chan1.play(music_bouton[button_pointer][1])
                        GPIO.output(bouton_led[music_bouton[button_pointer][0]], 1)
                        while chan1.get_busy():
                            pass
                        GPIO.output(bouton_led[music_bouton[button_pointer][0]], 0)
                        button_pointer = button_pointer + 1
                        print("GOOD")
                        if button_pointer+1 in list_boutons:
                            print("Keep going... (next one: " + str(list_boutons[button_pointer+1]) +")")
                        break
                    elif GPIO.input(bouton[0]) == 1 and bouton[0] != music_bouton[button_pointer][0]:
                        print("pressed " + str(bouton[0]) + " instead of " + str(music_bouton[button_pointer][0]))
                        while GPIO.input(bouton[0]) == 1:
                            pass
                        print("YOU LOST")
                        chan1.play(song_simon_wrong)
                    
                        while chan1.get_busy():
                            play_wrong()
                        reset = True
                        game_running = False
                        break

while True:
    loop_simon()