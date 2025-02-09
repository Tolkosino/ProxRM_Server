import tkinter as Tk
import tkinter.font as TkFont
import client


class MainWindow(Tk.Tk):
    conn = client.connection
    
    serverlist = {
        "VM Host": "pve",
        "MC - ATM 9": "100",
        "WOL-Test": "101",
        "Test VM 2": "102"
    }

    def get_selectedVMid(self):
        return self.serverlist.get(self.lb_serverSelection.get(self.lb_serverSelection.curselection()))

    def get_VMInfo(self):
        vmID = self.get_selectedVMid()
        
        self.conn.establish_connection("get_VMStatus", vmID)
        
        #return currStatus, assignedRessourcCPU, assignedRessourceRAM, usedRessources
    
    def start_server(self, event):
        VMiD = self.get_selectedVMid()
        self.conn.establish_connection(self.conn,VMiD,"set_VMAction;start")

    def stop_server(self, event):
        VMiD = self.get_selectedVMid()
        self.conn.establish_connection(self.conn,VMiD,"set_VMAction;stop")
        
    def update_serverinfo(self, event):
        VMiD = self.get_selectedVMid()
        if VMiD != "pve":
            serverinfo = self.conn.establish_connection(self.conn,VMiD,"get_VMStatus")
            infoArr = serverinfo.get("result").split(",")
            
            self.vmstatus = infoArr[0][2:-1]
            self.maxmemGB = round(float(infoArr[1]),2)
            self.maxdiskGB = round(float(infoArr[2]),2)
            self.netin = infoArr[3]
            self.netout = infoArr[4]
            self.diskwrite = infoArr[5]
            self.diskread = infoArr[6]
            self.cpus = infoArr[7]
            self.uptime = infoArr[8]
            
            self.lb_statusInfo.config(text = self.vmstatus)
            self.lb_cpuRessourceInfo.config(text = self.cpus)
            self.lb_maximumRam.config(text = str(self.maxmemGB)+"GB")
            self.lb_diskspaceInfo.config(text = str(self.maxdiskGB)+"GB")
            self.lb_netinInfo.config(text = self.netin+"GB")
            self.lb_netoutInfo.config(text = self.netout+"GB")
            self.lb_diskreadInfo.config(text = self.diskread)
            self.lb_diskwriteInfo.config(text = self.diskwrite)
        
        else:
            self.lb_statusInfo.config(text = "Host info not available")
            self.lb_cpuRessourceInfo.config(text = "Host info not available")
            self.lb_maximumRam.config(text = "Host info not available")
            self.lb_diskspaceInfo.config(text = "Host info not available")
            self.lb_netinInfo.config(text = "Host info not available")
            self.lb_netoutInfo.config(text = "Host info not available")
            self.lb_diskreadInfo.config(text = "Host info not available")
            self.lb_diskwriteInfo.config(text = "Host info not available")    
        #Update content on rightside of window (aka specific server infos)
        pass

    def __init__(self):
        super().__init__()
        self.geometry("800x400")
        self.setup()

    
    def setup(self):                
        #Initial Window Setup
        
        #Setup Fonts
        default_font = TkFont.Font(family="Arial", size=8, weight="normal")
        small_font = TkFont.Font(family="Arial", size=6, weight="normal")
        boldheader_font = TkFont.Font(family="Arial", size=9, weight="bold")
        boldInfo_font = TkFont.Font(family="Arial", size=8, weight="bold")
                
    #left Toolbox        
        fr_Left = Tk.Frame(self,width=100,height=340)
        fr_Left.grid(row=0,column=0,padx=10,pady=5)
        
            #Serverselection Listbox
        keys = []
        for key in self.serverlist.keys():
            keys.append(key)
        listItems = Tk.Variable(value=keys)
        
        self.lb_serverSelection = Tk.Listbox(fr_Left,selectmode="single",listvariable=listItems)
        self.lb_serverSelection.grid(row=0,column=0,padx=10,pady=5)
        self.lb_serverSelection.select_set(0)
        self.lb_serverSelection.bind("<<ListboxSelect>>", self.update_serverinfo)
                
            #Buttons to start and Stop Server
        btn_start = Tk.Button(fr_Left,text="Start VM")
        btn_start.bind("<Button-1>", self.start_server)
        btn_start.grid(row=2,column=0,padx=10,pady=5)
        
        btn_stop = Tk.Button(fr_Left,text="Stop VM")
        btn_stop.bind("<Button-1>", self.stop_server)
        btn_stop.grid(row=3,column=0,padx=10,pady=5)
        
        lb_copyright = Tk.Label(fr_Left,justify="center",padx=10,pady=5,text="COPYRIGHT \n ©Tolkosino™®", font=default_font)
        lb_copyright.grid(row=4,column=0,padx=10,pady=5)
        lb_copyright_source = Tk.Label(fr_Left,justify="center",padx=10,pady=5,text="Quelle vertrau mir Bruder", font=small_font)
        lb_copyright_source.grid(row=5,column=0,padx=10,pady=5)
        
    #right serverinfo
        #currStatus, assignedRessourcCPU, assignedRessourceRAM, usedRessources = self.get_selectedVMid()
        
        fr_Right = Tk.Frame(self,width=300,height=340)
        fr_Right.grid(row=0,column=1,columnspan=2,padx=10,pady=5)
        
        lb_statusHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="Status:", font=boldheader_font)
        lb_statusHeader.grid(row=0, column=0, padx=10, pady=5)
        
        self.lb_statusInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_statusInfo.grid(row=0, column=1, padx=10, pady=5)
        
        lb_maximumRamHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="RAM:", font=boldheader_font)
        lb_maximumRamHeader.grid(row=1, column=0, padx=10, pady=5)
        
        self.lb_maximumRam = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_maximumRam.grid(row=1, column=1, padx=10, pady=5)
        
        lb_cpuRessourceHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="CPUs:", font=boldheader_font)
        lb_cpuRessourceHeader.grid(row=2, column=0, padx=10, pady=5)
        
        self.lb_cpuRessourceInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_cpuRessourceInfo.grid(row=2, column=1, padx=10, pady=5)
        
        lb_diskspaceHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="Speicher:", font=boldheader_font)
        lb_diskspaceHeader.grid(row=3, column=0, padx=10, pady=5)
        
        self.lb_diskspaceInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_diskspaceInfo.grid(row=3, column=1, padx=10, pady=5)
        
        lb_netinHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="Network Incoming:", font=boldheader_font)
        lb_netinHeader.grid(row=4, column=0, padx=10, pady=5)
        
        self.lb_netinInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_netinInfo.grid(row=4, column=1, padx=10, pady=5)
        
        lb_netoutHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="Network Outgoing:", font=boldheader_font)
        lb_netoutHeader.grid(row=5, column=0, padx=10, pady=5)
        
        self.lb_netoutInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_netoutInfo.grid(row=5, column=1, padx=10, pady=5)
        
        lb_diskwriteHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="Disk Write:", font=boldheader_font)
        lb_diskwriteHeader.grid(row=6, column=0, padx=10, pady=5)
        
        self.lb_diskwriteInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_diskwriteInfo.grid(row=6, column=1, padx=10, pady=5)
        
        lb_diskreadHeader = Tk.Label(fr_Right, justify="left",padx=10,pady=5,text="Disk Read:", font=boldheader_font)
        lb_diskreadHeader.grid(row=7, column=0, padx=10, pady=5)
        
        self.lb_diskreadInfo = Tk.Label(fr_Right, justify="left", padx=10, pady=5,text="Loading...", font=boldInfo_font)
        self.lb_diskreadInfo.grid(row=7, column=1, padx=10, pady=5)
        
        lb_headerDescription = Tk.Label(fr_Right, justify="left", padx=10, pady=5, text="Server Beschreibung:", font=default_font)
        lb_headerDescription.grid(row=8, column=0, padx=10, pady=5)
        
        lb_Description = Tk.Label(fr_Right, justify="left", padx=10, pady=5, 
                                        text="Dies ist ein bisschen Server Information bei der ich noch nicht genau weiss, \n wie ich sie am besten darstellen kann.", font=default_font)
        lb_Description.grid(row=8, rowspan=3, column=1, padx=10, pady=5)

# Start the event loop.
window = MainWindow()
window.mainloop()

