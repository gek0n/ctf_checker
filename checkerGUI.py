# -*- coding: utf-8 -*-
import Tkinter as tk
import tkFont
import webbrowser
import os
from PIL import ImageTk, Image
import ctypes


def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text.encode('cp1251', 'ignore'), title.encode('cp1251', 'ignore'), style)


class Application(tk.Frame):

    def __init__(self, pwd="", master=None):
        tk.Frame.__init__(self, master)
        self.initImages(pwd)
        self.master.resizable(width=False, height=False)
        self.index = 0
        self.master.bind("<Return>", self.close)
        self.grid()
        self.games = []
        global gamesHiddenFlags
        gamesHiddenFlags = {}

    def close(self, event):
        self.master.destroy()

    def center(self):  # Stolen from http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
        """
        centers a tkinter window
        """
        win = self.master
        win.minsize(100, 100)
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def initialize(self, games):
        self.games = games
        for game in self.games:
            gamesHiddenFlags[game.name] = tk.BooleanVar()
            self.createWidgetsFromGame(game, gamesHiddenFlags[game.name])

    def addGame(self, game):
        self.games.append(game)

    def addGames(self, listOfGames):
        self.games.extend(listOfGames)

    def initImages(self, path):
        self.images = {}
        buf = Image.open(os.path.join(path, "images", "Classic.png"))
        buf = buf.resize((20, 20), Image.ANTIALIAS)  # The (250, 250) is (height, width)
        self.images['Classic'] = ImageTk.PhotoImage(buf)

        buf = Image.open(os.path.join(path, "images", "Jeopardy.png"))
        buf = buf.resize((20, 20), Image.ANTIALIAS)
        self.images['Jeopardy'] = ImageTk.PhotoImage(buf)

        buf = Image.open(os.path.join(path, "images", "On-site.png"))
        buf = buf.resize((20, 20), Image.ANTIALIAS)
        self.images['On-site'] = ImageTk.PhotoImage(buf)

        buf = Image.open(os.path.join(path, "images", "On-line.png"))
        buf = buf.resize((20, 20), Image.ANTIALIAS)
        self.images['On-line'] = ImageTk.PhotoImage(buf)

    def google_link_callback(event, site):
        webbrowser.open_new(site)

    def ShowImages(self, frame_in, type_img, place_img):
        type_img = type_img.replace("Attack-Defense", "Classic").replace("Attack", "Classic")
        type_img = type_img.replace("Hack quest", "Jeopardy")
        label = tk.Label(frame_in, image=self.images[type_img])
        label.pack(side="right")

        label = tk.Label(frame_in, image=self.images[place_img])
        label.pack(side="right")

    def createRow(self, frame, t, h, i):
        header = tk.Label(frame, anchor="nw", justify="left", text=t, height=h)
        header.grid(row=i, sticky="WE", column=self.index)

    def createWidgetsFromGame(self, game, flag):
        frame = tk.Frame(self, relief='sunken')
        frame.grid(row=0, column=self.index, sticky="WN")
        frame_in = tk.Frame(frame)
        frame_in.grid(row=0, sticky="WE", column=self.index)

        header = tk.Label(frame_in, anchor="nw", justify="left", text="Игра: ")
        header.pack(expand=True, fill="x", side="left")

        self.ShowImages(frame_in, game.type, game.place_type)

        self.createRow(frame, "Состояние: ", 1, 1)

        self.createRow(frame, "Дата проведения: ", 2, 3)

        self.createRow(frame, "Продолжительность: ", 1, 5)

        self.createRow(frame, "Сайт игры: ", 1, 6)

        self.createRow(frame, "Ранг: ", 1, 7)

        header = tk.Checkbutton(frame, text="Не показывать: ", variable=flag)
        header.grid(row=8, sticky="WE", column=self.index)

        self.index += 1

        frame2 = tk.Frame(self, relief='sunken')
        frame2.grid(row=0, column=self.index, sticky="WN")

        header = tk.Label(frame2, anchor="nw", justify="left", text=game.name)
        header.grid(row=0, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=game.state)
        header.grid(row=1, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=game.date['start'].strftime("с %d %B в %H:%M"))
        header.grid(row=2, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=game.date['end'].strftime("до %d %B в %H:%M"))
        header.grid(row=3, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text="%d дней %d часов" % (game.duration['days'], game.duration['hours']))
        header.grid(row=4, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", fg='blue', font=tkFont.Font(underline=1, size=10), cursor="hand2", text=game.site)
        header.bind("<Button-1>", lambda e: self.google_link_callback(game.site))
        header.grid(row=5, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=game.rank)
        header.grid(row=6, sticky="WE", column=self.index)

        self.index += 1

if __name__ == "__main__":
    app = Application()
    app.master.title('Sample application')
    app.mainloop()
