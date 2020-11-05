import pandas as pd
import json
import os
from connection import cer_connection
from datetime import date
from calendar import monthrange
import calendar
from dateutil.relativedelta import relativedelta
#TODO: add in the dataframe sorting before conversion to json

query_gas_traffic = "select [Date], \
[Alliance Pipeline Limited Partnership - Alliance Pipeline - Border] as [Alliance Pipeline - Border], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Kingsgate] as [Foothills System - Kingsgate], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Monchy] as [Foothills System - Monchy], \
[TransCanada PipeLines Limited - Canadian Mainline - Northern Ontario Line] as [TransCanada Mainline - Northern Ontario Line], \
[Capacity (1000 m3/d)] as [Capacity] \
from (SELECT \
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date], \
[Corporate Entity]+' - '+[Pipeline Name]+' - '+[Key Point] as [Point], \
round(avg(([Throughput (1000 m3/d)]/1000)),2) as [value] \
FROM [EnergyData].[dbo].[Pipelines_Gas] where \
([Year] >= '2015' and [Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or \
([Year] >= '2015' and [Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or \
([Year] >= '2015' and [Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or \
([Year] >= '2015' and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line') \
group by [Year], [Month], [Corporate Entity], [Pipeline Name], [Key Point], [Trade Type] \
union all \
select [Date], 'Capacity (1000 m3/d)' as [Point], round(sum([Capacity (1000 m3/d)]/1000),2) as [value] \
from (SELECT cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date],[Corporate Entity],[Pipeline Name], [Key Point], \
round(avg([Capacity (1000 m3/d)]),1) as [Capacity (1000 m3/d)] \
FROM [EnergyData].[dbo].[Pipelines_Gas] where \
([Year] >= '2015' and [Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or \
([Year] >= '2015' and [Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or \
([Year] >= '2015' and [Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or \
([Year] >= '2015' and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line') \
group by [Year],[Month],[Corporate Entity],[Pipeline Name], [Key Point] \
) as gas_cap group by [Date]) as SourceTable \
pivot (avg([value]) \
for Point in ([Alliance Pipeline Limited Partnership - Alliance Pipeline - Border], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Kingsgate], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Monchy], \
[TransCanada PipeLines Limited - Canadian Mainline - Northern Ontario Line], \
[Capacity (1000 m3/d)]) \
) as PivotTable order by [Date]"

query_rail_wcs = "select \
rail.Date, \
rail.Units, \
round(rail.Volume,1) as [Crude by Rail], \
round(wcs.[WCS Differential],1) as [WCS-WTI Differential] \
from ( \
SELECT \
[Date], \
[Volume], \
[Units] \
FROM [EnergyData].[dbo].[NEB_RailExports_Oil] \
where Units in ('bbl per day','m3 per day') \
) as rail left join ( \
SELECT \
year([SettlementDate]) as [Year], \
month([SettlementDate]) as [Month], \
round(avg([SettlementValue]),2)*-1 as [WCS Differential] \
FROM [EnergyData].[dbo].[Net_Energy_Spot] where Market = 'WCS' \
group by year([SettlementDate]),month([SettlementDate])) as wcs \
on year(rail.Date) = wcs.Year and month(rail.Date) = wcs.Month where year(rail.Date) >= 2015 \
order by rail.Units, rail.Date"

query_ne2 = "SELECT \
cast(str(month([SettlementDate]))+'-'+'1'+'-'+str(year([SettlementDate])) as date) as [Date],\
round(avg([SettlementPriceImplied]),1) as [WCS],\
round(avg([WTI Spot]),1) as [WTI]\
FROM [EnergyData].[dbo].[vw_net_energy_and_eia_prices]\
where Market = 'WCS' and year([SettlementDate]) >= 2015\
group by year([SettlementDate]), month([SettlementDate])\
order by cast(str(month([SettlementDate]))+'-'+'1'+'-'+str(year([SettlementDate])) as date)"

query_oil_throughcap = "select \
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date], \
[Corporate Entity], \
[Pipeline Name], \
[Key Point], \
[Direction of Flow], \
[Trade Type], \
Product, \
round([Throughput (1000 m3/d)],2) as [Throughput (1000 m3/d)], \
round([Available Capacity (1000 m3/d)],2) as [Available Capacity (1000 m3/d)] \
from ( \
SELECT \
throughput.[Month], \
throughput.[Year], \
throughput.[Corporate Entity], \
throughput.[Pipeline Name], \
throughput.[Key Point], \
[Direction of Flow], \
[Trade Type], \
[Product], \
[Throughput (1000 m3/d)], \
capacity.[Available Capacity (1000 m3/d)] \
FROM [EnergyData].[dbo].[Pipelines_Throughput_Oil] as throughput \
left join [EnergyData].[dbo].[Pipelines_Capacity_Oil] as capacity on \
throughput.Year = capacity.Year and throughput.Month = capacity.Month \
and throughput.[Corporate Entity] = capacity.[Corporate Entity] \
and throughput.[Pipeline Name] = capacity.[Pipeline Name] \
and throughput.[Key Point] = capacity.[Key Point] \
where throughput.[Corporate Entity] <> 'Trans Mountain Pipeline ULC' \
union all \
SELECT \
throughput.[Month], \
throughput.[Year], \
throughput.[Corporate Entity], \
throughput.[Pipeline Name], \
throughput.[Key Point], \
[Direction of Flow], \
[Trade Type], \
[Product], \
[Throughput (1000 m3/d)], \
capacity.[Available Capacity (1000 m3/d)] \
FROM [EnergyData].[dbo].[Pipelines_Throughput_Oil] as throughput \
left join [EnergyData].[dbo].[Pipelines_Capacity_Oil] as capacity on \
throughput.Year = capacity.Year and throughput.Month = capacity.Month and throughput.[Corporate Entity] = capacity.[Corporate Entity] \
and throughput.[Pipeline Name] = capacity.[Pipeline Name] \
where throughput.[Corporate Entity] = 'Trans Mountain Pipeline ULC' \
) as hc \
order by [Corporate Entity], [Pipeline Name], [Key Point], cast(str([Month])+'-'+'1'+'-'+str([Year]) as date)"

