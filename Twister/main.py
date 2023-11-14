from __future__ import print_function

USER_NAME = "midirasp02"
# USER_NAME = "pi"

import sys
sys.path.append("/home/" + USER_NAME + "/ola/python")

import pygame
import time
import os
import array
import subprocess
import glob
from dataclasses import dataclass
from typing import Dict
from typing import List
from RPiMCP23S17.MCP23S17 import MCP23S17
import RPi.GPIO as GPIO
import multiprocessing
from random import shuffle, randrange, choice
import json
from ola.ClientWrapper import ClientWrapper
from ola.OlaClient import Universe

DELAY_WAITING = 20
DELAY_WAITING_BETWEEN = 20
MAX_LIGHT = 255

GPIO.setmode(GPIO.BOARD)

# TODO: take into account index starts at 1

CHANNEL_RANGE = (0,45)
data_save = array.array('B', [0]*45)
universe = 1
range_channels = range(CHANNEL_RANGE[0], CHANNEL_RANGE[1])
def DmxSent(status):
  if status.Succeeded():
    print('Success!')
  else:
    print('Error: %s' % status.message, file=sys.stderr)

@dataclass
class Song:
    source_dir: str
    all_parts: list
    all_pygame_sounds: List[pygame.mixer.Sound]

@dataclass
class LedGroup:
    group_id: str
    leds: List[int]
    channel: MCP23S17

@dataclass
class ChannelGroup:
    group_name: str
    channels: List[int]

led_groups = json.load(open("/home/" + USER_NAME + "/TwisterSimon/Twister/leds_groups.json"))
animations = json.load(open("/home/" + USER_NAME + "/TwisterSimon/Twister/animations.json"))

DELAY_EMPTY = 0.1#second

BOUTON1 = 40#21  29#5
BOUTON2 = 38#20  31#6
BOUTON3 = 37#26  32#12
BOUTON4 = 36#16  36#16
BOUTON5 = 35#19  11#17 
BOUTON6 = 33#13  15#22 o 
BOUTON7 = 32#12  16#23 o
BOUTON8 = 31#6   18#24

SWITCH_TWISTER = 13

all_boutons = [
    [BOUTON1, 0], [BOUTON2, 0], [BOUTON3, 0], 
    [BOUTON4, 0], [BOUTON5, 0], [BOUTON6, 0], 
    [BOUTON7, 0], [BOUTON8, 0], ]

