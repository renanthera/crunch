I have several samples for all of the different behaviour from this week. In every case, inspect the Brewmaster Monk named "Katebruwu"

Case 1: <https://www.warcraftlogs.com/reports/7xNnGhDMK19vtVYF#fight=1&source=20> (Incorrect accumulator, Valdrakken Cleave Target Dummies w/ other people)

Case 2: <https://www.warcraftlogs.com/reports/7xNnGhDMK19vtVYF#fight=6&source=20> (Correct accumulator, Turnip Punching Bag, Solo, No White Tiger Statue / Niuzao)

Case 3: <https://www.warcraftlogs.com/reports/7xNnGhDMK19vtVYF#fight=17&source=20> (Correct accumulator, Turnip Punching Bag, Solo, White Tiger Statue + Niuzao)



Throughout the following two logs (excerpts of the first were used in the listed cases), there are several other samples of this behaviour.

The impact varies, but I have not seen a case where I measure correct accumulator behaviour when fighting target dummies with other people also fighting them this week.

<https://www.warcraftlogs.com/reports/7xNnGhDMK19vtVYF>
<https://www.warcraftlogs.com/reports/4aJx3yLZnGVmtBWP>

Test methodology notes:
- Against each target dummy configuration:
- Perform standard rotation against the selected target dummies and press CB fairly frequently.
- Some tests were performed without Invoke Niuzao and White Tiger Statue to rule out non-player sources failing to be accumulated.

Measurement methodology notes:
- Code can be found at <https://github.com/renanthera/crunch/tree/python-v2/python>. I apologize in advance, a lot of this is pretty old and commits many crimes.
- This system was working excellently previous weeks, and it matches up in Case 2 and Case 3 perfectly.
- Using the WCL v2 API, acquire the following three queries given a `startTime`, `endTime`, `reportCode`, and `sourceID`. These examples are pre-filled for Case 1.
```
{reportData{report(code:"7xNnGhDMK19vtVYF"){events(dataType:DamageDone abilityID:425299 startTime:34 endTime:317258 useAbilityIDs:true sourceID:20){data nextPageTimestamp}}}}
{reportData{report(code:"7xNnGhDMK19vtVYF"){events(dataType:DamageDone abilityID:406764 startTime:34 endTime:317258 useAbilityIDs:true sourceID:20){data nextPageTimestamp}}}}
{reportData{report(code:"7xNnGhDMK19vtVYF"){events(dataType:Buffs abilityID:425965 startTime:34 endTime:317258 useAbilityIDs:true sourceID:20){data nextPageTimestamp}}}}
```
- Merge events into a single list sorted by timestamp.
- Iterate over the entries in our list.
- If the spell id is `425299`, increment accumulator (`amt`) by `unimitigatedAmount`. Technically not guaranteed to be correct against targets with magic DRs, but effective in this case to manage overkill. Previous weeks strongly suggested overkill is included in accumulator.
- If spell ID is `425965` and the `type` is `applybuff`, capture `absorb` for absorb mean tracking, and report `absorb` and accumulator (`amt`). Additionally computes some potentially useful ratios to divine what is occurring.
- Once every event is consumed, print average applied `absorb` just to make us cry.

Possible test issues:
- Cleave Dummy v Turnip behaviour could be different. Hard to control for unless I can somehow figure out what is causing it and reproduce it on a Turnip OR get a variety of specs to assist on a turnip.

Script output:

Case 1:
```
Absorb: 54085
Damage Dealt since last: 57983
Difference: 3898
Ratio: 0.9327733990997361
Inverse ratio: 1.072071738929463

Absorb: 209015
Damage Dealt since last: 223392
Difference: 14377
Ratio: 0.935642279043117
Inverse ratio: 1.0687845369949525

Absorb: 116825
Damage Dealt since last: 124862
Difference: 8037
Ratio: 0.9356329387643959
Inverse ratio: 1.068795206505457

Absorb: 86355
Damage Dealt since last: 92315
Difference: 5960
Ratio: 0.9354384444564805
Inverse ratio: 1.0690174280585953

Absorb: 103560
Damage Dealt since last: 110533
Difference: 6973
Ratio: 0.9369147675354872
Inverse ratio: 1.0673329470838162

Absorb: 78621
Damage Dealt since last: 83965
Difference: 5344
Ratio: 0.9363544333948669
Inverse ratio: 1.0679716615153712

Absorb: 52877
Damage Dealt since last: 56243
Difference: 3366
Ratio: 0.9401525523176217
Inverse ratio: 1.063657166631995

100191.14285714286
```

Case 2:
```
Absorb: 179955
Damage Dealt since last: 0
Difference: -179955

Absorb: 202956
Damage Dealt since last: 202957
Difference: 1
Ratio: 0.9999950728479432
Inverse ratio: 1.0000049271763338

Absorb: 69444
Damage Dealt since last: 69445
Difference: 1
Ratio: 0.9999856001151991
Inverse ratio: 1.0000144000921607

Absorb: 79246
Damage Dealt since last: 79247
Difference: 1
Ratio: 0.9999873812257877
Inverse ratio: 1.0000126189334477

Absorb: 78653
Damage Dealt since last: 78654
Difference: 1
Ratio: 0.999987286088438
Inverse ratio: 1.0000127140732076

Absorb: 104249
Damage Dealt since last: 104250
Difference: 1
Ratio: 0.9999904076738609
Inverse ratio: 1.0000095924181527

Absorb: 51946
Damage Dealt since last: 51947
Difference: 1
Ratio: 0.9999807496101796
Inverse ratio: 1.000019250760405

Absorb: 92667
Damage Dealt since last: 92667
Difference: 0
Ratio: 1.0
Inverse ratio: 1.0

107389.5
```

Case 3:
```Absorb: 25786
Damage Dealt since last: 25787
Difference: 1
Ratio: 0.9999612207701555
Inverse ratio: 1.0000387807337314

Absorb: 96588
Damage Dealt since last: 96589
Difference: 1
Ratio: 0.9999896468541967
Inverse ratio: 1.000010353252992

Absorb: 72945
Damage Dealt since last: 72945
Difference: 0
Ratio: 1.0
Inverse ratio: 1.0

Absorb: 57626
Damage Dealt since last: 57627
Difference: 1
Ratio: 0.9999826470230968
Inverse ratio: 1.0000173532780343

Absorb: 73737
Damage Dealt since last: 73738
Difference: 1
Ratio: 0.9999864384713445
Inverse ratio: 1.0000135617125732

Absorb: 103162
Damage Dealt since last: 103163
Difference: 1
Ratio: 0.9999903066021733
Inverse ratio: 1.0000096934917897

Absorb: 49395
Damage Dealt since last: 49395
Difference: 0
Ratio: 1.0
Inverse ratio: 1.0

Absorb: 115314
Damage Dealt since last: 115315
Difference: 1
Ratio: 0.9999913281012878
Inverse ratio: 1.0000086719739147

Absorb: 120042
Damage Dealt since last: 120384
Difference: 342
Ratio: 0.9971590909090909
Inverse ratio: 1.002849002849003

Absorb: 103568
Damage Dealt since last: 103228
Difference: -340
Ratio: 1.0032936800092997
Inverse ratio: 0.9967171327050827

81816.3
```
