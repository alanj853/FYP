# from Tkinter import *
# import tkMessageBox
# import Tkinter, time

# top = Tk()

# Lb1 = Listbox(top, height = 28, width = 46)
# Lb1.insert(1, "=======================================")
# Lb1.insert(2, "===============CONTROLS================")
# Lb1.insert(3, "=======================================")
# Lb1.insert(4, "***************Thrust***************")
# Lb1.insert(5, "		     Take-off: p")
# Lb1.insert(6, "		High Increase: t")
# Lb1.insert(7, "		 Low Increase: w")
# Lb1.insert(8, "		High Increase: g")
# Lb1.insert(9, "		 Low Decrease: s")
# Lb1.insert(10, "***************Pitch***************")
# Lb1.insert(11, "		      Forward: up-arrow")
# Lb1.insert(12, "		    Backwards: down-arrow")
# Lb1.insert(13, "***************Roll***************")
# Lb1.insert(14, "			 Left: left-arrow")
# Lb1.insert(15, "			Right: right-arrow")
# Lb1.insert(16, "***************YAW***************")
# Lb1.insert(17, "			 Left: a")
# Lb1.insert(18, "			Right: d")
# Lb1.insert(19, "***************HOVER***************")
# Lb1.insert(20, "		     Hover ON: h")
# Lb1.insert(21, "		    Hover OFF: j")
# Lb1.insert(22, "***************LAND***************")
# Lb1.insert(23, "		         Land: l")
# Lb1.insert(24, "***************EMERGENCY STOP***************")
# Lb1.insert(25, "		   Motors OFF: o")
# Lb1.insert(26, "=======================================")
# Lb1.insert(27, "=======================================")
# Lb1.insert(28, "=======================================")

# #Lb1.height(28)

# Lb1.pack()
# top.mainloop()
# time.sleep(5)
# top.quit()

import time
from Tkinter import *
 
root = Tk()
root.geometry('100x50+20+20')
 
mainframe = Frame(root)
mainframe.grid(column=1000, row=1000, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
 
best = StringVar()
best.set('start')
x1 = 12
Label(mainframe,textvariable=best,bg='#321000',fg='#000fff000',font=("Helvetica",x1)).grid(column=1,row=1)
 
for x in range(10):
    time.sleep(1.0)
    best.set('test # %d' % (x))
    mainframe.update()
root.mainloop() 
