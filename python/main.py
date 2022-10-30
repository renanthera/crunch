from wcl import *
from caching import *

# wcl.py conatins some magic values for access to v2 api and local filenames of client secrets

# MANUAL
# enter warcraftlogs reportCode string as reportCode
# filter encounter selection gui with integer array of encounter ids
# construct basic queries that support caching.
# for more complicated queries, caching may not work. utilize the returnQuery method within wcl.py.
# process demonstrated in cachedReturnQuery of caching.py

reportCode = 'RL1v2DbxckJ9dTWq'
encounterIDBlacklist = []

startTime, endTime, id = executeMenus(reportCode, encounterIDBlacklist)

# stagger absorb events
abilityID = '115069'
dataType = 'Healing'
fields = ['data','reportData','report','events','data']
absorbTicks = cachedReturnQuery(reportCode, startTime, endTime, id, abilityID, dataType, fields)

# purification casts
abilityID = '119582'
dataType = 'Casts'
fields = ['data','reportData','report','events','data']
absorbTicks = cachedReturnQuery(reportCode, startTime, endTime, id, abilityID, dataType, fields)

# stagger damage tick events
abilityID = '124255'
dataType = 'DamageTaken'
fields = ['data','reportData','report','events','data']
absorbTicks = cachedReturnQuery(reportCode, startTime, endTime, id, abilityID, dataType, fields)

# brewmaster's rhythm
abilityID = '394797'
dataType = 'Buffs'
fields = ['data','reportData','report','events','data']
absorbTicks = cachedReturnQuery(reportCode, startTime, endTime, id, abilityID, dataType, fields)

# print api points spent to console (so you can see if you're an idiot)
pointsSpent()

# this will get removed once the c++ implementation is completed. exists as notes until then.

# s = []
# print(absorbTicks[0])
# for k in absorbTicks:
#     s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'amountA':k['amount'],'event':'a'})

# print(purificationCasts[0])
# for k in purificationCasts:
#     s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'event':'p'})

# print(damageTicks[0])
# for k in damageTicks:
#     s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'amountT':k['unmitigatedAmount'],'event':'t'})

# print(brewmasterRhythm[0])
# for k in brewmasterRhythm:
#     s.append({'timestamp':k['timestamp'],'niceTime':castMS(k['timestamp']-startTime, 3),'type':k['type'],'event':'s'})

# s = sorted(s, key=lambda x: x['timestamp'])

# bnw = staggerFabrication(s, p=1)
# opt = {'ticks':20,'purification':0.5,'t29':True,'dcheck':False}
# base = staggerFabrication(s, opt, p=1)
