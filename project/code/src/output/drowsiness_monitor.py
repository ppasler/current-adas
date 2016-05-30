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


resolution = (1600, 900)

METAL_STAES = {
    "drowsy": {
        "color": (127, 0, 0),
        "description": "Please stop for a break"
    },
    "awake": {
        "color": (0, 127, 0),
        "description": "You're fit like a sneaker :)"
    },
}

class DrowsinessMonitor(object):
    '''
    Simple Monitor whoch shows red (drowsy) and green (awake)
    '''


    def __init__(self):
        self.running = True
        self.state = "awake";

    def _handleEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                    return

    def _setText(self):
        font = pygame.font.Font(None, 64)
        text = font.render(self.curState["description"], 1, (255, 255, 255))
        text_pos = text.get_rect()
        text_pos.centery = self.screen.get_rect().centery
        text_pos.centerx = self.screen.get_rect().centerx
        self.screen.blit(text, text_pos)

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)
        
        while self.running:
            try:
                self._handleEvent()
                self.curState = METAL_STAES[self.state]
                self.screen.fill(self.curState["color"])
                self._setText()
                pygame.display.flip()
                sleep(1)
            except (Exception, KeyboardInterrupt):
                self.close()
                break
            
    def close(self):
        self.running = False
    
    def setStatus(self, status):
        '''
        Value > 0.5 means "drowsy", else "awake" 
        '''
        if status > 0.5:
            self.state = "awake"
        else:
            self.state = "drowsy"

if __name__ == "__main__":
    d = DrowsinessMonitor()
    t = threading.Thread(target=d.run)
    t.start()
    
    for i in range(10):
        d.setStatus(i%2)
        sleep(2)

    d.close()
    t.join()