import pygame
import time
import os
# os.environ['SDL_AUDIODRIVER'] = 'dsp'
import subprocess
import glob
from dataclasses import dataclass
from typing import Dict
from typing import List
from RPiMCP23S17.MCP23S17 import MCP23S17
import RPi.GPIO as GPIO
import multiprocessing
from random import shuffle, randrange

@dataclass
class Song:
    source_dir: str
    all_parts: list
    all_pygame_sounds: List[pygame.mixer.Sound]

@dataclass
class LedGroup:
    group_id: str
    leds: List[int]
    device: MCP23S17
    group_pin: int

mcp1 = MCP23S17(bus=0x00, pin_cs=0, device_id=0x00)
mcp2 = MCP23S17(bus=0x00, pin_cs=1, device_id=0x01)
mcp1.open()
mcp2.open()
mcp1._spi.max_speed_hz=1000000
mcp2._spi.max_speed_hz=1000000

all_led_group: Dict[str, LedGroup] = {
    'A': LedGroup('A', [1, 2], mcp1, 0),
    'B': LedGroup('B', [3], mcp1, 1),
    'C': LedGroup('C', [4, 5], mcp1, 2),
    'D': LedGroup('D', [6, 7], mcp1, 3),
    'E': LedGroup('E', [8], mcp1, 4),
    'F': LedGroup('F', [9, 10], mcp1, 5),
    'G': LedGroup('G', [11, 12], mcp1, 6),
    'H': LedGroup('H', [13, 14], mcp1, 7),
    'I': LedGroup('I', [15, 16], mcp1, 8),
    'J': LedGroup('J', [17], mcp1, 9),
    'K': LedGroup('K', [18, 19], mcp1, 10),
    'L': LedGroup('L', [20, 21], mcp1, 11),
    'M': LedGroup('M', [22, 23], mcp1, 12),
    'N': LedGroup('N', [24], mcp1, 13),
    'O': LedGroup('O', [25,26], mcp1, 14),
    'P': LedGroup('P', [27,28], mcp1, 15),
    'Q': LedGroup('Q', [29,30], mcp2, 0),
    'R': LedGroup('R', [31], mcp2, 1),
    'S': LedGroup('S', [32,33], mcp2, 2),
    'T': LedGroup('T', [34,35], mcp2, 3),
    'U': LedGroup('U', [36], mcp2, 4),
    'V': LedGroup('V', [37,38], mcp2, 5),
    'W': LedGroup('W', [39,40], mcp2, 6),
    'X': LedGroup('X', [41,42], mcp2, 7),
    'Y': LedGroup('Y', [43,44], mcp2, 8),
    'Z': LedGroup('Z', [45], mcp2, 9),
}

DELAY_EMPTY = 0.1#second

