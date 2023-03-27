import calendarParse

import tkinter
import customtkinter
import time
from time import strftime
import datetime
import calendar





class clockFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.noto = customtkinter.CTkFont(family='Noto Sans KR',size=80)
        self.notobold = customtkinter.CTkFont(family='Noto Sans KR', size=150, weight='bold')
        self.day_label = customtkinter.CTkLabel(master=self,anchor='se')
        self.clock_label = customtkinter.CTkLabel(master=self,anchor='sw')
        #self.grid_columnconfigure((0,1), weight=1)
        self.clockUpdate()

    def clockUpdate(self):
        time_string = strftime('%H:%M:%S')
        self.clock_label.configure(text=time_string, font=self.notobold)

        day_string = strftime('%m.%d. %a')
        self.day_label.configure(text=day_string, font=self.noto)

        self.day_label.place(relx=0.25,y=185,anchor='s')
        self.clock_label.place(relx=0.7,y=200,anchor='s')
        self.after(1000, self.clockUpdate)

class calendarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.userid = dict()
        self.now = datetime.datetime.now()
        self.todays_calendar = calendar.Calendar()
        self.todays_calendar.setfirstweekday(6)
        self.day_list = self.todays_calendar.monthdatescalendar(self.now.year, self.now.month)
        self.columnconfigure((0,1,2,3,4,5,6),weight=1,uniform='gay')
        self.rowconfigure((1,2,3,4,5),weight=1,uniform='gay')

        self.marked_day = self.now.date()

        self.cal_font = customtkinter.CTkFont(family='Noto Sans KR', size = 20)

        self.color_list = {'offday':'gray50', 'default':'azure', 'sun':'firebrick3', 'sat':'dodger blue', 'event':'OliveDrab1'}
        self.weekday_list = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']

        self.label_list = [[customtkinter.CTkLabel(master=self,pady=20,font=self.cal_font,text='wd') for i in range(7)]]+[[customtkinter.CTkLabel(master=self,anchor='nw',padx=10,font=self.cal_font,text='day',justify='left', wraplength=200) for i in range(7)] for j in range(len(self.day_list))]
        self.label_text_list = []

        rtn = []
        for i in range(7):
            self.label_list[0][i].configure(text=self.weekday_list[i], text_color=self.color_list['default'], fg_color='gray15')
            rtn.append(textManager(self.weekday_list[i], (self.color_list['default'], self.color_list['event']), 'gray15'))
        self.label_text_list.append(rtn)

        for i in range(len(self.day_list)):
            rtn = []
            for j in range(7):
                today = self.day_list[i][j]
                clr = self.colorPalette(today)
                ec = self.color_list['event']
                if today == self.now.date():
                    self.label_list[i+1][j].configure(text=today.day, text_color = clr, fg_color = 'gray40')
                    rtn.append(textManager(today.day, (clr,ec), 'gray40'))
                else:
                    self.label_list[i+1][j].configure(text=today.day, text_color = clr, fg_color = 'gray30')
                    rtn.append(textManager(today.day, (clr,ec), 'gray30'))
            self.label_text_list.append(rtn)

        for i in range(len(self.day_list)+1):
            for j in range(7):
                self.label_list[i][j].grid(row=i,column=j,sticky='nsew',padx=2,pady=2)
        
        self.eventUpdate()
        self.calendarUpdate()
        

    def calendarUpdate(self):
        self.now = datetime.datetime.now()
        self.todays_calendar = calendar.Calendar()
        self.todays_calendar.setfirstweekday(6)
        self.day_list = self.todays_calendar.monthdatescalendar(self.now.year, self.now.month)

        for i in range(len(self.day_list)+1):
            for j in range(7):
                current_value = self.label_text_list[i][j]
                self.label_list[i][j].configure(text = current_value.getText(), fg_color=current_value.fgc, text_color=current_value.tc)
        
        self.after(30000,self.calendarUpdate)


    def colorPalette(self, d):
        if d.month != self.now.month:
            return self.color_list['offday']
        if d.weekday() == 6:
            return self.color_list['sun']
        if d.weekday() == 5:
            return self.color_list['sat']
        return self.color_list['default']
    
    def eventUpdate(self):
        for i in self.label_text_list:
            for j in i:
                j.clearEvent()
        
        self.event_list = calendarParse.getiCal()
        linear_date = [j for sub in self.day_list for j in sub]
        for event in self.event_list:
            for i in range(len(linear_date)):
                starttime = event.start
                endtime = event.end
                today = linear_date[i]
                if starttime.date() == today:
                    today_text = self.label_text_list[i//7+1][i%7]
                    txt = '\n{1}-{2}\n{0}'.format(event.summary, starttime.strftime('%H:%M'), endtime.strftime('%H:%M'))
                    new_event = eventManager(starttime, endtime, txt)
                    today_text.addEvent(new_event)
                    break
        print('event updated')
        self.after(60000, self.eventUpdate)

class eventManager:
    def __init__(self, st, et, txt):
        self.start = st
        self.end = et
        self.txt = txt
    
    def __eq__(self, other):
        return self.start == other.start
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        return self.start < other.start

class textManager:
    def __init__(self, day, text_color, foreground_color):
        self.events = []
        self.day = day
        self.tc = text_color[0]
        self.__text_color = text_color # [w/ events, w/o events]
        self.fgc = foreground_color

    def addEvent(self, ev):
        self.events.append(ev)
        self.tc = self.__text_color[1]

    def clearEvent(self):
        self.events = []
        self.tc = self.__text_color[0]
    
    def getText(self):
        self.events.sort()
        rtn = str(self.day)+'\n'
        for e in self.events:
            rtn += e.txt
        return rtn

class todoFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

        # configure window
        self.title("iCal")
        self.geometry(f"{1920}x{1080}")
        self.attributes('-fullscreen', False)

        self.grid_rowconfigure(1,weight = 2)
        self.grid_columnconfigure(0,weight=1)

        self.clock_frame = clockFrame(master = self)
        self.clock_frame.grid(row=0,columnspan=2,sticky='new')

        self.calendar_frame = calendarFrame(master = self,)
        self.calendar_frame.grid(row=1,column=0,sticky='nsew')

        #self.todo_list_frame = todoFrame(master = self)
        #self.todo_list_frame.grid(row=1,column=1,sticky='nse')
    


if __name__ == "__main__":
    app = App()
    app.mainloop()