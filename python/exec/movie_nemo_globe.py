#!/usr/bin/env python

#       B a r a K u d a
#
#  Prepare 2D maps (monthly) that will later become a GIF animation!
#  NEMO output and observations needed
#
#    L. Brodeau, november 2016

import sys
import os
from string import replace
import numpy as nmp

from netCDF4 import Dataset

from mpl_toolkits.basemap import Basemap
#from mpl_toolkits.basemap import shiftgrid
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import warnings
warnings.filterwarnings("ignore")

import datetime

import barakuda_colmap as bcm

import barakuda_tool as bt

year_ref_ini = 1990

#jt0 = 248
jt0 = 0

#CTATM = 'T255'
CTATM = 'T1279'

cbox = 'Pac'

fig_type='png'

narg = len(sys.argv)
if narg < 4: print 'Usage: '+sys.argv[0]+' <file> <variable> <LSM_file>'; sys.exit(0)
cf_in = sys.argv[1] ; cv_in=sys.argv[2] ; cf_lsm=sys.argv[3]

# Ice:
#cv_ice  = 'siconc'
#cf_ice = replace(cf_in, 'grid_T', 'icemod')
#rmin_ice = 0.5
#cpal_ice = 'ncview_bw'
#vcont_ice = nmp.arange(rmin_ice, 1.05, 0.05)

if cv_in == 'socurl':
    cfield = 'CURL'
    tmin=-40. ;  tmax=40.   ;  dtemp = 5.
    cpal_fld = 'ncview_blue_red'    
    cunit = r'$^{\circ}C$'
    cb_jump = 2
    
if cv_in == 'sosstsst':
    cfield = 'SST'
    tmin=-2. ;  tmax=28.   ;  dtemp = 1.
    cpal_fld = 'ncview_nrl'    
    cunit = r'$^{\circ}C$'
    cb_jump = 2
    
elif cv_in == 'somxl010':
    cfield == 'MLD'
    tmin=50. ;  tmax=1500. ;  dtemp = 50.
    cpal_fld = 'viridis_r'
    

#bt.chck4f(cf_ice)

bt.chck4f(cf_in)
id_fld = Dataset(cf_in)
vtime = id_fld.variables['time_counter'][:]
id_fld.close()
Nt = len(vtime)

bt.chck4f(cf_lsm)
id_lsm = Dataset(cf_lsm)
XMSK  = id_lsm.variables['tmask'][0,0,:,:] ; # t, y, x
XLON  =  id_lsm.variables['glamf'][0,:,:] ; #LOLO for curl => F !!!
XLAT  =  id_lsm.variables['gphif'][0,:,:]
id_lsm.close()


[ nj , ni ] = nmp.shape(XMSK)

pmsk = nmp.ma.masked_where(XMSK[:,:] > 0.2, XMSK[:,:]*0.+40.)

idx_oce = nmp.where(XMSK[:,:] > 0.5)



params = { 'font.family':'Ubuntu',
           'font.size':       int(12),
           'legend.fontsize': int(12),
           'xtick.labelsize': int(12),
           'ytick.labelsize': int(12),
           'axes.labelsize':  int(12) }
mpl.rcParams.update(params)
cfont_clb   = { 'fontname':'Arial', 'fontweight':'normal', 'fontsize':13 }
cfont_title = { 'fontname':'Ubuntu Mono', 'fontweight':'normal', 'fontsize':18 }
cfont_mail  = { 'fontname':'Times New Roman', 'fontweight':'normal', 'fontstyle':'italic', 'fontsize':9, 'color':'0.5' }


# Colormaps for fields:
pal_fld = bcm.chose_colmap(cpal_fld)
norm_fld = colors.Normalize(vmin = tmin, vmax = tmax, clip = False)

#pal_ice = bcm.chose_colmap(cpal_ice)
#norm_ice = colors.Normalize(vmin = rmin_ice, vmax = 1, clip = False)

pal_lsm = bcm.chose_colmap('blk')
norm_lsm = colors.Normalize(vmin = 0., vmax = 1., clip = False)


print ''

rh = 7.5

for jt in range(jt0,Nt):

    ct = '%3.3i'%(jt+1)

    cd = str(datetime.datetime.strptime('1990 '+ct, '%Y %j'))
    cdate = cd[:10] ; print ' *** Date :', cdate

    cfig = 'figs/'+cv_in+'_NEMO'+'_d'+ct+'.'+fig_type    

    fig = plt.figure(num = 1, figsize=(rh,rh), dpi=None, facecolor='b', edgecolor='k')
    ax  = plt.axes([0.005, 0.005, 0.99, 0.99], axisbg = 'k')

    
    vc_fld = nmp.arange(tmin, tmax + dtemp, dtemp)


    print "\n *** Reading record #"+str(ct)+" of "+cv_in+" in "+cf_in
    id_fld = Dataset(cf_in)
    XFLD  = id_fld.variables[cv_in][jt,:,:] ; # t, y, x
    id_fld.close()
    print "  => done!"


    ### PROJ:
    #carte = Basemap(projection='ortho',lat_0=45,lon_0=-100,resolution='h')
    #carte = Basemap(projection='ortho',lat_0=0,lon_0=-165,resolution='h')


    rstart = 0
    rot = (rstart + 0.5*float(jt))%360.
    rot = -rot

    print ' *** reference longitude =', rot

    #carte = Basemap(projection='ortho',lat_0=30.,lon_0=rot,resolution='h')
    carte = Basemap(projection='ortho',lat_0=15.,lon_0=rot,resolution='h')
    
    x0,y0 = carte(XLON,XLAT)
    
    print ' *** Ploting on map...'
    cf = carte.pcolor(x0, y0, XFLD, cmap=pal_fld, norm=norm_fld)

    #cf.set_axis_bgcolor('red')
    #fig.patch.set_facecolor('blue')
    
    print ' *** Saving figure...'
    plt.savefig(cfig, dpi=160, orientation='portrait', transparent=True)
    print '  => '+cfig+' created!\n'
    plt.close(1)

    del XFLD, cf


