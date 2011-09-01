#!/usr/bin/env python
#
# statmac!
# Let's record everything evar.

import json # data format
import readline # completion, history
import sys # exit binary
import os # get home and columns
import datetime # current date and formatting
import struct # binary struct
import fcntl # ioctl syscalls yay
import termios # get some window size
import cmdtree # get some tree action!

STAT_FILE = str(os.environ.get('HOME', '/Users/jmickey')) + '/stat.json'

def writetree(res_dict):
    right_now = datetime.datetime.utcnow().strftime('%s')
    res_dict['ctime'] = right_now
    res_dict['mtime'] = right_now
    res_dict['utime'] = ''
    json_str = json.dumps(res_dict, sort_keys=True, separators=(',',':'))
    json_str = json_str.strip() + '\n'
    with open(STAT_FILE, 'a+') as sf:
        sf.write(json_str)
    print json_str.strip()

def get_term_size():
    """
    returns (lines:int, cols:int)
    """
    def ioctl_GWINSZ(fd):
        return struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
    try:
        return tuple(int(os.getenv(var)) for var in ("LINES", "COLUMNS"))
    except:
        pass
    for fd in (0, 1, 2):
        try:
            return ioctl_GWINSZ(fd)
        except:
            pass
    try:
        fd = os.open(os.ctermid(), os.O_RDONLY)
        try:
            return ioctl_GWINSZ(fd)
        finally:
            os.close(fd)
    except:
        pass
    try:
        return tuple(int(x) for x in os.popen("stty size", "r").read().split())
    except:
        pass
    return (25, 80)

def load_food_locs():
    return ['out bayhill vietnamese',
            'out bayhill bigmouth',
            'out bayhill chinese',
            'out bayhill grillades',
            'out bayhill mollie greens',
            'out sb mph',
            'out sb mrpickles',
            'out sb tsb',
            'out sb alibabas',
            'out sf tacoloco',
            'out sf cancun',
            'out sf',
            'in work',
            'in home',
           ]

def load_drink_types():
    return ['alcohol',
            'caffiene',
            'water',
            'other',
           ]

def load_drink_names():
    return ['water',
            'coke',
            'coffee',
            'beer',
            'wine',
            'bourbon',
           ]

def _add_children(ct):
    next_ct = cmdtree.CommandTree('body', 'Describe your physical self!')
    next_ct.add_child(cmdtree.CommandTree('weight', parse=float))
    next_ct.add_child(cmdtree.CommandTree('hips', parse=float))
    next_ct.add_child(cmdtree.CommandTree('waist', parse=float))
    next_ct.add_child(cmdtree.CommandTree('chest', parse=float))
    ct.add_child(next_ct)
    next_ct = cmdtree.CommandTree('note', 'Let\'s write some stuff!')
    next_ct.add_child(cmdtree.CommandTree('text', parse=str))
    next_ct.add_child(cmdtree.CommandTree('title', parse=str))
    ct.add_child(next_ct)
    next_ct = cmdtree.CommandTree('drink', 'What have you been drinking!?')
    next_ct.add_child(cmdtree.CommandTree('type', parse=str, completions=load_drink_types()))
    next_ct.add_child(cmdtree.CommandTree('name', parse=str, completions=load_drink_names()))
    ct.add_child(next_ct)
    next_ct = cmdtree.CommandTree('work', 'What are you doing at work!?')
    next_ct.add_child(cmdtree.CommandTree('arrival', parse=str))
    next_ct.add_child(cmdtree.CommandTree('departure', parse=str))
    next_ct.add_child(cmdtree.CommandTree('lunch_start', parse=str))
    next_ct.add_child(cmdtree.CommandTree('lunch_end', parse=str))
    ct.add_child(next_ct)
    next_ct = cmdtree.CommandTree('food', 'What are you eating?')
    next_ct.add_child(cmdtree.CommandTree('content', parse=str))
    next_ct.add_child(cmdtree.CommandTree('locations', parse=str, completions=load_food_locs()))
    ct.add_child(next_ct)
    
def _run():
    (termlines, termwidth) = get_term_size()

    header = '---[ statmac ]'
    datestr = datetime.datetime.now().strftime('[ %Y.%m.%d : %H:%M ]-')
    midwidth = termwidth - (len(header) + len(datestr))
    print header + ('-' * midwidth) + datestr
    ct = cmdtree.CommandTree('statmac')
    _add_children(ct)
    ct.runtree()
    agg = ct.aggregate()
    if agg:
        writetree(agg)
if __name__ == '__main__':
    _run()
