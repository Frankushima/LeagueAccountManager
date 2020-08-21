# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 21:23:20 2020

@author: Frank Yao

"""
import subprocess
import time
import pyautogui as ag
import PySimpleGUI as sg
import pickle
from ahk import AHK



seperator = f'--seperator--'

#./ means look in directory?
ahk = AHK(executable_path='AutoHotkey.exe')

# TO DO:
# DONE! Fix Bug that only allows 1 account to be added at a time
# DONE! Make it into an .exe file
# DONE! Encrypt the info? - Pickle it
# DONE! include a file searching gui to allow to modify if the file is not found (for game location)
# DONE! Include a file reading function to modify the dictionary based on whats inside
# DONE! warn user if they enter a ~, or make it a special code -  {seperator}
# progress bar?
# DONE! Include a graphical interface with MessageBoxes to add
# DONE! add deleting to GUI
# What if empty or something is corrupted?
# DONE! update GUI Live (deleting and adding accs)
# add an edit function? - Im too lazy
# DONE! find window coords to optimize this
# DONE! then section off the area of the window to omptimize this more

# Reminders
# When compiling as an EXE add:
# ahk.exe, the ahk/templates folder, the reference images, and Files folder


# Open pickled objects or intialize defaults

leaguePath = ''
userDict = {}

try:
    path_Pickle_in = open("path.pickle", "rb")
    leaguePath = pickle.load(path_Pickle_in)

    userDict_Pickle_in = open("userDict.pickle", "rb")
    userDict = pickle.load(userDict_Pickle_in)

except FileNotFoundError:
    leaguePath = 'C:\\Riot Games\\League of Legends\\LeagueClient.exe'
    userDict = {}

sg.theme('LightBlue6')


# returns a layout variable to whats currently on the text document and updates the UserDict
def setWin1():

    # Heres what this really long line says:
    # Hidden input (so filebrowse triggers events), browse button, add accounts button
    layout = [sg.Input(key = '-FILE-',visible= False, enable_events= True),sg.FileBrowse(button_text='Browse File Path for League',font =("Times New Roman", 24),button_color=('white', 'green')),sg.Button('Add Accounts', font=("Times New Roman", 24), button_color=('white', 'green'))],

    for name in userDict.keys():
        layout += [sg.Button(name, font=("Times New Roman", 24)),
                   sg.Button("X", button_color=('white', 'red'), font=("Times New Roman", 24),
                             key="-delete-" + name)],

    layout += [sg.Button('Quit', button_color=('black', 'red'), font=("Times New Roman", 24))],


    return sg.Window("Frank's League Account Manager", layout, finalize= True)


def setWin2():
    layout = [[sg.Text('Account Name'), sg.InputText(key='-IN-name')],
               [sg.Text('Username'), sg.InputText(key='-IN-user')],
               [sg.Text('Password'), sg.InputText(key='-IN-pass')],
               [sg.Submit(button_color=('white', 'green')), sg.Cancel(button_color=('white', 'red'))]]
    return  sg.Window("Add Accounts", layout, finalize= True)

def pickleVals():
    path_Pickle_out = open("path.pickle", "wb")
    pickle.dump(leaguePath, path_Pickle_out)
    path_Pickle_out.close()

    userDict_Pickle_out = open("userDict.pickle", "wb")
    pickle.dump(userDict, userDict_Pickle_out)
    userDict_Pickle_out.close()


# Creates windows are account selection and creation


win1,win2 = setWin1(), None
# handle account selection here
while True:
    window ,event, values = sg.read_all_windows()

    # Window 1
    if window == win1 and event in (sg.WIN_CLOSED,'Quit'):
        pickleVals()
        raise SystemExit(0)
    elif event.__contains__("-delete-"):
        name = event.replace('-delete-','')

        del userDict[name]

        win1.close()
        win1 = setWin1()
    elif event == 'Add Accounts' and not win2:
        win2 = setWin2()
    elif event == '-FILE-' and not win2:
        path = values['-FILE-']

        leaguePath = path.replace('/', '\\')

    elif not win2:
        userName, password = userDict[event][0] , userDict[event][1]
        break

    # Window 2
    if window == win2 and event in (sg.WIN_CLOSED,'Cancel'):
        win2.close()
        win2 = None
    elif window == win2 and event == 'Submit':

        userDict[values['-IN-name']] = [values['-IN-user'],values['-IN-pass']]

        win2.close()
        win2 = None
        win1.close()
        win1 = setWin1()


# close win2 if its still open
if win2 is not None:
    win2.close()


try:
    subprocess.Popen(leaguePath)
except FileNotFoundError:
    ag.alert(text = "Error 404, File not found, change file path to correct one", title = "Error", button = "OK")
timePassed = 0

while True:
    tic = time.perf_counter()
    win = ahk.win_get(title = "Riot Client")

    # Honestly this might be a waste of time considering Window Active != actually showing up on screen
    if win.exist:
        break
    elif timePassed > 60:
        break
        ag.alert(text = "Timed out, League Client is not running properly", title = "Error", button = "OK")

    time.sleep(0.05)
    toc = time.perf_counter()
    timePassed += tic - toc

win.activate()

winLoc = win.rect
winX = winLoc[0]
winY = winLoc[1]
winX2 = winX + (winLoc[2] // 2)
winY2 = winY + winLoc[3]

resetClickLoc = ()

while True:
    resetClickLoc = ahk.image_search(image_path='ReferenceImages\\reference.png', color_variation=70,upper_bound= [winX,winY],lower_bound = [winX2,winY2])
    if resetClickLoc is not None:
        break

resetClickLoc = ahk.image_search(image_path = 'ReferenceImages\\reference.png', color_variation= 70,upper_bound= [winX,winY],lower_bound = [winX2,winY2])
ahk.click(resetClickLoc[0],resetClickLoc[1])

# Pause to make sure the computer has time to rescan the login screen after mouse is moved off the username button
time.sleep(0.1)

userLoc = ahk.image_search(image_path='ReferenceImages\\usernameBox.jpg', color_variation=70,upper_bound= [winX,winY],lower_bound = [winX2,winY2])
ahk.click(userLoc[0] + 150, userLoc[1] + 30)
# ahk.type() doesn't work for equal signs
ag.write(userName)

passLoc = ahk.image_search(image_path = 'ReferenceImages\\passwordBox.jpg', color_variation= 70,upper_bound= [winX,winY],lower_bound = [winX2,winY2])
ahk.click(passLoc[0] + 150,passLoc[1] + 30)
ag.write(password)
ahk.send_event('{Enter}')

# pickle all objects here
pickleVals()
