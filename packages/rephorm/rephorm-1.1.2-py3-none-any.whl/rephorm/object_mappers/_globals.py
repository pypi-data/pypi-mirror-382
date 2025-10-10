# central storage for globals
from os.path import defpath

figure_map = []

def set_figure_map(data):
    global figure_map
    figure_map.append(data)

def get_figure_map():
    global figure_map
    return figure_map

def reset_figure_map():
    global figure_map
    figure_map = []