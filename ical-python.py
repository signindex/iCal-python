import click
import sys
from pyicloud import PyiCloudService

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
        #self.clock_label.tag_configure('start', foreground = 'red')
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

        #self.userid = dict()
        #self.userReader()
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

        self.label_list = [[customtkinter.CTkTextbox(master=self,pady=20,font=self.cal_font,height=10) for i in range(7)]]+[[customtkinter.CTkTextbox(master=self,padx=10,font=self.cal_font) for i in range(7)] for j in range(len(self.day_list))]
        self.event_list = []

        for i in range(7):
            self.label_list[0][i].configure(text_color=self.color_list['default'], fg_color='gray15')
            self.label_list[0][i].insert('end', self.weekday_list[i])

        for i in range(len(self.day_list)):
            for j in range(7):
                today = self.day_list[i][j]
                clr = self.colorPalette(today)
                if today == self.now.date():
                    self.label_list[i+1][j].configure(text_color = clr, fg_color = 'gray40')
                else:
                    self.label_list[i+1][j].configure(text_color = clr, fg_color = 'gray30')
                self.label_list[i+1][j].insert('end', today.day)

        for i in range(len(self.day_list)+1):
            for j in range(7):
                self.label_list[i][j].grid(row=i,column=j,sticky='nsew',padx=2,pady=2)
        
        #self.eventUpdate()
        #self.calendarUpdate()
        

    def calendarUpdate(self):
        self.now = datetime.datetime.now()
        self.todays_calendar = calendar.Calendar()
        self.todays_calendar.setfirstweekday(6)
        self.day_list = self.todays_calendar.monthdatescalendar(self.now.year, self.now.month)

        for i in range(len(self.day_list)+1):
            for j in range(7):
                current_value = self.label_text_list[i][j]
                self.label_list[i][j].configure(fg_color=current_value[2], text = current_value[0], text_color = current_value[1])
        
        self.after(30000,self.calendarUpdate)
        
    def colorPalette(self, d):
        if d.month != self.now.month:
            return self.color_list['offday']
        if d.weekday() == 6:
            return self.color_list['sun']
        if d.weekday() == 5:
            return self.color_list['sat']
        return self.color_list['default']
    
    def getiCal(self):
        print("Py iCloud Services")
        api = PyiCloudService(self.userid['id'], self.userid['pw'])

        if api.requires_2fa:
            print("Two-factor authentication required. Your trusted devices are:")

            devices = api.trusted_devices
            for i, device in enumerate(devices):
                print(
                    "  %s: %s"
                    % (i, device.get("deviceName", "SMS to %s" % device.get("phoneNumber")))
                )

            device = click.prompt("Which device would you like to use?", default=0)
            device = devices[device]
            if not api.send_verification_code(device):
                print("Failed to send verification code")
                sys.exit(1)

            code = click.prompt("Please enter validation code")
            if not api.validate_verification_code(device, code):
                print("Failed to verify verification code")
                sys.exit(1)

        event_list_raw = api.calendar.events()
        return event_list_raw
    
    def userReader(self):
        try:
            idfile = open("./userid.txt", 'r')
            l = idfile.readlines()
            for line in l:
                key,val = line.split('=')
                self.userid[key] = val
            idfile.close()
            self.getiCal() #test
        except:
            print('Failed to get user id. Please enter it manually.')
            self.userid['id'] = input('your email: ')
            self.userid['pw'] = input('your password: ')

            ans = input('Do you want to save the login data? Y/N: ')
            while True:
                if ans == 'Y' or ans == 'y':
                    idfile_save = open('./userid.txt', 'w')
                    idfile_save.write("id={0}\npw={1}".format(self.userid['id'], self.userid['pw']))
                    idfile_save.close()
                    break
                elif ans == 'N' or ans == 'n':
                    break
                else:
                    ans = input('Y/N: ')

    def eventUpdate(self):
        self.event_list = self.getiCal()
        linear_date = [j for sub in self.day_list for j in sub]
        for event in self.event_list:
            for i in range(len(linear_date)):
                starttime = datetime.datetime(*event['startDate'][1:6])
                endtime = datetime.datetime(*event['endDate'][1:6])
                today = linear_date[i]
                if starttime.date() == today:
                    today_text = self.label_text_list[i//7+1][i%7]
                    txt = '{0}\n{2}-{3}\n{1}'.format(today.day, event['title'], starttime.strftime('%H:%M'), endtime.strftime('%H:%M'))

                    self.label_text_list[i//7+1][i%7] = (txt, self.color_list['event'], self.label_text_list[i//7+1][i%7][2])
                    break

        self.after(60000, self.eventUpdate)

class event:
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
    def __init__(self):
        self.events = []
    
    def addEvent(self, ev):
        self.events.append(ev)
    
    def __repr__(self) -> str:
        self.events.sort()
        rtn = ''
        for e in self.events:
            rtn += e.txt+'\n'
        return rtn[:-1]

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
        self.attributes('-fullscreen', True)

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