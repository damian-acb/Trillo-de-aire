import customtkinter as ctk
import tkinter.messagebox as tkm
import numpy as np


class GUI:

    def __init__(self, size, slider):

        self.size = str(size[0])+'x'+str(size[1])
        self.timers = []

        # Create root window
        self.root = ctk.CTk()
        self.root.geometry(self.size)
        self.root.title('Slider controls')
        self.root.protocol('WM_DELETE_WINDOW', self.close)

        # Create sensor window
        self.sensors = ctk.CTk()
        self.sensors.geometry(self.size+'+'+str(slider.screen.get_size()[0] + size[0])+'+0')
        self.sensors.title('Sensors')
        self.sensors.protocol('WM_DELETE_WINDOW', self.close)

        # Some variables
        self.play_button_text = ctk.StringVar()
        self.play_button_text.set('Play')
        self.mu = ctk.Variable()
        self.mu.set(0)

        self.quit = False
        self.slider = slider

        ctk.set_appearance_mode('light')
        ctk.set_default_color_theme('dark-blue')

        # Create play button
        self.play_button = ctk.CTkButton(master=self.root, textvariable=self.play_button_text, command=self.play,
                                         cursor='hand2', fg_color='#be2517', hover_color='#9e1f13')
        self.play_button.pack(pady=12, padx=30)

        # Create friction frame
        self.frame2 = ctk.CTkFrame(master=self.root)
        self.frame2.pack(pady=12, padx=30, fill='both')

        self.mu_label = ctk.CTkLabel(master=self.frame2, text='Friction')
        self.mu_label.pack(pady=6, padx=20)

        # Create mass frame
        self.frame1 = ctk.CTkFrame(master=self.root)
        self.frame1.pack(pady=20, padx=25, fill='both')

        self.add_entry = ctk.CTkEntry(master=self.frame1, placeholder_text='Insert mass in grams')
        self.add_entry.pack(pady=6, padx=20)

        self.add_button = ctk.CTkButton(master=self.frame1, text='Add', command=self.check_mass, cursor='hand2')
        self.add_button.pack(pady=6, padx=20)

        self.mu_slider = ctk.CTkSlider(master=self.frame2, from_=0, to=1, variable=self.mu, hover=True)
        self.mu_slider.pack(pady=6, padx=4)

        # Create mass options frame
        self.frame3 = ctk.CTkFrame(master=self.root)
        self.mass_label = ctk.CTkLabel(master=self.frame3, text='')
        self.frame4 = ctk.CTkFrame(master=self.frame3)
        self.move_mass_button = ctk.CTkButton(master=self.frame4, text='Move', cursor='hand2')
        self.remove_mass_button = ctk.CTkButton(master=self.frame4, text='Remove', cursor='hand2')

        #
        self.frame5 = ctk.CTkFrame(master=self.root)
        self.add_timer_button = ctk.CTkButton(master=self.frame5, text='Add timer', cursor='hand2', command=self.add_timer)
        self.frame5.pack(pady=20, padx=25)
        self.add_timer_button.pack(pady=6, padx=20)

    def check_mass(self):
        try:
            m = self.add_entry.get()
            n = float(m)/1000
            if 0.001 <= n <= 10:
                self.add_button.configure(state='disabled')
                self.slider.add_mass(n)
            else:
                tkm.showinfo('Value error: mass', 'The range of mass is 10 - 10,000 grams')

        except ValueError:
            tkm.showinfo('Value error: mass', 'Only numbers allowed')

        self.add_entry.delete(0, ctk.END)

    def close(self):
        if tkm.askokcancel('Quit', 'Do you want to close the program ?'):
            self.slider.play = False
            self.quit = True

    def play(self):
        if self.slider.play:
            self.slider.play = False
            self.play_button_text.set('Play')
            self.frame1.pack(pady=20, padx=25, fill='both')
            self.frame5.pack(pady=20, padx=25)
            self.add_timer_button.pack(pady=6, padx=20)

        else:
            self.slider.play = True
            self.play_button_text.set('Pause')
            self.play_button.focus_set()
            self.add_entry.delete(0, ctk.END)
            self.frame1.pack_forget()
            self.frame5.pack_forget()
            self.unselect_mass()

    def select_mass(self, n):

        mass = 'Mass: '+str(self.slider.masses[n]['mass']*1000)+'gr'

        self.frame3.pack(pady=12, padx=30, fill='both', side=ctk.BOTTOM)
        self.mass_label.pack(pady=10)
        self.mass_label.configure(text=mass)
        self.frame4.pack(fill='both', side=ctk.BOTTOM)
        self.frame4.columnconfigure(index=0, weight=1)
        self.frame4.columnconfigure(index=1, weight=1)
        self.move_mass_button.configure(command=lambda: self.move_mass(n))
        self.move_mass_button.grid(row=0, column=0, padx=(0, 10))
        self.remove_mass_button.configure(command=lambda: self.remove_mass(n))
        self.remove_mass_button.grid(row=0, column=1)

    def move_mass(self, n): self.slider.moving_mass = [True, n]

    def remove_mass(self, n):
        self.slider.masses.pop(n)
        self.unselect_mass()

    def unselect_mass(self): self.frame3.pack_forget()

    def add_timer(self):
        self.slider.add_timer()
        Timer = self.slider.timers[-1]
        color = self.rgb_to_hex(self.slider.timers[-1]['color'])
        timer = ctk.CTkFrame(master=self.sensors, fg_color=color)
        timer.pack(pady=12, padx=30, fill='both')

        time = ctk.CTkLabel(master=timer, bg_color='#ffffff')
        time.pack(pady=8, padx=30, fill='x')

        time.configure(text=f'{0: .3f}'+' s')

        buttons = ctk.CTkFrame(master=timer, fg_color=color)
        buttons.pack(fill='both')
        buttons.columnconfigure(index=0, weight=1)
        buttons.columnconfigure(index=1, weight=1)
        buttons.columnconfigure(index=2, weight=1)
        buttons.rowconfigure(index=0, weight=1)
        buttons.rowconfigure(index=1, weight=1)

        pulse_b = ctk.CTkButton(master=buttons, text='Pulse', cursor='hand2',
                                   height=10, corner_radius=0, border_color='#000000', fg_color='#000000')

        pulse_b.configure(command=lambda: self.pulse(Timer))
        pulse_b.grid(row=0, column=0)

        gate_b = ctk.CTkButton(master=buttons, text='Gate', cursor='hand2',
                                   height=10, corner_radius=0, border_color='#000000', fg_color='#666666')
        gate_b.configure(command=lambda: self.gate(Timer))
        gate_b.grid(row=0, column=1)

        add_sensor = ctk.CTkButton(master=buttons, text='Add', cursor='hand2',
                                   height=10, corner_radius=0, border_color='#000000')
        add_sensor.configure(command=lambda: self.slider.add_sensor(Timer))
        add_sensor.grid(row=1, column=0)

        rem_sensor = ctk.CTkButton(master=buttons, text='Remove', cursor='hand2',
                                   height=10, corner_radius=0, border_color='#000000')
        rem_sensor.configure(command=lambda: self.slider.rem_sensor(Timer, True))
        rem_sensor.grid(row=1, column=1)

        res_sensor = ctk.CTkButton(master=buttons, text='Reset', cursor='hand2',
                                   height=10, corner_radius=0, border_color='#000000')
        res_sensor.configure(command=lambda: self.reset_timer(Timer))
        res_sensor.grid(row=1, column=2)

        X = ctk.CTkButton(master=timer, text='x', cursor='hand2', fg_color='#be2517', hover_color='#9e1f13', width=6, height=4)
        X.configure(command=lambda: self.rem_timer(Timer))
        X.place(relx=1., rely=0., x=0, y=0, anchor=ctk.NE)

        self.timers.append([timer, time, Timer, pulse_b, gate_b])

    @staticmethod
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    def update_timer(self, n, reset):
        e = np.random.normal(0, .003, 1)[0] if not reset else 0
        time = self.slider.timers[n]['time'] + e
        self.timers[n][1].configure(text=f'{time: .3f}'+' s')

    def rem_timer(self, Timer):
        self.slider.rem_sensor(Timer, False)
        for timer in self.timers:
            if timer[2] == Timer:
                index = self.timers.index(timer)
                self.timers[index][0].pack_forget()
                self.timers.remove(timer)

    def reset_timer(self, timer):
        n = self.slider.index_timer(timer['id'])
        self.slider.reset_timer(n)
        self.update_timer(n, True)

    def pulse(self, timer):
        n = self.slider.index_timer(timer['id'])
        self.slider.timers[n]['type'] = 'pulse'
        self.timers[n][3].configure(fg_color='#000000')
        self.timers[n][4].configure(fg_color='#666666')

    def gate(self, timer):
        n = self.slider.index_timer(timer['id'])
        self.slider.timers[n]['type'] = 'gate'
        self.timers[n][4].configure(fg_color='#000000')
        self.timers[n][3].configure(fg_color='#666666')