query_gas_throughcap = "SELECT \
cast(cast([Month] as varchar)+'-'+'1'+'-'+cast([Year] as varchar) as date) as [Date], \
[Corporate Entity], \
[Pipeline Name], \
[Key Point], \
[Direction of Flow], \
[Trade Type], \
'Natural Gas' as [Product], \
round(avg([Capacity (1000 m3/d)]),1) as [Capacity (1000 m3/d)], \
round(avg([Throughput (1000 m3/d)]),1) as [Throughput (1000 m3/d)] \
FROM [EnergyData].[dbo].[Pipelines_Gas] \
where cast(str([Month])+'-'+str([Date])+'-'+str([Year]) as date) >= '2015-01-01' \
group by [Year],[Month],[Corporate Entity],[Pipeline Name],[Key Point],[Direction of Flow], [Trade Type] \
order by [Corporate Entity],[Pipeline Name],[Key Point],cast(cast([Month] as varchar)+'-'+'1'+'-'+cast([Year] as varchar) as date)"

query_fin_resource = "SELECT \
[variable] as [Financial Instrument], \
left([All Class], CHARINDEX(' ',[ALL Class])) as [Commodity], \
count(distinct [Company]) as [Companies using Financial Instrument], \
sum([values]) as [Financial Instrument Total] \
FROM [EnergyData].[dbo].[Pipeline_Fin_Resource] \
where variable <> 'ALL Limit' and left([All Class], CHARINDEX(' ',[ALL Class])) not in ('Commodity','CO2') \
group by [variable], left([All Class], CHARINDEX(' ',[ALL Class])) \
union all \
SELECT \
[variable] as [Financial Instrument], \
'All' as [Commodity], \
count(distinct [Company]) as [Companies using Financial Instrument], \
sum([values]) as [Financial Instrument Total] \
FROM [EnergyData].[dbo].[Pipeline_Fin_Resource] \
where variable <> 'ALL Limit' and left([All Class], CHARINDEX(' ',[ALL Class])) not in ('Commodity','CO2') \
group by [variable] \
order by left([All Class], CHARINDEX(' ',[ALL Class])), count(distinct [Company]) desc"

query_fin_resource_class = "SELECT \
fin.[ALL Class] as [Pipeline Group], \
left([All Class], CHARINDEX(' ',[ALL Class])) as [Commodity], \
sum(fin.[values]) as [Financial Resource] \
FROM [EnergyData].[dbo].[Pipeline_Fin_Resource] as fin \
where variable = 'ALL Limit' and [ALL Class] not in ('CO2 or Water Class','Commodity class 1') \
group by fin.[ALL Class] \
order by left([All Class], CHARINDEX(' ',[ALL Class])) desc, sum(fin.[values]) desc"

query_fin_resource_class_names = "SELECT \
[ALL Class], \
[Company] \
FROM [EnergyData].[dbo].[Pipeline_Fin_Resource] as fin \
where variable = 'ALL Limit' and [ALL Class] not in ('CO2 or Water Class','Commodity class 1') \
order by [ALL Class], fin.[values], [Company]"

query_gas_2019 = "SELECT [Year],[Corporate Entity],[Pipeline Name],[Key Point],[Trade Type], \
case when [Trade Type] = 'import' then round(avg([Capacity (1000 m3/d)]/1000),2)*-1 \
else round(avg([Capacity (1000 m3/d)]/1000),2) end as [Capacity], \
case when [Trade Type] = 'import' then round(avg([Throughput (1000 m3/d)]/1000),2)*-1 \
else round(avg([Throughput (1000 m3/d)]/1000),2) end as [Throughput] \
FROM [EnergyData].[dbo].[Pipelines_Gas] where \
([Year] = 2019 and [Corporate Entity] = 'NOVA Gas Transmission Ltd. (NGTL)' and [Key Point] = 'Upstream of James River') or \
([Year] = 2019 and [Corporate Entity] = 'NOVA Gas Transmission Ltd. (NGTL)' and [Key Point] = 'West Gate') or \
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Prairies') or \
([Year] = 2019 and [Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Huntingdon Export') or \
([Year] = 2019 and [Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or \
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Niagara' and [Trade Type] = 'import') or \
([Year] = 2019 and [Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Iroquois' and [Trade Type] = 'export') or \
([Year] = 2019 and [Corporate Entity] = 'Maritimes & Northeast Pipeline' and [Key Point] = 'Baileyville, Ma. / St. Stephen N.B.' and [Trade Type] = 'import') or \
([Year] = 2019 and [Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] = 'Monchy' and [Trade Type] = 'export') or \
([Year] = 2019 and [Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] = 'Kingsgate' and [Trade Type] = 'export')  \
group by [Year],[Corporate Entity],[Pipeline Name],[Key Point],[Trade Type]"

