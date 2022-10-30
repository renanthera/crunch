from math import trunc

def eventA(current, previous, opt):
    out = {}
    out['pool'] = previous['pool'] + current['amountA']
    out['damageStaggered'] = previous['damageStaggered'] + current['amountA']
    out['tick'] = out['pool'] / opt['ticks']
    return out

def eventP(current, previous, opt):
    out = {}
    if (opt['t29']): purification = opt['purification'] + previous['stack'] * 0.03
    out['pool'] = previous['pool'] * (1 - purification)
    out['tick'] = previous['tick'] * (1 - purification)
    return out

def eventT(current, previous, opt):
    out = {}
    out['pool'] = previous['pool'] - previous['tick']
    out['tickDamageTaken'] = previous['tickDamageTaken'] + previous['tick']
    if (opt['dcheck']):
        out['delta'] = current['amountT'] - trunc(previous['tick'])
        if (abs(out['delta']) > 1): return 'reorder'
        out['e'] = previous['e'] + out['delta']
    return out

def eventS(current, previous, opt):
    out = {}
    if (current['type'] == 'applybuff'): out['stack'] = 1
    if (current['type'] == 'removebuff'): out['stack'] = 0
    if (current['type'] == 'applybuffstack' and previous['stack'] < 4): out['stack'] = previous['stack'] + 1
    return out

def mergeEvent(new, current, previous):
    out = {}
    blacklist = ['type']
    for k in previous:
        if (k not in blacklist):
            out[k] = previous[k]
    for k in current:
        if (k not in blacklist):
            out[k] = current[k]
    for k in new:
        if (k not in blacklist):
            out[k] = new[k]
    return out

def staggerFabrication(s, opt={'ticks':26,'purification':0.5,'t29':True,'dcheck':True}, p=None):
    initial = {'pool':0,'tick':0,'stack':0,'tickDamageTaken':0,'damageStaggered':0}
    if (opt['dcheck']): initial = initial | {'e':0}
    s.insert(0,initial)
    out = [initial]

    i = 1
    while True:
        match s[i]['event']:
            case 'a': mutate = eventA(s[i],out[i-1],opt)
            case 'p': mutate = eventP(s[i],out[i-1],opt)
            case 't': mutate = eventT(s[i],out[i-1],opt)
            case 's': mutate = eventS(s[i],out[i-1],opt)
        if (mutate != 'reorder'):
            out.append(mergeEvent(mutate,s[i],out[i-1]))
        if (mutate == 'reorder'):
            s[i], s[i-1] = s[i-1], s[i]
            i -= 1
            out.pop()
            continue
        i += 1
        if (i >= len(s)): break
    s.pop(0)
    out.pop(0)
    if (p == 2):
        print(tabulate(out,headers='keys'))
    if (p >= 1):
        print('Purification rate:',out[len(out)-1]['tickDamageTaken'],'/',out[len(out)-1]['damageStaggered'],'=>',1-out[len(out)-1]['tickDamageTaken']/out[len(out)-1]['damageStaggered'])
    return out
