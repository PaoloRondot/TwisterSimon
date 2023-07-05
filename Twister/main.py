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

@dataclass
class SongProcess:
    process: multiprocessing.Process = None
    master_slave: tuple = (None, None)
    song: pygame.mixer.Sound = None

@dataclass
class Song:
    source_dir: str
    all_parts: list
    all_processes: List[SongProcess]

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

all_boutons = [
    [BOUTON1, 0], [BOUTON2, 0], [BOUTON3, 0], 
    [BOUTON4, 0], [BOUTON5, 0], [BOUTON6, 0], 
    [BOUTON7, 0], [BOUTON8, 0], [BOUTON9, 0], 
    [BOUTON10, 0]]

# GPIO.setmode(GPIO.BCM)
mcp1 = MCP23S17(bus=0x00, pin_cs=0, device_id=0x00)
mcp2 = MCP23S17(bus=0x00, pin_cs=1, device_id=0x01)
mcp1.open()
mcp2.open()
mcp1._spi.max_speed_hz=1000000
mcp2._spi.max_speed_hz=1000000

for bouton in all_boutons:
    GPIO.setup(bouton[0], GPIO.IN)

for x in range(0, 16):
    mcp1.setDirection(x, mcp1.DIR_OUTPUT)
    mcp2.setDirection(x, mcp2.DIR_OUTPUT)

for x in range(0, 16, -1):
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

bouton_led = {
    BOUTON1: [(mcp1, 1), (mcp1, 2), (mcp2, 1)],
    BOUTON2: [(mcp1, 4), (mcp1, 2), (mcp2, 3)],
    BOUTON3: [(mcp1, 6), (mcp1, 7), (mcp2, 5)],
    BOUTON4: [(mcp1, 2), (mcp1, 10), (mcp2, 7)],
    BOUTON5: [(mcp1, 11), (mcp1, 12), (mcp2, 9)],
    BOUTON6: [(mcp1, 1), (mcp1, 3), (mcp2, 11)],
    BOUTON7: [(mcp1, 2), (mcp1, 4), (mcp2, 13)],
    BOUTON8: [(mcp1, 6), (mcp1, 8), (mcp2, 15)],
    BOUTON9: [(mcp1, 7), (mcp1, 6), (mcp2, 5)],
    BOUTON10: [(mcp1, 1), (mcp1, 2), (mcp2, 4)],
}

list_dir = ['/home/pi/TwisterSimon/STEM/*.mp3']
song_dir:Dict[int, Song] = dict()
song_list = list()

# song_path1 = "/home/pi/STEM/Bad STEM Jackson Bass.mp3"
# song_path2 = "/home/pi/STEM/Bad STEM Jackson Drum.mp3"
# song_path3 = "/home/pi/STEM/Bad STEM Jackson Guitar.mp3"
# song_path4 = "/home/pi/STEM/Bad STEM Jackson Vocal_Back.mp3"
# song_path5 = "/home/pi/STEM/Bad STEM Jackson Drum_Clap.mp3"
# song_path6 = "/home/pi/STEM/Bad STEM Jackson Group_Moog.mp3"
# song_path7 = "/home/pi/STEM/Bad STEM Jackson Keys.mp3"
# song_path8 = "/home/pi/STEM/Bad STEM Jackson Vocal.mp3"

pygame.mixer.init(buffer=1024)
# pygame.init()

# sound1 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Bass.mp3")
# sound2 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Drum.mp3")
# sound3 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Guitar.mp3")
# sound4 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Vocal_Back.mp3")
# sound5 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Drum_Clap.mp3")
# sound6 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Group_Moog.mp3")
# sound7 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Keys.mp3")
# sound8 = pygame.mixer.Sound("/home/pi/STEM/Bad STEM Jackson Vocal.mp3")

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

for index, dir in enumerate(list_dir):
    print(glob.glob(dir))
    song_dir[index] = Song(dir, glob.glob(dir), [])
    for song_path in song_dir[index].all_parts:
        song_dir[index].all_processes.append(SongProcess(None, None, pygame.mixer.Sound(song_path)))

