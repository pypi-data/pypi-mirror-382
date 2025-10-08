#import matplotlib.colors as colors
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from scipy.stats import gaussian_kde
from holtztools import struct
import numpy as np
import sys
import pdb

from matplotlib.widgets import Lasso
from matplotlib.collections import RegularPolyCollection
from matplotlib import colors as mcolors, path

# default values for event handling
_index = 0
_data = None
_button = None
_id_cols = ['APOGEE_ID']
_new_data = True
_axes = None
_data_x = None
_data_y = None
_block = 0

def event(fig) :
    '''
    Define event handler, on a key press, will set _button (key pressed) and _index (index of nearest point), and
    if _data is not None, will list _id_cols from the structure _data[_index]
    '''
    global _block
    def onpress(event) :
        global _index, _block, _x, _y, _button, _new_data, tree, _axes
        _button = event.key
        try:
            inv = event.inaxes.transData.inverted()
            _x,_y = inv.transform((event.x,event.y))
            #print(_x, _y)
            #A[KDTree(A).query([event.x,event.y])[1]]
            #distance,index = KDTree(A).query([event.x,event.y])
            if _data_x is not None and _data_y is not None :
                #print('Transform', len(_data_x))
                # n key will reset transformation, e.g. if limits changed interactively
                if _button == 'n' or _new_data or event.inaxes != _axes :
                    A = event.inaxes.transData.transform(list(zip(_data_x,_data_y)))
                    #print('KDTree')
                    tree=KDTree(A)
                    _new_data = False
                    _axes = event.inaxes
                #print('query')
                distance,index = tree.query([event.x,event.y])
                _index = [index]
                if _data is not None :
                    struct.list(_data,ind=_index,cols=_id_cols)
                #else :
                #    print('_index: ',_index,_data_x[_index],_data_y[_index])
        except :
            _x,_y = (None,None)
        if _block == 1 :
            _block = 0
            fig.canvas.stop_event_loop()
    def onclose(event) :
        global _index, _block, _x, _y, _button, _new_data, tree, _axes
        _x,_y,_button = (None,None,None)
        if _block == 1 :
            _block = 0
            fig.canvas.stop_event_loop()

    cid = fig.canvas.mpl_connect('key_press_event',onpress)
    cid = fig.canvas.mpl_connect('close_event',onclose)
    if _block == 1 : fig.canvas.start_event_loop(0)

def mark(fig,index=False) :
    """ Return cursor position and key pressed
    """
    global _block, _x, _y, _button
    _block = 1
    event(fig)
    if index :return _x, _y, _button, _index[0]
    else : return _x, _y, _button


def plotc(ax,x,y,z,xerr=None,yerr=None,xr=None,yr=None,zr=None,size=5,cmap='rainbow',colorbar=False,xt=None,yt=None,zt=None,label=None,linewidth=0,edgecolor=None,marker='o',draw=True,orientation='vertical',labelcolor='k',tit=None,nxtick=None,nytick=None,rasterized=None,alpha=None) :
    """
    Plots a scatter plot with point color-coded by z data

    Args:
      ax (axis)  : existing axes
      x (float)  : x values
      y (float)  : y values
      z (float)  : z values, or a single color

    Keyword args:
      xr : x range  (default=None)
      yr : y range (default=None)
      zr : z range (default=None)
      xt : x axis title (default=None) (default=None)
      yt : y axis title (default=None)
      zt : z axis title (default=None)
      marker : marker type (default='o')
      cmap : colormap (default='rainbow')
      size : point size(s) in points (default=5)
      linewidth : linewidth (default=0)
      colorbar (bool) : draw a colorbar? (default=False)
      orientation : colorbar orientation (default='vertical')
      label [x,y,text] : label plot with text at position x,y in relative (0:1,0:1) coordinates
      labelcolor : color for label

    Returns:
      aximage

    """
    global _data_x, _data_y, _new_data

    set_limits_ticks(ax,xr,yr,nxtick,nytick)
    if xt is not None : ax.set_xlabel(xt) 
    if yt is not None : ax.set_ylabel(yt)
    if tit is not None : ax.set_title(tit)
    if xerr is not None or yerr is not None :
        ax.errorbar(x,y,xerr=xerr,yerr=yerr,fmt='none',capsize=0,ecolor='k')
    if zr is None :
        scat=ax.scatter(x,y,c=z,s=size,cmap=cmap,
                 linewidth=linewidth, marker=marker,edgecolor=edgecolor,
                 rasterized=rasterized,alpha=alpha)
    else :
        scat=ax.scatter(x,y,c=z,vmin=zr[0],vmax=zr[1],s=size,cmap=cmap,
                 linewidth=linewidth,marker=marker,edgecolor=edgecolor,
                 rasterized=rasterized,alpha=alpha)

    if label is not None :
        ax.text(label[0],label[1],label[2],transform=ax.transAxes,color=labelcolor) 
    if colorbar :
        cb=plt.colorbar(scat,ax=ax,orientation=orientation)
        cb.ax.set_ylabel(zt)
    if draw : plt.draw()
    _data_x = np.array(x)[np.isfinite(x)]
    _data_y = np.array(y)[np.isfinite(y)]
    _new_data = True
    return scat

