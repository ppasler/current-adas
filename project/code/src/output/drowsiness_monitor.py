#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import threading
from time import sleep

import pygame
from config.config import ConfigProvider


resolution = (1600, 900)

MENTAL_STATES = {
    "drowsy": {
        "color": (127, 0, 0),
        "description": "Please have a kitkat and a break"
    },
    "awake": {
        "color": (0, 127, 0),
        "description": "You're fit like a sneaker :)"
    },
}

class DrowsinessMonitor(object):
    '''
    Simple Monitor which shows red (drowsy) and green (awake)
    '''


    def __init__(self):
        self.running = True
        self.state = "awake";
        self.info = ""
        self.classes = ConfigProvider().getConfig("class")
        self.drowsyCount = 0

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
        
        drowsyAlert = font.render("drowsyCount: " + str(self.drowsyCount), 1, (255, 255, 255))
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
                print e.message
                self.close()

    def close(self):
        self.running = False
    
    def setStatus(self, status, info=None):
        self.state = self.classes[str(status)]
        if self.state == "drowsy":
            self.drowsyCount += 1
        self.info = str(info)

if __name__ == "__main__":
    d = DrowsinessMonitor()
    t = threading.Thread(target=d.run)
    t.start()
    
    for i in range(10):
        d.setStatus(i%2, i%2)
        sleep(2)

    d.close()
    t.join()