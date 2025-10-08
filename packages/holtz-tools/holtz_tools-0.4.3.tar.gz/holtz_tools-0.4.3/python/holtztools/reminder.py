#!/home/local/Anaconda3-2020.02/envs/py3.9/bin/python

from datetime import datetime
import subprocess
import pdb
import copy
import argparse
import numpy as np
from argparse import RawTextHelpFormatter

def send(tsvfile,ndays=7,broadcast=None,individual=False,domain='nmsu.edu',
             header='astro-ph this week:') :
    """ Go through tsvfile and send mail if day is within ndays from today
        Currently hardwired to send columns 1, 2, and 4

        tsvfile (str) : file to read date (1st column, format includes Month 
                         and ends with day, e.g.  Thursday, May 10), plus
                         other columns to include in reminder 
        ndays (int) : send message if date is within ndays from today
        broadcast (str) : if not None, send message to this address
        individual (bool) : if True, send to address in column 3
        header (str) : string to prepend before spreadsheet line(s)
    """

    print('ndays: ', ndays)
    print('broadcast: ', broadcast)
    print('individual: ', individual)

    # setup for dates, get current day number
    months=['Jan','Feb','Mar','Apr','May','Jun',
            'Jul','Aug','Sep','Oct','Nov','Dec']
    daynow=datetime.now().timetuple().tm_yday

    # start to construct the email message
    fout=open('message','w')
    for h in header.split('\\n') :
        fout.write(h+'\n')

    # read through the file, getting event dates
    m=0
    oldout=''
    fp=open(tsvfile)
    # get year from 1st column of 2nd line
    line=fp.readline()
    line=fp.readline()
    year=int(line.split('\t')[0])
    send = False
    indiv = []
    for line in fp:
        date=line.split('\t')[0]
        for imonth,month in enumerate(months) :
            if month in date : 
                m = imonth+1
                d=date.split(' ')[-1]
        if m < 1 : continue

        # get day number of event
        date=datetime(year=year,month=m,day=int(d))
        dayno=date.timetuple().tm_yday
        if dayno < daynow : continue
  
        # if event is within ndays from now, add event to message 
        if dayno-daynow < ndays and oldout != None: 
            out=line.split('\t')
            if len(out[0]) == 0 : out[0] = oldout[0]
            if out[1] != '' : 
                fout.write('  {:<24s} {:10s} {:s}\n'.format(out[0],out[1],out[3]))
                send = True
            oldout=copy.copy(out)
            if individual : indiv.append(out[2])

    fout.close()

    # send message to requested recipients
    if send :
        if individual :
            for i in indiv :
                if len(i) == 0 : continue
                j=np.char.find(i,'@')
                if j < 0 : i+='@'+domain
                fin = open('message')
                subprocess.run(['mail','-s','astroph reminder',i],
                               stdin=fin)
                fin.close()
                print('mail sent to: ', i)

        if broadcast != None :
            j=np.char.find(broadcast,'@')
            if j < 0 : broadcast+='@'+domain
            fin = open('message')
            subprocess.run(['mail','-s','astroph reminder',broadcast],
                           stdin=fin)
            fin.close()
            print('mail sent to: ', broadcast)
