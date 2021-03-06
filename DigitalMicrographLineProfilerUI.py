import os
import json
import jsonpickle
import tkinter
from tkinter import Tk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pickle
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class SetupOptions:
    def __init__(self):
        self.useCenteredLine = True
        self.useLogData = True
        self.profileLineWidth = 3
        self.imageFilePath = ''


def fileHandling(annotationFileName):
    with open(annotationFileName, 'rb') as handle:
        fileContents = pickle.loads(handle.read())
    return fileContents


def getFileOrDir(fileOrFolder: str = 'file', titleStr: str = 'Choose a file', fileTypes: str = None, initialDirOrFile: str = os.getcwd()):
    if os.path.isfile(initialDirOrFile) or os.path.isdir(initialDirOrFile):
        initialDir = os.path.split(initialDirOrFile)[0]
    else:
        initialDir = initialDirOrFile
    root = Tk()
    root.withdraw()
    assert fileOrFolder.lower() == 'file' or fileOrFolder.lower() == 'folder', "Only file or folder is an allowed string choice for fileOrFolder"
    if fileOrFolder.lower() == 'file':
        fileOrFolderList = filedialog.askopenfilename(initialdir=initialDir, title=titleStr, filetypes=[(fileTypes + "file", fileTypes)])
    else:  # Must be folder from assert statement
        fileOrFolderList = filedialog.askdirectory(initialdir=initialDir, title=titleStr)
    if not fileOrFolderList:
        fileOrFolderList = initialDirOrFile
    root.destroy()
    return fileOrFolderList


def strToFloat(numberString):
    if numberString:
        charFreeStr = ''.join(ch for ch in numberString if ch.isdigit() or ch == '.' or ch == ',')
        if charFreeStr:
            return float(locale.atof(charFreeStr))
        return ''
    return ''


def get_file(entryField, entryFieldText, titleMessage, fileFormatsStr):
    listName = getFileOrDir('file', titleMessage, fileFormatsStr, entryFieldText.get().replace('~', os.path.expanduser('~')))
    entryFieldText.set(listName.replace(os.path.expanduser('~'), '~'))
    entryField.config(width=len(listName.replace(os.path.expanduser('~'), '~')))


def get_setupOptions(savedJSONFileName):
    try:
        with open(savedJSONFileName) as infile:
            inputFile = json.load(infile)
        setupOptions = jsonpickle.decode(inputFile)
    except FileNotFoundError:
        setupOptions = SetupOptions()
    return setupOptions


def on_closing(win, setupOptions, savedJSONFileName, ImageEntryText, useLogDataVar, useCenteredLineVar, profileLineWidthVar):
    setupOptions.imageFilePath = ImageEntryText.get().replace('~', os.path.expanduser('~'))
    setupOptions.useLogData = useLogDataVar.get()
    setupOptions.useCenteredLine = useCenteredLineVar.get()
    setupOptions.profileLineWidth = int(strToFloat(profileLineWidthVar.get()))

    with open(savedJSONFileName, 'w') as outfile:
        json.dump(jsonpickle.encode(setupOptions), outfile)
    win.destroy()


class TextValidator(object):
    def __init__(self, tkWindow, minimumProfileWidth, maximumProfileWidth):
        self.tkWindow = tkWindow
        self.minimumProfileWidth = minimumProfileWidth
        self.maximumProfileWidth = maximumProfileWidth

    def stringNumberRangeValidator(self, proposedText, minimumValue, maximumValue):
        if proposedText == '':
            return True
        if not proposedText.replace('.', '', 1).isdigit():
            self.tkWindow.bell()
            return False
        numberFloat = strToFloat(proposedText)
        if minimumValue <= numberFloat <= maximumValue:
            return True
        self.tkWindow.bell()
        return False

    def profileWidthValidator(self, proposedText):
        return self.stringNumberRangeValidator(proposedText, self.minimumProfileWidth, self.maximumProfileWidth)


def uiInput(win, setupOptions, savedJSONFileName):
    win.title("Spectrum Data Processing Setup UI")
    ImageEntryText = tkinter.StringVar(value=setupOptions.imageFilePath.replace(os.path.expanduser('~'), '~'))
    useLogDataVar = tkinter.BooleanVar(value=setupOptions.useLogData)
    useCenteredLineVar = tkinter.BooleanVar(value=setupOptions.useCenteredLine)
    profileLineWidthVar = tkinter.StringVar(value=setupOptions.profileLineWidth)

    tkinter.Label(win, text="Image File:").grid(row=0, column=0)
    ImageFileEntry = tkinter.Entry(win, textvariable=ImageEntryText, width=len(setupOptions.imageFilePath.replace(os.path.expanduser('~'), '~')))
    ImageFileEntry.grid(row=1, column=0)
    tkinter.Button(win, text='Choose File', command=lambda: get_file(ImageFileEntry, ImageEntryText, 'Choose DM File', '.dm3 .dm4')).grid(row=1, column=1)

    tkinter.Label(win, text="Data scaling type").grid(row=2, column=0)
    tkinter.Radiobutton(win, text="Log", variable=useLogDataVar, value=1).grid(row=2, column=1)
    tkinter.Radiobutton(win, text="Linear", variable=useLogDataVar, value=0).grid(row=2, column=2)

    tkinter.Label(win, text="Constrain line center to transmitted beam").grid(row=3, column=0)
    tkinter.Radiobutton(win, text="Centered", variable=useCenteredLineVar, value=1).grid(row=3, column=1)
    tkinter.Radiobutton(win, text="Free", variable=useCenteredLineVar, value=0).grid(row=3, column=2)

    tkinter.Label(win, text="Profile line averaging width (pixels)").grid(row=4, column=0)

    txtValidator = TextValidator(win, 1, 1000)
    validateFunction = (win.register(txtValidator.profileWidthValidator), '%P')
    tkinter.Entry(win, textvariable=profileLineWidthVar, validate='all', validatecommand=validateFunction).grid(row=4, column=1)

    win.protocol("WM_DELETE_WINDOW", lambda: on_closing(win, setupOptions, savedJSONFileName, ImageEntryText, useLogDataVar, useCenteredLineVar, profileLineWidthVar))
    win.mainloop()


def setupOptionsUI():
    savedJSONFileName = 'DigitalMicrographLineProfilerSetupOptions.json'
    setupOptions = get_setupOptions(savedJSONFileName)  # Read previously used setupOptions
    uiInput(Tk(), setupOptions, savedJSONFileName)
    return setupOptions


# setupOptionsUI()