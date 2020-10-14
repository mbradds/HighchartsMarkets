SELECT 
[Year],
[Corporate Entity],
[Pipeline Name],
[Key Point],
[Trade Type],
case when [Trade Type] = 'import' then round(avg([Capacity (1000 m3/d)]),2)*-1 else round(avg([Capacity (1000 m3/d)]),2)
end as [Capacity],
case when [Trade Type] = 'import' then round(avg([Throughput (1000 m3/d)]),2)*-1 else round(avg([Throughput (1000 m3/d)]),2) 
end as [Throughput] 
FROM [EnergyData].[dbo].[Pipelines_Gas]
where
([Year] = 2019 and [Corporate Entity] = 'NOVA Gas Transmission Ltd. (NGTL)' and [Key Point] = 'Upstream of James River') or
([Year] = 2019 and [Corporate Entity] = 'NOVA Gas Transmission Ltd. (NGTL)' and [Key Point] = 'West Gate') or
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Prairies') or
([Year] = 2019 and [Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Huntingdon Export') or 
([Year] = 2019 and [Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Niagara' and [Trade Type] = 'import') or
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Chippawa' and [Trade Type] = 'import') 
group by [Year],[Corporate Entity],[Pipeline Name],[Key Point],[Trade Type]