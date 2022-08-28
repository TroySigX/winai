from tkinter import *
from tkinter import ttk
import pickle
from PIL import Image, ImageTk
from global_function import Choosing_Avatar_Set_False

avtr = []
avtb = []
global avtrRoot, my_canvas, my_scrollbar

#scrollbar positions by row
starting_point = [0.013114754098360656, 0.20655737704918034, 0.40491803278688526, 0.5, 0.5]
ending_point = [0.5, 0.5, 0.5983606557377049, 0.7950819672131147, 0.9918032786885246]

with open('Resources/userData/settings.pck', 'rb') as file:
	loadSettings = pickle.load(file)
current_selected = loadSettings['user_avatar']

def closeWindow(event=None):
	Choosing_Avatar_Set_False()
	global avtrRoot
	avtrRoot.destroy()


def SavePhoto(event=None):
	with open('Resources/userData/settings.pck', 'wb') as file:
		pickle.dump(loadSettings, file)
	closeWindow()


def selectAVATAR(avt):
	global current_selected
	loadSettings['user_avatar'] = avt
	current_selected = avt

	global avtb
	for i in range(15):
		if i == avt:
			avtb[i]['state'] = DISABLED
		else:
			avtb[i]['state'] = NORMAL

def on_mousewheel(event):
	my_canvas.yview_scroll(-1*event.delta//120, "units")

def adjust_scrollbar():
	row = current_selected // 3
	scrollbar_position = my_scrollbar.get()
	if starting_point[row] < scrollbar_position[0]:
		my_canvas.yview_moveto(str(starting_point[row]))
	if ending_point[row] > scrollbar_position[1]:
		my_canvas.yview_moveto(str(ending_point[row] - 0.5))

def down_clicked(event):
	global current_selected
	row = current_selected // 3
	if row < 4:
		current_selected += 3
	selectAVATAR(current_selected)
	adjust_scrollbar()

def up_clicked(event):
	global current_selected
	row = current_selected // 3
	if row > 0:
		current_selected -= 3
	selectAVATAR(current_selected)
	adjust_scrollbar()

def left_clicked(event):
	global current_selected
	if current_selected > 0:
		current_selected -= 1
	selectAVATAR(current_selected)
	adjust_scrollbar()

def right_clicked(event):
	global current_selected
	if current_selected < 14:
		current_selected += 1
	selectAVATAR(current_selected)
	adjust_scrollbar()

def run_code(root):
	background = '#F6FAFB'
	global avtrRoot
	avtrRoot = Toplevel(root)
	avtrRoot.resizable(0, 0)
	avtrRoot.protocol('WM_DELETE_WINDOW', closeWindow)
	avtrRoot.title('Choose Avatar')
	avtrRoot.config(bg=background)
	avtrRoot.focus_set()
	w_width, w_height = 500, 450
	s_width, s_height = avtrRoot.winfo_screenwidth(), avtrRoot.winfo_screenheight()
	x, y = (s_width / 2) - (w_width / 2), (s_height / 2) - (w_height / 2)
	avtrRoot.geometry('%dx%d+%d+%d' % (w_width, w_height, x, y - 30))
	avtrRoot.iconbitmap("Resources/images/changeProfile.ico")
	avtrRoot.bind('<Down>', down_clicked)
	avtrRoot.bind('<Left>', left_clicked)
	avtrRoot.bind('<Right>', right_clicked)
	avtrRoot.bind('<Up>', up_clicked)
	avtrRoot.bind('<Return>', SavePhoto)
	avtrRoot.bind('<Escape>', closeWindow)

	Label(avtrRoot, text="Choose Your Avatar", font=('arial bold', 15), bg=background, fg='#303E54').pack(pady=10)

	avatarContainer = Frame(avtrRoot, bg=background)
	avatarContainer.pack(pady=10, ipadx=50, ipady=20)

	# create a main frame
	main_frame = Frame(avatarContainer)
	main_frame.pack(fill=BOTH, expand=1)

	# create a canvas
	global my_canvas
	my_canvas = Canvas(main_frame, bg=background)
	my_canvas.pack(side=LEFT, expand=1, fill=BOTH)

	# add a scrollbar to the canvas
	global my_scrollbar
	my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
	my_scrollbar.pack(side=RIGHT, fill=Y)

	# configure the canvas
	my_canvas.config(yscrollcommand=my_scrollbar.set)

	# create another frame inside the canvas
	second_frame = Frame(my_canvas)

	# add that new frame to a window in the canvas
	my_canvas.create_window((0, 0), window=second_frame, anchor='nw')
	my_canvas.bind_all('<MouseWheel>', on_mousewheel)

	global avtr
	avtr = []
	size = 100
	for i in range(15):
		avtr.append(ImageTk.PhotoImage(Image.open(f'Resources/images/avatars/a{i}.png').resize((size, size)),
								   Image.ANTIALIAS))

	global avtb
	avtb = []
	for i in range(15):
		avtb.append(Button(second_frame, image=avtr[i], bg=background, activebackground=background, relief=FLAT, bd=0))
		avtb[i].grid(row=int(i / 3), column=i % 3, ipadx=25, ipady=10)
	avtb[0]['command'] = lambda: selectAVATAR(0)
	avtb[1]['command'] = lambda: selectAVATAR(1)
	avtb[2]['command'] = lambda: selectAVATAR(2)
	avtb[3]['command'] = lambda: selectAVATAR(3)
	avtb[4]['command'] = lambda: selectAVATAR(4)
	avtb[5]['command'] = lambda: selectAVATAR(5)
	avtb[6]['command'] = lambda: selectAVATAR(6)
	avtb[7]['command'] = lambda: selectAVATAR(7)
	avtb[8]['command'] = lambda: selectAVATAR(8)
	avtb[9]['command'] = lambda: selectAVATAR(9)
	avtb[10]['command'] = lambda: selectAVATAR(10)
	avtb[11]['command'] = lambda: selectAVATAR(11)
	avtb[12]['command'] = lambda: selectAVATAR(12)
	avtb[13]['command'] = lambda: selectAVATAR(13)
	avtb[14]['command'] = lambda: selectAVATAR(14)

	avtb[current_selected]['state'] = DISABLED

	my_canvas.configure(scrollregion=my_canvas.bbox('all'))
	my_canvas.yview_moveto('0.3180327868852459')

	BottomFrame = Frame(avtrRoot, bg=background)
	BottomFrame.pack(pady=10)
	Button(BottomFrame, text='         Update         ', font=('Montserrat Bold', 15), bg='#01933B', fg='white', bd=0,
			relief=FLAT, command=SavePhoto).grid(row=0, column=0, padx=10)
	Button(BottomFrame, text='         Cancel         ', font=('Montserrat Bold', 15), bg='#EDEDED', fg='#3A3834', bd=0,
			relief=FLAT, command=closeWindow).grid(row=0, column=1, padx=10)