def set_limits_ticks(ax,xr,yr,nxtick=None,nytick=None) :
    if nxtick is not None:
        if xr is not None : ax.set_xlim(xr[0],xr[1])
        ax.xaxis.set_ticks(np.linspace(ax.get_xlim()[0],ax.get_xlim()[1],nxtick)[1:-1])
    else :
        if xr is not None : ax.set_xlim(xr[0]+0.01*(xr[1]-xr[0]),xr[1]-0.01*(xr[1]-xr[0]))
    if nytick is not None:
        if yr is not None : ax.set_ylim(yr[0],yr[1])
        ax.yaxis.set_ticks(np.linspace(ax.get_ylim()[0],ax.get_ylim()[1],nytick)[1:-1])
    else :
        if yr is not None : ax.set_ylim(yr[0]+0.01*(yr[1]-yr[0]),yr[1]-0.01*(yr[1]-yr[0]))

def plotc_append(ax,x,y,z,size=25,linewidth=1,marker='o',facecolor='none',draw=True,edgecolor=None) :
    '''
    Adds points to a plot
    '''
    scat=ax.scatter(x,y,s=size,linewidth=linewidth,marker=marker,facecolor=facecolor,edgecolor=edgecolor)
    #scat=ax.scatter(x,y,c=z,s=size,linewidth=linewidth,marker=marker,facecolor=facecolor,edgecolor=edgecolor)
    if draw : plt.draw()

def plotrow(ax,img,r,norm=True,draw=True) :
    '''
    Plots a row of an input image

    Args:
      ax (axis)    : existing axes
      img (float)  : image to plot
      r (int)      : row or rows ([rmin,rmax]) to plot

    Keyword args:
      norm         : for multiple row plots, average instead of sum (default=True)
    '''
    ax.set_xlim(xr[0],xr[1])
    ax.set_ylim(yr[0],yr[1])
    if len(r) == 1 :
        ax.plotl(img[r,:])
    elif len(r) == 2 :
        if norm :
            ax.plotl(np.average(img[r[0]:r[1],:],axis=1))
        else :
            ax.plotl(np.sum(img[r[0]:r[1],:],axis=1))
    if draw : plt.draw()

