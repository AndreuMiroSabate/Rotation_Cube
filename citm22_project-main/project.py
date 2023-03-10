import customtkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.

from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

import numpy as np
import math

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class Arcball(customtkinter.CTk):

    def __init__(self):

        super().__init__()

        # Orientation vars. Initialized to represent 0 rotation
        self.quat = np.array([[1],[0],[0],[0]])
        self.rotM = np.eye(3)
        self.AA = {"axis": np.array([[0],[0],[0]]), "angle":0.0}
        self.rotv = np.array([[0],[0],[0]])
        self.euler = np.array([[0],[0],[0]])

        # configure window
        self.title("Holroyd's arcball")
        self.geometry(f"{1100}x{580}")
        self.resizable(False, False)

        self.grid_columnconfigure((0,1), weight=0   )
        self.grid_rowconfigure((0,1), weight=1)
        self.grid_rowconfigure(2, weight=0)

        # Cube plot
        self.init_cube()

        self.canvas = FigureCanvasTkAgg(self.fig, self)  # A tk.DrawingArea.
        self.bm = BlitManager(self.canvas,[self.facesObj])
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.pressed = False #Bool to bypass the information that mouse is clicked
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.canvas.mpl_connect('button_release_event', self.onrelease)
        
        # Reset button
        self.resetbutton = customtkinter.CTkButton(self, text="Reset", command=self.resetbutton_pressed)
        self.resetbutton.grid(row=3, column=0, padx=(0, 0), pady=(5, 20), sticky="ns")
        
        # Selectable atti
        self.tabview = customtkinter.CTkTabview(self, width=150, height=150)
        self.tabview.grid(row=0, column=1, padx=(0, 20), pady=(20, 0), sticky="nsew")
        self.tabview.add("Axis angle")
        self.tabview.add("Rotation vector")
        self.tabview.add("Euler angles")
        self.tabview.add("Quaternion")

        # Selectable atti: AA
        self.tabview.tab("Axis angle").grid_columnconfigure(0, weight=0)  # configure grid of individual tabs
        self.tabview.tab("Axis angle").grid_columnconfigure(1, weight=0)  # configure grid of individual tabs

        self.label_AA_axis= customtkinter.CTkLabel(self.tabview.tab("Axis angle"), text="Axis:")
        self.label_AA_axis.grid(row=0, column=0, rowspan=3, padx=(80,0), pady=(45,0), sticky="e")


        self.button_AA = customtkinter.CTkButton(self.tabview.tab("Axis angle"), text="Apply", command=self.apply_AA, width=180)
        self.button_AA.grid(row=5, column=0, columnspan=2, padx=(0, 0), pady=(5, 0), sticky="e")

        # Selectable atti: rotV
        self.tabview.tab("Rotation vector").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Rotation vector").grid_columnconfigure(1, weight=0)
        
        self.label_rotV= customtkinter.CTkLabel(self.tabview.tab("Rotation vector"), text="rot. Vector:")
        self.label_rotV.grid(row=0, column=0, rowspan=3, padx=(2,0), pady=(45,0), sticky="e")


        self.button_rotV = customtkinter.CTkButton(self.tabview.tab("Rotation vector"), text="Apply", command=self.apply_rotV, width=180)
        self.button_rotV.grid(row=5, column=0, columnspan=2, padx=(0, 60), pady=(5, 0), sticky="e")

        # Selectable atti: Euler angles
        self.tabview.tab("Euler angles").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Euler angles").grid_columnconfigure(1, weight=0)
        
        self.label_EA_roll= customtkinter.CTkLabel(self.tabview.tab("Euler angles"), text="roll:")
        self.label_EA_roll.grid(row=0, column=0, padx=(2,0), pady=(50,0), sticky="e")

        self.label_EA_pitch= customtkinter.CTkLabel(self.tabview.tab("Euler angles"), text="pitch:")
        self.label_EA_pitch.grid(row=1, column=0, padx=(2,0), pady=(5,0), sticky="e")

        self.label_EA_yaw= customtkinter.CTkLabel(self.tabview.tab("Euler angles"), text="yaw:")
        self.label_EA_yaw.grid(row=2, column=0, rowspan=3, padx=(2,0), pady=(5,10), sticky="e")


        self.button_EA = customtkinter.CTkButton(self.tabview.tab("Euler angles"), text="Apply", command=self.apply_EA, width=180)
        self.button_EA.grid(row=5, column=0, columnspan=2, padx=(0, 60), pady=(5, 0), sticky="e")

        # Selectable atti: Quaternion
        self.tabview.tab("Quaternion").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Quaternion").grid_columnconfigure(1, weight=0)
        
        self.label_quat_0= customtkinter.CTkLabel(self.tabview.tab("Quaternion"), text="q0:")
        self.label_quat_0.grid(row=0, column=0, padx=(2,0), pady=(50,0), sticky="e")

        self.label_quat_1= customtkinter.CTkLabel(self.tabview.tab("Quaternion"), text="q1:")
        self.label_quat_1.grid(row=1, column=0, padx=(2,0), pady=(5,0), sticky="e")

        self.label_quat_2= customtkinter.CTkLabel(self.tabview.tab("Quaternion"), text="q2:")
        self.label_quat_2.grid(row=2, column=0, padx=(2,0), pady=(5,0), sticky="e")

        self.label_quat_3= customtkinter.CTkLabel(self.tabview.tab("Quaternion"), text="q3:")
        self.label_quat_3.grid(row=3, column=0, padx=(2,0), pady=(5,10), sticky="e")
   

        self.button_quat = customtkinter.CTkButton(self.tabview.tab("Quaternion"), text="Apply", command=self.apply_quat, width=180)
        self.button_quat.grid(row=4, column=0, columnspan=2, padx=(0, 60), pady=(5, 0), sticky="e")



        # Rotation matrix info
        self.RotMFrame = customtkinter.CTkFrame(self, width=150)
        self.RotMFrame.grid(row=1, column=1, rowspan=3, padx=(0, 20), pady=(20, 20), sticky="nsew")

        self.RotMFrame.grid_columnconfigure((0,1,2,3,4), weight=1)

        self.label_RotM= customtkinter.CTkLabel(self.RotMFrame, text="RotM = ")
        self.label_RotM.grid(row=0, column=0, rowspan=3, padx=(2,0), pady=(20,0), sticky="e")
        
        #aaaa
        self.changeRotMatrix()
        self.change_Values()
        pass


    def destroyInputs(self):

        # Angle / Axis
        self.entry_AA_ax1.destroy()
        self.entry_AA_ax2.destroy()
        self.entry_AA_ax3.destroy()
        self.entry_AA_angle.destroy()

        # rotV
        self.entry_rotV_1.destroy()
        self.entry_rotV_2.destroy()
        self.entry_rotV_3.destroy()

        # Euler angles
        self.entry_EA_roll.destroy()
        self.entry_EA_pitch.destroy()
        self.entry_EA_yaw.destroy()

        # Quaternion 
        self.entry_quat_0.destroy()
        self.entry_quat_1.destroy()
        self.entry_quat_2.destroy()
        self.entry_quat_3.destroy()

        pass

    def destroyMat(self):
        self.entry_RotM_11.destroy()
        self.entry_RotM_12.destroy()
        self.entry_RotM_13.destroy()
        self.entry_RotM_21.destroy()
        self.entry_RotM_22.destroy()
        self.entry_RotM_23.destroy()
        self.entry_RotM_31.destroy()
        self.entry_RotM_32.destroy()
        self.entry_RotM_33.destroy()

        pass

    def changeRotMatrix(self):        

        #aaaa
        self.entry_RotM_11= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_11.insert(0, self.Rm[0][0])
        self.entry_RotM_11.configure(state="disabled")
        self.entry_RotM_11.grid(row=0, column=1, padx=(2,0), pady=(20,0), sticky="ew")

        self.entry_RotM_12= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_12.insert(0, self.Rm[0][1])
        self.entry_RotM_12.configure(state="disabled")
        self.entry_RotM_12.grid(row=0, column=2, padx=(2,0), pady=(20,0), sticky="ew")

        self.entry_RotM_13= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_13.insert(0, self.Rm[0][2])
        self.entry_RotM_13.configure(state="disabled")
        self.entry_RotM_13.grid(row=0, column=3, padx=(2,0), pady=(20,0), sticky="ew")

        self.entry_RotM_21= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_21.insert(0, self.Rm[1][0])
        self.entry_RotM_21.configure(state="disabled")
        self.entry_RotM_21.grid(row=1, column=1, padx=(2,0), pady=(2,0), sticky="ew")

        self.entry_RotM_22= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_22.insert(0, self.Rm[1][1])
        self.entry_RotM_22.configure(state="disabled")
        self.entry_RotM_22.grid(row=1, column=2, padx=(2,0), pady=(2,0), sticky="ew")

        self.entry_RotM_23= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_23.insert(0, self.Rm[1][2])
        self.entry_RotM_23.configure(state="disabled")
        self.entry_RotM_23.grid(row=1, column=3, padx=(2,0), pady=(2,0), sticky="ew")

        self.entry_RotM_31= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_31.insert(0, self.Rm[2][0])
        self.entry_RotM_31.configure(state="disabled")
        self.entry_RotM_31.grid(row=2, column=1, padx=(2,0), pady=(2,0), sticky="ew")

        self.entry_RotM_32= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_32.insert(0, self.Rm[2][1])
        self.entry_RotM_32.configure(state="disabled")
        self.entry_RotM_32.grid(row=2, column=2, padx=(2,0), pady=(2,0), sticky="ew")

        self.entry_RotM_33= customtkinter.CTkEntry(self.RotMFrame, width=50, border_width=0)
        self.entry_RotM_33.insert(0, self.Rm[2][2])
        self.entry_RotM_33.configure(state="disabled")
        self.entry_RotM_33.grid(row=2, column=3, padx=(2,0), pady=(2,0), sticky="ew")
        
        pass


    def change_Values(self):
        
        # Angle / Axis  
        ax, ang = rotMat2Eaa(self.Rm)

        self.entry_AA_ax1 = customtkinter.CTkEntry(self.tabview.tab("Axis angle"))
        self.entry_AA_ax1.insert(0, float(ax[0]))
        self.entry_AA_ax1.grid(row=0, column=1, padx=(5, 0), pady=(50, 0), sticky="ew")

        self.entry_AA_ax2 = customtkinter.CTkEntry(self.tabview.tab("Axis angle"))
        self.entry_AA_ax2.insert(0, float(ax[1]))
        self.entry_AA_ax2.grid(row=1, column=1, padx=(5, 0), pady=(5, 0), sticky="ew")

        self.entry_AA_ax3 = customtkinter.CTkEntry(self.tabview.tab("Axis angle"))
        self.entry_AA_ax3.insert(0, float(ax[2]))
        self.entry_AA_ax3.grid(row=2, column=1, padx=(5, 0), pady=(5, 10), sticky="ew")

        self.label_AA_angle = customtkinter.CTkLabel(self.tabview.tab("Axis angle"), text="Angle:")
        self.label_AA_angle.grid(row=3, column=0, padx=(120,0), pady=(10, 20),sticky="w")
        self.entry_AA_angle = customtkinter.CTkEntry(self.tabview.tab("Axis angle"))
        self.entry_AA_angle.insert(0, ang)
        self.entry_AA_angle.grid(row=3, column=1, padx=(5, 0), pady=(0, 10), sticky="ew")


        # rotV
        rotV = np.array([[0],[0],[0]])
        rotV = ax*(ang*np.pi/180)
        self.entry_rotV_1 = customtkinter.CTkEntry(self.tabview.tab("Rotation vector"))
        self.entry_rotV_1.insert(0,rotV[0,0])
        self.entry_rotV_1.grid(row=0, column=1, padx=(5, 60), pady=(50, 0), sticky="ew")

        self.entry_rotV_2 = customtkinter.CTkEntry(self.tabview.tab("Rotation vector"))
        self.entry_rotV_2.insert(0,rotV[1,0])
        self.entry_rotV_2.grid(row=1, column=1, padx=(5, 60), pady=(5, 0), sticky="ew")

        self.entry_rotV_3 = customtkinter.CTkEntry(self.tabview.tab("Rotation vector"))
        self.entry_rotV_3.insert(0,rotV[2,0])
        self.entry_rotV_3.grid(row=2, column=1, padx=(5, 60), pady=(5, 10), sticky="ew")

        
        # Euler angles
        yaw, pitch, roll = rotM2eAngles(self.Rm)

        self.entry_EA_roll = customtkinter.CTkEntry(self.tabview.tab("Euler angles"))
        self.entry_EA_roll.insert(0, roll)
        self.entry_EA_roll.grid(row=0, column=1, padx=(5, 60), pady=(50, 0), sticky="ew")

        self.entry_EA_pitch = customtkinter.CTkEntry(self.tabview.tab("Euler angles"))
        self.entry_EA_pitch.insert(0, pitch)
        self.entry_EA_pitch.grid(row=1, column=1, padx=(5, 60), pady=(5, 0), sticky="ew")

        self.entry_EA_yaw = customtkinter.CTkEntry(self.tabview.tab("Euler angles"))
        self.entry_EA_yaw.insert(0, yaw)
        self.entry_EA_yaw.grid(row=2, column=1, padx=(5, 60), pady=(5, 10), sticky="ew") 


        # Quaternion
        if self.Rm.all() == np.identity(3).all():
            self.quat = np.array([[1],[0],[0],[0]])

        self.entry_quat_0 = customtkinter.CTkEntry(self.tabview.tab("Quaternion"))
        self.entry_quat_0.insert(0, float(self.quat[0]))
        self.entry_quat_0.grid(row=0, column=1, padx=(5, 60), pady=(50, 0), sticky="ew")

        self.entry_quat_1 = customtkinter.CTkEntry(self.tabview.tab("Quaternion"))
        self.entry_quat_1.insert(0, float(self.quat[1]))
        self.entry_quat_1.grid(row=1, column=1, padx=(5, 60), pady=(5, 0), sticky="ew")

        self.entry_quat_2 = customtkinter.CTkEntry(self.tabview.tab("Quaternion"))
        self.entry_quat_2.insert(0, float(self.quat[2]))
        self.entry_quat_2.grid(row=2, column=1, padx=(5, 60), pady=(5, 0), sticky="ew")

        self.entry_quat_3 = customtkinter.CTkEntry(self.tabview.tab("Quaternion"))
        self.entry_quat_3.insert(0, float(self.quat[3]))
        self.entry_quat_3.grid(row=3, column=1, padx=(5, 60), pady=(5, 10), sticky="ew")

        pass


    def resetbutton_pressed(self):
        """
        Event triggered function on the event of a push on the button Reset
        """
        self.M = np.array(
            [[ -1,  -1, 1],   
            [ -1,   1, 1],    
            [1,   1, 1],      
            [1,  -1, 1],      
            [-1,  -1, -1],    
            [-1,  1, -1],     
            [1,   1, -1],     
            [1,  -1, -1]], dtype=float).transpose() 

        self.Rm = np.identity(3)

        self.destroyInputs()
        self.change_Values()

        self.update_cube()

        pass

    
    def apply_AA(self):
        """
        Event triggered function on the event of a push on the button button_AA
        """
        #Example on hot to get values from entries:
        angle = self.entry_AA_angle.get()
        angle = math.radians(float(angle))
        axis = np.zeros((3,1))
        Ux = np.zeros((3,3))
        axis[0,0] = self.entry_AA_ax1.get()
        axis[1,0] = self.entry_AA_ax2.get()
        axis[2,0] = self.entry_AA_ax3.get()
        axis = axis/np.linalg.norm(axis)

        Ux[1,0] = axis[2,0]
        Ux[0,1] = -axis[2,0]
        Ux[0,2] = axis[1,0]
        Ux[2,0] = -axis[1,0]
        Ux[1,2] = -axis[0,0]
        Ux[2,1] = axis[0,0]
        
        print(Ux)
        Raa = np.empty((3,3))
        Raa = np.identity(3)*math.cos(angle)+((1-math.cos(angle))*(axis@axis.T)) + Ux*math.sin(angle)

        self.Rm = Raa

        print(Raa)

        self.M = Raa.dot(self.M)
        self.update_cube()
 
        #Example string to number
        print(float(angle)*2)

        pass

    
    def apply_rotV(self):
        """
        Event triggered function on the event of a push on the button button_rotV 
        """
        Rvector = np.zeros((3,1))
        Rx = np.zeros((3,3))
        Rvector[0,0] = self.entry_rotV_1.get()
        Rvector[1,0] = self.entry_rotV_2.get()
        Rvector[2,0] = self.entry_rotV_3.get()
       
        Rvector = Rvector/np.linalg.norm(Rvector)
        Rmodule = np.linalg.norm(Rvector)

        Rx[1,0] = Rvector[2,0]
        Rx[0,1] = -Rvector[2,0]
        Rx[0,2] = Rvector[1,0]
        Rx[2,0] = -Rvector[1,0]
        Rx[1,2] = -Rvector[0,0]
        Rx[2,1] = Rvector[0,0]


        Rvr = np.empty((3,3))
        Rvr = (np.identity(3)*math.cos(Rmodule))+(((math.sin(Rmodule)/Rmodule)*Rx)) + (((1-math.cos(Rmodule))/Rmodule**2)*(Rvector@Rvector.T))
        print(Rvr)
        
        self.Rm = Rvr
        self.M = Rvr.dot(self.M)

        
        self.update_cube()
        pass

    
    def apply_EA(self):
        """
        Event triggered function on the event of a push on the button button_EA
        """
        roll = ( float(self.entry_EA_roll.get()) * math.pi)/180
        yaw = (float(self.entry_EA_yaw.get()) * math.pi)/180
        pitch = (float(self.entry_EA_pitch.get()) * math.pi)/180

        Rx = np.array([[1,0,0],[0,math.cos(roll),math.sin(roll)],[0,-math.sin(roll),math.cos(roll)]])
        Ry = np.array([[math.cos(pitch),0,-math.sin(pitch)],[0,1,0],[math.sin(pitch),0,math.cos(pitch)]])
        Rz = np.array([[math.cos(yaw),math.sin(yaw),0],[-math.sin(yaw),math.cos(yaw),0],[0,0,1]])
        
        Rea = Rx @ Ry @ Rz
        Rea = Rea.transpose()

        self.Rm = Rea


        self.M = Rea.dot(self.M)
        self.update_cube()
        
        pass

    
    def apply_quat(self):
        """
        Event triggered function on the event of a push on the button button_quat
        """
        q = np.zeros((4,1))
        q[0,0] = self.entry_quat_0.get()
        q[1,0] = self.entry_quat_1.get()
        q[2,0] = self.entry_quat_2.get()
        q[3,0] = self.entry_quat_3.get()
        q = q/np.linalg.norm(q)
        
        Rq = np.zeros((3,3))
        Rq[0,0] = (q[0]**2+ q[1]**2-q[2]**2-q[3]**2)
        Rq[1,1] = q[0]**2- q[1]**2+q[2]**2-q[3]**2
        Rq[2,2] = q[0]**2- q[1]**2-q[2]**2+q[3]**2
        Rq[0,1] = (2*q[1]*q[2])- (2*q[0]*q[3])
        Rq[1,0] = (2*q[1]*q[2])+ (2*q[0]*q[3])
        Rq[0,2] = (2*q[1]*q[3])+ (2*q[0]*q[2])
        Rq[2,0] = (2*q[1]*q[3])- (2*q[0]*q[2])
        Rq[2,1] = (2*q[2]*q[3])+ (2*q[0]*q[1])
        Rq[1,2] = (2*q[2]*q[3])- (2*q[0]*q[1])

        
        print(Rq)
        print(np.linalg.det(Rq))
        
        self.Rm = Rq

        self.M = Rq.dot(self.M)
        print(self.M)
        self.update_cube()

        return Rq

    
    def onclick(self, event):
        """
        Event triggered function on the event of a mouse click inside the figure canvas
        """
        print("Pressed button", event.button)

        if event.button:
            x_fig_0, y_fig_0 = self.canvas_coordinates_to_figure_coordinates(event.x,event.y)
            
            r = (x_fig_0*x_fig_0+y_fig_0*y_fig_0)*2
            if(x_fig_0**2 + y_fig_0**2 < 1/2*r):
                self.M0[0,0] = x_fig_0
                self.M0[1,0] = y_fig_0
                self.M0[2,0] = np.sqrt(r-x_fig_0**2-y_fig_0**2)
            elif(x_fig_0**2 + y_fig_0**2 >= 1/2*r):
                self.M0[0,0] = x_fig_0
                self.M0[1,0] = y_fig_0
                self.M0[2,0] = r/2*np.sqrt(x_fig_0**2+y_fig_0**2)

                self.M0 = self.M0*np.sqrt(r)/np.linalg.norm(self.M0)

            self.pressed = True # Bool to control(activate) a drag (click+move)


    def onmove(self,event):
        """
        Event triggered function on the event of a mouse motion
        """
        M1 = np.zeros((3,1))
        qp = np.zeros((4,1))
        self.quat = np.zeros((4,1))
        #Example
        if self.pressed: #Only triggered if previous click
            
            x_fig,y_fig= self.canvas_coordinates_to_figure_coordinates(event.x,event.y) #Extract viewport coordinates

            r = (x_fig*x_fig+y_fig*y_fig)*2
            if(x_fig**2 + y_fig**2 < 1/2*r):
                M1[0,0] = x_fig
                M1[1,0] = y_fig
                M1[2,0] = np.sqrt(r-x_fig**2-y_fig**2)
            elif(x_fig**2 + y_fig**2 >= 1/2*r):
                M1[0,0] = x_fig
                M1[1,0] = y_fig
                M1[2,0] = r/2*np.sqrt(x_fig**2+y_fig**2)

                M1 = M1*np.sqrt(r)/np.linalg.norm(M1)

        angle = math.acos((M1.T@self.M0)/(np.linalg.norm(M1)*np.linalg.norm(self.M0)))
        
        print("x: ", x_fig)
        print("y", y_fig)
        print("r2", x_fig*x_fig+y_fig*y_fig)

        

        self.quat[0,0]=math.cos(angle/2)
        self.quat[1:,0] = math.sin(angle/2)*(np.cross(self.M0.T,M1.T)/np.linalg.norm(np.cross(self.M0.T,M1.T)))

        if(qp[0,0] !=0 or qp[1,0] !=0 or qp[2,0] !=0 or qp[3,0] !=0):
            self.quat = self.quat
            self.quat[0,0] = (self.quat[0,0]*qp[0,0])-(self.quat[1:0].T@qp[1:,0])
            self.quat[1:,0] = (self.quat[0,0]*qp[1:,0]) + (qp[0,0]*self.quat[1:,0]) + (np.cross(self.quat[1:,0],qp[1:,0]))

        Rq = np.zeros((3,3))
        Rq[0,0] = (self.quat[0]**2+ self.quat[1]**2-self.quat[2]**2-self.quat[3]**2)
        Rq[1,1] = self.quat[0]**2- self.quat[1]**2+self.quat[2]**2-self.quat[3]**2
        Rq[2,2] = self.quat[0]**2- self.quat[1]**2-self.quat[2]**2+self.quat[3]**2
        Rq[0,1] = (2*self.quat[1]*self.quat[2])- (2*self.quat[0]*self.quat[3])
        Rq[1,0] = (2*self.quat[1]*self.quat[2])+ (2*self.quat[0]*self.quat[3])
        Rq[0,2] = (2*self.quat[1]*self.quat[3])+ (2*self.quat[0]*self.quat[2])
        Rq[2,0] = (2*self.quat[1]*self.quat[3])- (2*self.quat[0]*self.quat[2])
        Rq[2,1] = (2*self.quat[2]*self.quat[3])+ (2*self.quat[0]*self.quat[1])
        Rq[1,2] = (2*self.quat[2]*self.quat[3])- (2*self.quat[0]*self.quat[1])

        self.Rm = Rq
        self.M = Rq.dot(self.M) #Modify the vertices matrix with a rotation matrix M

        qp = self.quat
        self.M0 = M1

        self.destroyInputs()
        self.change_Values()
        self.update_cube() #Update the cube


    def onrelease(self,event):
        """
        Event triggered function on the event of a mouse release
        """
        self.pressed = False # Bool to control(deactivate) a drag (click+move)


    def init_cube(self):
        """
        Initialization function that sets up cube's geometry and plot information
        """

        self.M = np.array(
            [[ -1,  -1, 1],   #Node 0
            [ -1,   1, 1],    #Node 1
            [1,   1, 1],      #Node 2
            [1,  -1, 1],      #Node 3
            [-1,  -1, -1],    #Node 4
            [-1,  1, -1],     #Node 5
            [1,   1, -1],     #Node 6
            [1,  -1, -1]], dtype=float).transpose() #Node 7

        self.con = [
            [0, 1, 2, 3], #Face 1
            [4, 5, 6, 7], #Face 2
            [3, 2, 6, 7], #Face 3
            [0, 1, 5, 4], #Face 4
            [0, 3, 7, 4], #Face 5
            [1, 2, 6, 5]] #Face 6

        self.Rm = np.identity(3)
        self.M0 = np.zeros((3,1))


        faces = []

        for row in self.con:
            faces.append([self.M[:,row[0]],self.M[:,row[1]],self.M[:,row[2]],self.M[:,row[3]]])

        self.fig = plt.figure()
        ax = self.fig.add_subplot(111, projection='3d')

        for item in [self.fig, ax]:
            item.patch.set_visible(False)

        self.facesObj = Poly3DCollection(faces, linewidths=.2, edgecolors='k',animated = True)
        self.facesObj.set_facecolor([(0,0,1,0.9), #Blue
        (0,1,0,0.9), #Green
        (.9,.5,0.13,0.9), #Orange
        (1,0,0,0.9), #Red
        (1,1,0,0.9), #Yellow
        (0,0,0,0.9)]) #Black

        #Transfering information to the plot
        ax.add_collection3d(self.facesObj)

        #Configuring the plot aspect
        ax.azim=-90
        ax.roll = -90
        ax.elev=0   
        ax.set_xlim3d(-2, 2)
        ax.set_ylim3d(-2, 2)
        ax.set_zlim3d(-2, 2)
        ax.set_aspect('equal')
        ax.disable_mouse_rotation()
        ax.set_axis_off()

        self.pix2unit = 1.0/60 #ratio for drawing the cube 


    def update_cube(self):
        """
        Updates the cube vertices and updates the figure.
        Call this function after modifying the vertex matrix in self.M to redraw the cube
        """
    	
        faces = []

        for row in self.con:
            faces.append([self.M[:,row[0]],self.M[:,row[1]],self.M[:,row[2]], self.M[:,row[3]]])

        self.facesObj.set_verts(faces)
        self.bm.update()

        self.destroyMat()
        self.changeRotMatrix()


    def canvas_coordinates_to_figure_coordinates(self,x_can,y_can):
        """
        Remap canvas coordinates to cube centered coordinates
        """

        (canvas_width,canvas_height)=self.canvas.get_width_height()
        figure_center_x = canvas_width/2+14
        figure_center_y = canvas_height/2+2
        x_fig = (x_can-figure_center_x)*self.pix2unit
        y_fig = (y_can-figure_center_y)*self.pix2unit

        return(x_fig,y_fig)


    def destroy(self):
        """
        Close function to properly destroy the window and tk with figure
        """
        try:
            self.destroy()
        finally:
            exit()


