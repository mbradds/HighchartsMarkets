SELECT 
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date],
[Corporate Entity]+' - '+[Pipeline Name]+' - '+[Key Point] as [Point],
round(avg([Throughput (1000 m3/d)]),1) as [Throughput (1000 m3/d)]
FROM [EnergyData].[dbo].[Pipelines_Gas]
where 
([Year] >= '2010') and
([Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or
([Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or
([Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or
([Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line')
group by [Year], [Month], [Corporate Entity], [Pipeline Name], [Key Point], [Trade Type]
order by [Corporate Entity],[Pipeline Name],[Key Point],cast(str([Month])+'-'+'1'+'-'+str([Year]) as date)