leds_anim_Simon_won = [
    ['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J'], ['K', 'L'], ['M', 'N'], ['O', 'P'], ['Q', 'R'], ['S', 'T'], ['U', 'V'], ['W', 'X'], ['Y', 'Z'], [],
    ['A', 'B', 'Y', 'Z'], ['C', 'D', 'Y', 'Z'], ['E', 'F', 'Y', 'Z'], ['G', 'H', 'Y', 'Z'], ['I', 'J', 'Y', 'Z'], ['K', 'L', 'Y', 'Z'], ['M', 'N', 'Y', 'Z'], ['O', 'P', 'Y', 'Z'], ['Q', 'R', 'Y', 'Z'], ['S', 'T', 'Y', 'Z'], ['U', 'V', 'Y', 'Z'], ['W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'W', 'X', 'Y', 'Z'], ['K', 'L', 'W', 'X', 'Y', 'Z'], ['M', 'N', 'W', 'X', 'Y', 'Z'], ['O', 'P', 'W', 'X', 'Y', 'Z'], ['Q', 'R', 'W', 'X', 'Y', 'Z'], ['S', 'T', 'W', 'X', 'Y', 'Z'], ['U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['K', 'L', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['M', 'N', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['O', 'P', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['Q', 'R', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['K', 'L', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['M', 'N', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['O', 'P', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['K', 'L', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['M', 'N', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['K', 'L', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], [],
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], []
]

leds_anim_Simon_lose = [
    ['Y', 'Z'], ['W', 'X'], ['U', 'V'], ['S', 'T'], ['Q', 'R'], ['O', 'P'], ['M', 'N'], ['K', 'L'], ['I', 'J'], ['G', 'H'], ['E', 'F'], ['C', 'D'], ['A', 'B'], ['A', 'B'], ['C', 'D'], ['E', 'F'], ['G', 'H'], ['I', 'J'], ['K', 'L'], ['M', 'N'], ['O', 'P'], ['Q', 'R'], ['S', 'T'], ['U', 'V'], ['W', 'X'], ['Y', 'Z'], []
]

BOUTON1 = 29#5
BOUTON2 = 31#6
BOUTON3 = 32#12
BOUTON4 = 36#16
BOUTON5 = 11#17 
BOUTON6 = 15#22 o 
BOUTON7 = 16#23 o
BOUTON8 = 18#24
BOUTON9 = 22#25
BOUTON10 = 37#26

SWITCH_TWISTER = 13

all_boutons = [
    [BOUTON1, 0], [BOUTON2, 0], [BOUTON3, 0], 
    [BOUTON4, 0], [BOUTON5, 0], [BOUTON6, 0], 
    [BOUTON7, 0], [BOUTON8, 0], [BOUTON9, 0], 
    [BOUTON10, 0]]

for bouton in all_boutons:
    GPIO.setup(bouton[0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SWITCH_TWISTER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

for x in range(0, 16):
    mcp1.setDirection(x, mcp1.DIR_OUTPUT)
    mcp2.setDirection(x, mcp2.DIR_OUTPUT)

for x in range(0, 16, -1):
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

bouton_led:Dict[int, List[LedGroup]] = {
    BOUTON1: [(mcp1, 15), (mcp1, 2), (mcp2, 8)],
    BOUTON2: [(mcp1, 13), (mcp1, 2), (mcp2, 9)],
    BOUTON3: [(mcp1, 6), (mcp1, 7), (mcp2, 10)],
    BOUTON4: [(mcp1, 2), (mcp1, 10), (mcp2, 11)],
    BOUTON5: [(mcp1, 11), (mcp1, 12), (mcp2, 8)],
    BOUTON6: [(mcp1, 1), (mcp1, 3), (mcp2, 9)],
    BOUTON7: [(mcp1, 2), (mcp1, 4), (mcp2, 10)],
    BOUTON8: [(mcp1, 15), (mcp1, 8), (mcp2, 11)],
    BOUTON9: [(mcp1, 7), (mcp1, 6), (mcp2, 8)],
    BOUTON10: [(mcp1, 12), (mcp1, 2), (mcp2, 9)],
}

pygame.mixer.init(buffer=1024)
pygame.mixer.set_num_channels(50)

chan1 = pygame.mixer.Channel(0)
chan2 = pygame.mixer.Channel(1)
chan3 = pygame.mixer.Channel(2)
chan4 = pygame.mixer.Channel(3)
chan5 = pygame.mixer.Channel(4)
chan6 = pygame.mixer.Channel(5)
chan7 = pygame.mixer.Channel(6)
chan8 = pygame.mixer.Channel(7)
chan9 = pygame.mixer.Channel(8)
chan10 = pygame.mixer.Channel(9)
all_channels = [chan1, chan2, chan3, chan4, chan5, chan6, chan7, chan8, chan9, chan10]

list_dir_twister = ['/home/pi/TwisterSimon/Lacoste/*.mp3']
song_dir_twister:Dict[int, Song] = dict()

for index, dir in enumerate(list_dir_twister):
    print(glob.glob(dir))
    song_dir_twister[index] = Song(dir, glob.glob(dir), [])
    for song_path in song_dir_twister[index].all_parts:
        song_dir_twister[index].all_pygame_sounds.append(pygame.mixer.Sound(song_path))

song_dir_simon:Dict[int, Song] = dict()
list_dir_simon = ['/home/pi/TwisterSimon/SimonPrev/*.mp3']
song_dir_simon[0] = Song(dir, ['/home/pi/TwisterSimon/Simon/' + str(i)+".mp3" for i in range(1,12)], [])
print(song_dir_simon[0].all_parts)
for song_path in song_dir_simon[0].all_parts:
    print(song_path)
    song_dir_simon[0].all_pygame_sounds.append(pygame.mixer.Sound(song_path))
song_full_simon = pygame.mixer.Sound("/home/pi/TwisterSimon/SimonPrev/full.mp3")

for x in range(15, -1, -1):
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

for x in range(0, 16):
    time.sleep(0.05)
    mcp1.digitalWrite(x, MCP23S17.LEVEL_HIGH)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_HIGH)

for x in range(15, -1, -1):
    time.sleep(0.05)
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

# sudo mount /dev/sda1 /mnt/usb -o uid=pi,gid=pi
# sudo mkdir /mnt/usb

def read_anim(leds_anim: list):
    for rows in leds_anim:
        if not rows:
            time.sleep(DELAY_EMPTY)
            continue
        for id_group, group in all_led_group.items():
            if id_group in rows:
                group.device.digitalWrite(group.group_pin, MCP23S17.LEVEL_HIGH)
            else:
                group.device.digitalWrite(group.group_pin, MCP23S17.LEVEL_LOW)

def anim_waiting():
    while True:
        for x in range(0, 16):
            time.sleep(0.1)
            for bouton_i, bouton in enumerate(all_boutons):
                if GPIO.input(bouton[0]) == 1:
                    print(bouton_i)
                    return
            mcp1.digitalWrite(x, MCP23S17.LEVEL_HIGH)
            mcp2.digitalWrite(x, MCP23S17.LEVEL_HIGH)

        for x in range(15, -1, -1):
            for bouton_i, bouton in enumerate(all_boutons):
                if GPIO.input(bouton[0]) == 1:
                    print(bouton_i)
                    return
            time.sleep(0.1)
            mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
            mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

def anim_won():
    for x in range(0, 16):
        time.sleep(0.01)
        mcp1.digitalWrite(x, MCP23S17.LEVEL_HIGH)
        mcp2.digitalWrite(x, MCP23S17.LEVEL_HIGH)

    for x in range(15, -1, -1):
        time.sleep(0.01)
        mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
        mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

def loop_twister():
    if GPIO.input(SWITCH_TWISTER) == 0:
        return
    while True:
        print("new loop...", end=" ")
        num_song = len(song_dir_twister[0].all_parts)
        for pg_sound_i, pg_sound in enumerate(song_dir_twister[0].all_pygame_sounds):
            all_channels[pg_sound_i].play(pg_sound)
            all_channels[pg_sound_i].set_volume(0)

        while chan8.get_busy():
            if GPIO.input(SWITCH_TWISTER) == 0:
                return
            for bouton_i, bouton in enumerate(all_boutons):
                if bouton_i >= num_song:
                    continue
                if GPIO.input(bouton[0]) != bouton[1]:
                    print(str(GPIO.input(bouton[0])) + " " + str(bouton[1]))
                    print("changed" + str(bouton_i))
                    if bouton[1] == 0:
                        for led_tuple in bouton_led[all_boutons[bouton_i][0]]:
                            led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
                        all_channels[bouton_i].set_volume(100)
                        bouton[1] = 1
                    elif bouton[1] == 1:
                        for led_tuple in bouton_led[all_boutons[bouton_i][0]]:
                            led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_LOW)
                        all_channels[bouton_i].set_volume(0)
                        bouton[1] = 0

        for bouton in all_boutons:
            bouton[1] = 0

# loop_twister()
def loop_simon():
    if GPIO.input(SWITCH_TWISTER) == 1:
        return
    bouton_music:Dict[int, tuple[int, pygame.mixer.Sound]] = dict()
    reset = True
    game_running = False
    while True:
        if GPIO.input(SWITCH_TWISTER) == 1:
            return
        if reset:
            list_boutons:List[int] = [i for i in range(0, 10)]
            list_boutons.append(randrange(10))
            shuffle(list_boutons)
            print(list_boutons)
            for bouton_i, bouton in enumerate(list_boutons):
                bouton_music[bouton_i] = (all_boutons[bouton][0], song_dir_simon[0].all_pygame_sounds[bouton_i])
            reset = False
        
        # for bouton_i, bouton in enumerate(all_boutons):
        #     if GPIO.input(bouton[0]) == 1:
        anim_waiting()
        for x in range(15, -1, -1):
            mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
            mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)
        game_running = True
        start_time = time.time()
        level = 0
        button_pointer = 0
        my_turn = True
        while game_running:
            if GPIO.input(SWITCH_TWISTER) == 1:
                return
            if time.time() - start_time > 30:
                reset = True
                game_running = False
                break

            if my_turn:
                if level == 11:
                    print("YOU WON")
                    reset = True
                    game_running = False
                    chan1.play(song_full_simon)
                    read_anim(leds_anim_Simon_won)
                    while chan1.get_busy():
                        pass
                    break
                for i in range(0,level+1):
                    chan1.play(bouton_music[i][1])
                    for led_tuple in bouton_led[bouton_music[i][0]]:
                        led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
                    while chan1.get_busy():
                        pass
                    for led_tuple in bouton_led[bouton_music[i][0]]:
                            led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_LOW)
                my_turn = False
                print("YOUR TURN")
                print(str(bouton_music[button_pointer][0]))

            if not my_turn:
                if button_pointer == level + 1:
                    my_turn = True
                    button_pointer = 0
                    level = level + 1
                    continue
                for bouton_i, bouton in enumerate(all_boutons):
                    if GPIO.input(bouton[0]) == 1 and bouton[0] == bouton_music[button_pointer][0]:
                        start_time = time.time()
                        print("pressed " + str(bouton[0]))
                        while GPIO.input(bouton[0]) == 1:
                            pass
                        chan1.play(bouton_music[button_pointer][1])
                        for led_tuple in bouton_led[bouton_music[button_pointer][0]]:
                            led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
                        while chan1.get_busy():
                            pass
                        for led_tuple in bouton_led[bouton_music[button_pointer][0]]:
                                led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_LOW)
                        button_pointer = button_pointer + 1
                        print("GOOD")
                        if button_pointer != level + 1:
                            print("Keep going... (next one: " + str(list_boutons[button_pointer+1]) +")")
                    elif GPIO.input(bouton[0]) == 1 and bouton[0] != bouton_music[button_pointer][0]:
                        print("pressed " + str(bouton[0]) + " instead of " + str(bouton_music[button_pointer][0]))
                        while GPIO.input(bouton[0]) == 1:
                            pass
                        print("YOU LOST")
                        read_anim(leds_anim_Simon_lose)
                        reset = True
                        game_running = False
                        break

while True:
    loop_simon()
    loop_twister()
#         while True:
#             num_song = len(song_dir[index].all_parts)
#             for process_i, process in enumerate(song_dir[index].all_processes):
#                 all_channels[process_i].play(process.song)
#                 all_channels[process_i].set_volume(0)

#             while chan8.get_busy():
#                 if GPIO.input(SWITCH_TWISTER) == 0:
#                     return
#                 for bouton_i, bouton in enumerate(all_boutons):
#                     if bouton_i >= num_song:
#                         continue
#                     if GPIO.input(bouton[0]) != bouton[1]:
#                         print(str(GPIO.input(bouton[0])) + " " + str(bouton[1]))
#                         print("changed" + str(bouton_i))
#                         # song_dir[index].all_processes[bouton_i].master_slave[1].send('trig')
#                         # os.write(song_dir[index].all_processes[bouton_i].master_slave[1], b'u')
#                         if bouton[1] == 0:
#                             for led_tuple in bouton_led[all_boutons[bouton_i][0]]:
#                                 led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
#                             all_channels[bouton_i].set_volume(100)
#                             bouton[1] = 1
#                         elif bouton[1] == 1:
#                             for led_tuple in bouton_led[all_boutons[bouton_i][0]]:
#                                 led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_LOW)
#                             all_channels[bouton_i].set_volume(0)
#                             bouton[1] = 0
#             # for song_path in song_dir[index].all_parts:
#             #     song_dir[index].all_processes.clear()

#             for bouton in all_boutons:
#                 bouton[1] = 0


# while True:
#     for bouton_i, bouton in enumerate(all_boutons):
#         a = GPIO.input(bouton[0])
#         print(str(bouton_i) + " : " + str(a))

# song_path1 = "/home/pi/STEM/Bad STEM Jackson Bass.mp3"
# song_path2 = "/home/pi/STEM/Bad STEM Jackson Drum.mp3"
# song_path3 = "/home/pi/STEM/Bad STEM Jackson Guitar.mp3"
# song_path4 = "/home/pi/STEM/Bad STEM Jackson Vocal_Back.mp3"
# song_path5 = "/home/pi/STEM/Bad STEM Jackson Drum_Clap.mp3"
# song_path6 = "/home/pi/STEM/Bad STEM Jackson Group_Moog.mp3"
# song_path7 = "/home/pi/STEM/Bad STEM Jackson Keys.mp3"
# song_path8 = "/home/pi/STEM/Bad STEM Jackson Vocal.mp3"
# master1, slave1 = os.openpty()
# master2, slave2 = os.openpty()
# master3, slave3 = os.openpty()
# master4, slave4 = os.openpty()
# master5, slave5 = os.openpty()
# master6, slave6 = os.openpty()
# master7, slave7 = os.openpty()
# master8, slave8 = os.openpty()
# master9, slave9 = os.openpty()
# master10, slave10 = os.openpty()

# all_master_slave = [
#     (master1, slave1), (master2, slave2), (master3, slave3), (master4, slave4),
#     (master5, slave5), (master6, slave6), (master7, slave7), (master8, slave8),
#     (master9, slave9), (master10, slave10)]

# receiver1, sender1 = multiprocessing.Pipe()
# receiver2, sender2 = multiprocessing.Pipe()
# receiver3, sender3 = multiprocessing.Pipe()
# receiver4, sender4 = multiprocessing.Pipe()
# receiver5, sender5 = multiprocessing.Pipe()
# receiver6, sender6 = multiprocessing.Pipe()
# receiver7, sender7 = multiprocessing.Pipe()
# receiver8, sender8 = multiprocessing.Pipe()
# receiver9, sender9 = multiprocessing.Pipe()
# receiver10, sender10 = multiprocessing.Pipe()

# all_master_slave = [
#     (receiver1, sender1), (receiver2, sender2), (receiver3, sender3), (receiver4, sender4),
#     (receiver5, sender5), (receiver6, sender6), (receiver7, sender7), (receiver8, sender8),
#     (receiver9, sender9), (receiver10,sender10)]

# # pygame.mixer.init()
# # pygame.mixer.music.load("../STEM/Bad STEM Jackson Bass.mp3")
# # pygame.mixer.music.play()
# # x = pygame.mixer.Sound("../STEM/Bad STEM Jackson Bass.mp3")
# # x.play(0)
# # pygame.mixer.Channel(0).play

# def one_process_is_running(all_processes:list[SongProcess]) -> bool:
#     for process in all_processes:
#         if process.process.is_alive():
#             return True
#     return False

# def run_song_part(song_path:str, receiver):
#     # if receiver.poll():
#     #     comm = receiver.recv()
#     #     if comm is not None:
#     #         if comm == "play":
#     master, slave = os.openpty()
#     # process = subprocess.Popen(["/usr/bin/mpg123", "-C", "-q", "-T", song_path], stdout=subprocess.DEVNULL, stdin=master)
#     process = subprocess.Popen(["/usr/bin/mpg123", "-C", "-q", song_path], stdout=subprocess.DEVNULL, stdin=master)
#     # os.write(slave, b'u')
#     os.write(slave, b's')
#     while process.poll() is None:
#         if receiver.poll():
#             comm = receiver.recv()
#             if comm is not None:
#                 if comm == "play":
#                     os.write(slave, b's')
#                 else:
#                     os.write(slave, b'u')

# # process = multiprocessing.Process(target=run_playlist, kwargs={"button":button, "receiver":receiver})

# index = 0

# while True:
#     print("popen##################################################################")
#     index += 1
#     if index == len(song_dir):
#         index = 0
#     num_song = -1
#     for song_i, song_path in enumerate(song_dir[index].all_parts):
#         print(str(song_i) + ": " + song_path)
#         # song_dir[index].all_processes.append(SongProcess(None, os.openpty()))
#         # song_dir[index].all_processes[-1].process = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path], stdout=None, stdin=song_dir[index].all_processes[-1].master_slave[0], stderr=None)
#         song_dir[index].all_processes.append(SongProcess(multiprocessing.Process(target=run_song_part, kwargs={"song_path":song_path, "receiver":all_master_slave[song_i][0]}), all_master_slave[song_i]))
#         # os.write(all_master_slave[song_i][1], b'u')
#         num_song += 1
#     start_time = time.time()
#     for process_i, process in enumerate(song_dir[index].all_processes):
#         print("--- %s seconds ---" % (time.time() - start_time))
#         start_time = time.time()
#         process.process.start()
#         # print("--- %s seconds ---" % (time.time() - start_time))

#     for process_i, process in enumerate(song_dir[index].all_processes):
#         # print("--- %s seconds ---" % (time.time() - start_time))
#         # start_time = time.time()
#         process.master_slave[1].send('play')
#     # process1 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path1], stdout=None, stdin=master1, stderr=None)
#     # os.write(slave1, b'u')
#     # process2 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path2], stdout=None, stdin=master2, stderr=None)
#     # os.write(slave2, b'u')
#     # process3 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path3], stdout=None, stdin=master3, stderr=None)
#     # os.write(slave3, b'u')
#     # process4 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path4], stdout=None, stdin=master4, stderr=None)
#     # os.write(slave4, b'u')
#     # process5 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path5], stdout=None, stdin=master5, stderr=None)
#     # os.write(slave5, b'u')
#     # process6 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path6], stdout=None, stdin=master6, stderr=None)
#     # os.write(slave6, b'u')
#     # process7 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path7], stdout=None, stdin=master7, stderr=None)
#     # os.write(slave7, b'u')
#     # process8 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path8], stdout=None, stdin=master8, stderr=None)
#     # os.write(slave8, b'u')


#     while one_process_is_running(song_dir[index].all_processes):
#         for bouton_i, bouton in enumerate(all_boutons):
#             if bouton_i > num_song:
#                 continue
#             if GPIO.input(bouton[0]) != bouton[1]:
#                 print(str(GPIO.input(bouton[0])) + " " + str(bouton[1]))
#                 print("changed" + str(bouton_i))
#                 song_dir[index].all_processes[bouton_i].master_slave[1].send('trig')
#                 # os.write(song_dir[index].all_processes[bouton_i].master_slave[1], b'u')
#                 if bouton[1] == 0:
#                     bouton[1] = 1
#                 elif bouton[1] == 1:
#                     bouton[1] = 0
#         # a = input("butt")
#         # if a == "1":
#         #     os.write(slave1, b'u')
#         # elif a == "2":
#         #     os.write(slave2, b'u')
#         # elif a == "3":
#         #     os.write(slave3, b'u')
#         # elif a == "4":
#         #     os.write(slave4, b'u')
#         # elif a == "5":
#         #     os.write(slave5, b'u')
#         # elif a == "6":
#         #     os.write(slave6, b'u')
#         # elif a == "7":
#         #     os.write(slave7, b'u')
#         # elif a == "8":
#         #     os.write(slave8, b'u')
#         pass

#     for song_path in song_dir[index].all_parts:
#         song_dir[index].all_processes.clear()

#     for bouton in all_boutons:
#         bouton[1] = 0