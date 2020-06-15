# coding: UTF-8

"""
FlexTiles-K.
FlexTiles is to generate tiled pattenrs by rotating each tile.
This is an adjusted version of FlexTiles, which were originally 
developed in 2011 for SOMACCA (Syntax of Mind) project. 
This version has a new feature which is to draw each tile, 
as if a tile is a canvas for a geometric drawing like Kandinsky's
drawings.

This program was coded and tested in macOS 10.13.

Jinook Oh, Cognitive Biology dept., University of Vienna.
May. 2020.

Dependency:
    wxPython (4.0)

------------------------------------------------------------------------
Copyright (C) 2020 Jinook Oh & Tecumseh Fitch 
- Contact: jinook0707@gmail.com, tecumseh.fitch@univie.ac.at

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
------------------------------------------------------------------------
"""

from sys import argv
from os import getcwd, path, mkdir
from glob import glob
from copy import copy
from random import randint
from time import time

import wx, wx.adv
#from wx.lib.wordwrap import wordwrap
import wx.lib.scrolledpanel as SPanel 
import numpy as np

from modFFC import GNU_notice, get_time_stamp, getWXFonts, stopAllTimers
from modFFC import updateFrameSize, add2gbs, receiveDataFromQueue
from modFFC import set_img_for_btn, load_img, setupStaticText
import modFTAnalysis as ftA

DEBUG = False 
__version__ = "0.1.1"

#=======================================================================