query_gas_prices = "SELECT \
[Location], \
cast(str(month(Date))+'-'+'1'+'-'+str(year(Date)) as date) as [Date], \
round(avg([Price ($CN/GIG)]),2) as [Price ($CN/GIG)], \
round(avg([Price ($US/MMB)]),2) as [Price ($US/MMB)] \
FROM [EnergyData].[dbo].[vwPlatts_NextDay_converted] \
where [Location] in ('Henry Hub TDt Com','Dawn Ontario TDt Com','TC Alb AECO-C TDt Com Dly','Westcoast Stn 2 TDt Com') \
group by [Location], year([Date]), month([Date]) \
having (round(avg([Price ($CN/GIG)]),2) is not null) and (round(avg([Price ($US/MMB)]),2) is not null) \
order by year([Date]), month([Date]), [Location]" 

query_st_stephen = "select [Date],[Capacity],[import] as [Imports],[export] as [Exports] \
from (SELECT cast(str(gas.Month)+'-'+'1'+'-'+str(gas.Year) as date) as [Date],gas.[Trade Type], \
round(avg(gas.[Capacity (1000 m3/d)]/1000),1) as [Capacity], \
round(avg(gas.[Throughput (1000 m3/d)]/1000),1) as [Throughput] \
FROM [EnergyData].[dbo].[Pipelines_Gas] as gas \
where  gas.[Corporate Entity]='Maritimes & Northeast Pipeline' and gas.[Pipeline Name] = 'Canadian Mainline' \
group by gas.Year,gas.Month, gas.[Trade Type]) as mnp pivot \
(avg([Throughput]) for [Trade Type] in ([import],[export])) as mnp_untidy order by [Date]"

query_ns_offshore = "select si.Date, \
round((dp.Volume/si.Days)/1000,1) as [Deep Panuke], \
round((si.Volume/si.Days)/1000,1) as [Sable Island] \
from (SELECT [Date],Product,sum(Volume) as [Volume],Units, \
'Deep Panuke' as [Rig] FROM [EnergyData].[dbo].[CNSOPB_DeepPanuke] as dp \
where Product = 'Gas Equivalent Volume' group by [Date],[Product],Units) as dp \
right join ( \
SELECT [Date], \
datediff(day, dateadd(day, 1-day([Date]), [Date]), \
dateadd(month, 1, dateadd(day, 1-day([Date]), [Date]))) as [Days], \
Product,sum(Volume) as [Volume],Units,'Sable Island' as [Rig] \
FROM [EnergyData].[dbo].[CNSOPB_SableIsland] as si \
where Product = 'Gas Equivalent Volume' group by [Date],[Product],Units) as si \
on dp.Date = si.Date and dp.Product = si.Product and dp.Units = si.Units \
where year(si.Date)>='2006' order by dp.Date"

def normalize_dates(df,date_list):
    for date_col in date_list:
        df[date_col] = pd.to_datetime(df[date_col])
        df[date_col] = df[date_col].dt.date
    return df

def normalize_text(df,text_list):
    for text_col in text_list:
        df[text_col] = [x.strip() for x in df[text_col]]
    return df

def normalize_numeric(df,num_list,decimals):
    for num_col in num_list:
        df[num_col] = pd.to_numeric(df[num_col])
        df[num_col] = df[num_col].round(decimals)
    return df

def daysInYear(year):
    d1 = date(year, 1, 1)
    d2 = date(year + 1, 1, 1)
    return (d2 - d1).days

def readCersei(query,name=None):
    conn,engine = cer_connection()
    df = pd.read_sql_query(query,con=conn)
    if name == 'crude_by_rail_wcs.json':
        df['Crude by Rail'] = [x/1000 if u=='bbl per day' else x for x,u in zip(df['Crude by Rail'],df['Units'])]
        df['Units'] = df['Units'].replace({'bbl per day':'Mb/d','m3 per day':'m3/d'})
        df = normalize_numeric(df, ['Crude by Rail'], 1)
        write_path = os.path.join(os.getcwd(),'Colette/crude_by_rail/',name)
    if name == 'gas_traffic.json':
        df['Date'] = pd.to_datetime(df['Date'])
        write_path = os.path.join(os.getcwd(),'Sara/gas_traffic/',name)
    if name == 'fin_resource_totals.json':
        write_path = os.path.join(os.getcwd(),'Jennifer/financial_instruments/',name)
        for text_col in ['Financial Instrument','Commodity']:
            df[text_col] = [x.strip() for x in df[text_col]]
    if name == 'fin_resource_class.json':
        write_path = os.path.join(os.getcwd(),'Jennifer/financial_instruments/',name)
        for text_col in ['Pipeline Group','Commodity']:
            df[text_col] = [x.strip() for x in df[text_col]]
        df['Financial Resource'] = pd.to_numeric(df['Financial Resource'])
    if name == 'fin_resource_class_names.json':
        write_path = os.path.join(os.getcwd(),'Jennifer/financial_instruments/',name)
        df = normalize_text(df, ['ALL Class','Company'])
        classes = list(set(df['ALL Class']))
        names = {}
        for group in classes:
            dfg = df[df['ALL Class']==group].copy()
            names[group] = sorted(list(set(dfg['Company'])))
        
        #names = [names]
        with open(write_path, 'w') as f:
            json.dump(names, f)
        #return names
        
    if name == 'gas_2019.json':
        write_path = os.path.join(os.getcwd(),'Sara/gas_2019/',name)
        df.loc[df['Corporate Entity'] == 'TransCanada PipeLines Limited', 'Pipeline Name'] = 'TCPL Canadian Mainline'
        df.loc[df['Corporate Entity'] == 'Maritimes & Northeast Pipeline', 'Pipeline Name'] = 'M&NP Pipeline'
        df['Key Point'] = df['Key Point'].replace({'Baileyville, Ma. / St. Stephen N.B.':'St. Stephen'})
        #df['Spare Capacity'] = df['Capacity'] - df['Throughput']
        df['Series Name'] = df['Pipeline Name']+' - '+df['Key Point']+' - '+df['Trade Type']
        df = df.sort_values(by=['Capacity'], ascending=False)
        delete = ['Corporate Entity','Pipeline Name','Key Point','Trade Type','Year']
        for d in delete:
            del df[d]
    if name == 'gas_prices.json':
        write_path = os.path.join(os.getcwd(),'Rebecca/gas_prices/',name)
    
    if (name != None and name not in ['fin_resource_class_names.json','st_stephen.json','ns_offshore.json']):
        df.to_json(write_path,orient='records')
    conn.close()
    return df

