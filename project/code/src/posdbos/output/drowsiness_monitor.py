#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from time import sleep

import pygame
from collections import deque
import logging

resolution = (1600, 900)

MENTAL_STATES = {
    "drowsy": {
        "color": (127, 0, 0),
        "description": "PLEASE take a break immediately!",
        "count": 0
    },
    "tired": {
        "color": (230, 200, 1),
        "description": "Please consider taking a break soon",
        "count": 0
    },
    "awake": {
        "color": (0, 127, 0),
        "description": "No signs of drowsiness!",
        "count": 0
    },
}

class DrowsinessMonitor(object):
    '''
    Simple Monitor which shows red (drowsy) and green (awake)
    '''


    def __init__(self):
        self.running = True
        self.info = ""
        self.drowsyCount = 0
        self.maxlen = 60
        self.results = deque(maxlen=self.maxlen)
        self._initStates()

    def _initStates(self):
        self.state = "awake";
        self.states = MENTAL_STATES
        for _,v in self.states.iteritems():
            v["count"] = 0

    def _handleEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                    pygame.quit()
                    return

    def _setText(self):
        font = pygame.font.Font(None, 64)
        text = font.render(self.curState["description"], 1, (255, 255, 255))
        text_pos = text.get_rect()
        text_pos.centery = self.screen.get_rect().centery
        text_pos.centerx = self.screen.get_rect().centerx
        self.screen.blit(text, text_pos)

        if self.info != None:
            info = font.render(self.info, 1, (255, 255, 255))
            info_pos = info.get_rect()
            info_pos.centery = self.screen.get_rect().centery+64
            info_pos.centerx = self.screen.get_rect().centerx
            self.screen.blit(info, info_pos)

        counts = "; ".join([k + ": " + str(v["count"]) for k,v in self.states.iteritems()])
        drowsyAlert = font.render(counts, 1, (255, 255, 255))
        drowsyAlert_pos = drowsyAlert.get_rect()
        drowsyAlert_pos.centery = self.screen.get_rect().centery-200
        drowsyAlert_pos.centerx = self.screen.get_rect().centerx
        self.screen.blit(drowsyAlert, drowsyAlert_pos)

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)

        while self.running:
            try:
                self._handleEvent()
                self.curState = MENTAL_STATES[self.state]
                self.screen.fill(self.curState["color"])
                self._setText()
                pygame.display.flip()
                sleep(0.5)
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                logging.error(e.message)
                self.close()

    def close(self):
        self.running = False

    def setState(self, status, info=None):
        self.results.append(status)
        drowsySum = sum(self.results)
        if drowsySum > (0.6*self.maxlen):
            self.state = "drowsy"
        elif drowsySum > (0.4*self.maxlen):
            self.state = "tired"
        else:
            self.state = "awake"
        self.states[self.state]["count"] += 1
        self.info = "drowsySum %d, state: %d" % (drowsySum, status)