class FlexTilesFrame(wx.Frame):
    """ wxPython frame for FlexTiles 

    Args:
        None
     
    Attributes:
        Each attribute is commented in 'setting up attributes' section.
    """
    
    def __init__(self):
        if DEBUG: print("FlexTilesFrame.__init__()")
        
        ### init 
        wPos = (0, 20)
        wg = wx.Display(0).GetGeometry()
        wSz = (wg[2], int(wg[3]*0.9))
        wx.Frame.__init__(
              self,
              None,
              -1,
              "FlexTiles-K v.%s"%(__version__), 
              pos = tuple(wPos),
              size = tuple(wSz),
              style=wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX),
              )
        self.SetBackgroundColour('#AAAABB')
        
        ### set app icon
        self.tbIcon = wx.adv.TaskBarIcon(iconType=wx.adv.TBI_DOCK)
        icon = wx.Icon("icon.ico")
        self.tbIcon.SetIcon(icon)
        
        ##### [begin] setting up attributes -----
        self.wSz = wSz # window size
        self.fonts = getWXFonts()
        self.flagBlockUI = False # flag to determine temporary UI block
        pi = self.setPanelInfo() # set panel info
        self.pi = pi # panel information
        self.gbs = {} # for GridBagSizer
        self.panel = {} # panels
        self.timer = {} # timers
        self.csvFP = "" # CSV file path
        self.outputPath = path.join(CWD, "output") # output file path
        if not path.isdir(self.outputPath): mkdir(self.outputPath)
        self.ani = None # to store animation info. to run
        self.kD = None # to store drawing info. (used when in Kandinsky mode)
        self.colors = {} # some preset colors
        self.colors["ftBGCol"] = "#111111" # background color of FlexTiles panel
        self.colors["highlightedTile"] = "#eeee33" # for highlighting a tile
        self.nRows = 8 # number of rows in FlexTiles
        self.nCols = 8 # number of columns in FlexTiles
        self.tileSz = 75 # size in pixels
        ### resize tile-size if it bigger than window size
        if self.nCols*self.tileSz > wSz[0]:
            self.tileSz *= int(wSz[0] / (self.nCols*self.tileSz))
        if self.nRows*self.tileSz > wSz[1]:
            self.tileSz = int(self.tileSz * (wSz[1]/(self.nRows*self.tileSz)))
        ### load initial tile image
        initTileImg = "tile_init.png"
        self.initTileImg = load_img(initTileImg)
        # store initial (large) image for Kandinsky mode
        self.tileImgLarge = self.initTileImg.Copy() 
        # store image for FlexTiles mode
        self.tileImg = self.initTileImg.Copy() 
        ### if size doesn't match with desired size, rescale it.
        imgSz = self.tileImg.GetSize()
        if imgSz[0] != self.tileSz or imgSz[1] != self.tileSz:
            self.tileImg = self.tileImg.Rescale(self.tileSz, 
                                                self.tileSz, 
                                                wx.IMAGE_QUALITY_HIGH)
        lX = int(self.wSz[0]/2 - (self.tileSz*self.nCols)/2)
        tY = int(self.wSz[1]/2 - (self.tileSz*self.nRows)/2)
        # store rect of entire FlexTiles
        self.ftR = [lX,  # x1
                    tY, # y1 
                    lX + self.tileSz*self.nCols, # x2 
                    tY + self.tileSz*self.nRows] # y2
        self.idxMouseOn = (None, None) # row, column indices of tile, where
          # mouse pointer is currently on
        ### initialize angles and click-counters of all tiles
        d = []
        for ri in range(self.nRows):
            d.append([])
            for ci in range(self.nCols):
                #angle = randint(0,3) * 90
                angle = 0
                click = 0
                d[ri].append([angle, click])
        self.ftArr = np.asarray(d, dtype=np.uint16) # store it as array
        self.ftSeq = [] # to store sequence of tile clicks
        self.progInitTime = time() # starting time of the program
        self.currMP = None # current mouse pointer position
        self.flagKandinsky = False # whether it's in Kandinsky mode
        self.kDBtns = ["fill", "line", "rectangle",
                       "circle", "curvyline", "polygon", 
                       "pencil"] # button names for Kandinsky mode
        self.selectedDBtn = "" # selected drawing button name
        self.selectedFCol = "#cccccc" # selected filling color
        self.selectedSCol = "#0000ff" # selected stroke color
        self.selectedSThick = 1 # selected stroke thickness
        self.flagFreePencilDrawing = False # free drawing is on
        self.freePencilDrawingPts = [] # points for free pencil drawing
        ##### [end] setting up attributes -----
        
        updateFrameSize(self, wSz)
        
        ### create panels
        for k in pi.keys():
            if k == "lp":
                self.panel[k] = SPanel.ScrolledPanel(self, 
                                                     pos=pi[k]["pos"],
                                                     size=pi[k]["sz"],
                                                     style=pi[k]["style"])
            elif k == "mp":
                self.panel[k] = wx.Panel(self,
                                         pos=pi[k]["pos"],
                                         size=pi[k]["sz"],
                                         style=pi[k]["style"])
            self.panel[k].SetBackgroundColour(pi[k]["bgCol"])
        
        ### set up main-panel
        self.panel["mp"].Bind(wx.EVT_PAINT, self.onPaint)
        self.panel["mp"].Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.panel["mp"].Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.panel["mp"].Bind(wx.EVT_RIGHT_UP, self.onRightClick)
        self.panel["mp"].Bind(wx.EVT_MOTION, self.onMouseMove)
        
        ##### [begin] set up left panel interface -----
        nCol = 2
        hlSz = (pi["lp"]["sz"][0]-10, -1) # size of horizontal line separator
        self.gbs["lp"] = wx.GridBagSizer(0,0)
        row = 0; col = 0
        sTxt = setupStaticText(self.panel["lp"],
                               label="DrawingTools",
                               font=self.fonts[2],
                               fgColor="#cccccc")
        add2gbs(self.gbs["lp"], sTxt, (row,col), (1,2))
        row += 1
        for i in range(len(self.kDBtns)):
            bn = self.kDBtns[i].capitalize() # button name
            btn = wx.Button(self.panel["lp"],
                            -1,
                            size=(45,45),
                            name="draw%s_btn"%(bn))
            # set image for button
            set_img_for_btn("img_draw%s_off.png"%(bn), btn)
            btn.Bind(wx.EVT_LEFT_DOWN, self.onButtonPressDown)
            add2gbs(self.gbs["lp"], btn, (row,col), (1,1), bw=5)
            if i % 2 != 0:
                row += 1
                col = 0
            else:
                col += 1
        if len(self.kDBtns) % 2 != 0:
            row += 1
            col = 0
        sTxt = setupStaticText(self.panel["lp"],
                               label="Fill",
                               font=self.fonts[2],
                               fgColor="#cccccc")
        add2gbs(self.gbs["lp"], sTxt, (row,col), (1,1))
        col += 1
        cpc = wx.ColourPickerCtrl(self.panel["lp"],
                                  -1,
                                  name="drawFCol_cpc")
        cpc.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorPicked)
        cpc.SetColour(self.selectedFCol)
        add2gbs(self.gbs["lp"], cpc, (row,col), (1,1), bw=0)
        row += 1
        col = 0
        sTxt = setupStaticText(self.panel["lp"],
                               label="Stroke",
                               font=self.fonts[2],
                               fgColor="#cccccc")
        add2gbs(self.gbs["lp"], sTxt, (row,col), (1,1))
        col += 1
        cpc = wx.ColourPickerCtrl(self.panel["lp"],
                                  -1,
                                  name="drawSCol_cpc")
        cpc.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorPicked)
        cpc.SetColour(self.selectedSCol)
        add2gbs(self.gbs["lp"], cpc, (row,col), (1,1), bw=0)
        row += 1
        col = 0
        sTxt = setupStaticText(self.panel["lp"],
                               label="Stroke thickness",
                               font=self.fonts[0],
                               fgColor="#cccccc")
        add2gbs(self.gbs["lp"], sTxt, (row,col), (1,1))
        col += 1
        spin = wx.SpinCtrl(self.panel["lp"],
                           -1,
                           size=(50,-1),
                           min=1,
                           max=50,
                           initial=self.selectedSThick,
                           name='strokeThick_spin',
                           style=wx.SP_ARROW_KEYS|wx.SP_WRAP)
        spin.Bind(wx.EVT_SPINCTRL, self.onSpinCtrl)
        add2gbs(self.gbs["lp"], spin, (row,col), (1,1))
        row += 1
        col = 0
        add2gbs(self.gbs["lp"],
                wx.StaticLine(self.panel["lp"],
                              -1,
                              size=hlSz,
                              style=wx.LI_HORIZONTAL),
                (row,col),
                (1,nCol)) # horizontal line separator
        self.panel["lp"].SetSizer(self.gbs["lp"])
        self.gbs["lp"].Layout()
        self.panel["lp"].SetupScrolling()
        self.panel["lp"].Hide()
        ##### [end] set up top panel interface -----

        ### set up menu
        menuBar = wx.MenuBar()
        mainMenu = wx.Menu()
        kModeMenu = mainMenu.Append(wx.Window.NewControlId(), 
                                    item="Kandinsky drawing mode\tCTRL+K")
        self.Bind(wx.EVT_MENU, self.onKandinskyMode, kModeMenu)
        saveMenu = mainMenu.Append(wx.Window.NewControlId(), 
                                   item="Save\tCTRL+S")
        self.Bind(wx.EVT_MENU, self.onSave, saveMenu)
        quitMenu = mainMenu.Append(wx.Window.NewControlId(), 
                                   item="Quit\tCTRL+Q")
        self.Bind(wx.EVT_MENU, self.onClose, quitMenu)
        menuBar.Append(mainMenu, "&FlexTiles")
        self.SetMenuBar(menuBar)

        ### keyboard binding
        kMode_btnId = wx.NewIdRef(count=1)
        save_btnId = wx.NewIdRef(count=1)
        exit_btnId = wx.NewIdRef(count=1)
        self.Bind(wx.EVT_MENU, self.onKandinskyMode, id=kMode_btnId)
        self.Bind(wx.EVT_MENU, self.onSave, id=save_btnId)
        self.Bind(wx.EVT_MENU, self.onClose, id=exit_btnId)
        accel_tbl = wx.AcceleratorTable([
                                    (wx.ACCEL_CMD,  ord('K'), kMode_btnId),
                                    (wx.ACCEL_CMD,  ord('S'), save_btnId),
                                    (wx.ACCEL_CMD,  ord('Q'), exit_btnId),
                                    ])
        self.SetAcceleratorTable(accel_tbl)

        self.Bind(wx.EVT_CLOSE, self.onClose)
     
    #-------------------------------------------------------------------
   
    def setPanelInfo(self):
        """ Set up panel information.
        
        Args:
            None
        
        Returns:
            pi (dict): Panel information.
        """
        if DEBUG: print("FlexTilesFrame.setPanelInfo()")

        wSz = self.wSz
        pi = {} # information of panels
        # main panel for showing FlexTiles 
        pi["mp"] = dict(pos=(0, 0),
                        sz=wSz,
                        bgCol="#000000",
                        style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        # left panel for drawing tools 
        pi["lp"] = dict(pos=(0, 0), 
                        sz=(int(wSz[0]*0.12), wSz[1]),
                        bgCol="#333333",
                        style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        return pi

    #-------------------------------------------------------------------

    def onButtonPressDown(self, event, objName=""):
        """ wx.Butotn was pressed.
        
        Args:
            event (wx.Event)
            objName (str, optional): objName to emulate the button press
              of the button with the given name. 
        
        Returns:
            None
        """
        if DEBUG: print("FlexTilesFrame.onButtonPressDown()")

        if objName == '': # user's button-click
            obj = event.GetEventObject()
            objName = obj.GetName()
            self.playSnd("leftClick")
        else: # internal call
            obj = wx.FindWindowByName(objName, self.panel["lp"])
        
        if self.flagBlockUI: return
        if obj != None and obj.IsEnabled() == False: return
        
        if objName.startswith("draw"):
        # one of drawing buttons was selected
            if self.selectedDBtn != "":
                ### unselecte previously selected button
                _bl = self.selectedDBtn.capitalize()
                _obj = wx.FindWindowByName("draw%s_btn"%(_bl), self.panel["lp"])
                set_img_for_btn("img_draw%s_off.png"%(_bl), _obj)
                self.kD = None # make dictionary for drawing to None
            _bl = objName[4:-4] # remove 1st and last 4 charaters
              # 'draw' at the beginning and '_btn' at the end.
            if self.selectedDBtn == _bl:
            # clicked button is as same as previously selected button 
                self.selectedDBtn = "" # unselect
            else:
                self.selectedDBtn = _bl # store selected button label
                # set image for selected button
                set_img_for_btn("img_draw%s.png"%(_bl.capitalize()), obj)
        
    #-------------------------------------------------------------------
    ''' 
    def openCSVFile(self):
        """ Open data CSV file. 
        
        Args:
            None
        
        Returns:
            None 
        """
        if DEBUG: print("FlexTilesFrame.openCSVFile()")

        ### choose result CSV file 
        wc = 'CSV files (*.csv)|*.csv' 
        dlg = wx.FileDialog(self, 
                            "Open CSV file", 
                            wildcard=wc, 
                            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL: return
        dlg.Destroy()
        csvFP = dlg.GetPath()
        
        ### update CSV file path
        self.csvFP = csvFP
        self.loadData() # load CSV data
     
    #-------------------------------------------------------------------
    
    def loadData(self):
        """ load CSV data 

        Args: None
        
        Returns: None
        """
        if DEBUG: print("FlexTilesFrame.loadData()")

        csvTxt = self.stcCSV.GetText()
        try:
            self.pgd.loadData(csvTxt) # load CSV data
        except: # failed to load data
            self.csvFP = ""
            self.pgd.csvFP = ""
            self.stcCSV.SetEditable(True)
            self.stcCSV.SetText("")
            self.stcCSV.SetEditable(False) # CSV text is read-only
            msg = "Failed to load CSV data"
            wx.MessageBox(msg, "Error", wx.OK|wx.ICON_ERROR)
        self.panel["mp"].Refresh() # draw FlexTiles 
    ''' 
    #-------------------------------------------------------------------
    
    def onPaint(self, event):
        """ processing wx.EVT_PAINT event

        Args:
            event (wx.Event)

        Returns:
            None
        """
        if DEBUG: print("FlexTilesFrame.onPaint()")

        event.Skip()
        
        dc = wx.PaintDC(self.panel["mp"])
        if self.flagKandinsky:
            self.drawInKMode(dc)
        else:
            self.draw(dc)
    
    #-------------------------------------------------------------------
  
    def draw(self, dc):
        """ Draw FlexTiles
        
        Args:
            dc (wx.PaintDC): PaintDC to draw on.
         
        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.draw()")

        dc.SetBackground(wx.Brush(self.colors["ftBGCol"]))
        dc.Clear()
        ani = self.ani # animation
        ftR = self.ftR # FlexTile's rect
        tSz = self.tileSz # tile size
         
        ### draw tile in rotate animation first
        if ani != None and ani["name"] == "rotate":
            ri = ani["ri"]
            ci = ani["ci"]
            x = ftR[0] + (ci * tSz)
            y = ftR[1] + (ri * tSz)
            deg = self.ftArr[ri,ci,0]
            radian = np.deg2rad(-deg)
            cx = x + tSz/2
            cy = y + tSz/2
            img = self.tileImg.Copy()
            img = img.Rotate(radian, (cx, cy), interpolating=True)
            imgSz = img.GetSize()
            offset = int((imgSz[0]-tSz)/2)
            dc.DrawBitmap(wx.Bitmap(img), x-offset, y-offset)
            
        ### draw rest of tiles
        imo = self.idxMouseOn # row, column indices of tile,
          # where mouse pointer is currently on
        dc.SetPen(wx.Pen(self.colors["highlightedTile"], 3))
        dc.SetBrush(wx.Brush('#000000', wx.TRANSPARENT))
        for ri in range(self.nRows):
            y = ftR[1] + (ri * tSz)
            if y >= ftR[3]: break # break if it's out of rect.
            for ci in range(self.nCols):
                if ani != None and ani["name"] == "rotate":
                    if ani["ri"] == ri and ani["ci"] == ci: continue
                x = ftR[0] + (ci * tSz)
                if x >= ftR[2]: break # break if it's out of rect.
                img = self.tileImg.Copy()
                deg = self.ftArr[ri,ci,0]
                if deg != 0:
                    ### rotate tile
                    n = int(deg / 90)
                    for i in range(n): img = img.Rotate90()
                dc.DrawBitmap(wx.Bitmap(img), x, y)
                        
                if imo == (ri, ci): # currently mouse pinter is on this tile
                    # highlight this tile
                    dc.DrawRectangle(x, y, tSz, tSz) 
   
        if ani != None and ani["name"] == "rotate": 
            ### Cover outside of FlexTiles, when 
            ###   rotating tile is occuring at the edge of FlexTiles
            ###   (rotating tile is larger than other tiles 
            ###    with black color bg.)
            dc.SetPen(wx.Pen('#000000', 1, wx.TRANSPARENT))
            dc.SetBrush(wx.Brush(self.colors["ftBGCol"]))
            if ani["ci"] == 0: # left side
                dc.DrawRectangle(ftR[0]-tSz, 0, tSz, self.wSz[1])
            elif ani["ci"] == self.nCols-1: # right side
                dc.DrawRectangle(ftR[2], 0, tSz, self.wSz[1])
            if ani["ri"] == 0: # top side
                dc.DrawRectangle(0, ftR[1]-tSz, self.wSz[0], tSz)
            elif ani["ri"] == self.nRows-1: # bottom side
                dc.DrawRectangle(0, ftR[3], self.wSz[0], tSz)

    #-------------------------------------------------------------------
  
    def drawInKMode(self, dc):
        """ Drawing in Kandinsky mode 
        
        Args:
            dc (wx.PaintDC): PaintDC to draw on.
         
        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.drawInKMode()")
        
        img = self.tileImgLarge.Copy()
        ftR = self.ftR # rect of FlexTiles area
        
        ##### [begin] drawing
        sz = self.tileSz 
        bmp = wx.Bitmap(sz, sz, depth=-1)
        memDC = wx.MemoryDC()
        memDC.SelectObject(bmp)
        
        ### draw existing tile image
        if img.GetSize()[0] != sz:
            img = img.Rescale(sz, sz, wx.IMAGE_QUALITY_HIGH)
        memDC.DrawBitmap(wx.Bitmap(img), 0, 0)
        
        isTempDrawing = False # temporary drawing is for some cases
          # such as line drawing (x1,y1 is determined but not x2, y2)
        
        ### make new drawings, if available
        if self.kD != None:
            memDC.SetPen(wx.Pen(self.selectedSCol, self.selectedSThick))
            memDC.SetBrush(wx.Brush(self.selectedFCol))
            kD = self.kD
            
            if kD["name"] == "fill":
                memDC.SetBackground(wx.Brush(self.selectedFCol))
                memDC.Clear()
                self.kD = None
            
            elif kD["name"] in ["line", "rectangle", "circle"]:
            # can be drawn with two points
                if kD["x1"] != None:
                    x1 = kD["x1"]
                    y1 = kD["y1"]
                    if kD["x2"] == None:
                        x2 = self.currMP[0] - ftR[0]
                        y2 = self.currMP[1] - ftR[1]
                        isTempDrawing = True
                    else:
                        x2 = kD["x2"]
                        y2 = kD["y2"]
                        self.kD = None
                    if kD["name"] == "line":
                        memDC.DrawLine(x1, y1, x2, y2)
                    elif kD["name"] == "rectangle":
                        memDC.DrawRectangle(x1, y1, (x2-x1), (y2-y1))
                    elif kD["name"] == "circle":
                        rad = int(np.sqrt((x2-x1)**2 + (y2-y1)**2))
                        memDC.DrawCircle(x1, y1, rad)
            
            elif kD["name"] == "curvyline": # curvy line drawing
                if kD["x1"] != None:
                    pen = wx.Pen(self.selectedSCol, self.selectedSThick)
                    x1 = kD["x1"]
                    y1 = kD["y1"]
                    if kD["x2"] == None:
                        x2 = self.currMP[0] - ftR[0]
                        y2 = self.currMP[1] - ftR[1]
                        memDC.DrawLine(x1, y1, x2, y2)
                        isTempDrawing = True
                    else:
                        x2 = kD["x2"]
                        y2 = kD["y2"]
                        gc = wx.GraphicsContext.Create(memDC)
                        gc.SetPen(wx.Pen(self.selectedSCol, 
                                         self.selectedSThick))
                        path = gc.CreatePath() 
                        path.MoveToPoint(x1, y1)
                        if kD["x3"] == None:
                            x3 = self.currMP[0] - ftR[0]
                            y3 = self.currMP[1] - ftR[1]
                            path.AddCurveToPoint(x1, y1, x2, y2, x3, y3)
                            isTempDrawing = True
                        else:
                            x3 = kD["x3"]
                            y3 = kD["y3"]
                            path.AddCurveToPoint(x1, y1, x2, y2, x3, y3)
                            self.kD = None
                        gc.StrokePath(path)
            
            elif kD["name"] == "polygon":
                pts = copy(kD["pts"])
                if not kD["isClosed"]: # when it's not complete
                    # add current mouse pointer position to the point list
                    pts.append((self.currMP[0]-ftR[0], self.currMP[1]-ftR[1]))
                if len(pts) == 2: # not polygon yet
                    # draw as line
                    memDC.DrawLine(pts[0][0], pts[0][1], pts[1][0], pts[1][1])
                    isTempDrawing = True
                elif len(pts) > 2:
                    if kD["isClosed"]: self.kD = None
                    else: isTempDrawing = True
                    memDC.DrawPolygon(pts) # draw polygon
            
            elif kD["name"] == "pencil":
                pts = self.freePencilDrawingPts
                l = len(pts)
                if l > 1:
                    memDC.DrawLines(pts)
                    self.freePencilDrawingPts = [copy(pts[-1])]
        memDC.SelectObject(wx.NullBitmap)
        ##### [end] drawing
        
        # draw tile on the given DC 
        dc.DrawBitmap(bmp, ftR[0], ftR[1])
        if not isTempDrawing:
            # update tile image
            self.tileImgLarge = bmp.ConvertToImage()
     
    #-------------------------------------------------------------------

    def onTimer(self, event, flag):
        """ Processing on wx.EVT_TIMER event
        
        Args:
            event (wx.Event)
            flag (str): Key (name) of timer
        
        Returns:
            None
        """
        #if DEBUG: print("FlexTilesFrame.onTimer()") 

        if flag == "ani":
        # animation is running
            
            ### set some parameters
            if self.ani["name"] == "rotate":
                aStep = 10 # degree to rotate for 'rotate' 
            else:
                # size of tile to increase/decrease for 'zoomIn/Out'
                tStep = max(5, int(abs(self.tileSz-self.ani["targetSz"])/10))
            
            isAniEnded = False
            if self.ani["name"] == "rotate":
            # rotating tile
                ri = self.ani["ri"]
                ci = self.ani["ci"]
                tAng = self.ani["tAng"]
                if self.ftArr[ri,ci,0] < tAng:
                    self.ftArr[ri,ci,0] += aStep 
                else: # reached target angle
                    if self.ftArr[ri,ci,0] == 360: self.ftArr[ri,ci,0] = 0
                    isAniEnded = True
             
            elif self.ani["name"] == "zoomIn":
            # zooming in (when Kandinsky mode is turned on)
                tSz = self.ani["targetSz"]
                if self.tileSz < tSz:
                    self.tileSz += tStep 
                else: # reached target tile size
                    isAniEnded = True
            
            elif self.ani["name"] == "zoomOut":
            # zooming out (when Kandinsky mode is turned off)
                tSz = self.ani["targetSz"]
                if self.tileSz > tSz:
                    self.tileSz -= tStep 
                else: # reached target tile size
                    isAniEnded = True
             
            if isAniEnded: # animation ended
                self.timer["ani"].Stop()
                self.timer["ani"] = None
                self.flagBlockUI = False
                if self.ani["name"] == "zoomIn":
                    self.flagKandinsky = True
                    self.panel["lp"].Show() 
                    if self.selectedDBtn != "":
                    # if there's a selected drawing button
                        # de-select it
                        self.onButtonPressDown(
                                None, 
                                "draw%s_btn"%(self.selectedDBtn.capitalize())
                                )
                self.ani = None
            self.panel["mp"].Refresh() # redraw FlexTiles
    
    #-------------------------------------------------------------------
    
    def calcIdxFromCoord(self, mp):
        """ Calculates indices of row and column of FlexTiles
        with given x,y coordinates
        
        Args:
            mp (tuple) : x, y coordinates of clicked point by mouse
        
        Returns:
            (tuple): Indices of row and column of FlexTiles. 
              Values are None, if click occured outside of tiles.
        """ 
        if DEBUG: print("FlexTilesFrame.calcIdxFromCoord()")

        ri = None; ci = None
        r = self.ftR
        if r[0] <= mp[0] <= r[2] and r[1] <= mp[1] <= r[3]:
        # click occurred in FlexTiles
            ci = int((mp[0]-r[0]) / self.tileSz)
            ri = int((mp[1]-r[1]) / self.tileSz)
        return (ri, ci)

    #-------------------------------------------------------------------
    
    def onLeftDown(self, event):
        """ Processing when left mouse button pressed down 
        
        Args:
            event (wx.Event)
        
        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.onLeftDown()")
        
        if self.flagBlockUI: return
         
        mp = event.GetPosition()
      
        if self.flagKandinsky:
        # Kandinsky drawing mode
            sdBtn = self.selectedDBtn.lower()
            if sdBtn == "pencil":
                self.kD = dict(name="pencil")
                self.flagFreePencilDrawing = True
        self.panel["mp"].Refresh() # re-draw FlexTiles

    #-------------------------------------------------------------------
    
    def onLeftUp(self, event):
        """ Processing when left mouse button was clicked 
        
        Args:
            event (wx.Event)
        
        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.onLeftUp()")
        
        if self.flagBlockUI: return
         
        mp = event.GetPosition()
        ftR = self.ftR
      
        if self.flagKandinsky:
        # Kandinsky drawing mode
            sdBtn = self.selectedDBtn.lower()
            mp = (mp[0]-ftR[0], mp[1]-ftR[1])
            if sdBtn == "fill":
                self.kD = dict(name="fill")
            elif sdBtn in ["line", "rectangle", "circle"]:
            # things can be drawn with two points
                if self.kD == None: # no coordinate info is available 
                    x1 = mp[0]; y1 = mp[1] # store the 1st point
                    x2 = None; y2 = None
                else:
                    x1 = self.kD["x1"]; y1 = self.kD["y1"]
                    x2 = mp[0]; y2 = mp[1] # store the 2nd point
                self.kD = dict(name=sdBtn, x1=x1, y1=y1, x2=x2, y2=y2)
            elif sdBtn == "curvyline":
                x1=None; y1=None; x2=None; y2=None; x3=None; y3=None
                if self.kD == None: # no coordinate info is available 
                    x1 = mp[0]; y1 = mp[1] # store the 1st point
                else:
                    if self.kD["x2"] == None:
                        x1 = self.kD["x1"]; y1 = self.kD["y1"]
                        x2 = mp[0]; y2 = mp[1] # store the 2nd point
                    else:
                        if self.kD["x3"] == None:
                            x1 = self.kD["x1"]; y1 = self.kD["y1"]
                            x2 = self.kD["x2"]; y2 = self.kD["y2"]
                            x3 = mp[0]; y3 = mp[1] # store the 3rd point
                self.kD = dict(name=sdBtn, 
                               x1=x1, y1=y1, 
                               x2=x2, y2=y2,
                               x3=x3, y3=y3) 
            elif sdBtn == "polygon":
                isClosed = False
                if self.kD == None: # no coordinate info is available
                    pts = [mp]
                else:
                    pts = self.kD["pts"]
                    if len(pts) > 2:
                        th = (ftR[2]-ftR[0])*0.02 # threshold distance to 
                          # determine whether it's close enough point
                        d2first = np.sqrt((pts[0][0]-mp[0])**2 + \
                                          (pts[0][1]-mp[1])**2)
                        if d2first < th:
                            isClosed = True
                        else:
                            flag = True 
                            for i in range(len(pts)):
                                dist = np.sqrt((pts[i][0]-mp[0])**2 + \
                                               (pts[i][1]-mp[1])**2)
                                if dist < th: flag = False 
                            if flag:
                                pts.append(mp)
                    else:
                        pts.append(mp)
                self.kD = dict(name=sdBtn, pts=pts, isClosed=isClosed)
            elif sdBtn == "pencil":
                self.flagFreePencilDrawing = False 
                self.freePencilDrawingPts = []
        
        else:
        # FlexTiles mode
            ri, ci = self.calcIdxFromCoord(mp)
            if ri != None:
            # if clicked in FlexTiles
                self.playSnd("leftClick")
                self.flagBlockUI = True # temporarily block user input 
                # store clicked tile index and time
                self.ftSeq.append([ri, ci, time()-self.progInitTime]) 
                # increase number of clicks for this tile
                self.ftArr[ri,ci,1] += 1
                targetAngle = self.ftArr[ri,ci,0] + 90
                self.ani = dict(name="rotate", ri=ri, ci=ci, tAng=targetAngle)
                ### set timer for rotating animation 
                self.timer["ani"] = wx.Timer(self)
                self.Bind(wx.EVT_TIMER,
                          lambda event: self.onTimer(event, "ani"),
                          self.timer["ani"])
                self.timer["ani"].Start(5) 
             
        self.panel["mp"].Refresh() # re-draw FlexTiles
    
    #-------------------------------------------------------------------
    
    def onRightClick(self, event):
        """ Processing when left mouse click occurred 
        
        Args:
            event (wx.Event)

        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.onRightClick()")

        if self.flagBlockUI: return
         
        mp = event.GetPosition()
      
        if self.flagKandinsky:
        # Kandinsky drawing mode
            self.kD = None # cancel any drawing
        
        self.panel["mp"].Refresh() # re-draw FlexTiles

    #-------------------------------------------------------------------
    
    def onMouseMove(self, event):
        """ Mouse pointer moving on FlexTiles 
        
        Args:
            event (wx.Event)

        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.onMouseMove()")

        if self.flagBlockUI: return

        mp = event.GetPosition()
        self.currMP = mp # update current mouse position
       
        if self.flagKandinsky:
        # Kandinsky drawing mode
            if self.flagFreePencilDrawing:
                x = mp[0] - self.ftR[0]
                y = mp[1] - self.ftR[1]
                self.freePencilDrawingPts.append((x,y))
                if len(self.freePencilDrawingPts) > 10:
                    self.panel["mp"].Refresh() # re-drawing 
            else:
                self.panel["mp"].Refresh() # re-drawing 
         
        else: # FlexTiles mode 
            ri, ci = self.calcIdxFromCoord(mp)
            if ri == None: self.idxMouseOn = (None, None)
            else: self.idxMouseOn = (ri, ci)
            self.panel["mp"].Refresh() # re-drawing 
    
    #-------------------------------------------------------------------
    
    def screenShot(self):
        """ Return FlexTiles (or Tile in Kandinsky mode) part of screen 
            as wx.Image

        Args:
            None 

        Returns:
            croppedImg (wx.Image): Screen image. 
        """
        if DEBUG: print("FlexTilesFrame.screenShot()") 

        sz = self.pi["mp"]["sz"]
        bmp = wx.Bitmap(sz[0], sz[1], depth=-1)
        memDC = wx.MemoryDC()
        memDC.SelectObject(bmp)
        if self.flagKandinsky: self.drawInKMode(memDC) # draw tile
        else: self.draw(memDC) # draw FlexTiles
        memDC.SelectObject(wx.NullBitmap)
        img = bmp.ConvertToImage()
        r = self.ftR
        croppedImg = img.GetSubImage((r[0], r[1], r[2]-r[0], r[3]-r[1]))
        return croppedImg
    
    #-------------------------------------------------------------------
    
    def onSave(self, event):
        """ Save the current FlexTiles 

        Args:
            event (wx.Event)

        Returns:
            None
        """
        if DEBUG: print("FlexTilesFrame.onSave()") 

        if self.flagKandinsky: return # save works only with FlexTiles
        
        ### file names to write
        timestamp = get_time_stamp().replace("_","")[:14]
        imgFN = "ft_%s.png"%(timestamp)
        imgFP = path.join(self.outputPath, imgFN)
        csvFN = imgFN.replace(".png", ".csv")
        csvFP = path.join(self.outputPath, csvFN)
         
        ### save FlexTiles image 
        croppedImg = self.screenShot() 
        croppedImg.SaveFile(imgFP, wx.BITMAP_TYPE_PNG) # save as file
        
        ##### [begin] saving CSV
        arr = self.ftArr
        rows, cols, __ = arr.shape
        fh = open(csvFP, 'w')
        
        ### writing final states of tiles 
        analysis_list = []
        fh.write("# Final state of each tile\n")
        fh.write("# - rows and columns match with FlexTiles shown in UI\n")
        fh.write("# -----------------------------------------------------\n")
        for ri in range(rows):
            for ci in range(cols):
                # write FT data (degree of rotation of each tile)
                #   as a blank padded number, such as ' 90', '180', ...
                deg = arr[ri,ci,0]
                fh.write(str(deg).rjust(3, ' '))
                if ci < cols-1: fh.write(", ")
                analysis_list.append(deg)
            fh.write("\n")
        fh.write("\n")

        ### writing number of clicks in each tile
        fh.write("# Number of clicks in each tile\n")
        fh.write("# - rows and columns match with FlexTiles shown in UI\n")
        fh.write("# -----------------------------------------------------\n")
        for ri in range(rows):
            for ci in range(cols):
                nClicks = arr[ri,ci,1]
                fh.write(str(nClicks).rjust(3, ' '))
                if ci < cols-1: fh.write(", ")
            fh.write("\n")
        fh.write("\n")

        ### prep. final-state data
        nStates = 4 # number of possible states (90, 180, 270, 360)
        binaryFlag = False
        # create array for sum over the states, starting with 0
        # the final result represents the probability P of occurrence
        analysis_x = [0.0 for i in range(nStates)]
        for i in range(len(analysis_list)):
            stateIdx = int(analysis_list[i] / (360/nStates))
            # add the state to the array
            analysis_x[stateIdx] += 1
        # divide by the overall sum of entries
        analysis_x = [x/len(analysis_list) for x in analysis_x]
        if rows == cols:
            flexTileWidth = 0 # If it's square FlexTiles, 
              # width (n of columns) will be calculated in other functions
        else:
            flexTileWidth = cols
        ### calculates analysis values
        entropyValue = round(ftA.Entropy(analysis_x), 3)
        symmetryValues = ftA.roundArray(
                            ftA.getSymmetryValues(analysis_list,
                                                  binaryFlag,
                                                  flexTileWidth),
                            3)
        rotationalSymmetries = ftA.roundArray(
                                ftA.getRotationalSymmetries(analysis_list,
                                                            binaryFlag,
                                                            flexTileWidth),
                                3)
        translationalSymmetry = round((1-(entropyValue)/2), 3)
        tileMakerSymmetry = round(ftA.getTileMakerSymmetry(
                                    analysis_list, 
                                    False, 
                                    flexTileWidth
                                    ), 3) 
        
        ### writing analysis results 
        fh.write("# Analysis results\n")
        fh.write("# -----------------------------------------------------\n")
        fh.write("The Entropy of this final state, %s\n"%str(entropyValue))
        fh.write("Orientation ratio ")
        fh.write("[0/90/180/270], [")
        tmpStr = ''
        for i in range(len(analysis_x)):
            tmpStr += str(analysis_x[i]) + "/"
        tmpStr = tmpStr.rstrip("/")
        fh.write(tmpStr + "]")
        fh.write('\n')
        fh.write("Symmetries [hor/ver/1dia/2dia], [")
        tmpStr = ''
        for i in range(len(symmetryValues)):
            tmpStr += str(symmetryValues[i]) + "/"
        tmpStr = tmpStr.rstrip("/")
        fh.write(tmpStr + "]\n")
        fh.write("Translational Symmetry, %s\n"%str(translationalSymmetry))
        fh.write("Tile Maker Symmetry, "+ str(tileMakerSymmetry) + '\n')
        fh.write("Rotational Symmetries [180/90], [")
        tmpStr = ''
        for i in range(len(rotationalSymmetries)):
            tmpStr += str(rotationalSymmetries[i]) + "/"
        tmpStr = tmpStr.rstrip("/")
        fh.write(tmpStr + "]\n")
        fh.write("\n")
        
        ### writing the sequnce of tile-clicks
        fh.write("# Sequence of FlexTile-Clicks\n")
        fh.write("# - click-time is seconds after program-start-time.\n")
        fh.write("# [sequence], [row-index], [column-index], [click-time]\n")
        fh.write("# -----------------------------------------------------\n")
        cnt = 1
        for i in range(len(self.ftSeq)):
            ri, ci, eT = self.ftSeq[i]
            fh.write("%i, %i, %i, %.3f\n"%(cnt, ri, ci, eT))
            cnt += 1
        fh.write("\n")
        fh.close()
        ##### [end] saving CSV
        
        msg = "Finished saving"
        msg += 'Saved\n'
        msg += imgFN + "\n"
        msg += csvFN + "\n"
        msg += " in output folder."
        wx.MessageBox(msg, "Info.", wx.OK|wx.ICON_INFORMATION)
    
    #-------------------------------------------------------------------
    
    def playSnd(self, flag=""):
        """ Play sound 

        Args:
            flag (str): Which sound to play.

        Returns:
            None
        """ 
        if DEBUG: print("FlexTilesFrame.playSnd()")

        if flag == "leftClick":
            ### play click sound
            snd_click = wx.adv.Sound("snd_click.wav")
            snd_click.Play(wx.adv.SOUND_ASYNC)

    #-------------------------------------------------------------------

    def onKandinskyMode(self, event):
        """ Turn Kandinsky mode on.
        
        Args: event (wx.Event)
        
        Returns: None
        """
        if DEBUG: print("FlexTilesApp.onKandinskyMode()")
        
        if self.flagBlockUI: return
        
        self.flagBlockUI = True # temporarily block user input 
       
        if self.flagKandinsky: # zooming out from Kandinsky mode
            self.panel["lp"].Hide()
            self.flagKandinsky = False
            self.tileImg = self.tileImgLarge.Copy()
            tSz = self.initTileSz
            if self.tileImg.GetSize()[0] != tSz:
                self.tileImg = self.tileImg.Rescale(
                                            tSz,
                                            tSz, 
                                            wx.IMAGE_QUALITY_HIGH
                                            ) # resize
            self.ani = dict(name="zoomOut", targetSz=tSz)
        else: # zooming into a tile for Kandinsky mode
            tSz = int(self.wSz[1] * 0.75)
            self.initTileSz = copy(self.tileSz) # store original tile size 
            self.ani = dict(name="zoomIn", targetSz=tSz)
        
        ### set & start timer for animation 
        self.timer["ani"] = wx.Timer(self)
        self.Bind(wx.EVT_TIMER,
                  lambda event: self.onTimer(event, "ani"),
                  self.timer["ani"])
        self.timer["ani"].Start(10) 

    #-------------------------------------------------------------------

    def onColorPicked(self, event):
        """ a color is picked by a color picker 
        
        Args: event (wx.Event)
        
        Returns: None
        """
        if DEBUG: print("FlexTilesApp.onColorPicked()")

        obj = event.GetEventObject()
        objName = obj.GetName()
        
        if objName == "drawFCol_cpc":
            self.selectedFCol = obj.GetColour()
        elif objName == "drawSCol_cpc":
            self.selectedSCol = obj.GetColour()
   
    #-------------------------------------------------------------------

    def onSpinCtrl(self, event):
        """ value has changed in wx.SpinCtrl
        
        Args: event (wx.Event)
        
        Returns: None
        """
        if DEBUG: print("FlexTilesApp.onSpinCtrl()")

        obj = event.GetEventObject()
        objName = obj.GetName()

        if objName == "strokeThick_spin":
            self.selectedSThick = obj.GetValue()
    
    #-------------------------------------------------------------------

    def onClose(self, event):
        """ Close this frame.
        
        Args: event (wx.Event)
        
        Returns: None
        """
        if DEBUG: print("FlexTilesApp.onClose()")

        stopAllTimers(self.timer)
        wx.CallLater(100, self.Destroy)

    #-------------------------------------------------------------------

#=======================================================================

class FlexTilesApp(wx.App):
    def OnInit(self):
        if DEBUG: print("FlexTilesApp.OnInit()")
        self.frame = FlexTilesFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

#=======================================================================

if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == '-w': GNU_notice(1)
        elif argv[1] == '-c': GNU_notice(2)
    else:
        GNU_notice(0)
        CWD = getcwd()
        app = FlexTilesApp(redirect = False)
        app.MainLoop()