def readCsv(name):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_csv(read_path)
    df['Period'] = pd.to_datetime(df['Period'])
    df.to_json(name.split('.')[0]+'.json',orient='records')
    return df

def readExcel(name,sheet='pq',flatten=False):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet_name=sheet)
    
    if name == 'Crude_Oil_Production.xlsx':
        df['Year'] = pd.to_numeric(df['Year'])
        products = ['Conventional Light','Conventional Heavy','C5+','Field Condensate','Mined Bitumen','In Situ Bitumen']
        for crude in products:
            df[crude] = df[crude]/1000
        df = normalize_numeric(df, products, 3)
        #df['Value'] = pd.to_numeric(df['Value'])
        write_path = os.path.join(os.getcwd(),'Kevin/crude_production/',name.split('.')[0]+'.json')
    if name == 'UScrudeoilimports.xlsx':
        df['Attribute'] = [x.strip() for x in df['Attribute']]
        write_path = os.path.join(os.getcwd(),'Kevin/us_imports/',name.split('.')[0]+'.json')
        df['Value'] = df['Value'].round(2)
    if name == 'natural-gas-liquids-exports-monthly.xlsx':
        df['Period'] = pd.to_datetime(df['Period'],errors='raise')
        df['Days in Month'] = [monthrange(x.year,x.month)[-1] for x in df['Period']]
        df['Region'] = df['Region'].replace({'Québec':'Quebec'})
        df = df[df['Period'].dt.year >= 2010]
        df = df[df['Units']=='bbl'].copy()
        for delete in ['Units','Total']:
            del df[delete]
        
        for col in ['Pipeline','Railway','Truck','Marine']:
            df[col] = ((df[col]/df['Days in Month'])/1000).round(1)
        del df['Days in Month']
        write_path = os.path.join(os.getcwd(),'Ryan/ngl_exports/',name.split('.')[0]+'.json')
        df.to_json(write_path,orient='records',force_ascii=False)
        
        if flatten:
            df = pd.melt(df,id_vars=['Period','Product','Region','Units'])
            write_path = os.path.join(os.getcwd(),'Ryan/ngl_exports/',name.split('.')[0]+'_flat.json')
            df = df[df['value'].notnull()]
            df = df[df['variable']!='Total']
            df.to_json(write_path,orient='records',force_ascii=False)
    
    if name == 'crude-oil-exports-by-destination-annual.xlsx':
        df = df[df['PADD'] != 'Total']
        df = df[df['Unit']!='m3/d']
        df['Value'] = (df['Value']/1000000).round(2)
        df['Unit'] = df['Unit'].replace({'bbl/d':'MMb/d'})
        write_path = os.path.join(os.getcwd(),'Kevin/crude_exports/',name.split('.')[0]+'.json')
    
    if name == 'UScrudeoilimports.xlsx':
        df['Value'] = [round(x,2) for x in df['Value']]
        write_path = os.path.join(os.getcwd(),'Kevin/us_imports/',name.split('.')[0]+'.json')
    
    if name == 'fgrs-eng.xlsx' and sheet=='pq':
        df = df.rename(columns={'TransMountain':'Trans Mountain Pipeline',
                                'Aurora/Rangeland':'Aurora Pipeline',
                                'Express':'Express Pipeline',
                                'Milk River':'Milk River Pipeline'})
        write_path = os.path.join(os.getcwd(),'Colette/crude_takeaway/',name.split('.')[0]+'.json')
    
    if name == 'marine_exports.xlsx':
        write_path = os.path.join(os.getcwd(),'Colette/marine_exports/',name.split('.')[0]+'.json')
        del df['b/d']
        df['Thousand m3/d'] = df['Mb/d']
        df = normalize_numeric(df, ['Mb/d'], 1)
        df = normalize_dates(df, ['Date'])
        
    if name == 'fgrs-eng.xlsx' and sheet=='ngl production':
        products = ['Ethane','Propane','Butanes']
        df = normalize_numeric(df, products, 1)
        write_path = os.path.join(os.getcwd(),'Ryan/ngl_production/',name.split('.')[0]+'.json')
    
    if name == 'CrudeRawData-2019-01-01-2019-12-01.xlsx':
        df['Percent'] = df['Percent'].round(2)
        for delete in ['Value','Total Volume']:
            del df[delete]
        df = df[df['Attribute']!='Truck']
        df['Attribute'] = df['Attribute'].replace({'Railroad':'Rail'})
        write_path = os.path.join(os.getcwd(),'Colette/crude_export_mode/',name.split('.')[0]+'.json')
    
    if name == 'Natural_Gas_Production.xlsx':
        write_path = os.path.join(os.getcwd(),'Rebecca/gas_production/',name.split('.')[0]+'.json')
    if name == 'natural-gas-exports-and-imports-annual.xlsx':
        cal = calendar.Calendar()
        df['Days in Year'] = [daysInYear(x) for x in df['Year']]
        df['Volume (Bcf/d)'] = (df['Volume (MCF)']/1000000)/df['Days in Year']
        df['Volume (Million m3/d)'] = (df['Volume (Thousand m3)']/1000)/df['Days in Year']
        for delete in ['Volume (MCF)','Days in Year','Volume (Thousand m3)']:
            del df[delete]
        df = normalize_numeric(df,['Volume (Bcf/d)','Volume (Million m3/d)'],2)
        write_path = os.path.join(os.getcwd(),'Rebecca/gas_trade/',name.split('.')[0]+'.json')
    if name == 'CreditTables.xlsx':
        if sheet == 'ratings categories':
            df = normalize_text(df, ['Corporate Entity','Type','Credit Quality'])
            #allow for multiselect on company
            df = df[~df['Corporate Entity'].isin(['MPLL shareholders - Royal Dutch Shell Plc',
                                                  'MPLL shareholders - Suncor Energy Inc.',
                                                  'Plains All American Pipeline',
                                                  'MPLL shareholders - Imperial Oil Limited'])]
            
            df['series'] = df['Corporate Entity']+' - '+df['Type']
            write_path = os.path.join(os.getcwd(),'Jennifer/credit_ratings/',name.split('.')[0]+'.json')
        if sheet == 'Scale':
            write_path = os.path.join(os.getcwd(),'Jennifer/credit_ratings/',sheet+'.json')
            del df['Level']
            df = df.rename(columns={'DBRS Morningstar':'DBRS','Level Inverted':'Level'})
            df = normalize_text(df, ["Credit Quality","DBRS","S&P","Investment Grade","Moody's"])
            levels = {}
            for index,l in enumerate(df['Level']):
                levels[l] = {"creditQuality":df['Credit Quality'][index],
                             "S&P":df['S&P'][index],
                             "DBRS":df['DBRS'][index],
                             "Moody's":df["Moody's"][index],
                             "investmentGrade":df['Investment Grade'][index]}
            with open(write_path, 'w') as f:
                json.dump(levels, f)
    if name == "abandonment funding data.xlsx":
        df = normalize_text(df, ['Company'])
        df['Amount to Recover'] = df['ACE'] - df['Amounts Set Aside']
        df = df.sort_values(by=['ACE'],ascending=False)
        write_path = os.path.join(os.getcwd(),'Jennifer/abandonment_funding/',sheet+'.json')
        
    #df = df.astype(object).where(pd.notnull(df), None)
    if sheet != 'Scale':
        df.to_json(write_path,orient='records',force_ascii=False)
    return df

