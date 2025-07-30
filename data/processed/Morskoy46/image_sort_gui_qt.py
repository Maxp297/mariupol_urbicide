#!/usr/bin/env python3
# image_sort_gui_qt.py
# PySimpleGUIQt-based image sorter for rapid triage (fixed for image bytes handling)

import os
import shutil
import PySimpleGUIQt as sg
from PIL import Image
import io

SRC_DIR = os.path.join(os.path.dirname(__file__), 'telegram_images_raw')
DST_DIR = os.path.join(os.path.dirname(__file__), 'telegram_images_sorted', 'building_facade_reference')
os.makedirs(DST_DIR, exist_ok=True)

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
img_files = [f for f in os.listdir(SRC_DIR) if os.path.splitext(f)[1].lower() in IMG_EXTS]
img_files.sort()

layout = [
    [sg.Image(key='-IMAGE-', size=(900, 600))],
    [sg.Text('', key='-FILENAME-')],
    [sg.Button('Move to Facade Folder', key='-MOVE-', button_color=('white', 'green')),
     sg.Button('Skip', key='-SKIP-'),
     sg.Button('Delete', key='-DELETE-', button_color=('white', 'red')),
     sg.Button('Exit')],
    [sg.Input('', key='-HIDDEN-', visible=False)]
]

window = sg.Window('Image Sorter (Qt)', layout, resizable=True, finalize=True)
idx = 0

def show_image(idx):
    if idx >= len(img_files):
        window['-IMAGE-'].update(filename=None)
        window['-FILENAME-'].update('Done! No more images.')
        return
    img_path = os.path.join(SRC_DIR, img_files[idx])
    img = Image.open(img_path)
    img.thumbnail((900, 600))
    tmp_path = os.path.join(os.path.dirname(__file__), '.tmp_image_sorter.png')
    img.save(tmp_path, format='PNG')
    window['-IMAGE-'].update(filename=tmp_path)
    window['-FILENAME-'].update(f'{img_files[idx]} ({idx+1}/{len(img_files)})')
    window['-HIDDEN-'].set_focus()

show_image(idx)
window['-HIDDEN-'].set_focus()

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    # Hotkeys: Z (move), X (skip), C (delete)
    elif event == '-MOVE-' or event == 'z':
        src = os.path.join(SRC_DIR, img_files[idx])
        dst = os.path.join(DST_DIR, img_files[idx])
        shutil.move(src, dst)
        idx += 1
        show_image(idx)
        window['-HIDDEN-'].set_focus()
    elif event == '-SKIP-' or event == 'x':
        idx += 1
        show_image(idx)
        window['-HIDDEN-'].set_focus()
    elif event == '-DELETE-' or event == 'c':
        src = os.path.join(SRC_DIR, img_files[idx])
        os.remove(src)
        idx += 1
        show_image(idx)
        window['-HIDDEN-'].set_focus()
    elif event is not None and isinstance(event, str) and event.lower() in ['z', 'x', 'c']:
        # Defensive: ensure lowercase keys work
        if event.lower() == 'z':
            src = os.path.join(SRC_DIR, img_files[idx])
            dst = os.path.join(DST_DIR, img_files[idx])
            shutil.move(src, dst)
            idx += 1
            show_image(idx)
            window['-HIDDEN-'].set_focus()
        elif event.lower() == 'x':
            idx += 1
            show_image(idx)
            window['-HIDDEN-'].set_focus()
        elif event.lower() == 'c':
            src = os.path.join(SRC_DIR, img_files[idx])
            os.remove(src)
            idx += 1
            show_image(idx)
            window['-HIDDEN-'].set_focus()

window.close()
