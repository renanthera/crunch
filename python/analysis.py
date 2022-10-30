from math import floor

def avg(l,o, p=None):
    if (p!=None):
        print(sorted(l))
    l = sorted(l[1:])[o:-1*o]
    s = 0
    for k in l:
        s += k
    return s / len(l)

def max(l):
    s = 0
    for k in l[1:]:
        if k > s: s = k
    return s

def min(l):
    s = 2**32
    for k in l[1:]:
        if k < s: s = k
    return s

def castS(t, r):
    m = floor(t/60)
    if (m<10):
        minutes = '0'+str(m)+':'
    else:
        minutes = str(m)+':'
    s = round((t - m * 60), r)
    if (s<10):
        seconds = '0'+str(s)
    else:
        seconds = str(s)
    while (len(seconds) < 3 + r):
        seconds += '0'
    return minutes + seconds

def castMS(t, r):
    return castS(t/1000, r)

def avgmaxmin(l, o, segmentStart, p=None):
    init = segmentStart
    deltas = []
    prevT = segmentStart
    for k in l:
        deltas.append(k['timestamp']-prevT)
        prevT = k['timestamp']
    av = avg(deltas,o)
    ma = max(deltas)
    mi = min(deltas)
    i = 0
    if (p == 2):
        for k in deltas:
            s = (l[i]['timestamp']-init)/1000
            t = ''
            if (k == mi): t += '------'
            if (k == ma): t += '++++++'
            if (i==0): print('0\t~\t',s)
            else:
                print(castS(s, 3), '', k, t, sep='\t')
            i += 1
    if (p == 1 or p == 2): print(round(av,3),ma,mi,len(l),sep='\t')
    return [deltas,av,ma,mi,len(l)]