for bouton in all_boutons:
    GPIO.setup(bouton[0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SWITCH_TWISTER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# result = subprocess.run(["ola_dev_info"], stdout=subprocess.PIPE)
# print(result.stdout)
subprocess.Popen(["ola_patch", "-d", "3", "-p", "0", "-u", "1"], stdout = subprocess.PIPE, text = True)
wrapper = ClientWrapper()
client = wrapper.Client()

bouton_led:List[ChannelGroup] = [None]*8

for group in led_groups["config_1"]:
    bouton_led[group["bouton_id"]] = ChannelGroup(group["group_id"],group["channels"])

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

all_channels = [chan1, chan2, chan3, chan4, chan5, chan6, chan7, chan8]

list_dir_twister = ['/home/' + USER_NAME + '/TwisterSimon/Lacoste/*.mp3']
song_dir_twister:Dict[int, Song] = dict()

for index, dir in enumerate(list_dir_twister):
    print(glob.glob(dir))
    song_dir_twister[index] = Song(dir, glob.glob(dir), [])
    for song_path in song_dir_twister[index].all_parts:
        song_dir_twister[index].all_pygame_sounds.append(pygame.mixer.Sound(song_path))

# song_dir_simon:Dict[int, Song] = dict()
# list_dir_simon = ['/home/' + USER_NAME + '/TwisterSimon/Simon/*.mp3']
# song_dir_simon[0] = Song(dir, ['/home/' + USER_NAME + '/TwisterSimon/SimonPrev/' + str(i)+".mp3" for i in range(1,12)], [])
# print(song_dir_simon[0].all_parts)
# for song_path in song_dir_simon[0].all_parts:
#     print(song_path)
#     song_dir_simon[0].all_pygame_sounds.append(pygame.mixer.Sound(song_path))
# song_full_simon = pygame.mixer.Sound("/home/" + USER_NAME + "/TwisterSimon/SimonPrev/full.mp3")

def write_group(group: List[int], mode: int, value: int = MAX_LIGHT):
    if type(group) != list:
        group = [group]
    print(group)
    for chan in group:
        data_save[chan-1] = mode*value
    client.SendDmx(universe, data_save, DmxSent)

def write_everything(mode: int, value: int = MAX_LIGHT):
    data = array.array('B')
    for idx in range_channels:
        data.append(mode * value)
    data_save = data
    client.SendDmx(universe, data, DmxSent)

write_everything(0)

time.sleep(1)
write_everything(1, 255)

time.sleep(1)
write_everything(0)

# sudo mount /dev/sda1 /mnt/usb -o uid=pi,gid=pi
# sudo mkdir /mnt/usb

def sleep_custom(delay_sec: int):
    counter: int = 0
    while True:
        time.sleep(delay_sec / 100)
        if check_interrupt():
            return
        if counter == delay_sec * 100:
            break
        counter += 1

def check_interrupt() -> bool:
    for bouton_i, bouton in enumerate(all_boutons):
        if GPIO.input(bouton[0]) == 1:
            print(bouton_i)
            return True
    return False

def read_anim(sequence: list, delay: float, repeat: int):
    if repeat == 0:
        for group in sequence:
            data = array.array('B')
            for chan in range_channels:
                if chan in group:
                    data.append(MAX_LIGHT)
                else:
                    data.append(0)
            client.SendDmx(universe, data, DmxSent)
            sleep_custom(delay)
    else:
        for i in range(0, repeat):
            for group in sequence:
                group_minus = [i-1 for i in group]
                data = array.array('B')
                for chan in range_channels:
                    if chan in group_minus:
                        data.append(MAX_LIGHT)
                    else:
                        data.append(0)
                client.SendDmx(universe, data, DmxSent)
                if not check_interrupt():
                    sleep_custom(delay)
                else:
                    write_everything(0)
                    return
    write_everything(0)

def play_anim(name_anim: str):
    for anim_type in animations["animations"]:
        print(anim_type)
        for anims in anim_type:
            for anim in anim_type[anims]:
                print(anim)
                if anim["anim_name"] == name_anim:
                    read_anim(anim["sequence"], anim["delay_sec_between"], anim["repeat"])
                    break

def pick_random_and_play(anim_type: str):
    pygame.mixer.music.load("/home/" + USER_NAME + "/TwisterSimon/wait.mp3")
    pygame.mixer.music.play(-1,0)
    while True:
        if check_interrupt():
            pygame.mixer.music.stop()
            return
        list_anims = animations["animations"]
        for anim in list_anims:
            if anim_type not in anim:
                continue
            anim_picked = choice(anim[anim_type])
            break
        read_anim(anim_picked["sequence"], anim_picked["delay_sec_between"], anim_picked["repeat"])
        start_time = time.time()
        while time.time() - start_time < DELAY_WAITING_BETWEEN:
            if check_interrupt():
                pygame.mixer.music.stop()
                return
        if check_interrupt():
            pygame.mixer.music.stop()
            return
# while True:
#     play_anim("test_charlie")
#     time.sleep(5)
# input("paolo")
def loop_twister():
    # if GPIO.input(SWITCH_TWISTER) == 0:
    #     chan1.stop()
    #     return
    start_time = time.time()
    while True:
        print("new loop...", end=" ")
        num_song = len(song_dir_twister[0].all_parts)
        for pg_sound_i, pg_sound in enumerate(song_dir_twister[0].all_pygame_sounds):
            all_channels[pg_sound_i].play(pg_sound)
            all_channels[pg_sound_i].set_volume(0)
        
        if time.time() - start_time > DELAY_WAITING:
            pick_random_and_play("waiting")
            start_time = time.time()

        while chan8.get_busy():
            if time.time() - start_time > DELAY_WAITING:
                break
            # if GPIO.input(SWITCH_TWISTER) == 0:
            #     chan1.stop()
            #     return
            for bouton_i, bouton in enumerate(all_boutons):
                if bouton_i >= num_song:
                    continue
                if GPIO.input(bouton[0]) != bouton[1]:
                    start_time = time.time()
                    print(str(GPIO.input(bouton[0])) + " " + str(bouton[1]))
                    print("changed" + str(bouton_i))
                    if bouton[1] == 0:
                        write_group(bouton_led[bouton_i].channels, 1)
                        # for led_tuple in bouton_led[all_boutons[bouton_i][0]]:
                        #     led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
                        all_channels[bouton_i].set_volume(100)
                        bouton[1] = 1
                    elif bouton[1] == 1:
                        write_group(bouton_led[bouton_i].channels, 0)
                        all_channels[bouton_i].set_volume(0)
                        bouton[1] = 0

        for bouton in all_boutons:
            bouton[1] = 0

# loop_twister()
# def loop_simon():
#     if GPIO.input(SWITCH_TWISTER) == 1:
#         return
#     chan1.set_volume(100)
#     bouton_music:Dict[int, tuple[int, pygame.mixer.Sound]] = dict()
#     reset = True
#     game_running = False
#     while True:
#         if GPIO.input(SWITCH_TWISTER) == 1:
#             return
#         if reset:
#             list_boutons:List[int] = [i for i in range(0, 10)]
#             list_boutons.append(randrange(10))
#             shuffle(list_boutons)
#             print(list_boutons)
#             for bouton_i, bouton in enumerate(list_boutons):
#                 bouton_music[bouton_i] = (all_boutons[bouton][0], song_dir_simon[0].all_pygame_sounds[bouton_i])
#             reset = False
        
#         # for bouton_i, bouton in enumerate(all_boutons):
#         #     if GPIO.input(bouton[0]) == 1:
#         anim_waiting()
#         for x in range(15, -1, -1):
#             mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
#             mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)
#         game_running = True
#         start_time = time.time()
#         level = 0
#         button_pointer = 0
#         my_turn = True
#         while game_running:
#             if GPIO.input(SWITCH_TWISTER) == 1:
#                 return
#             if time.time() - start_time > 30:
#                 reset = True
#                 game_running = False
#                 break

#             if my_turn:
#                 if level == 11:
#                     print("YOU WON")
#                     reset = True
#                     game_running = False
#                     chan1.play(song_full_simon)
#                     read_anim(leds_anim_Simon_won)
#                     while chan1.get_busy():
#                         pass
#                     break
#                 for i in range(0,level+1):
#                     chan1.play(bouton_music[i][1])
#                     for led_tuple in bouton_led[bouton_music[i][0]]:
#                         led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
#                     while chan1.get_busy():
#                         pass
#                     for led_tuple in bouton_led[bouton_music[i][0]]:
#                             led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_LOW)
#                 my_turn = False
#                 print("YOUR TURN")
#                 print(str(bouton_music[button_pointer][0]))

#             if not my_turn:
#                 if button_pointer == level + 1:
#                     my_turn = True
#                     button_pointer = 0
#                     level = level + 1
#                     continue
#                 for bouton_i, bouton in enumerate(all_boutons):
#                     if GPIO.input(bouton[0]) == 1 and bouton[0] == bouton_music[button_pointer][0]:
#                         start_time = time.time()
#                         print("pressed " + str(bouton[0]))
#                         while GPIO.input(bouton[0]) == 1:
#                             pass
#                         chan1.play(bouton_music[button_pointer][1])
#                         for led_tuple in bouton_led[bouton_music[button_pointer][0]]:
#                             led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_HIGH)
#                         while chan1.get_busy():
#                             pass
#                         for led_tuple in bouton_led[bouton_music[button_pointer][0]]:
#                                 led_tuple[0].digitalWrite(led_tuple[1], MCP23S17.LEVEL_LOW)
#                         button_pointer = button_pointer + 1
#                         print("GOOD")
#                         if button_pointer != level + 1:
#                             print("Keep going... (next one: " + str(list_boutons[button_pointer+1]) +")")
#                     elif GPIO.input(bouton[0]) == 1 and bouton[0] != bouton_music[button_pointer][0]:
#                         print("pressed " + str(bouton[0]) + " instead of " + str(bouton_music[button_pointer][0]))
#                         while GPIO.input(bouton[0]) == 1:
#                             pass
#                         print("YOU LOST")
#                         read_anim(leds_anim_Simon_lose)
#                         reset = True
#                         game_running = False
#                         break

while True:
    # loop_simon()
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