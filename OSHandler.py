import datetime
import os
import psutil
import wmi
import music
from global_function import string_similarity, data_exist, Adjust_Volume_Off, Adjust_Volume_On
from pynput.keyboard import Key, Controller, KeyCode
import pickle
import threading
import re
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import cpuinfo
import json
import PIL.ImageGrab
import winshell
import shutil
import win32security
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32con
import win32gui,win32process

computer_username = os.getlogin()

def batteryInfo():
    battery = psutil.sensors_battery()
    pr = str(battery.percent)
    if battery.power_plugged:
        return "Your System is currently on Charging Mode and it's " + pr + "% done."
    return "Your System is currently on " + pr + "% battery life."


cpu_usage = 0.0
def Monitor_CPU():
    while True:
        global cpu_usage
        cpu_usage = psutil.cpu_percent(interval=1)


threading.Thread(target=Monitor_CPU, daemon=True).start()

def Delete_Trash_Files():
    if os.path.exists('Resources/web scraping/billboard/result.json'):
        os.remove('Resources/web scraping/billboard/result.json')
    if os.path.exists('Resources/web scraping/covid/result.json'):
        os.remove('Resources/web scraping/covid/result.json')
    folder = 'Resources/web scraping/imgDownloads'
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            pass

def systemInfo(type):
    if type == 0:
        c = wmi.WMI()
        my_system_1 = c.Win32_LogicalDisk()[0]
        my_system_2 = c.Win32_ComputerSystem()[0]
        info = ['Total Disk Space: ' + str(round(int(my_system_1.Size) / (1024 ** 3), 2)) + ' GB',
                'Free Disk Space: ' + str(round(int(my_system_1.Freespace) / (1024 ** 3), 2)) + ' GB',
                'Manufacturer: ' + my_system_2.Manufacturer,
                'Model: ' + my_system_2.Model,
                'Owner: ' + my_system_2.PrimaryOwnerName,
                'Number of Processors: ' + str(my_system_2.NumberOfProcessors),
                'System Type: ' + my_system_2.SystemType]
    elif type == 1:
        info = ['Total: ' + str(round(psutil.virtual_memory().total / (1024**3), 1)) + ' GB']
    else:
        cpu = json.loads(cpuinfo.get_cpu_info_json())
        info = ['Brand: ' + cpu['brand_raw'],
                'Based speed: ' + str(round(psutil.cpu_freq().current / 1000, 2)) + ' GHz',
                'Processors: ' + str(cpu['count']),
                'Cores: ' + str(cpu['family'])]

    return info


def systemUsage(type, app_use=False):
    if type == 0:
        return str(round(cpu_usage))

    mem = psutil.virtual_memory()
    percent = round(mem.used / mem.total * 100)
    if type == 1:
        if app_use:
            process = psutil.Process(os.getpid())
            mem_used = process.memory_info().rss
            percent = round(mem_used / mem.total * 100)
            return [round(mem_used / (1024**2), 1), percent]
        return [str(round(mem.used / (1024**3), 1)), percent]

    return ['CPU: ' + str(round(cpu_usage)) + '%',
            'RAM: ' + str(round(mem.used / (1024**3), 1)) + ' GB (' + str(percent) + '%)']

list_of_program = set()