all_channels = [chan1, chan2, chan3, chan4, chan5, chan6, chan7, chan8, chan9, chan10]

# sound1.play()
# sound2.play()
# sound3.play()
# sound4.play()
# sound5.play()
# sound6.play()
# sound7.play()
# sound8.play()
for x in range(15, -1, -1):
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)

for x in range(0, 16):
    time.sleep(0.2)
    mcp1.digitalWrite(x, MCP23S17.LEVEL_HIGH)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_HIGH)

for x in range(15, -1, -1):
    time.sleep(0.2)
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)
time.sleep(1)


while True:
    num_song = -1
    print("la")
    for song_i, song_path in enumerate(song_dir[index].all_parts):
        # print(str(song_i) + ": " + song_path)
        # song_dir[index].all_processes.append(SongProcess(None, os.openpty()))
        # song_dir[index].all_processes[-1].process = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path], stdout=None, stdin=song_dir[index].all_processes[-1].master_slave[0], stderr=None)
        # song_dir[index].all_processes.append(SongProcess(None, None, pygame.mixer.Sound(song_path)))
        # os.write(all_master_slave[song_i][1], b'u')
        num_song += 1

    for process_i, process in enumerate(song_dir[index].all_processes):
        all_channels[process_i].play(process.song)
        all_channels[process_i].set_volume(0)
        # process.process.start()
    # chan1.play(sound1)
    # chan2.play(sound2)
    # chan3.play(sound3)
    # chan4.play(sound4)
    # chan5.play(sound5)
    # chan6.play(sound6)
    # chan7.play(sound7)
    # chan8.play(sound8)
    # chan1.set_volume(0)
    # chan2.set_volume(0)
    # chan3.set_volume(0)
    # chan4.set_volume(0)
    # chan5.set_volume(0)
    # chan6.set_volume(0)
    # chan7.set_volume(0)
    # chan8.set_volume(0)
    while chan8.get_busy():
        for bouton_i, bouton in enumerate(all_boutons):
            if bouton_i > num_song:
                continue
            if GPIO.input(bouton[0]) != bouton[1]:
                print(str(GPIO.input(bouton[0])) + " " + str(bouton[1]))
                print("changed" + str(bouton_i))
                # song_dir[index].all_processes[bouton_i].master_slave[1].send('trig')
                # os.write(song_dir[index].all_processes[bouton_i].master_slave[1], b'u')
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
    # for song_path in song_dir[index].all_parts:
    #     song_dir[index].all_processes.clear()

    for bouton in all_boutons:
        bouton[1] = 0



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

receiver1, sender1 = multiprocessing.Pipe()
receiver2, sender2 = multiprocessing.Pipe()
receiver3, sender3 = multiprocessing.Pipe()
receiver4, sender4 = multiprocessing.Pipe()
receiver5, sender5 = multiprocessing.Pipe()
receiver6, sender6 = multiprocessing.Pipe()
receiver7, sender7 = multiprocessing.Pipe()
receiver8, sender8 = multiprocessing.Pipe()
receiver9, sender9 = multiprocessing.Pipe()
receiver10, sender10 = multiprocessing.Pipe()

all_master_slave = [
    (receiver1, sender1), (receiver2, sender2), (receiver3, sender3), (receiver4, sender4),
    (receiver5, sender5), (receiver6, sender6), (receiver7, sender7), (receiver8, sender8),
    (receiver9, sender9), (receiver10,sender10)]

# pygame.mixer.init()
# pygame.mixer.music.load("../STEM/Bad STEM Jackson Bass.mp3")
# pygame.mixer.music.play()
# x = pygame.mixer.Sound("../STEM/Bad STEM Jackson Bass.mp3")
# x.play(0)
# pygame.mixer.Channel(0).play

def one_process_is_running(all_processes:list[SongProcess]) -> bool:
    for process in all_processes:
        if process.process.is_alive():
            return True
    return False

