#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code for creating a genome browser with dna_feature_viewer

@author: jgalag
"""

import matplotlib.pyplot as plt
# import matplotlib as mpl
import numpy as np

from dna_features_viewer import BiopythonTranslator
from bokeh.plotting import figure, show, output_file, save
from bokeh.layouts import gridplot, column, row
from bokeh.models import Span, Text, LabelSet,ColumnDataSource,Range1d,WheelZoomTool,BoxZoomTool,PanTool,ResetTool
from bokeh.models import Spinner,Slider,CustomJS,TextInput,Button,Paragraph,NumeralTickFormatter,LinearAxis
from bokeh.events import RangesUpdate
from bokeh.io import export_svgs, export_png

from bokeh.colors import RGB
# import itertools  

from dna_features_viewer import GraphicFeature, GraphicRecord,BiopythonTranslator

from Bio import SeqIO
from . import util
import re
from os.path import exists
from . import CONFIG




#%% Custom Translator Class
class MyCustomTranslator(BiopythonTranslator):
    """Custom translator 

    """
    
    def __init__(self,rstart=-1,rstop=float('inf'),features_filters=(), features_properties=None):
        self.start=rstart
        self.stop=rstop
        self.features_filters = features_filters
        self.features_properties = features_properties
        

    def compute_feature_color(self, feature):
        if feature.type == "CDS":
            return "green"
        else:
            return 'black'
        

    def compute_feature_label(self, feature):
 
        # if self.stop-self.start>500000:
        #     return None
        
        if feature.type == "CDS":
            
            return BiopythonTranslator.compute_feature_label(self, feature)
        else:
            return None

    def compute_filtered_features(self, features):
        print('Computing features')
        
        fs= [
            feature for feature in features
            if ((((feature.type == "CDS" or feature.type=='nucleotide_motif') and ((feature.location.end<self.stop and feature.location.end > self.start) or (feature.location.start>self.start and feature.location.start < self.stop))) 
                or bool(re.match(r".*binding.*",feature.type))) and (feature.location.start>0))
        ]
        # pdb.set_trace()
        print('Done')
        return fs


#%% Browser Class

class Browser:
    
    def __init__(self,gb_file = None,region=[],fwidth=20,fheight=100,dataroot=CONFIG.server_data_root,memeroot=CONFIG.server_meme_root,filename='',filedir=CONFIG.browser_dir, gcplot=0,showseq=True, data_sources: dict = None):

        if gb_file is None:
            self.gbfile = SeqIO.read("%s/U00096.3.gbk"%CONFIG.data_dir, "genbank")
        else:
            self.gbfile = SeqIO.read("%s/%s"%(CONFIG.data_dir,gb_file), "genbank")
        self.genome=genome=str(self.gbfile.seq)
        self.filename=filename
        self.dataroot=dataroot
        self.memeroot=memeroot
        
        self.dataroot = data_sources.get('server_data_root') if data_sources else self.dataroot
        self.memeroot = data_sources.get('server_meme_root') if data_sources else self.memeroot
        
        if (len(region)<2):
            self.region=[1,len(genome)]
        else:
            self.region=region
        
        print(self.region)
        self.plots=[]
        self.bwidth=fwidth  # ths is bokeh units
        self.fwidth=[]      # this will be matplotlib units
        self.fheight=fheight
        self.wlength=50000  # for generating the graphic record
        
        self.gr_palette=['#2CA02C', '#D62728'] # green and red colors
        self.rg_palette=['#D62728','#2CA02C']
        self.rgb_palette=['#ff7c00','#1ac938','#023eff']  # no longer rgb but ygb for color blindness - pulled from seaborn bright
        
    
        
   
        # CUSTOM FILENAME
        if (self.filename):
            self.customOutputFile(self.filename,filedir)
      

       # LOADING AFTER THIS
        self.loadGenome(showseq=showseq)                                                             # genome
        if (gcplot):
            # this calculates the gc content in the region of the genome
            gcw=100 # the window over which we ave gc
            gc = lambda s: 100.0 * len([c for c in s if c in "GC"]) / gcw
            xx = np.arange(self.region[0],self.region[1] - gcw,gcw)
            yy = [gc(self.gbfile.seq[x : x + gcw]) for x in xx]
            yy=np.array(yy)
            
            self.gc=(xx+gcw/2,yy)
            self.loadValTrack([self.gc[0]],[self.gc[1]],thlines=[50],title='GC Content')  # gc

    #------------------------
    def customOutputFile(self,filename,filedir=CONFIG.browser_dir):
        
        output_file(filename="%s/%s.html"%(filedir,filename), title=filename)


    #------------------------
    def loadGenome(self,showseq=True):

        # GENOME
        # this is a hack to get the correct fwidth
        fig = plt.figure(figsize=(self.bwidth,1))
        (self.fwidth, fheight) = [int(100 * e) for e in fig.get_size_inches()]      
        plt.close(fig)

        bt=MyCustomTranslator(self.region[0],self.region[1])
        print('\nCreating graphical record....')
        graphic_record = bt.translate_record(self.gbfile)
        graphic_record.sequence_length=self.wlength
        
        print('\nPlotting record....')
        p=graphic_record.plot_with_bokeh(figure_width=self.bwidth,tools=["reset"])
        p.x_range=Range1d(self.region[0],self.region[1])
        p.toolbar.active_scroll=p.select_one(WheelZoomTool)
        print('\nDone')
    
        self.plots.append(p)
        
        # SEQUENCE
        #% this generates the sequence track on the genome region - 
        if showseq:
            xxx=list(range(self.region[0],self.region[1]))
            yyy=np.zeros(len(xxx))-0.8
            text = [self.genome[i] for i in range(self.region[0]-1,self.region[1]-1)] #since range is 1 based, and genome is zero-based, we need to subtract 1
            self.seqletters = ColumnDataSource(dict(x=xxx, y=yyy, text=text))
    
            
            if (self.region[1]-self.region[0]<100000):
                self.plots[0].text(x='x',y='y',text='text',source=self.seqletters,text_font_size='9px')
                
    
    
    #------------------------    
    def loadFimoFile(self,tf_name):
        '''Load a fimo file into the browser
        Right now fimo file locations are hardcoded to be:
                memeroot/tf_name/meme_out/fimo_out/fimo.gff'
        '''
        
        print('\nLoading fimo file for %s\n'%tf_name)
        gffname='%s/%s/meme_out/fimo_out/fimo.gff'%(self.memeroot,tf_name)
        if (exists(gffname)):
            self.loadGFFFile(gffname,title='FIMO')
        else:
            print('WARNING: Cannot find fimo file %s'%gffname)
    
        
    #------------------------    
    def loadGenericFeatures(self,starts,ends,strands=None,labels=None,title='',fheight=0.1):
        
        features=[]
        for i in range(0,len(starts)):
            
            if (strands==None):
                st=0
            else:
                st=strands[i]
                
            if (labels==None):
                lb=None
            else:
                lb=labels[i]
            
            
            gf=GraphicFeature(start=starts[i],end=ends[i],label=lb,strand=st)
            features.append(gf)
            
        slen=self.region[1]-self.region[0]+1
        graphic_record=GraphicRecord(sequence_length=slen,features=features)
        p=graphic_record.plot_with_bokeh(figure_width=self.bwidth,figure_height=fheight,tools=["reset"])
        
        p.x_range=self.plots[0].x_range
        p.add_tools(ResetTool(),PanTool(dimensions='width'), WheelZoomTool(dimensions='width'), BoxZoomTool(dimensions='width'))

        p.toolbar.active_scroll=p.select_one(WheelZoomTool)
        p.toolbar.active_drag=p.select_one(BoxZoomTool)

        p.title=title
        self.plots.append(p)
        
    #------------------------    
    def loadGFFFile(self,fname,fheight=0.1,title=''):
        
        print(fname)
        graphic_record = MyCustomTranslator(self.region[0],self.region[1]).translate_record(fname)
        
        if (graphic_record.features != []):
            p=graphic_record.plot_with_bokeh(figure_width=self.bwidth,figure_height=fheight,tools='')
            p.x_range=self.plots[0].x_range
            p.add_tools(PanTool(dimensions='width'), WheelZoomTool(dimensions='width'), BoxZoomTool(dimensions='width'),ResetTool())
    
            p.toolbar.active_scroll=p.select_one(WheelZoomTool)
            p.toolbar.active_drag=p.select_one(BoxZoomTool)
    
            p.title=title
            self.plots.append(p)
        else:
            print('WARNING" No graphic features found for %s'%fname)
        
        return
    
    
    #------------------------    
    def loadSampleTrack(self,run,samp,f_name = None,ylims=[],masks=[],title='',**kwargs):
        # custom to galagan lab samples

        p=None
        
        if f_name is None:
            fname='%s/runs/%s/%s/SPAT_COVERAGE/U00096.wig'%(self.dataroot,run,samp)
        else:
            fname='%s/runs/%s/%s/SPAT_COVERAGE/%s'%(self.dataroot,run,samp,f_name)
        if (exists(fname)):
            if title=='':
                title=samp
            
            p=self.loadWigFile(fname,title=title,ylims=ylims,winsize=50,masks=masks,**kwargs)
        else:
            print('WARNING: Could not find sample track file %s'%fname)
        
        return p
    
    #------------------------    
    def loadWigFile(self,fname,title='',ylims=[],winsize=5,masks=[],**kwargs):
        # ASSUMES THAT WIG HAS ONE VALUE PER POSITION - SIMPLE WIG
        wig=util.read_wig_file(fname)
        mn=np.mean(wig[:,1])
        wig[:,1]=wig[:,1]/mn
        wig[:,2]=wig[:,2]/mn
        wig[:,3]=wig[:,3]/mn
        
        
        # now we want to average windows of winsize just in this region
        p1=self.region[0]
        p2=self.region[1]
        
        xx = np.arange(p1,p2 - winsize,winsize)
        forc = [np.mean(wig[x : x + winsize,2]) for x in xx]
        revc = [np.mean(wig[x : x + winsize,3]) for x in xx]   
        totc = [np.mean(wig[x : x + winsize,1]) for x in xx]
        
        forc=np.array(forc)
        revc=np.array(revc)
        totc=np.array(totc)
    
        # self.loadValTrack([wig[p1:p2,0],wig[p1:p2,0]],[wig[p1:p2,2],wig[p1:p2,3]],title=title,palette=self.rg_palette,ylims=ylims) 
        p=self.loadValTrack([xx,xx,xx],[forc,revc,totc],title=title,palette=self.rgb_palette,ylims=ylims,masks=masks,**kwargs) 

        return p
    
    #------------------------
    def addRightAxisToValTrack(self,p,xx,yy,ylims,col='red', thlines=[],accent_th=[],title='',ylabel='',masks=[]):
        
        p.extra_y_ranges = {"right": Range1d(start=ylims[0], end=ylims[1])}
        ax=LinearAxis(y_range_name='right')
        ax.axis_line_color=col
        ax.major_tick_line_color=col
        ax.minor_tick_line_color=col
        ax.major_label_text_color=col

        p.add_layout(ax, 'right')
         
        for i in range(len(xx)):
            x=xx[i]
            y=yy[i]
            
            # Plot the actual values
            p.line(x, y,line_color=col,y_range_name="right")
        
        return p
    
    #------------------------
    def loadValTrack(self,xx,yy,thlines=[],accent_th=[],palette=[],title='',ylabel='',ylims=[],masks=[],line_width=2,fill=True,**kwargs):
        

        # create the new figure
        # TOOLS = 'xwheel_zoom,box_zoom,xpan,reset'
        p2 = figure(title=title,y_axis_label=ylabel,x_range=self.plots[0].x_range,width=self.fwidth,height=self.fheight,tools='')
        p2.add_tools(PanTool(dimensions='width'), WheelZoomTool(dimensions='width'), BoxZoomTool(dimensions='width'),ResetTool())
        

        
        # add any threshold lines
        for thline in thlines:
            vline = Span(location=thline, dimension='width', line_color='black', line_width=1)
            p2.renderers.extend([vline])
        
        if (palette==[]):
            palette = self.cmap2pallete('tab10')
            
        
        if (len(masks)>0):
            ymax=0  
            ymin=float('inf')
        
        
        # add the actual values with masking
        #Start----- for each trace in xx, yy
        for i in reversed(range(len(xx))):
            x=xx[i]
            y=yy[i]
            
            # Plot the actual values
            if len(palette)==1:
                p2.line(x, y,line_color=palette[0],alpha=0.6,line_width=line_width)
                
                if fill:
                    xm=np.concatenate([x[0:1],x,x[-1:]])
                    ym=np.concatenate([[0],y,[0]])                
                    p2.varea(xm,ym,alpha=0.8,fill_color=palette[0])
            else:
                p2.line(x, y,line_color=palette[i],alpha=0.6,line_width=line_width)
                
                if fill:
                    xm=np.concatenate([x[0:1],x,x[-1:]])
                    ym=np.concatenate([[0],y,[0]])
                    p2.varea(xm,ym,alpha=0.6,fill_color=palette[i])


            # remove grids            
            p2.xgrid.visible = False
            p2.ygrid.visible = False
            p2.outline_line_color = None
            
            # mask out the mask regions
            if (len(masks)>0):
                ind_mask=np.array([])
                for mask in masks:
                    ind=[i for i,v in enumerate(x) if (v>mask[0] and v<mask[1])]
                    
                    if len(ind)>0:
                        xm=np.concatenate([x[ind[0:1]],x[ind],x[ind[-1:]]])
                        ym=np.concatenate([[0],y[ind],[0]])
                        if len(xm)!=len(ym):
                            pdb.set_trace()
                        
                        #masked regions in gray
                        p2.line(xm, ym,line_color='#D3D3D3',line_width=line_width+0.5)
                        
                        if fill:
                            p2.varea(xm,ym,fill_color='#D3D3D3')
        
                        ind_mask=np.concatenate([ind_mask,ind])
                    
                # keep track of the ymax and ymin for unmasked regions
                # pdb.set_trace()
                ind=list(set(range(len(x)))-set(ind_mask)) # the unmasked regions
                ymax=np.max((ymax,np.max(y[ind])))
                ymin=np.min((ymin,np.min(y[ind])))
        
            # add accent dots to values greater than accent_th
            if (accent_th):
                ind=[i for i,v in enumerate(y) if v > accent_th[i]]
                p2.circle(x[ind],y[ind],size=10)
                
                
             
                
 
        #End----- for each trace in xx, yy
 
        p2.outline_line_width = 3
        p2.toolbar.active_scroll=p2.select_one(WheelZoomTool)
        p2.toolbar.active_drag=p2.select_one(BoxZoomTool)
        p2.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
        
        if (ylims):
            p2.y_range=Range1d(ylims[0],ylims[1])
        elif (len(masks)>0):
            p2.y_range=Range1d(ymin,ymax)
        
        p2.yaxis[0].ticker.desired_num_ticks = 2
        p2.xaxis.minor_tick_line_color = None         
        p2.yaxis.minor_tick_line_color = None    
        p2.yaxis.major_tick_line_color = None 
        
        self.plots.append(p2)
        
        return p2
    
    
    #------------------------
    def addGotoWidget(self):
        '''Adds a goto gene or position widget
        
        TODO: I have disabled the window size widget for now because it stopped working
        '''

        # title1 = Paragraph(text='Window:', align='center',height=10)
        widgwindow = TextInput(title="", value='5000',width=150,height=10)
        
        title2 = Paragraph(text='Position or Gene Symbol:', align='center',height=10)
        widg = TextInput(title="", value='',width=250,height=10)

        
        # curr_start_widg = Paragraph(text='Current Stop: %d'%self.region[0])
        # curr_stop_widg = Paragraph(text='Current Stop: %d'%self.region[1])

        
        db=ecoliDB()
        allgenes=db.getAllGeneLocations()
        db.close()
        
        genes=ColumnDataSource(data=dict(name=list(allgenes['symbol']),start=list(allgenes['start']),end=list(allgenes['stop'])))

        callback = CustomJS(args=dict(source=self.plots[0].x_range,widgpos=widg, widgwindow=widgwindow,genes=genes), code="""
            
            if (!isNaN(parseInt(widgpos.value))) {
                    source.end=parseInt(widgpos.value)+parseInt(widgwindow.value)
                    source.start=parseInt(widgpos.value)-parseInt(widgwindow.value)
                    console.log(this.value) }
            else {
                const data=genes.data
                const n=data['name']
                const start=data['start']
                const end=data['end']

                for (let i=0; i<start.length; i++) {
                        if (widgpos.value.toLowerCase()==n[i].toLowerCase()) {
                            console.log('match')
                            console.log(n[i])
                            console.log(start[i])
                            source.start=parseInt(start[i])-parseInt(widgwindow.value)
                            source.end=parseInt(end[i])+parseInt(widgwindow.value)
                        }
                }

            }
            

                
        """)


        widg.js_on_change('value', callback)
                
        # Cant get this to work - need to find an event that triggers when any plot is resized by any other plot
        # self.plots[1].js_on_event(RangesUpdate,CustomJS(args=dict(source=self.plots[0].x_range,curr_start_widg=curr_start_widg,curr_stop_widg=curr_stop_widg), code="""
        #     console.log('Range Update')    
            # curr_start_widg.text="Current Start: " + String(source.start)
            # curr_stop_widg.text="Current Stop: " + String(source.end)
            
        # """))
        
        
        b = Button(label='Reset View')
        b.js_on_click(CustomJS(args=dict(p=self.plots[0]), code="""
            p.reset.emit()
        """))
        
        self.plots.append(row(title2,widg,b))
        
    #------------------------
    def show(self):
        # add any last elements and show plot
        
        self.addGotoWidget()
        show(column(self.plots))
    
    #------------------------
    def save(self):
        # add any last elements and save plot
        
        self.addGotoWidget()
        save(column(self.plots))
        
    #------------------------    
    def export_png(self,filename):
        # Export figure to png
        
        export_png(column(self.plots),filename=filename)
    
    
    #------------------------    
    def export_svg(self,filename):
        # Export figure to png

        for p in self.plots:
            if hasattr(p,'output_backend'):
                p.output_backend = "svg"
        export_svgs(column(self.plots),filename=filename, timeout=1000)
        
    #%%%%% Some utility functions
    
    
    def cmap2pallete(self,cmapname):
        cmap = plt.get_cmap(cmapname)
        cmap_rgb = (255 * cmap(range(256))).astype('int')
        palette = [RGB(*tuple(rgb)).to_hex() for rgb in cmap_rgb]
        
        return palette