def readExcelPipeline(name,sheet='Data',sql=False):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet_name=sheet)
    text = ['Table','Owner','Pipeline','Category','Type','Unit']
    capital = ['Table','Owner','Pipeline','Category','Type']
    for t in text:
        df[t] = [x.strip() for x in df[t]]
        
    del df['Table']
    df['Value'] = pd.to_numeric(df['Value'],errors='coerce')
    df = df.astype(object).where(pd.notnull(df), None)
    
    df['Type'] = [[r.capitalize().strip() for r in x.split(' ')] for x in df['Type']]
    df['Type'] = [' '.join(x) for x in df['Type']]
    
    type_switch = {'Deemed Equity':'Deemed Equity Ratio',
                   'Return On Common Equity':'Actual Return on Equity',
                   'Return On Equity':'Actual Return on Equity',
                   'Achieved Return On Equity':'Actual Return on Equity',
                   'Total Revenue':'Revenue',
                   'Revenues':'Revenue',
                   'Rate Base [average Plant In Service]':'Rate Base',
                   'Average Rate Base':'Rate Base',
                   'Rate Of Return On Rate Base':'Return on Rate Base',
                   'Return On Net Plant':'Return on Net Plant',
                   'Cost Of Service':'Cost of Service',
                   'Return On Rate Base':'Return on Rate Base'}
    
    df['Type'] = df['Type'].replace(type_switch)
    df = df[df['Type'].isin(['Deemed Equity Ratio','Actual Return on Equity','Revenue','Rate Base'])]
    df['Pipeline'] = df['Pipeline'].replace({'Trans Québec & Maritimes Pipeline':'Trans Quebec & Maritimes Pipeline'})    
    oil_lines = ['Aurora Pipeline','Enbridge Mainline','Enbridge Norman Wells Pipeline','Express Pipeline','Cochin Pipeline','Milk River Pipeline','Montreal Pipeline','Southern Lights Pipeline','Trans Mountain Pipeline','Keystone Pipeline System','Trans-Northern Pipeline','Wascana','Westspur Pipeline']
    df['Category'] = ['Oil' if x in oil_lines else 'Gas' for x in df['Pipeline']]
    
    df['Pipeline'] = df['Pipeline'].replace({'Canadian Mainline':'TransCanada Mainline',
                                             'NGTL':'NGTL System',
                                             'Westcoast Transmission System':'Westcoast System',
                                             'Foothills Pipeline System':'Foothills System'})
    
    df = normalize_numeric(df, ['Value'], 0)
    df = df.sort_values(by=['Type','Category','Year','Value'])
    write_path = os.path.join(os.getcwd(),'Cassandra/all_pipes/',name.split('.')[0]+'.json')
    df.to_json(write_path,orient='records',force_ascii=False)
   
    if sql:
        conn,engine = cer_connection()
        df.to_sql('Pipeline_Financial_Metrics',con=conn,index=False,if_exists='replace')
        conn.close()
    return df

