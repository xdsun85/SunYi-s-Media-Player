from tkinter import *
from tkinter import filedialog
import pygame
import os

root = Tk()
# root.iconbitmap('portrait.ico')     # must be in format ".ico"
root.title('Sun Yi\'s Media Player')
root.geometry('300x345+100+100')
root.resizable(0, 0)
root.config(background='#EEEEEE')

pygame.mixer.init()
pygame.init()

menubar = Menu(root)
root.config(menu=menubar)

songs_list = []
cur_song = ''       # current song name
cur_len = 0         # current song length (in sec)
cur_prog = 0      # current play progress (in sec)
ff_span = rew_span = 5     # the span when FF or Rew (in sec)
offset = 0      # the moving offset when FF, Rew and ProgScale changing (in sec)
new_start = True        # whether a song is newly started (not pause / unpause)
paused = False
tar_ratio_str = ''          # the value of the ProgScale in real time (in str)
sc_changing = False     # whether the ProgScale is changing

# convert the second num into standard time display formation
def time_formatting(tot_secs):
    if tot_secs < 0.0:
        return 'Negative Time Input is NOT Acceptable!'

    hour = int(tot_secs / 3600)
    min = int(tot_secs % 3600 / 60)
    sec = int(tot_secs % 60)

    rs = ''
    if hour > 0:
        rs = '%s:' % hour
    if min < 10:
        rs += '0%s' % min
    else:
        rs += '%s' % min
    if sec < 10:
        rs += ':0%s' % sec
    else:
        rs += ':%s' % sec

    return rs

def load_music():
    global cur_song, cur_len, cur_prog, offset

    root.directory = filedialog.askdirectory()

    for song in os.listdir(root.directory):
        name, ext = os.path.splitext(song)
        if ext == '.mp3' or ext == '.flac' or ext == '.wav':
            songs_list.append(song)

    for song in songs_list:
        song_Listbox.insert('end', song)

    song_Listbox.selection_set(0)
    cur_song = songs_list[song_Listbox.curselection()[0]]
    cur_len = pygame.mixer.Sound(root.directory + '/' + cur_song).get_length()
    len_lbl['text'] = time_formatting(cur_len)
    cur_prog = 0
    offset = 0

def play_pause_music():
    global cur_song, cur_len, cur_prog, offset, new_start, paused

    if cur_song:
        if new_start:           # from stop to play (newly start)
            pygame.mixer.music.load(os.path.join(root.directory, cur_song))
            pygame.mixer.music.play(start=0, loops=0)
            prog_sc.set(0)
            play_pause_btn.config(image=pause_img)
            new_start = False
            cur_len = pygame.mixer.Sound(root.directory + '/' + cur_song).get_length()
            len_lbl['text'] = time_formatting(cur_len)
            cur_prog = 0
            offset = 0
        elif not paused:      # from play to pause
            pygame.mixer.music.pause()
            play_pause_btn.config(image=play_img)
            paused = True
        else:           # from pause to play
            pygame.mixer.music.unpause()
            play_pause_btn.config(image=pause_img)
            paused = False

def next_music():
    global cur_song, new_start, paused

    try:
        song_Listbox.select_clear(0, END)
        next = songs_list.index(cur_song) + 1
        if next < len(songs_list):
            song_Listbox.selection_set(next)
        else:
            song_Listbox.selection_set(0)
        cur_song = songs_list[song_Listbox.curselection()[0]]
        new_start = True
        play_pause_music()
    except:
        pass

def prev_music():
    global cur_song, new_start, paused

    try:
        song_Listbox.select_clear(0, END)
        prev = songs_list.index(cur_song) - 1
        if prev >= 0:
            song_Listbox.selection_set(prev)
        else:
            song_Listbox.selection_set(len(songs_list) - 1)
        cur_song = songs_list[song_Listbox.curselection()[0]]
        new_start = True
        play_pause_music()
    except:
        pass

def ff_music():
    global cur_len, cur_prog, offset

    try:
        if cur_prog + ff_span <= cur_len:
            cur_prog += ff_span
            pygame.mixer.music.set_pos(cur_prog)    # 我tm也是醉了！不是说相对偏移吗？！
            prog_sc.set(cur_prog * 100 / cur_len)
            offset += ff_span
        else:
            next_music()
    except:
        pass

def rew_music():
    global cur_len, cur_prog, offset

    try:
        if cur_prog - rew_span >= 0:
            cur_prog -= rew_span
            pygame.mixer.music.set_pos(cur_prog)
            prog_sc.set(cur_prog * 100 / cur_len)
            offset -= rew_span
        else:
            pygame.mixer.music.rewind()
            offset -= cur_prog      # Do NOT write: offset = 0
            cur_prog = 0
            prog_sc.set(0)
    except:
        pass

def change_prog_sc(txt):
    global tar_ratio_str

    tar_ratio_str = prog.get()

def prog_sc_drag_detn(evt):	        # ProgScale drag detection
    global tar_ratio_str, sc_changing, cur_len, cur_prog, offset
    # print(evt.x_root - root.winfo_x() - 8, evt.y_root - root.winfo_y() - 32)

    if 4 <= evt.x_root - root.winfo_x() - 8 <= 240 and 300 <= evt.y_root - root.winfo_y() - 32 <= 311:
        if str(evt.type) == 'ButtonRelease' and evt.num == 1:
            sc_changing = False
            if tar_ratio_str:
                tar_prog = cur_len * float(tar_ratio_str) / 100  # in sec
                pygame.mixer.music.set_pos(tar_prog)
                prog_sc.set(tar_prog * 100 / cur_len)
                offset += tar_prog - cur_prog

        if str(evt.type) == 'ButtonPress' and evt.num == 1:
            sc_changing = True

