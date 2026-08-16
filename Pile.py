from tkinter import *
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

root = Tk()
root.geometry("1360x768")
root.title("Lateral Load by Reese & Matlock")

def load_data(file):
    data = pd.read_csv(file, sep=r"\s+", engine="python")
    β_l = data['β/l']
    z_l = data['z/l']
    KρH = data['KρH']
    KθH = data['KθH']
    KMH = data['KMH']
    KQH = data['KQH']
    KρM = data['KρM']
    KθM = data['KθM']
    KMM = data['KMM']
    KQM = data['KQM']

    return (β_l.to_numpy(), z_l.to_numpy(), KρH.to_numpy(), KθH.to_numpy(),
            KMH.to_numpy(), KQH.to_numpy(), KρM.to_numpy(), KθM.to_numpy(), KMM.to_numpy(), KQM.to_numpy())

file = ("matlock_0.csv", "matlock_1.csv", "matlock_2.csv", "matlock_3.csv")
data_import = []
for f in file:
    data_import.append(load_data(f))

class Example(Frame):

    def __init__(self, parent):

        Frame.__init__(self, parent)
        self.kh = None
        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = Frame(self.canvas, background="#ffffff")

        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.create_window(
            (4, 4),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.default_page()

    def default_page(self):

        # Labels
        Label(self.frame, text="Horizontal load [kN]").grid(row=0, column=0, padx=10, pady=10)
        Label(self.frame, text="Moment [kN*m]").grid(row=1, column=0, padx=10, pady=10)
        Label(self.frame, text="E [kN/m^2]").grid(row=2, column=0, padx=10, pady=10)
        Label(self.frame, text="Lenght [m]").grid(row=3, column=0, padx=10, pady=10)
        Label(self.frame, text="Name").grid(row=4, column=0, padx=10, pady=10)
        Label(self.frame, text="Diameter [m]").grid(row=5, column=0, padx=10, pady=10)
        Label(self.frame, text="kh_z=0 [kN/m^3]").grid(row=6, column=0, padx=10, pady=10)
        Label(self.frame, text="Fixed Head").grid(row=7, column=0, padx=10, pady=10)
        Label(self.frame, text="PinnedHead").grid(row=8, column=0, padx=10, pady=10)
        self.FixedHeadEV = BooleanVar()
        self.PinnedHeadEV = BooleanVar()
        Checkbutton(
            self.frame,
            variable=self.FixedHeadEV,
            onvalue=True,
            offvalue=False
        ).grid(row=7, column=1, padx=10, pady=10)
        Checkbutton(
            self.frame,
            variable=self.PinnedHeadEV,
            onvalue=True,
            offvalue=False
        ).grid(row=8, column=1, padx=10, pady=10)

        # Variables
        self.LoadEV = StringVar(value="100")
        self.MEV = StringVar(value="0")
        self.EEV = StringVar(value="30000000")
        self.LEV = StringVar(value="6")
        self.NameEV = StringVar()
        self.DEV=StringVar(value="1")
        self.KHEV=StringVar(value="10000")

        # Entries
        Entry(self.frame, textvariable=self.LoadEV).grid(row=0, column=1, padx=10, pady=10)
        Entry(self.frame, textvariable=self.MEV).grid(row=1, column=1, padx=10, pady=10)
        Entry(self.frame, textvariable=self.EEV).grid(row=2, column=1, padx=10, pady=10)
        Entry(self.frame, textvariable=self.LEV).grid(row=3, column=1, padx=10, pady=10)
        Entry(self.frame, textvariable=self.NameEV).grid(row=4, column=1, padx=10, pady=10)
        Entry(self.frame, textvariable=self.DEV).grid(row=5, column=1, padx=10, pady=10)
        Entry(self.frame, textvariable=self.KHEV).grid(row=6, column=1, padx=10, pady=10)

        # Buttons
        Button(self.frame, text="Submit", command=self.Submit).grid(row=1, column=2, padx=10, pady=10)
        Button(self.frame, text="List", command=self.Print).grid(row=2, column=2, padx=10, pady=10)
        Button(self.frame, text="Graph", command=self.Graph).grid(row=3, column=2, padx=10, pady=10)
        Button(self.frame, text="Export", command=self.Export).grid(row=4, column=2, padx=10, pady=10)

    def Submit(self):

        self.Yh = []
        self.Th = []
        self.Mh = []
        self.Sh = []

        self.Ym = []
        self.Tm = []
        self.Mm = []
        self.Sm = []

        self.Ytot = []
        self.Ttot = []
        self.Mtot = []
        self.Stot = []

        try:
            self.Load = float(self.LoadEV.get())
            self.M = float(self.MEV.get())
            self.E = float(self.EEV.get())
            self.L = float(self.LEV.get())
            self.D=float(self.DEV.get())
            self.kh=float(self.KHEV.get())
            self.fixed_head = self.FixedHeadEV.get()
            self.pinned_head = self.PinnedHeadEV.get()
        except ValueError:
            print("Please enter valid numeric values.")
            return

        self.z = []

        #choose the correct sheet
        self.J =(np.pi*self.D**4)/64 #moment of inertia
        Beta = ((self.kh * self.D) / (4 * self.E * self.J)) ** (1 / 4)
        checkbeta = Beta * self.L
        corrector=0
        if checkbeta < 2.5:  # 1
            corrector = 0
        elif (checkbeta >= 2.5 and checkbeta <= 3.5):  # 2
            corrector = 1
        elif (checkbeta >= 3.5 and checkbeta <= 4.5):  # 3
            corrector = 2
        elif (checkbeta >= 4.5 and checkbeta <= 5.5):  # 4
            corrector = 3

        #calculate the depth
        for i in range(17):
            self.z.append(data_import[corrector][1][i]*self.L)

        #initialize moment for fixed head
        M0=0
        if self.fixed_head is True:
            M0 = (self.Load / (2 * Beta)) * (data_import[corrector][3][0] / data_import[corrector][7][0])

        H0 = 0
        Msum = self.M + M0
        print("Msum", Msum)
        if self.pinned_head is True:
            H0 = - (Msum * Beta) * (data_import[corrector][6][0] / data_import[corrector][2][0])
            print("PINNED HEAD",H0)
            print("krhom",data_import[corrector][6][0] )
            print("krho h", data_import[corrector][2][0])

        #sum applied moment with fixed headDPU 6760 condition

        self.Load += H0
        print("Load",self.Load)

        #compute value
        for i in range(17):

            z = self.z[i]
            # Displacement
            rho=2*self.Load * Beta / (self.kh * self.D) * data_import[corrector][2][i]
            self.Yh.append(rho)

            # Slope
            theta=(2 * self.Load*Beta**2) / (self.kh * self.D) * (data_import[corrector][3][i])
            self.Th.append(theta)

            # Moment
            M=-self.Load / Beta * data_import[corrector][4][i]
            self.Mh.append(M)

            # Shear
            Shear=-self.Load * data_import[corrector][5][i]
            self.Sh.append(Shear)

            #momenti
            c6 = data_import[corrector][6][i]
            c7 = data_import[corrector][7][i]
            c8 = data_import[corrector][8][i]
            c9 = data_import[corrector][9][i]

            Y1,S1,M1,P1=self.compute_moment(Msum,Beta,self.kh,self.D,c6,c7,c8,c9)

            self.Ym.append(Y1)
            self.Tm.append(S1)
            self.Mm.append(M1)
            self.Sm.append(P1)

        self.Ytot = np.array(self.Yh) + np.array(self.Ym)
        self.Mtot = np.array(self.Mh) + np.array(self.Mm)
        self.Stot = np.array(self.Sh) + np.array(self.Sm)
        self.Ttot = np.array(self.Th) + np.array(self.Tm)

    def compute_moment(self, M0,Beta,kh,D,c6,c7,c8,c9):
        Ym = []
        Sm = []
        Mm = []
        Pm = []

        #Displacement
        Ym = 2 * M0 * Beta ** 2 / (kh * D) * c6

        # Slope
        Sm = -(4 * M0 * Beta ** 3) / (kh * D) * c7

        # Moment
        Mm = M0 * c8

        # Shear
        Pm = -2 * M0 * Beta * c9

        return Ym, Sm, Mm, Pm

    def Graph(self):

        fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(16, 5))

        # Displacement
        plt.subplot(1, 4, 1)
        plt.xlabel("Displacement (m)")
        plt.ylabel("Length (m)")
        plt.title("Displacement")
        plt.plot(self.Ytot, self.z)
        plt.ylim(max(self.z), min(self.z))
        plt.grid(True)

        # Slope
        plt.subplot(1, 4, 2)
        plt.xlabel("Slope %")
        plt.ylabel("Length (m)")
        plt.title("Slope")
        plt.plot(self.Ttot, self.z)
        plt.ylim(max(self.z), min(self.z))
        plt.grid(True)

        # Moment
        plt.subplot(1, 4, 3)
        plt.xlabel("Moment (kN*m)")
        plt.ylabel("Length (m)")
        plt.title("Moment")
        plt.plot(self.Mtot, self.z)
        plt.ylim(max(self.z), min(self.z))
        plt.grid(True)

        # Soil Reaction
        plt.subplot(1, 4, 4)
        plt.xlabel("Shear (kN)")
        plt.ylabel("Length (m)")
        plt.title("Shear")
        plt.plot(self.Stot, self.z)
        plt.ylim(max(self.z), min(self.z))
        plt.grid(True)

        fig.tight_layout()
        plt.show()

    def Print(self):

        self.newwin = Toplevel(root)
        self.newwin.geometry("1366x768")

        self.tv = ttk.Treeview(self.newwin, height=35)

        self.tv['columns'] = (
            'SR.NO',
            'Lenght',
            'Displacement (m)',
            'Slope',
            'Moment (kN*m)',
            'Shear (kN)'
        )

        self.tv.column('#0', width=0, stretch=NO)

        self.tv.column('SR.NO', anchor=CENTER, width=70)
        self.tv.column('Lenght', anchor=CENTER, width=100)
        self.tv.column('Displacement (m)', anchor=CENTER, width=100)
        self.tv.column('Slope', anchor=CENTER, width=100)
        self.tv.column('Moment (kN*m)', anchor=CENTER, width=100)
        self.tv.column('Shear (kN)', anchor=CENTER, width=120)

        self.tv.heading('#0', text='', anchor=CENTER)
        self.tv.heading('SR.NO', text='SR.NO', anchor=CENTER)
        self.tv.heading('Lenght', text='Lenght', anchor=CENTER)
        self.tv.heading('Displacement (m)', text='Displacement (m)', anchor=CENTER)
        self.tv.heading('Slope', text='Slope', anchor=CENTER)
        self.tv.heading('Moment (kN*m)', text='Moment (kN*m)', anchor=CENTER)
        self.tv.heading('Shear (kN)', text='Shear (kN)', anchor=CENTER)

        scrollbar = Scrollbar(
            self.newwin,
            orient=VERTICAL,
            command=self.tv.yview
        )

        self.tv.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=RIGHT, fill=Y)
        self.tv.pack(fill=BOTH, expand=True)

        for i in range(17):
            self.tv.insert(
                '',
                i,
                values=(
                    i + 1,
                    f"{self.z[i]:.2f}",
                    f"{self.Ytot[i]:.4f}",
                    f"{self.Ttot[i]:.4f}",
                    f"{self.Mtot[i]:.4f}",
                    f"{self.Stot[i]:.4f}"
                )
            )

    def Export(self):

        self.Name = self.NameEV.get()

        if self.Name == "":
            self.Name = "output"

        filename = self.Name + ".xlsx"

        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, filename)

        data = {
            'Length': self.z,
            'Displacement': self.Ytot,
            'Slope': self.Ttot,
            'Moment': self.Mtot,
            'Shear': self.Stot
        }

        df = pd.DataFrame(data)

        df.to_excel(filepath, index=False)

        print(f"File saved: {filepath}")

    def onFrameConfigure(self, event):

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

example = Example(root)
example.pack(side="top", fill="both", expand=True)

root.mainloop()
