SELECT 
cast(cast([Month] as varchar)+'-'+'1'+'-'+cast([Year] as varchar) as date) as [Date],
[Corporate Entity],
[Pipeline Name],
[Key Point],
[Direction of Flow],
[Trade Type],
'Natural Gas' as [Product],
round(avg([Capacity (1000 m3/d)]),1) as [Capacity (1000 m3/d)],
round(avg([Throughput (1000 m3/d)]),1) as [Throughput (1000 m3/d)] 
FROM [EnergyData].[dbo].[Pipelines_Gas]
where cast(str([Month])+'-'+str([Date])+'-'+str([Year]) as date) >= '2015-01-01'
group by [Year],[Month],[Corporate Entity],[Pipeline Name],[Key Point],[Direction of Flow], [Trade Type]
order by [Corporate Entity],[Pipeline Name],[Key Point],cast(cast([Month] as varchar)+'-'+'1'+'-'+cast([Year] as varchar) as date)