def Get_Programs(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.exe') or file.endswith('.lnk'):
                if file.endswith('.exe'):
                    list_of_program.add((os.path.join(root, file), ''))
                else:
                    shortcut = winshell.shortcut(os.path.join(root, file))
                    list_of_program.add((shortcut.path, shortcut.arguments))


def Update_Program_List():
    if new_program_list or delete_program_list:
        remove_program = []
        for program in delete_program_list:
            for exist_program in list_of_program:
                if program in exist_program[0]:
                    remove_program.append(exist_program)
                    break
        for exist_program in remove_program:
            list_of_program.remove(exist_program)

        for program in new_program_list:
            if os.path.isfile(program):
                if program.endswith('.exe') or program.endswith('.lnk'):
                    if program.endswith('.exe'):
                        list_of_program.add((program, ''))
                    else:
                        shortcut = winshell.shortcut(program)
                        list_of_program.add((shortcut.path, shortcut.arguments))
            else:
                Get_Programs(program)

        new_program_list.clear()
        delete_program_list.clear()
        with open('Resources/file path/program.pck', 'wb') as file:
            pickle.dump(list_of_program, file)

def Path_Update(type):
    def get_bit(x, pos):
        return (x >> pos) & 1

    if get_bit(type, 0) == 1:
        list_of_program.clear()
        thread1 = threading.Thread(target=Get_Programs, args=('C:\\Program Files',), daemon=True)
        thread2 = threading.Thread(target=Get_Programs,
                                   args=(f'C:\\Users\\{computer_username}\\Desktop',),
                                   daemon=True)
        thread1.start()
        thread2.start()
        Get_Programs('C:\\Program Files (x86)')
        thread1.join()
        thread2.join()
        with open('Resources/file path/program.pck', 'wb') as file:
            pickle.dump(list_of_program, file)

    if get_bit(type, 1) == 1:
        music.Update()

def Get_Program_List():
    global list_of_program
    if os.path.exists('Resources/file path/program.pck') is False:
        thread1 = threading.Thread(target=Get_Programs, args=('C:\\Program Files',), daemon=True)
        thread2 = threading.Thread(target=Get_Programs,
                                   args=(f'C:\\Users\\{computer_username}\\Desktop',),
                                   daemon=True)
        thread1.start()
        thread2.start()
        Get_Programs('C:\\Program Files (x86)')
        thread1.join()
        thread2.join()
        with open('Resources/file path/program.pck', 'wb') as file:
            pickle.dump(list_of_program, file)
    else:
        modified = False
        with open('Resources/file path/program.pck', 'rb') as file:
            tmp_list_of_program = pickle.load(file)
        for program in tmp_list_of_program:
            if os.path.isfile(program[0]):
                list_of_program.add(program)
            else:
                #some programs are deleted
                modified = True

        if modified:
            with open('Resources/file path/program.pck', 'wb') as file:
                pickle.dump(list_of_program, file)

new_program_list = set()
delete_program_list = set()

class MyHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        if event.src_path in new_program_list:
            new_program_list.remove(event.src_path)
        delete_program_list.add(event.src_path)

    def on_created(self, event):
        if event.src_path in delete_program_list:
            delete_program_list.remove(event.src_path)
        new_program_list.add(event.src_path)

    def on_moved(self, event):
        if event.src_path in new_program_list:
            new_program_list.remove(event.src_path)
        if event.dest_path in delete_program_list:
            delete_program_list.remove(event.dest_path)

        delete_program_list.add(event.src_path)
        new_program_list.add(event.dest_path)

event_handler = MyHandler()
observer = Observer()
observer.daemon = True
observer.schedule(event_handler, path='C:\\Program Files', recursive=False)
observer.schedule(event_handler, path=f'C:\\Users\\{computer_username}\\Desktop', recursive=False)
observer.schedule(event_handler, path='C:\\Program Files (x86)', recursive=False)
observer.start()

#return program path and arguments if needed
def Program_Obj(program):
    program = program.replace(' ', '')
    if program == '':
        return None

    Update_Program_List()

    with open('Resources/command/rename program.pck', 'rb') as file:
        rename_program = pickle.load(file)
    if program in rename_program:
        program = rename_program[program]

    name_match = []
    for program_obj in list_of_program:
        if os.path.isfile(program_obj[0]):
            if program in program_obj[0].lower().replace(' ', ''):
                program_name = os.path.splitext(os.path.basename(program_obj[0]))[0]
                name_match.append([program_obj, string_similarity(program_name.lower(), program)])

    if name_match:
        match_percentage = 0.0
        return_obj = []
        for x in name_match:
            if x[1] > match_percentage:
                return_obj = x[0]
                match_percentage = x[1]
        return return_obj

    return None


def Unikey_Switch():
    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press(Key.shift)
    keyboard.release(Key.ctrl)
    keyboard.release(Key.shift)


def Press(command, type_num):
    keyboard = Controller()
    for i in range(type_num):
        for x in command:
            keyboard.press(x)
        for x in command:
            keyboard.release(x)


def Type(word, type_num, enter):
    keyboard = Controller()
    for i in range(type_num):
        if i != 0:
            keyboard.press(Key.space)
            keyboard.release(Key.space)
        for x in word:
            keyboard.press(KeyCode(char=x))
            keyboard.release((KeyCode(char=x)))
    if enter:
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)


volume = cast(AudioUtilities.GetSpeakers().Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))

'''def Standard_Volume_Scale():
    if os.path.exists('Resources/userData/standard volume level'):
        return pickle.load(open('Resources/userData/standard volume level', 'rb'))
    standard_volume_decibel = -16.000192642211914
    current_level = round(volume.GetMasterVolumeLevelScalar(), 2)

    standard_volume_scale = -1
    min_diff = 1e9

    for i in range(101):
        volume.SetMasterVolumeLevelScalar(i / 100, None)
        level = volume.GetMasterVolumeLevel()
        if abs(level - standard_volume_decibel) < min_diff:
            min_diff = abs(level - standard_volume_decibel)
            standard_volume_scale = i

    volume.SetMasterVolumeLevelScalar(current_level, None)
    pickle.dump(standard_volume_scale, open('Resources/userData/standard volume level', 'wb'))

    return standard_volume_scale'''