def writeExcelCredit(name,sheet='Credit Ratings'):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet)
    df['Value'] = [str(x).strip() for x in df['Value']]
    df['Value'] = df['Value'].replace({'-':None})
    df = df.rename(columns={'Pipeline':'Corporate Entity'})
    df = normalize_text(df, ['Corporate Entity','Type','Value'])
    df['Value'] = df['Value'].replace({'A\xa0(low)':'A (low)','BBB(high)':'BBB (high)'})
    
    conn,engine = cer_connection()
    df.to_sql('Pipeline_Financial_Ratings',con=conn,index=False,if_exists='replace')
    conn.close()
    return df

def keyPoints():
    
    query_gas = "SELECT point.[Key Point],\
            point.[Corporate Entity],\
            point.[Pipeline Name],\
            [Latitude],\
            [Longitude],\
            direction.[Direction of Flow]\
            FROM [EnergyData].[dbo].[Pipelines_KeyPoints] as point\
            join\
            (\
            SELECT [Corporate Entity],\
            [Pipeline Name],\
            [Key Point],\
            [Direction of Flow]\
            FROM [EnergyData].[dbo].[Pipelines_Gas]\
            group by\
            [Corporate Entity],\
            [Pipeline Name],\
            [Key Point],\
            [Direction of Flow]\
            ) as direction\
            on point.[Key Point] = direction.[Key Point] and point.[Corporate Entity] = direction.[Corporate Entity]"
    
    query_oil = "SELECT point.[Key Point],\
            point.[Corporate Entity],\
            point.[Pipeline Name],\
            [Latitude],\
            [Longitude],\
            direction.[Direction of Flow]\
            FROM [EnergyData].[dbo].[Pipelines_KeyPoints] as point\
            join\
            (\
            SELECT [Corporate Entity],\
            [Pipeline Name],\
            [Key Point],\
            [Direction of Flow]\
            FROM [EnergyData].[dbo].[Pipelines_Throughput_Oil]\
            group by\
            [Corporate Entity],\
            [Pipeline Name],\
            [Key Point],\
            [Direction of Flow]\
            ) as direction\
            on point.[Key Point] = direction.[Key Point] and point.[Corporate Entity] = direction.[Corporate Entity]"
    
    replace_oil = {'Trans Mountain':'Trans Mountain Pipeline',
                   'Canadian Mainline':'Enbridge Canadian Mainline'}
    
    points_list = []
    conn,engine = cer_connection()
    for query in [[query_oil,'keyPointsOil.json'],[query_gas,'keyPointsGas.json']]:
        df = pd.read_sql_query(query[0],con=conn)
        df = normalize_text(df, ['Key Point','Corporate Entity','Pipeline Name','Direction of Flow'])
        for num in ['Latitude','Longitude']:
            df[num] = pd.to_numeric(df[num])
        if query[-1] == 'keyPointsOil.json':
            df['Pipeline Name'] = df['Pipeline Name'].replace(replace_oil)
        else:
            df.loc[df['Corporate Entity'] == 'Maritimes & Northeast Pipeline', 'Pipeline Name'] = 'M&NP Canadian Mainline'
            df.loc[df['Corporate Entity'] == 'TransCanada PipeLines Limited', 'Pipeline Name'] = 'TCPL Canadian Mainline'
            
        write_path = os.path.join(os.getcwd(),'Jennifer/throughcap/',query[-1])
        df.to_json(write_path,orient='records')
        points_list.append(df)
        
    conn.close()
    return points_list

def throughcap(query,name):
    
    #TODO: look into grouping this by year/month to reduce the file size
    conn,engine = cer_connection()
    df = pd.read_sql_query(query,con=conn)
    df['Date'] = pd.to_datetime(df['Date'])
    
    if name == 'gas_throughcap.json':
        numeric_cols = ['Capacity (1000 m3/d)','Throughput (1000 m3/d)']
        no_points_list = ['Brunswick Pipeline']
        df = df[~df['Pipeline Name'].isin(no_points_list)]
        df.loc[df['Corporate Entity'] == 'Maritimes & Northeast Pipeline', 'Pipeline Name'] = 'M&NP Canadian Mainline'
        df.loc[df['Corporate Entity'] == 'TransCanada PipeLines Limited', 'Pipeline Name'] = 'TCPL Canadian Mainline'
        
    elif name == 'oil_throughcap.json':
        numeric_cols = ['Available Capacity (1000 m3/d)','Throughput (1000 m3/d)']
        no_points_list = ['Trans-Northern','Westpur Pipeline','Southern Lights Pipeline']
        df = df[~df['Pipeline Name'].isin(no_points_list)]
        replace_oil = {'Canadian Mainline':'Enbridge Canadian Mainline'}
        df['Pipeline Name'] = df['Pipeline Name'].replace(replace_oil)
        
    for numeric in numeric_cols:
        df[numeric] = pd.to_numeric(df[numeric])
        df[numeric] = df[numeric].round(1)
    
    write_path = os.path.join(os.getcwd(),'Jennifer/throughcap/',name)
    df.to_json(write_path,orient='records')
    conn.close()
    return df

