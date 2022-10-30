from stagger import *
from wcl import *

# wcl.py conatins some magic values for access to v2 api and local filenames of client secrets

# the code to automagically provide a new token if authentication fails currently doesn't work. running just getToken() once will provide you a new one, and the rest of the script now works

reportCode = 'RL1v2DbxckJ9dTWq'
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

s = []
print(absorbTicks[0])
for k in absorbTicks:
    s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'amountA':k['amount'],'event':'a'})

print(purificationCasts[0])
for k in purificationCasts:
    s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'event':'p'})

print(damageTicks[0])
for k in damageTicks:
    s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'amountT':k['unmitigatedAmount'],'event':'t'})

print(brewmasterRhythm[0])
for k in brewmasterRhythm:
    s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'type':k['type'],'event':'s'})

s = sorted(s, key=lambda x: x['timestamp'])

bnw = staggerFabrication(s, p=1)
opt = {'ticks':20,'purification':0.5,'t29':True,'dcheck':False}
base = staggerFabrication(s, opt, p=1)

pointsSpent()
