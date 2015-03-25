import Tkinter as tk
import tkFont
import webbrowser
from PIL import ImageTk, Image

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.initImages()
        self.master.resizable(width=False, height=False)
        self.index = 0
        self.master.bind("<Return>", self.close)
        self.grid()

    def close(self, event):
        self.master.destroy()

    def center(self): #Stolen from http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
        """
        centers a tkinter window
        """
        win = self.master
        win.minsize(100,100)
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

    def initImages(self):
        self.images = {}
        buf = Image.open(r"images\Classic.png")
        buf = buf.resize((20, 20), Image.ANTIALIAS) #The (250, 250) is (height, width)
        self.images['Classic'] = ImageTk.PhotoImage(buf)

        buf = Image.open(r"images\Jeopardy.png")
        buf = buf.resize((20, 20), Image.ANTIALIAS)
        self.images['Jeopardy'] = ImageTk.PhotoImage(buf)

        buf = Image.open(r"images\On-site.png")
        buf = buf.resize((20, 20), Image.ANTIALIAS)
        self.images['On-site'] = ImageTk.PhotoImage(buf)

        buf = Image.open(r"images\On-line.png")
        buf = buf.resize((20, 20), Image.ANTIALIAS)
        self.images['On-line'] = ImageTk.PhotoImage(buf)

    def google_link_callback(event, site):
        webbrowser.open_new(site)

    def ShowImages(self, frame_in, type_img, place_img):
        label = tk.Label(frame_in, image=self.images[type_img])
        label.pack(side="right")

        label = tk.Label(frame_in, image=self.images[place_img])
        label.pack(side="right")

    def createWidgets(self, dict_of_data):
        frame = tk.Frame(self, relief='sunken')
        frame.grid(row=0, column=self.index, sticky="WN")
        frame_in = tk.Frame(frame)
        frame_in.grid(row=0, sticky="WE", column=self.index)

        header = tk.Label(frame_in, anchor="nw", justify="left", text="Игра: ")
        header.pack(expand=True, fill="x", side="left")

        self.ShowImages(frame_in, dict_of_data["type"], dict_of_data["place_type"])

        header = tk.Label(frame, anchor="nw", justify="left", text="Состояние: ")
        header.grid(row=1, sticky="WE", column=self.index)

        header = tk.Label(frame, anchor='nw', justify="left", text="Дата проведения: ", height=2)
        header.grid(row=3, sticky="WEN", column=self.index)

        header = tk.Label(frame, anchor="nw", justify="left", text="Продолжительность: ")
        header.grid(row=5, sticky="WE", column=self.index)

        header = tk.Label(frame, anchor="nw", justify="left", text="Сайт игры: ")
        header.grid(row=6, sticky="WE", column=self.index)

        header = tk.Label(frame, anchor="nw", justify="left", text="Ранг: ")
        header.grid(row=7, sticky="WE", column=self.index)

        self.index += 1

        frame2 = tk.Frame(self, relief='sunken')
        frame2.grid(row=0, column=self.index, sticky="WN")

        header = tk.Label(frame2, anchor="nw", justify="left", text=dict_of_data["name"])
        header.grid(row=0, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=dict_of_data["state"])
        header.grid(row=1, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=dict_of_data["date"]['start'].strftime("с %d %B в %H:%M"))
        header.grid(row=2, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=dict_of_data["date"]['end'].strftime("до %d %B в %H:%M"))
        header.grid(row=3, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text="%d дней %d часов" %(dict_of_data["duration"]['days'], dict_of_data["duration"]['hours']))
        header.grid(row=4, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", fg='blue', font=tkFont.Font(underline=1, size=10), cursor="hand2", text=dict_of_data["site"])
        header.bind("<Button-1>", lambda e:self.google_link_callback(dict_of_data["site"]))
        header.grid(row=5, sticky="WE", column=self.index)

        header = tk.Label(frame2, anchor="nw", justify="left", text=dict_of_data["rank"])
        header.grid(row=6, sticky="WE", column=self.index)

        self.index += 1

if __name__ == "__main__":
    app = Application()
    app.master.title('Sample application')
    app.createWidgets({'name':"Человек АНТОН", 'state':"", "type":"", "date":{"start":"", 'end':""}, 'duration':{'days':'', 'hours':''}, 'site':'', 'rank':''})
    app.mainloop()
