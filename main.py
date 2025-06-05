import analyzers
import wcl

# analyzers.overwhelming_force.coefficient( [
#   # strongboi
#   'CvKQW1AdD42wmMz3',
#   'gWMFdXk2pnL4fcx6',
#   'hGd96NyZ8v7Hpw34',
#   'HG2xLYBJVyvDPK6t',
#   'F1mZrfCP4MqK7dHg',
#   'v7KBtzr4jhN3TgGk',
#   'WtgAvP9N2aTFQJmr',
#   # malmie
#   'DXfYn9xA3jCPdVwp',
#   '9v1FZtJQGMC7qx8m',
#   '7JxTBf2DPKYht9vj',
#   '83bjtyX7ZzdWJ9HQ',
#   'CjTMhxdKwFgR7Pqc',
#   'X1WYaDcBvMrQmRpV',
#   'X7GzLdh8VB3q2MAb',
#   'ThpGywvM4BFcPx2b',
#   # dwarf
#   # 'QCyrLh7tG91B3TMP',
#   # 'PkrFRp28mXMwNTjJ',
#   # 'WT3VJ8dMknhAL7XB',
#   # 'NvPQc2YA1VnqkRMg'
# ] )

# analyzers.dual_threat.probability_at_count( [ 'gqyW1GPaYfX3mzKn' ] )

import json
params = {'id': 76827088, 'encounterID': 3009, 'difficulty': 5}
params = {'id': 76827088, 'encounterID': 3013, 'difficulty': 5}
params = {'id': 76827088, 'encounterID': 3015, 'difficulty': 5}
ranks = wcl.getRanksForFights(params)
codes = [parse.get("report", {}).get("code", "") for parse in ranks]

# analyzers.draw_boss_path.draw_path(codes, "The Geargrinder", params)
# analyzers.draw_boss_path.draw_path(codes, "Sprocketmonger Lockenstock", params)
analyzers.draw_boss_path.draw_path(codes, 229953, params)
