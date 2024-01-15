from .query import GQL_ENUM, GQL_OBJECT

class GQL_ENUM_CharacterRankingMetricType( GQL_ENUM ):
  allowed = [
    'bosscdps',
    'bossdps',
    'bossndps',
    'bossrdps',
    'default',
    'dps',
    'hps',
    'krsi',
    'playerscore',
    'playerspeed',
    'cdps',
    'ndps',
    'rdps',
    'tankhps',
    'wdps',
    'healercombineddps',
    'healercombinedbossdps',
    'healercombinedcdps',
    'healercombinedbosscdps',
    'healercombinedndps',
    'healercombinedbossndps',
    'healercombinedrdps',
    'healercombinedbossrdps',
    'tankcombineddps',
    'tankcombinedbossdps',
    'tankcombinedcdps',
    'tankcombinedbosscdps',
    'tankcombinedndps',
    'tankcombinedbossndps',
    'tankcombinedrdps',
    'tankcombinedbossrdps ',
  ]

class GQL_ENUM_EventDataType( GQL_ENUM ):
  allowed = [
    'All',
    'Buffs',
    'Casts',
    'CombatantInfo',
    'DamageDone',
    'DamageTaken',
    'Deaths',
    'Debuffs',
    'Dispels',
    'Healing',
    'Interrupts',
    'Resources',
    'Summons',
    'Threat ',
  ]

class GQL_ENUM_ExternalBuffRankFilter( GQL_ENUM ):
  allowed = [
    'Any',
    'Require',
    'Exclude'
  ]

class GQL_ENUM_FightRankingMetricType( GQL_ENUM ):
  allowed = [
    'default',
    'execution',
    'feats',
    'score',
    'speed',
    'progress',
  ]

class GQL_ENUM_GraphDataType( GQL_ENUM ):
  allowed = [
    'Summary',
    'Buffs',
    'Casts',
    'DamageDone',
    'DamageTaken',
    'Deaths',
    'Debuffs',
    'Dispels',
    'Healing',
    'Interrupts',
    'Resources',
    'Summons',
    'Survivability',
    'Threat ',
  ]
