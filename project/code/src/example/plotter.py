#!/usr/bin/python

import matplotlib.pyplot as plt

def plot():
    figure, (ax1, ax2) = plt.subplots(2, figsize=(16, 9))
    mng = plt.get_current_fig_manager()
    mng.window.wm_geometry("+0+0")
    ax1.plot([1, 2, 3], [1, 2, 3])
    
    ax2.plot([4, 5, 6], [4, 5, 6])
       
    plt.show()

if __name__ == "__main__":
    plot()
