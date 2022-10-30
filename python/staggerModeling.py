
# YEAH WELL THIS IS ALL WRONG. CHECK OUT stagger.py FOR SOMETHING CORRECT. SOME INTERESTING VIZ IDEAS HERE, THOUGH.


from analysis import *

# constant-sized return object based on duration spent with stagger debuff * 2
# can be converted into a tickless model by scanning for the stagger tick
# immediately following an absorb event
def tickedFabricateStagger(d, startTime):
    a = [['t','stamp','amnt']]
    lastA = 2**32
    tickout = 13*1000
    interval = 500
    ticks = int(tickout/interval)
    h = [['t','stamp','amnt']]
    index = 1
    for k in d[:5]:
        timestamp = k['timestamp']-startTime
        amount = k['amount']
        i = [castMS(timestamp,3),timestamp,amount]
        a.append(i)
        c = 0
        for m in range(0,ticks-1):
            if (len(h) > index + m):
                if (h[index+m][1] >= timestamp):
                    index = index+m
                    break
        if (c == ticks-1):
            index += 1
        for m in range(0,ticks-1):
            tsize = amount / ticks
            if (len(h) > m+index):
                h[m+index][2] += tsize
            else:
                tnext = timestamp+(m+1)*interval
                tpnext = castMS(tnext,3)
                h.append([tpnext, tnext, tsize])
        print(k)
    printTable(a)
    printTable(h)

# smallest subset of time purification-based dr can be estimated for is an
# entire stagger buff. per-event purification dr calculation cannot be done as
# it is impossible to know where stagger ticks would go without calculating
# their positions, which inherently causes it to no longer be tickless

# when damage events occur at less than one every 0.5s on average, this method
# produces a smaller returned object

# can be converted into a ticked model by filling all estimated stagger ticks
# as the previous absorb size until tickout has elapsed or an update occurs
def ticklessFabricateStagger(a, opt=None):
    if (opt==None):
        tickout = 13*1000
        interval = 500
    ticks = tickout/interval
    cursor = 0
    aM = []
    bM = []
    for k in a:
        aM.append(k['amount']/ticks)
        for l in range(cursor, len(aM)):
            if (k['timestamp']-a[l]['timestamp']<tickout):
                cursor = l
                break
        t = 0
        for l in range(cursor, len(aM)):
            t += aM[l]
        bM.append([k['timestamp'],t])
    return bM

def genTicklessMatrix(a, p, opt=None):
    # merge absorbs and purifies
    e = []
    aM = []
    for k in a:
        e.append({'timestamp':k['timestamp'],'type':'a','amount':k['amount']})
        aM.append(k['amount'])
    for k in p:
        e.append({'timestamp':k['timestamp'],'type':'p','amount':None})
    e = sorted(e,key=lambda x: x['timestamp'])
    # configure opts
    if (opt==None):
        tickout = 13*1000
        interval = 500
    ticks = tickout/interval
    cursor = 0
    bM = []
    i = 0
    # calculate interval of applicable events at event
    for k in e:
        for l in range(cursor, i):
            if (k['timestamp']-e[l]['timestamp']<tickout):
                cursor = l
                break
        if (k['type'] == 'a'):
            bM.append({'oldestA':cursor,'newestA':i,**k})
        else:
            bM.append({'oldestA':cursor,'newestA':i-1,**k})
        if (k['type'] == 'a'):
            i += 1
    return aM, bM

def partTwoElectricBoogaloo(b, startTime):
    o = []
    for k in b:
        t = [0] * k['oldestA']
        if (len(o) > 0):
            if (k['type'] == 'a'):
                t += o[len(o)-1]['row'][k['oldestA']:k['newestA']] + [1]
            else:
                #print(o[-1:][0]==o[len(o)-1],sep='\n')
                t += map(lambda x: x * 2, o[len(o)-1]['row'][k['oldestA']:k['newestA']] + [1])
        else:
            t += [1]
        t += [0] * (b[len(b)-1]['newestA'] - k['newestA'])
        o.append({'row':t,**k})
    return o