def plotp(ax,x,y,z=None,typeref=None,types=None,xr=None,yr=None,zr=None,ids=None,
          marker='o',size=5,linewidth=0,color='r',facecolors=None,
          xt=None,yt=None,draw=True,xerr=None,yerr=None,
          label=None,text=None,labelcolor='k',linewidths=None,nxtick=None,nytick=None,
          tit=None,contour=None,levels=None,alpha=None,rasterized=None) :
    '''
    Plot points, optionally with a series of different markers/sizes keyed to z data

    Args:
        ax : axes to plot in
        x : x data
        y : y data

    Keyword args:
        z=  : specifies data to be used to color points if using types to specify sizes, markers (default=None)
        typeref= : specfies array to be used to determine groupings
        types= : array of different types (from typeref) to plot with specified sizes, markers, colors
        size= : array of different sizes to plot for different types, or single size
        marker= : array of different markers to plot for different types, or single marker
        color= : array of different colors markers to plot for different types, or single color
        xr : x limits (default=None)
        yr : y limits (default=None)
        xt : x title (default=None)
        yt : y title (default=None)
        label : label for legend
        text=[x,y,text] : put text at (x,y) relative coords
        labelcolor=  : color for label
       
    '''
    global _data_x, _data_y, _new_data

    set_limits_ticks(ax,xr,yr,nxtick,nytick)
    if xt is not None : ax.set_xlabel(xt) 
    if yt is not None : ax.set_ylabel(yt)
    if tit is not None : ax.set_title(tit)
    if facecolors is None: facecolors=color

    if typeref is not None and types is not None :
        # Make sure types, sizes, markers are all lists
        try :
            test = len(types)
        except :
            types = [types]
        try :
            test = len(size)
        except :
            size = [size]
        try :
            test = len(marker)
        except :
            marker = [marker]
        try :
            test = len(color)
        except :
            color = [color]

        # loop through the types
        for i in range(len(types)) :
            gd = np.where(typeref == types[i])[0]
            sz= size[i] if (len(size) > 1)  else size[0]
            mark=marker[i] if (len(marker) > 1) else marker[0]
            col=color[i] if (len(color) > 1) else color[0]
            if facecolors == 'none' : facecol = 'none'
            else : facecol = col
            if z is not None :
                if zr is not None :
                    ax.scatter(x[gd],y[gd],c=z[gd],s=sz,marker=mark,vmin=zr[0],vmax=zr[1],linewidths=linewidths,rasterized=rasterized)
                else :
                    ax.scatter(x[gd],y[gd],c=z[gd],s=sz,marker=mark,linewidths=linewidths,rasterized=rasterized)
            else :
                ax.scatter(x[gd],y[gd],s=sz,marker=mark,facecolors=facecol,edgecolors=col,linewidths=linewidths,rasterized=rasterized,label=types[i])
            if yerr is not None :
                ax.errorbar(x[gd],y[gd],marker=mark,yerr=yerr[gd],fmt='none',capsize=0,ecolor=col,rasterized=rasterized)
        ax.legend(fontsize='xx-small')
    elif contour is not None:
        if contour <= 0 :
            gd = np.where((x > np.array(xr).min()) & (x < np.array(xr).max()) & (y>np.array(yr).min()) & (y<np.array(yr).max()) )[0]
            if len(gd) == 0 : return
            data = np.vstack([x[gd],y[gd]])
            kde = gaussian_kde(data)
            xgrid = np.linspace(np.array(xr).min(), np.array(xr).max(), 40)
            ygrid = np.linspace(np.array(yr).min(), np.array(yr).max(), 40)
            Xgrid, Ygrid = np.meshgrid(xgrid, ygrid)
            Z = kde.evaluate(np.vstack([Xgrid.ravel(), Ygrid.ravel()]))
            # Plot the result as an image
            ax.imshow(Z.reshape(Xgrid.shape), origin='lower', aspect='auto',vmin=Z.min(),vmax=Z.max(),
                       extent=[xr[0], xr[1], yr[0], yr[1]], cmap='Blues')
        else :
            im = np.histogram2d(y,x,range=[yr,xr],bins=20)
            if levels is None:
                levels=np.linspace(1.,im[0].max(),contour)
            ax.contour((im[2][0:-1]+im[2][1:])/2.,(im[1][0:-1]+im[1][1:])/2.,im[0],
               colors=color,levels=levels,alpha=alpha)
    elif ids is not None :
        for xx,yy,ii in zip(x,y,ids) :
          xlim=ax.get_xlim()
          ylim=ax.get_ylim()
          if np.isfinite(xx) and np.isfinite(yy) and xx >= xlim[0] and xx <= xlim[1] and yy >= ylim[0] and yy <= ylim[1] :
              ax.text(xx,yy,ii,color=color)
    else :
        ax.scatter(x,y,marker=marker,s=size,linewidth=linewidth,facecolors=facecolors,edgecolors=color,linewidths=linewidths,alpha=alpha,label=label,rasterized=rasterized)
        _data_x = x[np.isfinite(x)]
        _data_y = y[np.isfinite(y)]
        _new_data = True
        if xerr is not None or yerr is not None :
            ax.errorbar(x,y,marker=marker,xerr=xerr,yerr=yerr,fmt='none',capsize=0,ecolor=color)

    if text is not None :
        if labelcolor == 'k' and color is not None : labelcolor=color
        ax.text(text[0],text[1],text[2],transform=ax.transAxes,color=labelcolor)

    if draw : plt.draw()


