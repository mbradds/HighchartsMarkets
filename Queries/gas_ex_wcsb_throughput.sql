SELECT 
--[Date],
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date],
--[Month],
--[Year],
[Corporate Entity],
[Pipeline Name],
[Key Point],
--[Trade Type],
--[Capacity (1000 m3/d)],
--[Throughput (GJ/d)],
round(avg([Throughput (1000 m3/d)]),1) as [Throughput (1000 m3/d)]
FROM [EnergyData].[dbo].[Pipelines_Gas]

where 
([Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or
([Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or
([Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy'))

group by [Month], [Year], [Corporate Entity], [Pipeline Name], [Key Point], [Trade Type]

order by [Corporate Entity],[Pipeline Name],[Key Point],cast(str([Month])+'-'+'1'+'-'+str([Year]) as date)