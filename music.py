import os
import pickle
import random
from tkinter import *
from tkinter import ttk
import pygame
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from global_function import string_similarity, refine_sentence, data_exist, sr_dynamic_energy_on, sr_dynamic_energy_off
import webScraping
from tinytag import TinyTag
import time

global music_window, app
defined_music_window = False
with open('Resources/file path/folder path.pck', 'rb') as file:
    folder_path = pickle.load(file)
    global music_path
    for path in folder_path:
        if 'music' in path['name']:
            music_path = path['path']

pygame.init()
pygame.mixer.music.set_volume(0.8)
MUSIC_END = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(MUSIC_END)
list_of_song = {}

class Player(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()

        self.playlist = list_of_song
        self.current = 0
        self.paused = False
        self.song_elapsed_time_status = None
        self.check_endevent_status = None

        self.back_btn_img = PhotoImage(file='Resources/images/music/back.png')
        self.next_btn_img = PhotoImage(file='Resources/images/music/next.png')
        self.play_btn_img = PhotoImage(file='Resources/images/music/play.png')
        self.pause_btn_img = PhotoImage(file='Resources/images/music/pause.png')
        self.music_theme_img = PhotoImage(file='Resources/images/music/music.gif')

        self.create_frames()
        self.track_widgets()
        self.control_widgets()
        self.tracklist_widgets()

    def down_clicked(self, event):
        item_chosen = self.list.curselection()[0]
        self.list.selection_clear(item_chosen)
        item_chosen = (item_chosen + 1) % len(self.playlist['path'])
        self.list.selection_set(item_chosen)
        if item_chosen == 0:
            self.list.activate(item_chosen)
            self.list.yview_moveto('0.0')

    def up_clicked(self, event):
        item_chosen = self.list.curselection()[0]
        self.list.selection_clear(item_chosen)
        item_chosen = (item_chosen + len(self.playlist['path']) - 1) % len(self.playlist['path'])
        self.list.selection_set(item_chosen)
        if item_chosen == len(self.playlist['path']) - 1:
            self.list.activate(item_chosen)
            self.list.yview_moveto('1.0')

    def create_frames(self):
        self.track = LabelFrame(self, text='Song Track', font=("times new roman", 15, "bold"), bg='grey', fg='white',
                                bd=5, relief=GROOVE)
        self.track.config(width=410,height=300)
        self.track.grid(row=0, column=0, padx=10, pady=5)

        self.tracklist = LabelFrame(self, text=f'PlayList - {str(len(self.playlist["path"]))}',
                                    font=("times new roman", 15, "bold"), bg='grey', fg='white', bd=5, relief=GROOVE)
        self.tracklist.config(width=190, height=400)
        self.tracklist.grid(row=0, column=1, rowspan=2, pady=5)

        self.controls = Frame(self)
        self.controls.config(width=410, height=80)
        self.controls.grid(row=1, column=0)

        self.master.bind('<Down>', self.down_clicked)
        self.master.bind('<Up>', self.up_clicked)
        self.master.bind('<Return>', self.choose_song)

    def track_widgets(self):
        self.canvas = Label(self.track, image=self.music_theme_img)
        self.canvas.configure(width=400, height=240)
        self.canvas.grid(row=0, column=0)

        self.songtrack = Label(self.track, font=("times new roman", 16, "bold"),
                                  bg="white", fg="dark blue")
        self.songtrack['text'] = 'MP3 PLAYER'
        self.songtrack.config(width=30, height=1)
        self.songtrack.grid(row=1, column=0, padx=10)

    def convert_to_time_format(self, seconds):
        if seconds < 3600:
            time_format = '%M:%S'
        else:
            time_format = '%H:%M:%S'

        return str(time.strftime(time_format, time.gmtime(seconds)))

    def slide(self, event):
        self.slider_pressed = True
        current_position = self.slider.get()

        initial_value = 45 if current_position < 3600 else 36

        self.slider_time.config(text=self.convert_to_time_format(current_position))
        distance_begin_to_end = 315
        self.slider_time.place(x=initial_value + distance_begin_to_end / self.playlist['duration'][self.current] * current_position,
                               y=30)

    def slider_released(self, event):
        self.slider_last_drag_pos = int(self.slider.get())
        pygame.mixer.music.load(self.playlist['path'][self.current])

        pygame.mixer.music.play()
        pygame.mixer.music.rewind()
        pygame.mixer.music.set_pos(self.slider_last_drag_pos)
        if self.paused:
            pygame.mixer.music.pause()
        self.slider_time.place_forget()
        self.slider_pressed = False

    def song_elapsed_time(self):
        current_position = self.slider_last_drag_pos + pygame.mixer.music.get_pos() // 1000
        self.song_elapsed_time_label['text'] = self.convert_to_time_format(current_position)
        if not self.slider_pressed:
            self.slider['value'] = current_position
        self.song_elapsed_time_status = self.after(100, self.song_elapsed_time)

    def control_widgets(self):
        self.control_buttons = Frame(self.controls)
        self.control_buttons.grid(row=0, column=0, columnspan=3)

        self.prev = Button(self.control_buttons, image=self.back_btn_img, borderwidth=0, command=self.prev_song)
        self.prev.grid(row=0, column=0, padx=10)

        self.play = Button(self.control_buttons, image=self.play_btn_img, borderwidth=0, command=self.continue_song)
        self.play.grid(row=0, column=1)

        self.pause = Button(self.control_buttons, image=self.pause_btn_img, borderwidth=0, command=self.pause_song)
        self.pause.grid(row=0, column=1)

        self.next = Button(self.control_buttons, image=self.next_btn_img, borderwidth=0, command=self.next_song)
        self.next.grid(row=0, column=2, padx=10)

        self.song_elapsed_time_label = Label(self.controls, justify=RIGHT, width=6, font=('arial', 9))
        self.song_elapsed_time_label.grid(row=1, column=0, sticky='E', padx=3)

        self.slider = ttk.Scale(self.controls, orient=HORIZONTAL, length=330, command=self.slide)
        self.slider.grid(row=1, column=1, pady=10)
        self.slider_pressed = False
        self.slider.bind('<ButtonRelease>', self.slider_released)
        self.slider_last_drag_pos = 0

        # self.slider.bind('<1>', self.slider_jump)
        self.song_duration_label = Label(self.controls, justify=LEFT, font=('arial', 9))
        self.song_duration_label.grid(row=1, column=2, sticky='W', padx=3)

        self.slider_time = Label(self.controls)

    def tracklist_widgets(self):
        self.scrollbar = Scrollbar(self.tracklist, orient=VERTICAL)
        self.scrollbar.grid(row=0, column=1, rowspan=5, sticky='ns')

        self.list = Listbox(self.tracklist, selectmode=SINGLE,
                               yscrollcommand=self.scrollbar.set, selectbackground='sky blue')
        for song in self.playlist['name']:
            self.list.insert(END, song)
        self.list.config(height=23)
        self.list.bind('<Double-1>', self.choose_song)

        self.scrollbar.config(command=self.list.yview)
        self.list.grid(row=0, column=0, rowspan=5)
        self.list.selection_set(0)
        self.list.activate(0)
        self.list.focus_set()

    def check_endevent(self):
        for event in pygame.event.get():
            if event.type == MUSIC_END:
                self.next_song()

        self.check_endevent_status = self.after(100, self.check_endevent)

    def pause_song(self, event=None):
        self.paused = True
        self.master.unbind('<space>')
        self.master.bind('<space>', self.continue_song)
        pygame.mixer.music.pause()
        self.after_cancel(self.check_endevent_status)
        self.check_endevent_status = None
        self.after_cancel(self.song_elapsed_time_status)
        self.song_elapsed_time_status = None
        self.play.tkraise()
        sr_dynamic_energy_on()

    def continue_song(self, event=None):
        sr_dynamic_energy_off()
        self.paused = False
        self.master.unbind('<space>')
        self.master.bind('<space>', self.pause_song)
        pygame.mixer.music.unpause()
        self.check_endevent_status = self.check_endevent()
        self.song_elapsed_time_status = self.song_elapsed_time()
        self.pause.tkraise()

    def prev_song(self):
        self.list.itemconfigure(self.current, bg='white')
        self.list.selection_clear(self.list.curselection()[0])
        self.current = (self.current + len(self.playlist['path']) - 1) % len(self.playlist['path'])
        self.list.selection_set(self.current)
        self.list.activate(self.current)
        self.play_song()

    def next_song(self):
        self.list.itemconfigure(self.current, bg='white')
        self.list.selection_clear(self.list.curselection()[0])
        self.current = (self.current + 1) % len(self.playlist['path'])
        self.list.selection_set(self.current)
        self.list.activate(self.current)
        self.play_song()

    def play_song(self):
        sr_dynamic_energy_off()
        self.slider.config(to=self.playlist['duration'][self.current], value=0)
        self.song_duration_label['text'] = str(self.convert_to_time_format(self.playlist['duration'][self.current]))
        self.slider_last_drag_pos = 0
        pygame.mixer.music.load(self.playlist['path'][self.current])
        self.songtrack['anchor'] = 'w'
        self.songtrack['text'] = self.playlist['name'][self.current]
        self.pause.tkraise()
        self.list.itemconfigure(self.current, bg='sky blue')
        self.paused = False
        pygame.mixer.music.play()
        self.master.unbind('<space>')
        self.master.bind('<space>', self.pause_song)
        if self.check_endevent_status is None:
            self.check_endevent_status = self.check_endevent()
        if self.song_elapsed_time_status is None:
            self.song_elapsed_time_status = self.song_elapsed_time()

    def choose_song(self, event):
        self.list.itemconfigure(self.current, bg='white')
        self.current = self.list.curselection()[0]
        self.play_song()

    def jump_to_song(self, pos):
        self.list.itemconfigure(self.current, bg='white')
        self.list.selection_clear(self.list.curselection()[0])
        self.current = pos
        self.list.selection_set(self.current)
        self.list.activate(self.current)
        self.play_song()

def Initialize_Music_Window(root):
    global app, music_window, defined_music_window
    music_window = Toplevel(root)
    music_window.geometry('590x410')
    music_window.resizable(False, False)
    music_window.title('MP3 Player')
    music_window.iconbitmap('Resources/images/music/mp3 player.ico')
    music_window.protocol('WM_DELETE_WINDOW', Stop_Music)

    defined_music_window = True

    app = Player(master=music_window)

def Play_Music(root, song_name):
    pos = -1
    if list_of_song:
        if song_name == 'music':
            pos = random.randint(0, len(list_of_song['path']) - 1)
        else:
            name_match = []
            ignore_letters = [',', '.', '(', ')', '_', '-', '!']
            for i, song_title in enumerate(list_of_song['name']):
                for letter in ignore_letters:
                    song_title = song_title.replace(letter, ' ')
                song_title = refine_sentence(song_title)
                name_match.append([song_title, string_similarity(song_title, song_name), i])

            name_match.sort(key=lambda x: x[1], reverse=True)
            for x in name_match:
                candidate_song = x[0]
                for letter in ignore_letters:
                    candidate_song = candidate_song.replace(letter, ' ')
                candidate_song = refine_sentence(candidate_song)
                if data_exist([song_name], candidate_song, 6):
                    pos = x[2]
                    break

    if pos == -1:
        webScraping.youtube(song_name)
        return
    global app, defined_music_window
    initialize = False
    if not defined_music_window:
        list_of_song['path'][0], list_of_song['path'][pos] = list_of_song['path'][pos], list_of_song['path'][0]
        list_of_song['name'][0], list_of_song['name'][pos] = list_of_song['name'][pos], list_of_song['name'][0]
        list_of_song['duration'][0], list_of_song['duration'][pos] = list_of_song['duration'][pos], list_of_song['duration'][0]
        #shuffle songs
        tmp_path = list_of_song['path'][1:]
        tmp_name = list_of_song['name'][1:]
        tmp_duration = list_of_song['duration'][1:]
        pos = [x for x in range(len(list_of_song['path']) - 1)]
        random.shuffle(pos)
        for i in range(len(pos)):
            list_of_song['path'][i + 1] = tmp_path[pos[i]]
            list_of_song['name'][i + 1] = tmp_name[pos[i]]
            list_of_song['duration'][i + 1] = tmp_duration[pos[i]]
        Initialize_Music_Window(root)
        initialize = True

    if song_name == 'music':
        if initialize:
            app.play_song()
        else:
            app.continue_song()
    else:
        if initialize:
            app.play_song()
        else:
            app.jump_to_song(pos)

def Pause_Music():
    global app
    if not defined_music_window:
        return False

    app.pause_song()
    return True

def Stop_Music():
    global music_window, defined_music_window
    if not defined_music_window:
        return

    pygame.mixer.music.unload()
    music_window.destroy()
    defined_music_window = False

def Next_Song():
    global app
    if not defined_music_window:
        return False

    app.next_song()
    return True

def Prev_Song():
    global app
    if not defined_music_window:
        return False

    app.prev_song()
    return True

def Update():
    global list_of_song
    if os.path.isdir(music_path):
        tmp_list_of_song = {}
        tmp_list_of_song['path'] = []
        tmp_list_of_song['name'] = []
        tmp_list_of_song['duration'] = []
        songlist = os.listdir(music_path)
        for song in songlist:
            path = os.path.join(music_path, song)
            if Check_Audio_Format(path):
                tag = TinyTag.get(path)
                if tag.duration is None:
                    continue
                tmp_list_of_song['path'].append(path)
                if tag.title is not None:
                    name = tag.title
                    if tag.artist is not None:
                        name += ' - ' + tag.artist
                    tmp_list_of_song['name'].append(name)
                else:
                    tmp_list_of_song['name'].append(os.path.splitext(os.path.basename(path))[0])
                tmp_list_of_song['duration'].append(int(tag.duration))

        with open('Resources/file path/music.pck', 'wb') as file:
            pickle.dump(tmp_list_of_song, file)

        if defined_music_window:
            song_path_set = set(list_of_song['path'])
            for path, name, duration in zip(tmp_list_of_song['path'], tmp_list_of_song['name'], tmp_list_of_song['duration']):
                #if there is a new song, add to song list
                if path not in song_path_set:
                    list_of_song['path'].append(path)
                    list_of_song['name'].append(name)
                    list_of_song['duration'].append(duration)
                    song_path_set.add(path)
                    app.list.insert(END, os.path.splitext(os.path.basename(name))[0])
            app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'
        else:
            list_of_song = tmp_list_of_song

def Check_Audio_Format(file):
    if not os.path.isfile(file):
        return False
    #other can not get length
    #extensions = ['.mp3', '.mp4', '.ogg', '.flac', '.m4a', '.wav', '.wma', '.m4b']
    #other can not set position in pygame music
    extensions = ['.mp3', '.ogg']
    #extensions = ['.3gp', '.aa', '.aac', '.aax', '.act', '.aiff', '.alac', '.amr', '.ape', '.au', '.awb', '.dss', '.dvf', '.flac', '.gsm']
    #extensions.extend(['.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.nmf', '.ogg', '.oga', '.mogg', '.opus'])
    #extensions.extend(['.ra', '.rm', '.raw', '.rf64', '.sln', '.tta', '.voc', '.vox', '.wav', '.wma', '.wv', '.webm', '.8svx', '.cda'])
    return os.path.splitext(file)[1] in extensions

class MyHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        global app
        file = event.src_path
        if file in list_of_song['path']:
            pos = list_of_song['path'].index(file)
            del list_of_song['path'][pos]
            del list_of_song['name'][pos]
            del list_of_song['duration'][pos]
            if defined_music_window:
                pos_is_selected = (pos == app.list.curselection()[0])
                app.list.delete(pos)
                if app.current > pos:
                    app.current -= 1

                #if deleted file is selected, change selection to currently playing song
                if pos_is_selected:
                    app.list.selection_clear(pos)
                    app.list.selection_set(app.current)
                    app.list.activate(app.current)
                app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'

            with open('Resources/file path/music.pck', 'wb') as file:
                pickle.dump(list_of_song, file)

    def on_created(self, event):
        global app
        file = event.src_path
        print(file)
        if not os.path.isfile(file):
            return
        if not Check_Audio_Format(file):
            return
        if file not in list_of_song['path']:
            try:
                tag = TinyTag.get(file)
            except:
                print('create')
                return
            if tag.duration is None:
                return
            list_of_song['path'].append(file)
            if tag.title is not None:
                name = tag.title
                if tag.artist is not None:
                    name += ' - ' + tag.artist
            else:
                name = os.path.splitext(os.path.basename(file))[0]
            list_of_song['name'].append(name)
            list_of_song['duration'].append(int(tag.duration))

            if defined_music_window:
                app.list.insert(END, name)
                app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'
            with open('Resources/file path/music.pck', 'wb') as file:
                pickle.dump(list_of_song, file)

    def on_modified(self, event):
        global app, defined_music_window
        file = event.src_path
        if not os.path.isfile(file):
            return
        if not Check_Audio_Format(file):
            return

        try:
            tag = TinyTag.get(file)
        except:
            print('modify')
            return
        if tag.duration is None:
            if file in list_of_song['path']:
                pos = list_of_song['path'].index(file)
                del list_of_song['path'][pos]
                del list_of_song['name'][pos]
                del list_of_song['duration'][pos]
                if defined_music_window:
                    pos_is_selected = (pos == app.list.curselection()[0])
                    app.list.delete(pos)
                    if app.current > pos:
                        app.current -= 1

                    if pos_is_selected:
                        app.list.selection_clear(pos)
                        app.list.selection_set(app.current)
                        app.list.activate(app.current)
                    app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'

                with open('Resources/file path/music.pck', 'wb') as file:
                    pickle.dump(list_of_song, file)
            return
        if tag.title is not None:
            name = tag.title
            if tag.artist is not None:
                name += ' - ' + tag.artist
        else:
            name = os.path.splitext(os.path.basename(file))[0]

        if file not in list_of_song['path']:
            list_of_song['path'].append(file)
            list_of_song['name'].append(name)
            list_of_song['duration'].append(int(tag.duration))
            if defined_music_window:
                app.list.insert(END, name)
                app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'
        else:
            pos = list_of_song['path'].index(file)
            list_of_song['name'][pos] = name
            list_of_song['duration'][pos] = int(tag.duration)
            if defined_music_window:
                pos_is_selected = (pos == app.list.curselection()[0])
                if pos_is_selected:
                    app.list.selection_clear(pos)
                    app.list.selection_set(app.current)
                app.list.delete(pos)
                app.list.insert(pos, name)
                if pos_is_selected:
                    app.list.selection_clear(app.current)
                    app.list.selection_set(pos)
                    app.list.activate(pos)
        with open('Resources/file path/music.pck', 'wb') as file:
            pickle.dump(list_of_song, file)

    def on_moved(self, event):
        global app
        src_file = event.src_path
        dest_file = event.dest_path

        if not os.path.isfile(dest_file):
            return

        if not Check_Audio_Format(dest_file):
            return

        try:
            dest_file_tag = TinyTag.get(dest_file)
        except:
            print('move')
            return
        if dest_file_tag.duration is None:
            if src_file in list_of_song['path']:
                pos = list_of_song['path'].index(src_file)
                del list_of_song['path'][pos]
                del list_of_song['name'][pos]
                del list_of_song['duration'][pos]
                if defined_music_window:
                    pos_is_selected = (pos == app.list.curselection()[0])
                    app.list.delete(pos)
                    if app.current > pos:
                        app.current -= 1

                    if pos_is_selected:
                        app.list.selection_clear(pos)
                        app.list.selection_set(app.current)
                        app.list.activate(app.current)
                    app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'

                with open('Resources/file path/music.pck', 'wb') as file:
                    pickle.dump(list_of_song, file)
            return

        if dest_file_tag.title is not None:
            dest_file_name = dest_file_tag.title
            if dest_file_tag.artist is not None:
                dest_file_name += ' - ' + dest_file_tag.artist
        else:
            dest_file_name = os.path.splitext(os.path.basename(dest_file))[0]

        if src_file in list_of_song['path']:
            pos = list_of_song['path'].index(src_file)
            list_of_song['path'][pos] = dest_file
            list_of_song['name'][pos] = dest_file_name
            list_of_song['duration'][pos] = int(dest_file_tag.duration)
        else:
            if not os.path.isfile(dest_file):
                return
            if not Check_Audio_Format(dest_file):
                return

            list_of_song['path'].append(dest_file)
            list_of_song['name'].append(dest_file_name)
            list_of_song['duration'].append(dest_file_tag.duration)
            if defined_music_window:
                app.list.insert(END, dest_file_name)
                app.tracklist['text'] = f'PlayList - {str(len(app.playlist["path"]))}'

        with open('Resources/file path/music.pck', 'wb') as file:
            pickle.dump(list_of_song, file)

event_handler = MyHandler()
observer = Observer()
observer.daemon = True
if os.path.exists(music_path):
    observer.schedule(event_handler, path=music_path, recursive=False)
observer.start()

def Get_Song_List():
    global list_of_song
    list_of_song['path'] = []
    list_of_song['name'] = []
    list_of_song['duration'] = []
    if os.path.exists('Resources/file path/music.pck') is False:
        if os.path.isdir(music_path):
            tmp_list_of_song = os.listdir(music_path)
            for song in tmp_list_of_song:
                path = os.path.join(music_path, song)
                if Check_Audio_Format(path):
                    try:
                        tag = TinyTag.get(path)
                    except:
                        continue
                    if tag.duration is None:
                        continue
                    list_of_song['path'].append(path)
                    if tag.title is not None:
                        name = tag.title
                        if tag.artist is not None:
                            name += ' - ' + tag.artist
                        list_of_song['name'].append(name)
                    else:
                        list_of_song['name'].append(os.path.splitext(os.path.basename(path))[0])
                    list_of_song['duration'].append(int(tag.duration))
        with open('Resources/file path/music.pck', 'wb') as file:
            pickle.dump(list_of_song, file)
    else:
        modified = False
        with open('Resources/file path/music.pck', 'rb') as file:
            tmp_list_of_song = pickle.load(file)
            for path, name, duration in zip(tmp_list_of_song['path'], tmp_list_of_song['name'], tmp_list_of_song['duration']):
                if os.path.isfile(path):
                    list_of_song['path'].append(path)
                    list_of_song['name'].append(name)
                    list_of_song['duration'].append(duration)
                else:
                    #some songs are deleted
                    modified = True

        if modified:
            if list_of_song:
                with open('Resources/file path/music.pck', 'wb') as file:
                    pickle.dump(list_of_song, file)
            else:
                os.remove('Resources/file path/music.pck')