class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
            cv.draw_idle()


# algo falla? nose fa coses rares en l'angle diria pero es el que vam fer al lab Andreu i jo :(
def rotMat2Eaa(R):
    '''
    Returns the principal axis and angle encoded in the rotation matrix R
    '''

    if R.all() == np.identity(3).all():
        return(np.array([[1],[0],[0]]), 0)

    angle = np.arccos((np.trace(R)-1)/2)

    uaxis = (R-R.T)/(2 * math.sin(angle)) 

    us = np.array([abs(R[0][0]), abs(R[1][1]), abs(R[2][2])])
    index = np.where(us == max(us))
    
    # get the first highest number, otherwise it gets all positions.
    for num in us:
        if num != 0:
            index = int(num)
            break

    comparison = R-R.T == np.zeros(len(R))
    equal_arrays = comparison.all()
    if equal_arrays == True:
      axis = np.array([[R[0][index]], [R[1][index]], [R[2][index]]])

    else:
      axis = np.array([[uaxis[2][1]],[uaxis[0][2]],[uaxis[1][0]]])
    
    return(axis, angle*180/np.pi)

def rotM2eAngles(R): #psi, theta, phi
    '''
    Given a rotation matrix R returns a set of Euler angles 
    '''

    if R.all() == np.identity(3).all():
        return (0.0, 0.0, 0.0)

    pitch = np.arcsin(-R[2][0])

    roll = np.arctan2((R[2][1]/np.cos(pitch)),(R[2][2]/np.cos(pitch)))

    yaw = np.arctan2((R[1][0]/np.cos(pitch)),(R[0][0]/np.cos(pitch)))

    return (yaw*180/np.pi, pitch*180/np.pi,  roll*180/np.pi)

if __name__ == "__main__":
    app = Arcball()
    app.mainloop()
    exit()