def Volume(command):
    current_level = round(volume.GetMasterVolumeLevelScalar(), 2)

    if data_exist(['volume to'], command, 2):
        nums = re.findall(r'[0-9]+', command)
        if nums:
            num = int(nums[0])
        else:
            if not data_exist(['correct', 'adjust', 'auto', 'standard', 'default'], command):
                with open('Resources/userData/standard volume level.txt', 'r') as file:
                    num = file.read()
            else:
                num = 30
        num /= 100
        num = max(num, 0)
        num = min(num, 1)
        if data_exist(['correct', 'adjust', 'auto', 'standard', 'default'], command):
            return 'set standard volume to ' + str(int(num * 100))
        volume.SetMasterVolumeLevelScalar(num, None)
        return 'set volume to ' + str(int(num * 100))

    if data_exist(['correct', 'adjust', 'auto'], command, 5):
        if data_exist(['stop', 'off', 'disable', 'terminate'], command):
            Adjust_Volume_Off()
            return 'adjusting volume off'
        else:
            Adjust_Volume_On()
            return 'adjusting volume on'

    if data_exist(['unmute', 'on', 'unmuted'], command):
        volume.SetMute(False, None)
        return 'volume unmuted'

    if data_exist(['mute', 'off', 'shut up', 'muted'], command, 2):
        volume.SetMute(True, None)
        return 'volume muted'

    if data_exist(['standard', 'default'], command):
        with open('Resources/userData/standard volume level.txt', 'r') as file:
            num = file.read()
        return 'the current standard volume is ' + str(num)

    '''if data_exist(['twice'], command):
        num = 2
    else:
        nums = re.findall(r'[0-9]+', command)
        if nums:
            num = int(nums[0])
        else:
            num = 1

    if data_exist(['up', 'high'], command):
        target_level = min(current_level + num / 100, 1)
        volume.SetMasterVolumeLevelScalar(target_level, None)
        return 'set volume to ' + str(int(target_level * 100))

    if data_exist(['down', 'low'], command):
        target_level = max(current_level - num / 100, 0)
        volume.SetMasterVolumeLevelScalar(target_level, None)
        return 'set volume to ' + str(int(target_level * 100))'''

    return 'your current volume is: ' + str(int(current_level * 100))


def Screen_Capture():
    img = PIL.ImageGrab.grab()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    path = os.path.join(f'C:\\Users\\{computer_username}\\Pictures',
                        f'screenshot {current_time}.jpg')
    img.save(path)
    os.startfile(path)
    return path


def Delete_Temp_Files():
    folder = f'C:/Users/{computer_username}/AppData/Local/Temp'

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            pass


def Empty_Recycle_Bin():
    temp_file_thread = threading.Thread(target=Delete_Temp_Files, daemon=True)
    temp_file_thread.start()
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False,sound=False)
    except:
        pass
    temp_file_thread.join()


#return folder path
def Open_Folder(folder):
    with open('Resources/file path/folder path.pck', 'rb') as file:
        paths = pickle.load(file)
        for path in paths:
            path['name'].sort(key=lambda x : len(x), reverse=True)
        paths.sort(key=lambda x : len(x['name'][0]), reverse=True)

    for path in paths:
        if data_exist(path['name'], folder, 6):
            folder_path = path['path']
            folder_path = folder_path.replace('__os_UserName__', computer_username)
            folder_path = folder_path.replace('__security_identity__', str(win32security.LookupAccountName(None, computer_username)[0])[6:])
            if os.path.isdir(folder_path):
                for name in path['name']:
                    if data_exist([name], folder, 6):
                        return [name, folder_path]

    return None

def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def get_window_pid(title):
    hwnd = win32gui.FindWindow(None, title)
    threadid, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid

def Program_Already_Opened(program_path):
    top_windows = []
    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
    for i in top_windows:
        if win32gui.IsWindowVisible(i[0]):
            path = psutil.Process(get_window_pid(i[1])).exe()
            if program_path == path:
                    win32gui.ShowWindow(i[0], win32con.SW_MAXIMIZE)
                    win32gui.SetForegroundWindow(i[0])
                    return True
    return False

def Close_Program(program_name):
    with open('Resources/command/close system files rename.pck', 'rb') as file:
        close_system_files_rename = pickle.load(file)

    is_system_file = False
    program_exe = ''
    for file in close_system_files_rename:
        if data_exist(file['name'], program_name, 0):
            program_exe = file['rename']
            is_system_file = True
            break

    if not is_system_file:
        program_obj = Program_Obj(program_name)
        if program_obj is None:
            return
        program_exe = os.path.basename(program_obj[0])

    for process in psutil.process_iter():
        if process.name() == program_exe:
            process.kill()