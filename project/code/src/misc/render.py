#!/usr/bin/python
# Renders a window with graph values for each sensor and a box for gyro values.

import logging
import sys, os

import gevent
from pygame import FULLSCREEN
import pygame
import numpy as np
from emokit.emotiv import Emotiv


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import psyco
    psyco.full()
except ImportError:
    print 'No psyco. Expect poor performance. Not really...'



os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
resolution = (1600, 900)

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

class Grapher(object):
    """
    Worker that draws a line for the sensor value.
    """
    def __init__(self, screen, gheight, name, i):
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
        value = packet.sensors[self.name]['value']
        if np.isnan(value):
            value = 0
        self.buffer.append([value, packet.sensors[self.name]['quality'], packet.old_model])

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

class EEGRenderer():

    def __init__(self, channels, gheight):
        """
        Creates pygame window and graph drawing workers for each sensor.
        """
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)
        self.graphers = []

        self.record_packets = []
        self.fullscreen = False
        self.recording = False
        self.updated = False
        self.middle_x, self.middle_y = resolution[0]/2, resolution[1]/2
        for i, name in enumerate(channels):
            self.graphers.append(Grapher(self.screen, gheight, name, i))

        self.emotiv = Emotiv(display_output=False)
        gevent.spawn(self.emotiv.setup)
        gevent.sleep(0)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.emotiv.close()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.emotiv.close()
                    return
                elif event.key == pygame.K_f:
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(resolution)
                        self.fullscreen = False
                    else:
                        self.screen = pygame.display.set_mode(resolution, FULLSCREEN, 16)
                        self.fullscreen = True
                elif event.key == pygame.K_r:
                    if not self.recording:
                        self.record_packets = []
                        self.recording = True
                    else:
                        self.recording = False
                        self.recordings.append(list(self.record_packets))
                        self.record_packets = None


    def update(self, cursor_x, cursor_y):
        if self.updated:
            self.screen.fill((75, 75, 75))
            map(lambda x:x.draw(), self.graphers)
            pygame.draw.rect(self.screen, (255, 0, 255), [cursor_x, cursor_y, 5, 5], 5)
            pygame.display.flip()
            self.updated = False

    def main(self):
        while self.emotiv.running:
            self.handleEvents()
            packets_in_queue = 0
            try:
                cursor_x, cursor_y = self.middle_x, self.middle_y
                while packets_in_queue < 8:
                    packet = self.emotiv.dequeue()
                    if abs(packet.gyro_x) > 1:
                        cursor_x += packet.gyro_x-GYRO_DEFAULT
                    if abs(packet.gyro_y) > 1:
                        cursor_y += packet.gyro_y-GYRO_DEFAULT
                    map(lambda x: x.update(packet), self.graphers)
                    if self.recording:
                        self.record_packets.append(packet)
                    self.updated = True
                    packets_in_queue += 1
                cursor_x = self.middle_x + cursor_x / packets_in_queue
                cursor_y = self.middle_y + cursor_y / packets_in_queue
            except (Exception, KeyboardInterrupt) as e:
                raise e
    
            self.update(cursor_x, cursor_y)
            gevent.sleep(0)

if __name__ == "__main__":

    try:
        channels = 'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' ')
        gheight = (resolution[1]-resolution[1]*0.1) / len(channels)
        e = EEGRenderer(channels, gheight)
        e.main()
    except (Exception, KeyboardInterrupt):
        logging.exception()
    finally:
        pygame.quit()
        sys.exit(0) 
