
SELECT 
cast(str([Month])+'-'+str([Date])+'-'+str([Year]) as date) as [Date],
[Corporate Entity],
[Pipeline Name],
[Key Point],
[Direction of Flow],
[Trade Type],
'Natural Gas' as [Product],
[Capacity (1000 m3/d)],
--[Throughput (GJ/d)],
[Throughput (1000 m3/d)]
FROM [EnergyData].[dbo].[Pipelines_Gas]
where cast(str([Month])+'-'+str([Date])+'-'+str([Year]) as date) >= '2015-01-01'
order by [Corporate Entity],[Pipeline Name],[Key Point],[Date]