from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import datetime
from tkinter import *
import time
import vlc
import math

class Timer(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()

        self.time_on = None
        self.request_seconds = 0
        self.remaining_seconds = 0
        self.alarm_sound = vlc.MediaPlayer('Resources/audio/alarm sound.mp3')

        self.up_img = PhotoImage(file='Resources/images/timer/up arrow.png')
        self.selected_up_img = PhotoImage(file='Resources/images/timer/selected up arrow.png')
        self.down_img = PhotoImage(file='Resources/images/timer/down arrow.png')
        self.selected_down_img = PhotoImage(file='Resources/images/timer/selected down arrow.png')

        self.create_times_up_frame()
        self.create_timer_frame()

    def set_timer(self, duration):
        self.request_seconds = duration
        self.selected_hour = duration // 3600
        self.selected_minute = (duration % 3600) // 60
        self.selected_second = duration % 60

        self.hour_box.yview_moveto(self.selected_hour / 24)
        self.minute_box.yview_moveto(self.selected_minute / 60)
        self.second_box.yview_moveto(self.selected_second / 60)

    def on_mouseclick(self, event):
        if self.hour_box.curselection():
            self.hour_box.selection_clear(self.hour_box.curselection()[0])
        if self.minute_box.curselection():
            self.minute_box.selection_clear(self.minute_box.curselection()[0])
        if self.second_box.curselection():
            self.second_box.selection_clear(self.second_box.curselection()[0])

    def onhover_up_hour(self, event):
        self.hour_up_button.config(image=self.selected_up_img)

    def onhover_up_minute(self, event):
        self.minute_up_button.config(image=self.selected_up_img)

    def onhover_up_second(self, event):
        self.second_up_button.config(image=self.selected_up_img)

    def onleave_up_hour(self, event):
        self.hour_up_button.config(image=self.up_img)

    def onleave_up_minute(self, event):
        self.minute_up_button.config(image=self.up_img)

    def onleave_up_second(self, event):
        self.second_up_button.config(image=self.up_img)

    def up_pressed(self, type):
        if type == 0: #hour
            if self.hour_box.curselection():
                self.hour_box.selection_clear(self.hour_box.curselection()[0])
            if self.selected_hour != 23:
                self.selected_hour += 1
                self.hour_box.yview_scroll(1, 'units')
            self.hour_box.selection_set(self.selected_hour)
            self.hour_box.focus_set()
        elif type == 1: #second
            if self.minute_box.curselection():
                self.minute_box.selection_clear(self.minute_box.curselection()[0])
            if self.selected_minute != 59:
                self.selected_minute += 1
                self.minute_box.yview_scroll(1, 'units')
            self.minute_box.selection_set(self.selected_minute)
            self.minute_box.focus_set()
        else:
            if self.second_box.curselection():
                self.second_box.selection_clear(self.second_box.curselection()[0])
            if self.selected_second != 59:
                self.selected_second += 1
                self.second_box.yview_scroll(1, 'units')
            self.second_box.selection_set(self.selected_second)
            self.second_box.focus_set()

        if self.up_button_pressed is None:
            self.up_button_pressed = self.after(500, lambda : self.up_pressed(type))
        else:
            self.up_button_pressed = self.after(50, lambda: self.up_pressed(type))

    def up_released(self, event):
        self.after_cancel(self.up_button_pressed)
        self.up_button_pressed = None

    def create_up_buttons(self):
        self.up_buttons_frame = Frame(self.edit_time_frame, height=27, width=264, bg='#282828')
        self.up_buttons_frame.grid(row=0, padx=68)
        self.up_buttons_frame.grid_propagate(0)

        self.up_button_pressed = None

        self.hour_up_button = Button(self.up_buttons_frame, height=27, width=72, image=self.up_img, bd=0, bg='#282828', activebackground='#282828')
        self.hour_up_button.bind('<Enter>', self.onhover_up_hour)
        self.hour_up_button.bind('<Leave>', self.onleave_up_hour)
        self.hour_up_button.bind('<ButtonPress-1>', lambda event, type=0 : self.up_pressed(type))
        self.hour_up_button.bind('<ButtonRelease-1>', self.up_released)
        self.hour_up_button.grid(row=0, column=0)

        self.minute_up_button = Button(self.up_buttons_frame, height=27, width=72, image=self.up_img, bd=0, bg='#282828', activebackground='#282828')
        self.minute_up_button.bind('<Enter>', self.onhover_up_minute)
        self.minute_up_button.bind('<Leave>', self.onleave_up_minute)
        self.minute_up_button.bind('<ButtonPress-1>', lambda event, type=1: self.up_pressed(type))
        self.minute_up_button.bind('<ButtonRelease-1>', self.up_released)
        self.minute_up_button.grid(row=0, column=1, padx=21)

        self.second_up_button = Button(self.up_buttons_frame, height=27, width=72, image=self.up_img, bd=0, bg='#282828', activebackground='#282828')
        self.second_up_button.bind('<Enter>', self.onhover_up_second)
        self.second_up_button.bind('<Leave>', self.onleave_up_second)
        self.second_up_button.bind('<ButtonPress-1>', lambda event, type=2 : self.up_pressed(type))
        self.second_up_button.bind('<ButtonRelease-1>', self.up_released)
        self.second_up_button.grid(row=0, column=2)

    def onhover_down_hour(self, event):
        self.hour_down_button.config(image=self.selected_down_img)

    def onhover_down_minute(self, event):
        self.minute_down_button.config(image=self.selected_down_img)

    def onhover_down_second(self, event):
        self.second_down_button.config(image=self.selected_down_img)

    def onleave_down_hour(self, event):
        self.hour_down_button.config(image=self.down_img)

    def onleave_down_minute(self, event):
        self.minute_down_button.config(image=self.down_img)

    def onleave_down_second(self, event):
        self.second_down_button.config(image=self.down_img)

    def down_pressed(self, type):
        if type == 0: #hour
            if self.hour_box.curselection():
                self.hour_box.selection_clear(self.hour_box.curselection()[0])
            if self.selected_hour != 0:
                self.selected_hour -= 1
                self.hour_box.yview_scroll(-1, 'units')
            self.hour_box.selection_set(self.selected_hour)
            self.hour_box.focus_set()
        elif type == 1: #minute
            if self.minute_box.curselection():
                self.minute_box.selection_clear(self.minute_box.curselection()[0])
            if self.selected_minute != 0:
                self.selected_minute -= 1
                self.minute_box.yview_scroll(-1, 'units')
            self.minute_box.selection_set(self.selected_minute)
            self.minute_box.focus_set()
        else: #second
            if self.second_box.curselection():
                self.second_box.selection_clear(self.second_box.curselection()[0])
            if self.selected_second != 0:
                self.selected_second -= 1
                self.second_box.yview_scroll(-1, 'units')
            self.second_box.selection_set(self.selected_second)
            self.second_box.focus_set()

        if self.down_button_pressed is None:
            self.down_button_pressed = self.after(500, lambda : self.down_pressed(type))
        else:
            self.down_button_pressed = self.after(50, lambda: self.down_pressed(type))

    def down_released(self, event):
        self.after_cancel(self.down_button_pressed)
        self.down_button_pressed = None

    def create_down_buttons(self):
        self.down_buttons_frame = Frame(self.edit_time_frame, height=27, width=264, bg='#282828')
        self.down_buttons_frame.grid(row=2, padx=68)
        self.down_buttons_frame.grid_propagate(0)

        self.down_button_pressed = None

        self.hour_down_button = Button(self.down_buttons_frame, height=27, width=72, image=self.down_img, bd=0, bg='#282828',
                                       activebackground='#282828')
        self.hour_down_button.bind('<Enter>', self.onhover_down_hour)
        self.hour_down_button.bind('<Leave>', self.onleave_down_hour)
        self.hour_down_button.bind('<ButtonPress-1>', lambda event, type=0: self.down_pressed(type))
        self.hour_down_button.bind('<ButtonRelease-1>', self.down_released)
        self.hour_down_button.grid(row=0, column=0)

        self.minute_down_button = Button(self.down_buttons_frame, height=27, width=72, image=self.down_img, bd=0, bg='#282828', activebackground='#282828')
        self.minute_down_button.bind('<Enter>', self.onhover_down_minute)
        self.minute_down_button.bind('<Leave>', self.onleave_down_minute)
        self.minute_down_button.bind('<ButtonPress-1>', lambda event, type=1: self.down_pressed(type))
        self.minute_down_button.bind('<ButtonRelease-1>', self.down_released)
        self.minute_down_button.grid(row=0, column=1, padx=21)

        self.second_down_button = Button(self.down_buttons_frame, height=27, width=72, image=self.down_img, bd=0, bg='#282828', activebackground='#282828')
        self.second_down_button.bind('<Enter>', self.onhover_down_second)
        self.second_down_button.bind('<Leave>', self.onleave_down_second)
        self.second_down_button.bind('<ButtonPress-1>', lambda event, type=2: self.down_pressed(type))
        self.second_down_button.bind('<ButtonRelease-1>', self.down_released)
        self.second_down_button.grid(row=0, column=2)

    def create_edit_time_label_frame(self):
        self.edit_time_label_frame = Frame(self.edit_time_frame, height=75, width=264, bg='#282828')
        self.edit_time_label_frame.grid(row=1, padx=68)
        self.edit_time_label_frame.grid_propagate(0)

        self.hour_box = Listbox(self.edit_time_label_frame, height=1, width=2, font=('arial', 50), fg='white', bg='#282828', bd=0,
                           highlightthickness=0, selectbackground='#494949', activestyle='none', selectmode=SINGLE)
        for i in range(24):
            self.hour_box.insert(END, str(i).zfill(2))
        self.selected_hour = 0
        self.hour_box.grid(row=0, column=0)

        self.hour_minute_separator = Label(self.edit_time_label_frame, text=':', font=('arial', 50), fg='white', bg='#282828',
                                      bd=0, highlightthickness=0, height=0)
        self.hour_minute_separator.bind('<Button-1>', self.on_mouseclick)
        self.hour_minute_separator.grid(row=0, column=1)
        self.minute_box = Listbox(self.edit_time_label_frame, height=1, width=2, font=('arial', 50), fg='white', bg='#282828',
                             bd=0, highlightthickness=0, selectbackground='#494949', activestyle='none', selectmode=SINGLE)
        for i in range(60):
            self.minute_box.insert(END, str(i).zfill(2))
        self.selected_minute = 0
        self.minute_box.grid(row=0, column=2)

        self.minute_second_separator = Label(self.edit_time_label_frame, text=':', font=('arial', 50), fg='white', bg='#282828',
                                        bd=0, highlightthickness=0)
        self.minute_second_separator.bind('<Button-1>', self.on_mouseclick)
        self.minute_second_separator.grid(row=0, column=3)

        self.second_box = Listbox(self.edit_time_label_frame, height=1, width=2, font=('arial', 50), fg='white', bg='#282828',
                             bd=0, highlightthickness=0, selectbackground='#494949', activestyle='none', selectmode=SINGLE)
        for i in range(60):
            self.second_box.insert(END, str(i).zfill(2))
        self.selected_second = 0
        self.second_box.grid(row=0, column=4)

    def create_edit_time_frame(self):
        self.edit_time_frame = Frame(self.timer_frame, width=400, height=130, bg='#282828', bd=0)
        self.edit_time_frame.bind('<Button-1>', self.on_mouseclick)
        self.edit_time_frame.grid(row=0)
        self.edit_time_frame.grid_propagate(0)

        self.create_up_buttons()
        self.create_edit_time_label_frame()
        self.create_down_buttons()

    def timer_timesup(self):
        global timer_window
        timer_window.state('normal')
        timer_window.wm_attributes("-topmost", 1)
        timer_window.wm_attributes("-topmost", 0)

        self.time_on = None
        self.times_up_frame.tkraise()
        self.alarm_sound.play()

    def countdown(self):
        #can not do subtraction between float
        self.remaining_seconds = (self.remaining_seconds * 10 - 1) / 10
        self.time_label.config(text=str(time.strftime('%H:%M:%S', time.gmtime(int(math.ceil(self.remaining_seconds))))))
        if self.remaining_seconds:
            self.time_on = self.after(100, self.countdown)
        else:
            self.timer_timesup()

    def start(self):
        self.time_label_frame.tkraise()
        self.pause_button.tkraise()
        self.reset_button.config(state=NORMAL)

        self.request_seconds = self.selected_hour * 3600 + self.selected_minute * 60 + self.selected_second

        self.remaining_seconds = self.request_seconds - 1
        if self.remaining_seconds > 0:
            if self.hour_box.curselection():
                self.hour_box.selection_clear(self.hour_box.curselection()[0])
            if self.minute_box.curselection():
                self.minute_box.selection_clear(self.minute_box.curselection()[0])
            if self.second_box.curselection():
                self.second_box.selection_clear(self.second_box.curselection()[0])

            self.time_label['text'] = str(time.strftime('%H:%M:%S', time.gmtime(int(math.ceil(self.remaining_seconds)))))
            self.time_on = self.after(100, self.countdown)
        else:
            self.timer_timesup()

    def pause(self):
        self.resume_button.tkraise()
        self.after_cancel(self.time_on)
        self.time_on = None

    def reset(self):
        self.edit_time_frame.tkraise()
        if self.time_on is not None:
            self.after_cancel(self.time_on)
            self.time_on = None
        self.start_button.tkraise()
        self.reset_button['state'] = DISABLED

    def resume(self):
        self.pause_button.tkraise()
        self.time_on = self.after(100, self.countdown)

    def create_control_frame(self):
        self.control_frame = Frame(self.timer_frame, width=400, height=70, bd=0, bg='#282828')
        self.control_frame.grid(row=1)
        self.control_frame.grid_propagate(0)
        self.control_frame.bind('<Button-1>', self.on_mouseclick)

        self.reset_button = Button(self.control_frame, text='Reset', font=('arial', 15), bd=0, bg='#696969',
                              activebackground='#696969', fg='white', activeforeground='white', width=9)
        self.reset_button.config(state=DISABLED, command=self.reset)
        self.reset_button.grid(row=0, column=0, sticky='W', padx=48, pady=10)

        self.start_button = Button(self.control_frame, text='Start', font=('arial', 15), bd=0, bg='#13911d',
                              activebackground='#13911d', fg='white', activeforeground='white', width=9)
        self.start_button.config(command=self.start)
        self.start_button.grid(row=0, column=1, sticky='E', padx=45, pady=10)

        self.pause_button = Button(self.control_frame, text='Pause', font=('arial', 15), bd=0, bg='#f18814',
                              activebackground='#f18814', fg='white', activeforeground='white', width=9)
        self.pause_button.config(command=self.pause)
        self.pause_button.grid(row=0, column=1, sticky='E', padx=45, pady=10)

        self.resume_button = Button(self.control_frame, text='Resume', font=('arial', 15), bd=0, bg='#13911d',
                               activebackground='#13911d', fg='white', activeforeground='white', width=9)
        self.resume_button.config(command=self.resume)
        self.resume_button.grid(row=0, column=1, sticky='E', padx=45, pady=10)

        self.start_button.tkraise()

    def create_time_frame(self):
        self.time_label_frame = Frame(self.timer_frame, width=400, height=130, bg='#282828', bd=0)
        self.time_label_frame.grid(row=0)

        self.time_label = Label(self.time_label_frame, text=str(time.strftime('%H:%M:%S', time.gmtime(self.request_seconds))), width=7, font=('arial', 50), relief=GROOVE, justify=CENTER, bg='#282828',
                                fg='white', borderwidth=0)

        self.time_label.place(x=62, y=27)

    def create_timer_frame(self):
        self.timer_frame = Frame(self, width=400, height=200)
        self.timer_frame.grid(row=0)

        self.create_time_frame()
        self.create_edit_time_frame()
        self.create_control_frame()

    def stop_timer(self):
        self.alarm_sound.stop()
        self.reset()
        self.timer_frame.tkraise()

    def create_times_up_frame(self):
        self.times_up_frame = Frame(self, width=400, height=200, bg='#282828')
        self.times_up_frame.grid(row=0)

        self.times_up_label = Label(self.times_up_frame, text="Time's up", font=('arial', 40), bg='#282828', fg='white')
        self.times_up_label.place(x=83, y=25)

        self.times_up_button = Button(self.times_up_frame, text='Stop', font=('arial', 15), bg='red', fg='white', bd=0,
                                 activebackground='red', activeforeground='white', width=9)
        self.times_up_button.config(command=self.stop_timer)
        self.times_up_button.place(x=148, y=130)

global timer_app, timer_window
defined_timer_window = False

def Stop_Timer():
    global timer_window, defined_timer_window, timer_app

    if not defined_timer_window:
        return

    timer_app.stop_timer()
    timer_window.destroy()
    defined_timer_window = False

#return -1: timer has been set
def Set_Timer(root, duration, force_change=False):
    global timer_app, timer_window, defined_timer_window
    if not defined_timer_window:
        defined_timer_window = True
        timer_window = Toplevel(root)
        timer_window.title('Timer')
        timer_window.geometry('400x200')
        timer_window.resizable(0, 0)
        timer_window.protocol('WM_DELETE_WINDOW', Stop_Timer)

        timer_app = Timer(master=timer_window)
        timer_app.set_timer(duration)
        timer_app.start()

        return -1

    if not force_change:
        if timer_app.time_on:
            return timer_app.request_seconds

    timer_app.reset()
    timer_app.set_timer(duration)
    timer_app.start()
    return -1

def get_timezone(location):
    geolocator = Nominatim(user_agent='smartbot')
    loc_code = geolocator.geocode(location)

    if loc_code == None:
        return None

    return pytz.timezone(TimezoneFinder().timezone_at(lng=loc_code.longitude, lat=loc_code.latitude))

def Tell_Time(location):
    if location == 'here':
        return datetime.datetime.now().strftime('%I:%M %p')

    timezone = get_timezone(location)
    if timezone is None:
        return None

    return datetime.datetime.now(timezone).strftime('%I:%M %p')

def Tell_Day(tell_day):
    current_date = datetime.date.today().strftime('%B %d, %Y')
    current_day = datetime.datetime.today().strftime('%A')

    if tell_day:
        return [current_day, f', {current_date}']

    return [current_date, '']