def financialResources(name='NEB_DM_PROD - 1267261 - Financial Resource Types - Data.XLSX',sql=False):
    
    def process_vals(x):
        x = x.split('$')
        x = [r.strip() for r in x]
        return x
    
    def apply_base(v,b):
        if b == 'million':
            v = v*1000000
        elif b == 'billion':
            v = v*1000000000
        elif b == 'thousand':
            v = v*1000
        return v
    
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet_name='FinRes Types',skiprows=5)
    df.columns = [x.strip() for x in df.columns]
    del df['Notes']
    
    for col in df.columns:
        df[col] = df[col].astype('object')
        df[col] = [str(x).strip() for x in df[col]]
    
    df = pd.melt(df,id_vars=['Company','Filing','Approved?','ALL Class','Reliance on Parental Funds?'])
    df = df[(df['value']!='nan') & (df['value']!= '?')]
    #df['value'] = [x.split('$') for x in df['value']]
    df['value'] = [process_vals(x) for x in df['value']]
    notes,values,units = [],[],[]
    for vList in df['value']:
        if vList[0] != '':
            notes.append(vList[0])
            values.append('')
        else:
            notes.append('')
            values.append(vList[1].split(' '))
    df['notes'] = notes
    #df['values'] = values
    values_numeric,base,currency = [],[],[]
    for v in values:
        if type(v) == list:
            if len(v) > 2:
                currency.append(v[-1])
            else:
                currency.append('')
            
            values_numeric.append(v[0])
            base.append(v[1])
        else:
            values_numeric.append('')
            base.append('')
            currency.append('')
        
    df['values'] = [x.replace(',','') for x in values_numeric]
    df['base'] = [x.strip().lower() for x in base]
    df['base'] = df['base'].replace({'milion':'million'})
    df['currency'] = currency
    del df['value']
    df['values'] = pd.to_numeric(df['values'])
    df['values'] = [apply_base(v,b) for v,b in zip(df['values'],df['base'])]
    del df['base']
    df = df[df['Filing']!='Confid']
    if sql:
        conn,engine = cer_connection()
        df.to_sql('Pipeline_Fin_Resource',if_exists='replace',index=False,con=conn)
        conn.close()
    return df

def ne2_wcs_wti(query):
    
    conn,engine = cer_connection()
    df = readCersei(query)
    conn.close()
    df['Differential'] = (df['WTI'] - df['WCS'])*-1
    #df = pd.melt(df,id_vars=['Date'])
    write_path = os.path.join(os.getcwd(),'Kevin/crude_prices/','oil_prices.json')
    df.to_json(write_path,orient='records')
    return df

def tolls(name):
    
    def normalize(sheets,commodity,read_path):
        normal_list = []
        for sheet in sheets:
            try:
                df = pd.read_excel(read_path,sheet_name=sheet,skiprows=5)
                df = df[['Rate','Unit','Start','End']]
                df = df[df['Rate'].notnull()]
                if 'Current' in list(df['End']):
                    df['End'] = df['End'].replace('Current',date.today())
                df = normalize_dates(df, ['Start','End'])
        
                df['Rate'] = pd.to_numeric(df['Rate'])
                df['Pipeline'] = sheet.split('-')[-1].strip()
                df['Commodity'] = commodity
                df['Start'] = pd.to_datetime(df['Start'])
                df = df[df['Start'].dt.year>=2015]
                #normalize the tolls
                normalized = []
                toll_list = list(df['Rate'])
                for index,toll in enumerate(toll_list):
                    if index == 0:
                        normalized.append(toll/toll)
                    else:
                        #normalized.append(toll/toll_list[index-1]) #this is the old calculation
                        normalized.append(toll/toll_list[0])
                        
                df['Rate Normalized'] = normalized
                normal_list.append(df)
            except:
                raise
        
        #add in the gdp deflator for oil and gas tolls
        gdp = pd.read_excel(read_path,sheet_name='GDP Deflator',skiprows=26)
        gdp = gdp[['Start','End','Pipeline','Rate Normalized']]
        gdp = normalize_dates(gdp, ['Start','End'])
        gdp['Commodity'] = commodity
        normal_list.append(gdp)
        
        toll_list = pd.concat(normal_list, axis=0, sort=False, ignore_index=True)
        for delete in ['Rate','Unit']:
            del toll_list[delete]
        
        return toll_list
        
    read_path = os.path.join(os.getcwd(),'Data/',name)
    oil_sheets = ['Benchmark Toll - TNPI',
                  'Benchmark Toll - TMPL',
                  'Benchmark Toll - Keystone',
                  'Benchmark Toll - Express',
                  'Benchmark Toll - Enbridge ML']
    
    gas_sheets = ['Benchmark Toll - TC Mainline',
                  'Benchmark Toll - Westcoast',
                  'Benchmark Toll - TQM',
                  'Benchmark Toll - M&NP',
                  'Benchmark Toll - Alliance',
                  'Benchmark Toll - NGTL']
    
    oil = normalize(oil_sheets,'Crude Oil Breakdown',read_path)
    gas = normalize(gas_sheets,'Natural Gas Breakdown',read_path)
    
    #add in the commodity toll averages
    all_tolls = pd.read_excel(read_path,sheet_name='All Tolls')
    all_tolls['Commodity'] = 'Oil & Gas'
    all_tolls = normalize_dates(all_tolls,['Start','End'])
    
    df = pd.concat([oil,gas,all_tolls], axis=0, sort=False, ignore_index=True)
    df['Rate Normalized'] = df['Rate Normalized'].round(2)
    df['Pipeline'] = df['Pipeline'].replace({'Enbridge ML':'Enbridge Mainline',
                                             'Express':'Express Pipeline',
                                             'Keystone':'Keystone Pipeline',
                                             'TMPL':'Trans Mountain Pipeline',
                                             'TNPI':'Trans-Northern Pipeline',
                                             'Alliance':'Alliance Pipeline',
                                             'M&NP':'M&NP Pipeline',
                                             'NGTL':'NGTL System',
                                             'TC Mainline':'TransCanada Mainline',
                                             'TQM':'TQM Pipeline',
                                             'Westcoast':'Westcoast System'})
    df = df.sort_values(by=['Commodity','Pipeline','Start','End'])
    write_path = os.path.join(os.getcwd(),'Cassandra/tolls/','tolls.json')
    df.to_json(write_path,orient='records')
    return df