def plotl(ax,x,y,xr=None,yr=None,color=None,xt=None,yt=None,draw=True,label=None,ls=None,semilogy=False,linewidth=1.,tit=None,nxtick=None,nytick=None,linestyle='-',alpha=None) :
    '''
    Plot connected points
    '''
    if ls is not None : linestyle = ls
    set_limits_ticks(ax,xr,yr,nxtick,nytick)
    if xt is not None : ax.set_xlabel(xt) 
    if yt is not None : ax.set_ylabel(yt)
    if tit is not None : ax.set_title(tit)
    if semilogy :
        line = ax.semilogy(x,y,color=color,label=label,linewidth=linewidth,linestyle=linestyle,alpha=alpha)
    else :
        line = ax.plot(x,y,color=color,label=label,linewidth=linewidth,linestyle=linestyle,alpha=alpha)
    if draw : plt.draw()
    return line
    
def ax(subplot=111) :
    '''
    Return axes object for a new figure and desired subplots

    Keyword args :

    subplot  : matplotlib subplot specification
    '''
    fig=plt.figure()
    return fig.add_subplot(subplot)

def multi(nx,ny,figsize=None,hspace=1,wspace=1,sharex=False,sharey=False,squeeze=True,xtickrot=None,brokenx=False,equal=False) :
    '''
    Returns figure and axes array for grid of nx by ny plots, suppressing appropriate axes if requested by hspace and wspace

    Args:
       nx : number of plots in horizontal direction
       ny : number of plots in vertical direction

    Keyword args:
       figsize  : specifies figure size
       hspace (float)  : space (0.-1.) between vertical plots (height). Defaults to 1
       wspace (float)  : space (0.-1.) between horizont plots (width). Defaults to 1
       sharex (bool)   : force subplots to have same x-axes. Defaults to False
       sharey (bool)   : force subplots to have same y-axes. Defaults to False
       equal (bool)    : If True, set_aspect to 'equal'. Defaults to False.
       squeeze (bool)  : if True (default), output Axes will have only as many dimenions as needed, if False
                  will always be 2D (even if 1x1)
       brokenx (bool)  : different axes in x-direction will not have ylabels, and can be used to
                  make plots with different segments of x limits, appearing like a plot
                  with broken axes. Defaults to False
    '''
    fig,ax = plt.subplots(ny,nx,figsize=figsize,sharex=sharex,sharey=sharey,squeeze=squeeze)
    fig.subplots_adjust(hspace=hspace,wspace=wspace)

    if (hspace < 0.01) & (ny>1):
        # if we are vertical stacking, turn off xticks for all except bottom
        if squeeze and nx == 1 :
            ticklabels = ax[0].get_xticklabels()
            for i in range(1,ny-1) : 
                ticklabels = ticklabels + ax[i].get_xticklabels()
        else :
            ticklabels = ax[0,0].get_xticklabels()
            for i in range(nx) :
                for j in range(0,ny-1) : 
                    ticklabels = ticklabels + ax[j,i].get_xticklabels()
        plt.setp(ticklabels, visible=False)

    if (wspace < 0.01) & (nx> 1):
        # if we are horizontal stacking, turn off yticks for all except left
        if squeeze and ny == 1 :
            ticklabels = ax[1].get_yticklabels()
            for i in range(2,nx) : 
                ticklabels = ticklabels + ax[i].get_yticklabels()
        else :
            ticklabels = ax[0,1].get_yticklabels()
            for i in range(1,nx) :
                for j in range(ny) : 
                    ticklabels = ticklabels + ax[j,i].get_yticklabels()
        plt.setp(ticklabels, visible=False)

    if brokenx & (nx>1) :
        for i in range(0,nx) :
          for j in range(0,ny) :
            if ny == 1 : tmpax=ax[i]
            else : tmpax=ax[j,i]
            if i > 0 : 
                tmpax.spines['left'].set_visible(False)
                tmpax.tick_params(labelleft=False,left=False)  # don't put tick labels at the top
            tmpax.spines['right'].set_visible(False)
            tmpax.spines['top'].set_visible(False)
            tmpax.tick_params(labeltop=False)  # don't put tick labels at the top
            d=0.02
            if i < nx-1 :
                tmpax.plot([1-d,1+d],[-d,d],transform=tmpax.transAxes,color='k',clip_on=False)
            if i > 0 :
                tmpax.plot([-d,+d],[-d,d],transform=tmpax.transAxes,color='k',clip_on=False)

    if xtickrot is not None :
      for i in range(nx) :
        for j in range(0,ny) : 
          if squeeze and nx == 1 and ny == 1:
              print('setting rotation')
              for tick in ax.get_xticklabels(): tick.set_rotation( xtickrot ) 
          elif squeeze and nx>1 and ny == 1:
              for tick in ax[i].get_xticklabels(): tick.set_rotation( xtickrot ) 
          elif squeeze and ny>1 and nx == 1:
              for tick in ax[j].get_xticklabels(): tick.set_rotation( xtickrot ) 
          else :
              for tick in ax[j,i].get_xticklabels(): tick.set_rotation( xtickrot ) 
      fig.subplots_adjust(bottom=0.2)

    if equal :
      for i in range(nx) :
        for j in range(0,ny) : 
          if squeeze and nx == 1 and ny == 1:
              ax.set_aspect('equal')
          elif squeeze and nx>1 and ny == 1:
              ax[i].set_aspect('equal')
          elif squeeze and ny>1 and nx == 1:
              ax[j].set_aspect('equal')
          else :
              ax[j,i].set_aspect('equal')
    return fig,ax


