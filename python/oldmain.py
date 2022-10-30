from wcl import *
from analysis import *
from staggerModeling import *
from math import trunc
import numpy as np

# wcl.py conatins some magic values for access to v2 api and local filenames of client secrets

# grimtotem ptr testing
reportCode = 'Q7LNwTajrJ6cdDz9'
#reportCode = 'XnxCGyHkzrbDqaZ8'
# random leaderboard log
#reportCode = 'nVRJAMDpGhfB1v92'

#reportCode = 'W7bnFcZCNK3YpRX4'
reportCode = 'RL1v2DbxckJ9dTWq'
encounterIDBlacklist = [0]
encounterIDBlacklist = []

segmentList = getSegments(reportCode, encounterIDBlacklist, 1)
segmentSelection = int(input('Enter segment selection: '))
print()
startTime = segmentList[segmentSelection][4]
endTime = segmentList[segmentSelection][5]

playerList = getPlayers(reportCode, startTime, endTime, 1)
playerSelection = int(input('Enter player selection: '))
id = str(playerSelection)
if (type(playerSelection) == type([])):
    if (type(playerSelection[0]) == type([])):
        id = str(playerList[playerSelection][1])

# stagger absorb events
abilityID = '115069'
dataType = 'Healing'
fields = ['data','reportData','report','events','data']
eventSlice = completeEvent(startTime, endTime, id, abilityID, dataType)
absorbTicks = returnQuery(reportCode, eventSlice, fields)

# purification casts
abilityID = '119582'
dataType = 'Casts'
fields = ['data','reportData','report','events','data']
eventSlice = completeEvent(startTime, endTime, id, abilityID, dataType)
purificationCasts = returnQuery(reportCode, eventSlice, fields)

# stagger damage tick events
abilityID = '124255'
dataType = 'DamageTaken'
fields = ['data','reportData','report','events','data']
eventSlice = completeEvent(startTime, endTime, id, abilityID, dataType)
damageTicks = returnQuery(reportCode, eventSlice, fields)

# brewmaster's rhythm
abilityID = '394797'
dataType = 'Buffs'
fields = ['data','reportData','report','events','data']
eventSlice = completeEvent(startTime, endTime, id, abilityID, dataType)
brewmasterRhythm = returnQuery(reportCode, eventSlice, fields)

s1 = []
for k in absorbTicks:
    s1.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'amountA':k['amount'],'event':'a'})

for k in purificationCasts:
    s1.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'event':'p'})

for k in damageTicks:
    s1.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'amountT':k['unmitigatedAmount'],'event':'t'})

c = 0
for k in brewmasterRhythm:
    s1.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'type':k['type'],'event':'s'})

s1 = sorted(s1, key=lambda x: x['timestamp'])

# d must be populated with:
# amount (a, t)
# stack (p)
# type (s)

# r must be populated with:
# pool (a, p, t)
# tick (p, t)
# tickDamageTaken (t)
# damageStaggered (a)
# e (t)

def eventA(d, r, opt):
    d['pool'] = r['pool'] + d['amountA']
    d['damageStaggered'] = r['damageStaggered'] + d['amountA']
    d['tick'] = d['pool'] / opt['ticks']
    print(d['tick'])
    return d

def eventP(d, r, opt):
    if (opt['t29']): purification = opt['purification'] + d['stack'] * 0.03
    d['pool'] = r['pool'] * (1 - purification)
    d['tick'] = r['tick'] * (1 - purification)
    return d

def eventT(d, r, opt):
    d['pool'] = r['pool'] - r['tick']
    d['tickDamageTaken'] = r['tickDamageTaken'] + r['tick']
    if (opt['dcheck']):
        d['delta'] = d['amountT'] - trunc(r['tick'])
        if (abs(d['delta']) > 1): return 'reorder'
        d['e'] = r['e'] + d['delta']
    return d

def eventS(d, r, opt):
    if (d['type'] == 'applybuff'): d['stack'] = 1
    if (d['type'] == 'removebuff'): d['stack'] = 0
    if (d['type'] == 'applybuffstack' and r['stack'] < 4): d['stack'] = r['stack'] + 1
    return d

def completeEvent(d, r):
    blacklist = ['type','amountA','amountT']
    for k in r:
        if (k not in d and k not in blacklist):
            d[k] = r[k]


def staggerFabrication(s, opt={'ticks':26,'purification':0.5,'t29':True,'dcheck':True}, p=None):
    initial = {'pool':0,'tick':0,'stack':0,'tickDamageTaken':0,'damageStaggered':0}
    if (opt['dcheck']): initial = initial | {'e':0}
    s.insert(0,initial)

    i = 1
    while True:
#        print('relevant events:')
#        print(i-1,s[i-1])
#        print(i,s[i])
        match s[i]['event']:
            case 'a': mutate = eventA(s[i],s[i-1],opt)
            case 'p':
                s[i]['stack'] = s[i-1]['stack']
                mutate = eventP(s[i],s[i-1],opt)
            case 't': mutate = eventT(s[i],s[i-1],opt)
            case 's': mutate = eventS(s[i],s[i-1],opt)
#        print('m',mutate)
        if (mutate != 'reorder'):
            completeEvent(s[i],s[i-1])
        if (mutate == 'reorder'):
            s[i], s[i-1] = s[i-1], s[i]
            i -= 2