def negotiated_settlements(name='2020_Pipeline_System_Report_-_Negotiated_Settlements_and_Toll_Indicies.XLSX'):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet_name='Settlements Data',skiprows=2)
    df = df[['Company', 'Group', 'Oil/Gas',
       'Settlement Name and/or Reference', 'Original Settlement Approval',
       'Start Date', 'End Date (specified, or effective)',
       'Toll Design, Revenue Requirment, or Both', 'Notes']]
    df = df[~df['Start Date'].isnull()]
    for delete in ['Original Settlement Approval','Toll Design, Revenue Requirment, or Both','Notes']:
        del df[delete]
    df = df.rename(columns={'Settlement Name and/or Reference':'Settlement Name',
                            'End Date (specified, or effective)':'End Date',
                            'Oil/Gas':'Commodity'})
    
    df = normalize_dates(df, ['Start Date','End Date'])
    df = df.sort_values(by=['Company','Start Date','End Date'])
    #df = df[df['Company']=='NOVA Gas Transmission Ltd.']
    write_path = os.path.join(os.getcwd(),'Cassandra/negotiated_settlements/','settlements.json')
    df.to_json(write_path,orient='records')
    return df

def creditRatings():
    df = readExcel('CreditTables.xlsx',sheet='ratings categories')
    scale = readExcel('CreditTables.xlsx',sheet='Scale')
    return df,scale

def st_stephen():
    df_traffic = readCersei(query_st_stephen,'st_stephen.json')
    df_traffic = df_traffic[~df_traffic['Imports'].isnull()]
    df_prod = readCersei(query_ns_offshore,'ns_offshore.json')
    for df in [df_traffic,df_prod]:
        df['Date'] = pd.to_datetime(df['Date'])
    max_traffic = max(df_traffic['Date'])
    max_prod = max(df_prod['Date'])
    date_col,value_col = [],[]
    while max_prod < max_traffic:
        max_prod = max_prod+relativedelta(months=1)
        date_col.append(max_prod)
        value_col.append(None)
    df_none = pd.DataFrame.from_dict({'Date':date_col,'Deep Panuke':value_col,'Sable Island':value_col})
    df_prod = pd.concat([df_prod,df_none], axis=0, sort=False, ignore_index=True)
    
    for output in [[df_traffic,'st_stephen.json'],[df_prod,'ns_offshore.json']]:
        df = output[0]
        df = df.sort_values(by=['Date'])
        write_path = os.path.join(os.getcwd(),'Sara/st_stephen/',output[-1])
        df.to_json(write_path,orient='records')
    
    return df_traffic,df_prod
    

if __name__ == '__main__':
    
    #kevin
    #df = readExcel('Crude_Oil_Production.xlsx',sheet='pq')
    #df = readExcel('crude-oil-exports-by-destination-annual.xlsx',sheet='pq')
    #df = readExcel('UScrudeoilimports.xlsx',sheet='pq')
    #df = ne2_wcs_wti(query_ne2)
    
    #colette
    #df = readCersei(query_rail_wcs,'crude_by_rail_wcs.json')
    #df = readExcel('fgrs-eng.xlsx',sheet='pq')
    #df = readExcel('CrudeRawData-2019-01-01-2019-12-01.xlsx','Oil Mode')
    #df = readExcel('marine_exports.xlsx','marine exports')
    
    #sara
    #df = readCersei(query_gas_traffic,'gas_traffic.json')
    df = readCersei(query_gas_2019,'gas_2019.json')
    #df = readCersei(query_st_stephen,'st_stephen.json')
    #df = readCersei(query_ns_offshore,'ns_offshore.json')
    #df1,df2 = st_stephen()
    
    #rebecca
    #df = readCersei(query_gas_prices,'gas_prices.json')
    #df = readExcel('Natural_Gas_Production.xlsx')
    #df = readExcel('natural-gas-exports-and-imports-annual.xlsx','Gas Trade CER')
    
    #cassandra
    #df = readExcelPipeline('PipelineProfileTables.xlsx',sheet='Data')
    #df = tolls('2020_Pipeline_System_Report_-_Negotiated_Settlements_and_Toll_Indicies.XLSX')
    #df = negotiated_settlements()
    
    #ryan
    #df = readExcel('natural-gas-liquids-exports-monthly.xlsx',flatten=False) #TODO: move save location!
    #df = readExcel('fgrs-eng.xlsx',sheet='ngl production')
    
    #jennifer
    #df_oil = throughcap(query=query_oil_throughcap, name='oil_throughcap.json')
    #df_gas = throughcap(query=query_gas_throughcap, name='gas_throughcap.json')
    #df_point = keyPoints()
    #df_fin_insert = financialResources()
    #df_fin = readCersei(query_fin_resource,'fin_resource_totals.json')
    #df_fin_class = readCersei(query_fin_resource_class,'fin_resource_class.json')
    #df_fin_class_names = readCersei(query_fin_resource_class_names,'fin_resource_class_names.json')
    #df,scale = creditRatings()
    #df = readExcel("abandonment funding data.xlsx","Modified")

    #other
    #df = writeExcelCredit(name='CreditTables.xlsx')
    #df = crudeThroughput(name='oil_throughput.sql')
    #df = crudeCapacity(name='oil_capacity.sql')
    
#%%