def close() :
    '''
    Close open plots windows
    '''
    plt.close('all')

class LassoManager(object):
    ''' Simple Lasso manager to allow user to lasso points and get indices

        Adapted from version from Google search on matplotlib lasso
    '''
    def __init__(self, ax, x, y):
        '''  Initialize manager with axes, x, and y data arrays
        '''
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.Nxy = len(x)

        self.xys=[]
        for i in range(len(x)) :
            self.xys.append((x[i],y[i]))
        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)

    def callback(self, verts):
        ''' Once a Lasso is marked with mouse, get points within the path
        '''
        p = path.Path(verts)
        self.ind = p.contains_points(self.xys)
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso

    def onpress(self, event):
        '''called on button_press_event, runs Lasso with callback
        '''
        if self.canvas.widgetlock.locked():
            return
        if event.inaxes is None:
            return
        self.lasso = Lasso(event.inaxes,
                           (event.xdata, event.ydata),
                           self.callback)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)


# bokeh for interactive HTML plots

from bokeh.plotting import figure, show, output_file, save
from bokeh.layouts import gridplot, row, column
from bokeh.models import TabPanel, Tabs, ColumnDataSource, LinearColorMapper, ColorBar, Range1d, HoverTool
from bokeh.models.widgets import DateRangeSlider, Slider, RangeSlider
from bokeh.models.callbacks import CustomJS

