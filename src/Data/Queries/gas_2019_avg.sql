
SELECT 
[Year],
[Corporate Entity],
[Pipeline Name],
[Key Point],
[Trade Type],
round(avg([Capacity (1000 m3/d)]),2) as [Capacity (1000 m3/d)],
round(avg([Throughput (1000 m3/d)]),2) as [Throughput (1000 m3/d)] 
FROM [EnergyData].[dbo].[Pipelines_Gas]

where
([Year] = 2019 and [Corporate Entity] = 'NOVA Gas Transmission Ltd. (NGTL)' and [Key Point] = 'Upstream of James River') or
([Year] = 2019 and [Corporate Entity] = 'NOVA Gas Transmission Ltd. (NGTL)' and [Key Point] = 'West Gate') or
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Prairies') or
([Year] = 2019 and [Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Huntingdon Export') or 
([Year] = 2019 and [Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Niagara') or
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Iroquois') 

group by [Year],[Corporate Entity],[Pipeline Name],[Key Point],[Trade Type]

select 
[Corporate Entity],
[Key Point]
from [EnergyData].[dbo].[Pipelines_Gas]
group by [Corporate Entity],[Key Point]
order by [Corporate Entity]