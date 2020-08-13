# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 21:23:20 2020

@author: Frank Yao

"""
import subprocess
import time
import pyautogui as ag
import PySimpleGUI as sg
from ahk import AHK


seperator = '~~~'

ahk = AHK(executable_path='AutoHotkey.exe')

# TO DO:
# Fix Bug that only allows 1 account to be added at a time
# Make it into an .exe file
# Encrypt the info?
# include a file searching gui to allow to modify if the file is not found (for game location)
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


userDict = {}
infoPath = 'Files\\info.txt'
leaguePathFilePath = 'Files\\FilePath.txt'

PathFile = open(leaguePathFilePath, 'r')
leaguePath =  PathFile.readline().replace('/','\\')

sg.theme('LightBlue6')


# returns a layout variable to whats currently on the text document and updates the UserDict
def updateLayout():
    # clear userDict
    userDict = {}

    # read file, create list of lines, close file
    infoFile = open(infoPath, 'r')
    listOfInfo = infoFile.readlines()
    infoFile.close()

    # enter values into userDct and create layout
    for s in listOfInfo:
        info = s.split(seperator)
        userDict[info[0]] = [info[1],info[2]]

    # sg.FileBrowse(key = 'browse',button_text='Browse File Path for League',font =("Times New Roman", 24),button_color=('white', 'green'))
    layout = [sg.Button('Add Accounts', font=("Times New Roman", 24),button_color=('white', 'green'))],

    rowNum = 0
    for n in userDict.keys():
        layout += [sg.Button(n, font=("Times New Roman", 24)), sg.Button("X", button_color=('white', 'red'),font=("Times New Roman", 24), key="-delete-" + str(rowNum))],
        rowNum += 1


    layout += [sg.Button('Quit',button_color=('black', 'red'), font=("Times New Roman", 24))],

    return userDict,layout

# Deletes line found at num
def delLine(num):
    infoFile = open(infoPath, 'r')
    lines = infoFile.readlines()
    infoFile.close()

    del(lines[num])

    new_file = open(infoPath, "w+")
    for line in lines:
        new_file.write(line)

    new_file.close()

#
def setWin():
    return sg.Window("Frank's League Account Manager", layout1)

# Creates windows are account selection and creation
layout2 = [[sg.Text('Account Name'), sg.InputText(key='-IN-name')],
           [sg.Text('Username'), sg.InputText(key='-IN-user')],
            [sg.Text('Password'), sg.InputText(key='-IN-pass')],
                 [sg.Submit(button_color=('white', 'green')), sg.Cancel(button_color=('white', 'red'))]]


userDict, layout1 = updateLayout()

win1 = setWin()

# handle account selection here
while True:
    ev1, vals1 = win1.Read()

    if ev1 == sg.WIN_CLOSED or ev1 == 'Quit':
        raise SystemExit(0)
    elif ev1.__contains__("-delete-"):
        rowNum = ev1.replace('-delete-','')
        delLine(int(rowNum))
        win1.close()
        userDict, layout1 = updateLayout()
        win1 = setWin()
    elif ev1 == 'Add Accounts':
        while True:
            win2 = sg.Window("Add Accounts", layout2)
            ev2, vals2 = win2.Read()

            if ev2 == sg.WIN_CLOSED or ev2 == 'Cancel':
                win2.close()
                break
            else:
                f = open(infoPath, "a+")
                f.write(vals2['-IN-name'] + seperator + vals2['-IN-user'] + seperator + vals2['-IN-pass'] + '\n')
                win2.close()
                f.close()
                win1.close()
                userDict, layout1 = updateLayout()
                win1 = setWin()
                break
    else:
        userName, password = userDict[ev1][0] , userDict[ev1][1]
        break


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
ahk.type(userName)

passLoc = ahk.image_search(image_path = 'ReferenceImages\\passwordBox.jpg', color_variation= 70,upper_bound= [winX,winY],lower_bound = [winX2,winY2])
ahk.click(passLoc[0] + 150,passLoc[1] + 30)
ahk.type(password)
ahk.send_event('{Enter}')