def bokeh_figure(width=600, height=600) :
    """ Return a bokeh figure
    """
    return figure(width=width, height=height)

def bokeh_multi(nx,ny,width=600,height=600,sharex=False,sharey=False,xlog=False,ylog=False,slider=None,tab=None) :
    """ Return 2D array of bokeh figures for input nx, ny
    """
    ax=[]
    if ylog : y_axis_type = 'log'
    else : y_axis_type = 'auto'
    if xlog : x_axis_type = 'log'
    else : x_axis_type = 'auto'

    TOOLTIPS = [
        ("(x,y)", "($x, $y)"),
    ]
    for iy in range(ny) :
        xax=[]
        for ix in range(nx) :
            if ix == 0 and iy == 0 :
                xax.append(figure(width=width,height=height,y_axis_type=y_axis_type,x_axis_type=x_axis_type,tooltips=TOOLTIPS))
                xr=xax[0].x_range
                yr=xax[0].y_range
            elif sharex and sharey:
                xax.append(figure(width=width,height=height,x_range=xr,y_range=yr,
                           y_axis_type=y_axis_type,x_axis_type=x_axis_type,tooltips=TOOLTIPS))
            elif sharex :
                xax.append(figure(width=width,height=height,x_range=xr,
                           y_axis_type=y_axis_type,x_axis_type=x_axis_type,tooltips=TOOLTIPS))
            elif sharey :
                xax.append(figure(width=width,height=height,y_range=yr,
                           y_axis_type=y_axis_type,x_axis_type=x_axis_type,tooltips=TOOLTIPS))
            else :
                xax.append(figure(width=width,height=height,y_axis_type=y_axis_type,x_axis_type=x_axis_type,tooltips=TOOLTIPS))

        ax.append(xax)

    if slider is not None :
        xax=[]
        for ix in range(nx) :
            xax.append(RangeSlider(title=slider[0], start=slider[1], end=slider[2],
                                   value=(slider[1],slider[2]), step=1, width=int(0.8*width)))
        ax.append(xax)

    ax=np.array(ax)
    return bokeh_grid(ax,tab=tab),ax

def bokeh_grid(grid,tab=None) :
    """ Return bokeh layout for input grid array
    """
    if len(grid) == 1 and len(grid[0]) == 1 :
        fig = grid[0][0]
    elif len(grid) == 1 :
        fig = row(grid[0])
    elif len(grid[0]) == 1  :
        fig = column(np.array(grid)[:,0].tolist())
    else :
        fig = gridplot(grid.tolist())

    if tab is not None : return TabPanel(child=fig, title=tab)
    else : return fig 

def bokeh_show(fig,tab=False,outfile=None) :
    """ Display or save bokeh plots
    """
    if outfile is not None :
        output_file(outfile)
        if tab :
            save(Tabs(tabs=fig))
        else :
            save(fig)
        return

    if tab :
        show(Tabs(tabs=fig))
    else :
        show(fig)
        
def bokeh_plotp(ax,x,y,err=None,yerr=None,xr=None,yr=None,zr=None,size=5,color='red',xt=None,yt=None,
                label=None,marker='o',edgecolor=None,title=None,hover=False) :
    """
    Plot points in bokeh plot
    """

    source= ColumnDataSource({'x':x,'y':y})
    if label is not None :
        if marker == 'o' : ax.circle('x','y',source=source,fill_color=color,size=size,legend_label=label,line_color=edgecolor)
        elif marker == 's' : ax.square('x','y',source=source,fill_color=color,size=size,legend_label=label)
    else :
        if marker == 'o' : ax.circle('x','y',source=source,fill_color=color,size=size,line_color=None)
        elif marker == 's' : ax.square('x','y',source=source,fill_color=color,size=size)
    if xt is not None :
        ax.xaxis.axis_label = xt
    if yt is not None :
        ax.yaxis.axis_label = yt
    if xr is not None :
        ax.x_range = Range1d(xr[0],xr[1])
    if yr is not None :
        ax.y_range = Range1d(yr[0],yr[1])
    if title is not None :
        ax.title.text = title
    if hover :
        hover = HoverTool(tooltips=[('Label', '@labels')]) 
        ax.add_tools(hover) 