#        print(s[i])
#        print()
        i += 1
        if (i >= len(s)): break
    s.pop(0)
    if (p == 2):
        print(tabulate(s,headers='keys'))
    if (p >= 1):
        print(s[len(s)-1])
    return s

#def staggerFabrication(s, opt={'ticks':26,'purification':0.5,'t29':True,'dcheck':True}, p=None):
#    ticks = opt['ticks']
#    purification = opt['purification']
#    pool = 0
#    tick = 0
#    stack = 0
#    tickDamageTaken = 0
#    damageStaggered = 0
#    e = 0
#
#    i = 0
#    while True:
#        k = s[i]
#        if (k['event'] == 'a'):
#            pool += k['amount']
#            damageStaggered += k['amount']
#            tick = pool / ticks
#            k['pool'] = trunc(pool)
#            k['tick'] = tick
#            k['stack'] = stack
#            k['tickDamageTaken'] = tickDamageTaken
#            k['damageStaggered'] = damageStaggered
#            if (opt['dcheck']):
#                k['e'] = e
#        if (k['event'] == 'p'):
#            pb = purification
#            if (opt['t29']): pb += stack * 0.03
#            pool *= 1 - pb
#            tick *= 1 - pb
#            k['pool'] = trunc(pool)
#            k['tick'] = tick
#            k['stack'] = stack
#            k['tickDamageTaken'] = tickDamageTaken
#            k['damageStaggered'] = damageStaggered
#            if (opt['dcheck']):
#                k['e'] = e
#        if (k['event'] == 't'):
#            delta = k['amount'] - trunc(tick)
#            pool -= tick
#            tickDamageTaken += tick
#            if (opt['dcheck']):
#                k['delta'] = k['amount'] - trunc(tick)
#                e += delta
#                k['e'] = e
#            k['pool'] = trunc(pool)
#            k['tick'] = tick
#            k['stack'] = stack
#            k['tickDamageTaken'] = tickDamageTaken
#            k['damageStaggered'] = damageStaggered
#            if (abs(delta) > 1 and opt['dcheck']):
#                s[i], s[i-1] = s[i-1], s[i]
#                i -= 1
#                pool = s[i-1]['pool']
#                tick = s[i-1]['tick']
#                stack = s[i-1]['stack']
#                tickDamageTaken = s[i-1]['tickDamageTaken']
#                damageStaggered = s[i-1]['damageStaggered']
#                e = s[i-1]['e']
#                continue
#        if (k['event'] == 's'):
#            stack = k['stackCount']
#            k['pool'] = trunc(pool)
#            k['tick'] = tick
#            k['stack'] = stack
#            k['tickDamageTaken'] = tickDamageTaken
#            k['damageStaggered'] = damageStaggered
#            if (opt['dcheck']):
#                k['e'] = e
#        i += 1
#        if (i == len(s) or i < 0): break
#    if (p == 2):
#        print(tabulate(s,headers='keys'))
#    if (p >= 1):
#        print(tickDamageTaken,'/',damageStaggered,' : ',1-tickDamageTaken/damageStaggered,'-----------',end=' ')
#        if (opt['dcheck']): print(e)
#        else: print(0)
#    return 0

#for k in s:
#    print(k)
s2 = s1.copy()
bnw = staggerFabrication(s1, p=1)
opt = {'ticks':20,'purification':0.5,'t29':True,'dcheck':False}
base = staggerFabrication(s2, opt, p=1)

for k in range(len(bnw)-1):
    print(k,bnw[k]['tick'],base[k]['tick'],bnw[k]['tickDamageTaken'],base[k]['tickDamageTaken'])



#tickSizes, ticklessMatrix = genTicklessMatrix(absorbTicks, purificationCasts)
#purifiesAdded = partTwoElectricBoogaloo(ticklessMatrix, startTime)
#print()
#tickSizeSummation(purifiesAdded, tickSizes)


# old stuff

#fabricatedStaggerTickless = ticklessFabricateStaggerP(absorbTicks, purificationCasts)
#print(ticklessFabricateStagger(absorbTicks))
#print(ticklessMatrix)
#printTicklessMatrixDict(purifiesAdded)
#fabricatedStaggerTickedFromTickless = ticklessToTicked(fabricatedStaggerTickless)
#print(len(fabricatedStaggerTickedFromTickless))

#fabricateStagger(absorbTicks, startTime)
#avgmaxmin(absorbTicks, 2, int(startTime), 2)




#fabricatedStaggerTickedFromTicklessGivenTicks = ticklessToGivenTicks(fabricatedStaggerTickless, damageTicks)
#print(len(fabricatedStaggerTickedFromTicklessGivenTicks))
#for k in range(len(fabricatedStaggerTickedFromTicklessGivenTicks)):
#    if (len(fabricatedStaggerTickedFromTickless) > k):
#        print(fabricatedStaggerTickedFromTickless[k],end='\t')
#    else:
#        print(end='\t')
#    print(fabricatedStaggerTickedFromTicklessGivenTicks[k])


#avgmaxmin(damageTicks, 2, int(startTime), 1)

#print('','av','max','min','ct',sep='\t')
#print('damage',end='\t')
#damanal = avgmaxmin(damageTicks, 2, int(startTime), None)
#print('absorb',end='\t')

#print('\t\t\t'+str(len(absorbTicks)))

pointsSpent()