def run_song_part(song_path:str, receiver):
    # if receiver.poll():
    #     comm = receiver.recv()
    #     if comm is not None:
    #         if comm == "play":
    master, slave = os.openpty()
    # process = subprocess.Popen(["/usr/bin/mpg123", "-C", "-q", "-T", song_path], stdout=subprocess.DEVNULL, stdin=master)
    process = subprocess.Popen(["/usr/bin/mpg123", "-C", "-q", song_path], stdout=subprocess.DEVNULL, stdin=master)
    # os.write(slave, b'u')
    os.write(slave, b's')
    while process.poll() is None:
        if receiver.poll():
            comm = receiver.recv()
            if comm is not None:
                if comm == "play":
                    os.write(slave, b's')
                else:
                    os.write(slave, b'u')

# process = multiprocessing.Process(target=run_playlist, kwargs={"button":button, "receiver":receiver})

index = 0

while True:
    print("popen##################################################################")
    index += 1
    if index == len(song_dir):
        index = 0
    num_song = -1
    for song_i, song_path in enumerate(song_dir[index].all_parts):
        print(str(song_i) + ": " + song_path)
        # song_dir[index].all_processes.append(SongProcess(None, os.openpty()))
        # song_dir[index].all_processes[-1].process = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path], stdout=None, stdin=song_dir[index].all_processes[-1].master_slave[0], stderr=None)
        song_dir[index].all_processes.append(SongProcess(multiprocessing.Process(target=run_song_part, kwargs={"song_path":song_path, "receiver":all_master_slave[song_i][0]}), all_master_slave[song_i]))
        # os.write(all_master_slave[song_i][1], b'u')
        num_song += 1
    start_time = time.time()
    for process_i, process in enumerate(song_dir[index].all_processes):
        print("--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()
        process.process.start()
        # print("--- %s seconds ---" % (time.time() - start_time))

    for process_i, process in enumerate(song_dir[index].all_processes):
        # print("--- %s seconds ---" % (time.time() - start_time))
        # start_time = time.time()
        process.master_slave[1].send('play')
    # process1 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path1], stdout=None, stdin=master1, stderr=None)
    # os.write(slave1, b'u')
    # process2 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path2], stdout=None, stdin=master2, stderr=None)
    # os.write(slave2, b'u')
    # process3 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path3], stdout=None, stdin=master3, stderr=None)
    # os.write(slave3, b'u')
    # process4 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path4], stdout=None, stdin=master4, stderr=None)
    # os.write(slave4, b'u')
    # process5 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path5], stdout=None, stdin=master5, stderr=None)
    # os.write(slave5, b'u')
    # process6 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path6], stdout=None, stdin=master6, stderr=None)
    # os.write(slave6, b'u')
    # process7 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path7], stdout=None, stdin=master7, stderr=None)
    # os.write(slave7, b'u')
    # process8 = subprocess.Popen(["/usr/bin/mpg123", "-C", song_path8], stdout=None, stdin=master8, stderr=None)
    # os.write(slave8, b'u')


    while one_process_is_running(song_dir[index].all_processes):
        for bouton_i, bouton in enumerate(all_boutons):
            if bouton_i > num_song:
                continue
            if GPIO.input(bouton[0]) != bouton[1]:
                print(str(GPIO.input(bouton[0])) + " " + str(bouton[1]))
                print("changed" + str(bouton_i))
                song_dir[index].all_processes[bouton_i].master_slave[1].send('trig')
                # os.write(song_dir[index].all_processes[bouton_i].master_slave[1], b'u')
                if bouton[1] == 0:
                    bouton[1] = 1
                elif bouton[1] == 1:
                    bouton[1] = 0
        # a = input("butt")
        # if a == "1":
        #     os.write(slave1, b'u')
        # elif a == "2":
        #     os.write(slave2, b'u')
        # elif a == "3":
        #     os.write(slave3, b'u')
        # elif a == "4":
        #     os.write(slave4, b'u')
        # elif a == "5":
        #     os.write(slave5, b'u')
        # elif a == "6":
        #     os.write(slave6, b'u')
        # elif a == "7":
        #     os.write(slave7, b'u')
        # elif a == "8":
        #     os.write(slave8, b'u')
        pass

    for song_path in song_dir[index].all_parts:
        song_dir[index].all_processes.clear()

    for bouton in all_boutons:
        bouton[1] = 0