def bokeh_plotl(ax,x,y,err=None,yerr=None,xr=None,yr=None,zr=None,size=5,color='red',xt=None,yt=None,label=None,title=None) :
    """
    Plot lines in bokeh plot
    """

    source= ColumnDataSource({'x':x,'y':y})
    if label is not None :
        ax.line('x','y',source=source,legend_label=label,line_color=color)
    else :
        ax.line('x','y',source=source,line_color=color)
    if xt is not None :
        ax.xaxis.axis_label = xt
    if yt is not None :
        ax.yaxis.axis_label = yt
    if xr is not None :
        ax.x_range = Range1d(xr[0],xr[1])
    if yr is not None :
        ax.y_range = Range1d(yr[0],yr[1])
    if title is not None :
        ax.title.text = title

def bokeh_plotc(ax,x,y,z,xerr=None,yerr=None,xr=None,yr=None,zr=None,size=5,cmap='Viridis256',colorbar=False,xt=None,yt=None,zt=None,
                label=None,linewidth=0,edgecolor=None,marker='o',draw=True,orientation='vertical',labelcolor='k',tit=None,
                nxtick=None,nytick=None,rasterized=None,alpha=None,title=None,slider=None,sliderdata=None) :
    """
    Plot points in bokeh plot, color-coded by z value
    """

    if sliderdata is None :
        source=ColumnDataSource({'x':x,'y':y,'z':z})
    else :
        source=ColumnDataSource({'x':x,'y':y,'z':z, 'range' : sliderdata})
        source2=ColumnDataSource({'x':x,'y':y,'z':z, 'range' : sliderdata})
    if zr is None : zr=[z.min(),z.max()]
    exp_cmap=LinearColorMapper(palette=cmap,low=zr[0],high=zr[1])
    if label is not None :
        ax.circle('x','y',source=source,fill_color={'field' : 'z', 'transform' : exp_cmap},size=size,legend_label=label,line_color=edgecolor)
    else :
        ax.circle('x','y',source=source,fill_color={'field' : 'z', 'transform' : exp_cmap},size=size,line_color=edgecolor)
    if xt is not None :
        ax.xaxis.axis_label = xt
    if yt is not None :
        ax.yaxis.axis_label = yt
    if xr is not None :
        try: ax.x_range = Range1d(xr[0],xr[1])
        except :ax.x_range = xr
    if yr is not None :
        try :ax.y_range = Range1d(yr[0],yr[1])
        except :ax.y_range = yr
    if title is not None :
        ax.title.text = title
    if colorbar :
        color_bar = ColorBar(color_mapper=exp_cmap, 
                     label_standoff=12, border_line_color=None, location=(0,0))
        if zt is not None :
            color_bar.title = zt
            color_bar.title_text_align = 'right'
        ax.add_layout(color_bar, 'right')

    if slider is not None :
        callback = CustomJS(args=dict(source=source, ref_source=source2), code="""
            // print out array of slider limits
            //console.log(cb_obj.value);
            const data = source.data;
            const ref = ref_source.data;
            //console.log(ref)

            const rangevar = ref['range']
            let ind = []
            rangevar.forEach((val,index) => {
              if ((val >= cb_obj.value[0]) && (val <= cb_obj.value[1])) {
                ind.push(index)
              }
            })
            //console.log(ind);

            let x = []
            let y = []
            let z = []
            let r = []
            ind.forEach((val,index) => {
              x.push(ref['x'][val]);
              y.push(ref['y'][val]);
              z.push(ref['z'][val]);
              r.push(ref['range'][val]);
            })
            console.log(x);

            data['x'] = x;
            data['y'] = y;
            data['z'] = z;
            data['range'] = r;
            source.change.emit()

            """)

        slider.js_on_change('value',callback)