def change_vol_sc(txt):
    pygame.mixer.music.set_volume(float(vol.get()) / 87.5)      # float [0.0, 1.0]
    vol_lbl['text'] = vol.get()

def turn_up_vol():
    cur_vol = float(vol.get()) / 87.5
    tar_vol = min(1.2, cur_vol + 0.115)
    pygame.mixer.music.set_volume(tar_vol)
    vol_sc.set(tar_vol * 87.5)

def turn_dn_vol():
    cur_vol = float(vol.get()) / 87.5
    tar_vol = max(0.0, cur_vol - 0.115)
    pygame.mixer.music.set_volume(tar_vol)
    vol_sc.set(tar_vol * 87.5)

def key_detn(evt):
    if evt.char == ' ':
        play_pause_music()
    elif evt.keysym == 'Left':
        rew_music()
    elif evt.keysym == 'Right':
        ff_music()
    elif evt.keysym == 'Up':
        turn_up_vol()
    elif evt.keysym == 'Down':
        turn_dn_vol()

def sel_item(evt):
    global cur_song, new_start

    i = song_Listbox.curselection()[0]
    song_Listbox.selection_set(i)
    cur_song = songs_list[song_Listbox.curselection()[0]]
    new_start = True
    play_pause_music()

open_menu = Menu(menubar, tearoff=False)
open_menu.add_command(label='Browse', command=load_music)
menubar.add_cascade(label='Open', menu=open_menu)

song_Listbox = Listbox(root, bg='black', fg='white', width=100, height=14, selectmode='single')
song_Listbox.bind('<Double-Button-1>', sel_item)
song_Listbox.pack()

root.focus_set()
root.bind('<Key>', key_detn)
root.bind('<Left>', key_detn)
root.bind('<Right>', key_detn)
root.bind('<Up>', key_detn)
root.bind('<Down>', key_detn)
root.bind('<Button-1>', prog_sc_drag_detn)
root.bind('<ButtonRelease-1>', prog_sc_drag_detn)

prog_lbl = Label(root, text='00:00', anchor='w')
prog_lbl.place(x=2, y=263, width=120, height=10)

len_lbl = Label(root, text='00:00', anchor='e')
len_lbl.place(x=122, y=263, width=120, height=10)

vol_lbl = Label(root, text='50', anchor='c')
vol_lbl.place(x=245, y=263, width=55, height=10)

prog = StringVar()
prog_sc = Scale(root, from_=0, to=100, resolution=0.1, orient=HORIZONTAL, length=240, width=10, variable=prog, showvalue=0, sliderlength=15, command=change_prog_sc)
prog_sc.set(0)      # set initial value
prog_sc.place(x=2, y=278, width=242, height=16)

vol = StringVar()
vol_sc = Scale(root, from_=0, to=100, resolution=1, orient=HORIZONTAL, length=49, width=10, variable=vol, showvalue=0, sliderlength=10, command=change_vol_sc)
vol_sc.set(50)      # set initial value
vol_sc.place(x=245, y=278, width=55, height=16)

rew_img = PhotoImage(file='./Rewind_white_icon.png')        # 44 × 44
prev_img = PhotoImage(file='./Previous_white_icon.png')     # 44 × 44
play_img = PhotoImage(file='./Play_icon.png')                       # 44 × 44
pause_img = PhotoImage(file='./Pause_icon.png')                 # 44 × 44
next_img = PhotoImage(file='./Next_white_icon.png')           # 44 × 44
ff_img = PhotoImage(file='./FastForward_white_icon.png')    # 44 × 44

rew_btn = Button(root, image=rew_img, borderwidth=0, command=rew_music)
prev_btn = Button(root, image=prev_img, borderwidth=0, command=prev_music)
play_pause_btn = Button(root, image=play_img, borderwidth=0, command=play_pause_music)
next_btn = Button(root, image=next_img, borderwidth=0, command=next_music)
ff_btn = Button(root, image=ff_img, borderwidth=0, command=ff_music)

rew_btn.place(x=8, y=297, width=44, height=44)
prev_btn.place(x=68, y=297, width=44, height=44)
play_pause_btn.place(x=128, y=297, width=44, height=44)
next_btn.place(x=188, y=297, width=44, height=44)
ff_btn.place(x=248, y=297, width=44, height=44)

SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

def check_state():
    global cur_len, cur_prog, offset, sc_changing

    cur_prog = offset + pygame.mixer.music.get_pos() / 1000  # / 1000 ms
    prog_ratio = cur_prog * 100 / cur_len if cur_len != 0 else 0

    if not sc_changing:
        prog_sc.set(prog_ratio)
    if cur_prog > 0:
        prog_lbl['text'] = time_formatting(cur_prog)

    for event in pygame.event.get():
        if event.type == SONG_END:
            next_music()

    root.after(100, check_state)      # check every 100 ms

check_state()

root.mainloop()     # It seems that only UI is refreshed