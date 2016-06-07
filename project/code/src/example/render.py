#!/usr/bin/python
# Renders a window with graph values for each sensor and a box for gyro values.

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import psyco
    psyco.full()
except ImportError:
    print 'No psyco. Expect poor performance. Not really...'

import logging
import pygame
from pygame import FULLSCREEN
import gevent
from emokit.emotiv import Emotiv


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)

'''Tested value for no movement'''
GYRO_DEFAULT = 22*2

quality_color = {
    "0": (0, 0, 0),
    "1": (255, 0, 0),
    "2": (255, 0, 0),
    "3": (255, 255, 0),
    "4": (255, 255, 0),
    "5": (0, 255, 0),
    "6": (0, 255, 0),
    "7": (0, 255, 0),
}

'''Quality in EPOC+ reaches from 0 - 15'''
old_quality_color = {"0": (0, 0, 0)}

def createQuality():
    for i in range(4):
        old_quality_color[str(1+i)] = (255, 0, 0)
        old_quality_color[str(4+i)] = (255, 255, 0)
        old_quality_color[str(8+i)] = (0, 255, 0)
        old_quality_color[str(12+i)] = (0, 255, 0)

createQuality()

resolution = (1600, 900)
screen = None
emotiv = None
recordings = []
recording = False
fullscreen = False


class Grapher(object):
    """
    Worker that draws a line for the sensor value.
    """
    def __init__(self, screen, name, i):
        """
        Initializes graph worker
        """
        self.screen = screen
        self.name = name
        self.range = float(1 << 13)
        self.x_offset = 40
        self.y = i * gheight
        self.buffer = []
        font = pygame.font.Font(None, 24)
        self.text = font.render(self.name, 1, (255, 0, 0))
        self.text_pos = self.text.get_rect()
        self.text_pos.centery = self.y + gheight
        self.first_packet = True
        self.y_offset = 0

    def update(self, packet):
        """
        Appends value and quality values to drawing buffer.
        """
        if len(self.buffer) == resolution[0] - self.x_offset:
            self.buffer = self.buffer[1:]
        self.buffer.append([packet.sensors[self.name]['value'], packet.sensors[self.name]['quality'], packet.old_model])

    def calc_y(self, val):
        """
        Calculates line height from value.
        """
        return val - self.y_offset + gheight

    def draw(self):
        """
        Draws a line from values stored in buffer.
        """
        if len(self.buffer) == 0:
            return

        if self.first_packet:
            self.y_offset = self.buffer[0][0]
            self.first_packet = False
        pos = self.x_offset, self.calc_y(self.buffer[0][0]) + self.y
        for i, (value, quality, old_model) in enumerate(self.buffer):
            y = self.calc_y(value) + self.y
            if old_model:
                color = old_quality_color[str(quality)]
            else:
                color = quality_color[str(quality)]
            pygame.draw.line(self.screen, color, pos, (self.x_offset + i, y))
            pos = (self.x_offset + i, y)
        self.screen.blit(self.text, self.text_pos)

def handleEvents():
    global emotiv, screen, fullscreen, recording, recordings
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            emotiv.close()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                emotiv.close()
                return
            elif event.key == pygame.K_f:
                if fullscreen:
                    screen = pygame.display.set_mode(resolution)
                    fullscreen = False
                else:
                    screen = pygame.display.set_mode(resolution, FULLSCREEN, 16)
                    fullscreen = True
            elif event.key == pygame.K_r:
                if not recording:
                    record_packets = []
                    recording = True
                else:
                    recording = False
                    recordings.append(list(record_packets))
                    record_packets = None

def main():
    """
    Creates pygame window and graph drawing workers for each sensor.
    """
    global gheight, emotiv, pygame, screen
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    graphers = []
    record_packets = []
    updated = False
    middle_x, middle_y = resolution[0]/2, resolution[1]/2
    cursor_x, cursor_y = middle_x, middle_y
    for name in 'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' '):
        graphers.append(Grapher(screen, name, len(graphers)))
    emotiv = Emotiv(display_output=False)
    gevent.spawn(emotiv.setup)
    gevent.sleep(0)
    while emotiv.running:
        handleEvents()
        packets_in_queue = 0
        try:
            cursor_x, cursor_y = middle_x, middle_y
            while packets_in_queue < 8:
                packet = emotiv.dequeue()
                if abs(packet.gyro_x) > 1:
                    cursor_x += packet.gyro_x-GYRO_DEFAULT
                if abs(packet.gyro_y) > 1:
                    cursor_y += packet.gyro_y-GYRO_DEFAULT
                map(lambda x: x.update(packet), graphers)
                if recording:
                    record_packets.append(packet)
                updated = True
                packets_in_queue += 1
        except (Exception, KeyboardInterrupt) as e:
            raise e

        if updated:
            screen.fill((75, 75, 75))
            map(lambda x: x.draw(), graphers)
            cursor_x = middle_x+cursor_x/8
            cursor_y = middle_y+cursor_y/8
            pygame.draw.rect(screen, (255, 0, 255), [cursor_x, cursor_y, 5, 5], 5)
            pygame.display.flip()
            updated = False
        gevent.sleep(0)

if __name__ == "__main__":
    
    try:
        gheight = (resolution[1]-resolution[1]*0.1) / 14
        main()
    except (Exception, KeyboardInterrupt):
        logging.exception()
    finally:
        pygame.quit()
        sys.exit(0) 
