select [Date],
[Alliance Pipeline Limited Partnership - Alliance Pipeline - Border],
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Kingsgate],
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Monchy],
[TransCanada PipeLines Limited - Canadian Mainline - Northern Ontario Line],
[Capacity (1000 m3/d)] as [Capacity]
from
(
SELECT 
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date],
[Corporate Entity]+' - '+[Pipeline Name]+' - '+[Key Point] as [Point],
round(avg([Throughput (1000 m3/d)]),1) as [value]
FROM [EnergyData].[dbo].[Pipelines_Gas]
where 
([Year] >= '2010') and
([Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or
([Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or
([Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or
([Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line')
group by [Year], [Month], [Corporate Entity], [Pipeline Name], [Key Point], [Trade Type]
--order by [Corporate Entity],[Pipeline Name],[Key Point],cast(str([Month])+'-'+'1'+'-'+str([Year]) as date)
union all
select 
[Date],
'Capacity (1000 m3/d)' as [Point],
sum([Capacity (1000 m3/d)]) as [value]
from
(
SELECT 
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date],
[Corporate Entity],[Pipeline Name], [Key Point],
round(avg([Capacity (1000 m3/d)]),1) as [Capacity (1000 m3/d)]
FROM [EnergyData].[dbo].[Pipelines_Gas]
where
[Year] >= '2015' and
([Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or
([Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or
([Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or
([Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line') 
group by [Year],[Month],[Corporate Entity],[Pipeline Name], [Key Point]
) as gas_cap
group by [Date]
) as SourceTable
pivot
(
avg([value])
for Point in ([Alliance Pipeline Limited Partnership - Alliance Pipeline - Border],
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Kingsgate],
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Monchy],
[TransCanada PipeLines Limited - Canadian Mainline - Northern Ontario Line],
[Capacity (1000 m3/d)])
) as PivotTable
where year([Date]) >= '2015'
order by [Date]