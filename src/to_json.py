import pandas as pd
import json
import os
from connection import cer_connection
#TODO: add in the dataframe sorting before conversion to json
#TODO: remove the minute/second date precision. This should improve performance

query_gas_traffic = "select [Date], \
[Alliance Pipeline Limited Partnership - Alliance Pipeline - Border], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Kingsgate], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Monchy], \
[TransCanada PipeLines Limited - Canadian Mainline - Northern Ontario Line], \
[Capacity (1000 m3/d)] as [Capacity] \
from \
( \
SELECT \
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date], \
[Corporate Entity]+' - '+[Pipeline Name]+' - '+[Key Point] as [Point], \
round(avg([Throughput (1000 m3/d)]),1) as [value] \
FROM [EnergyData].[dbo].[Pipelines_Gas] \
where \
([Year] >= '2010') and \
([Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or \
([Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or \
([Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or \
([Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line') \
group by [Year], [Month], [Corporate Entity], [Pipeline Name], [Key Point], [Trade Type] \
union all \
select \
[Date], \
'Capacity (1000 m3/d)' as [Point], \
sum([Capacity (1000 m3/d)]) as [value] \
from \
( \
SELECT \
cast(str([Month])+'-'+'1'+'-'+str([Year]) as date) as [Date], \
[Corporate Entity],[Pipeline Name], [Key Point], \
round(avg([Capacity (1000 m3/d)]),1) as [Capacity (1000 m3/d)] \
FROM [EnergyData].[dbo].[Pipelines_Gas] \
where \
[Year] >= '2015' and \
([Corporate Entity] = 'Alliance Pipeline Limited Partnership' and [Key Point] = 'Border') or \
([Corporate Entity] = 'Westcoast Energy Inc.' and [Key Point] = 'Kingsvale') or \
([Corporate Entity] = 'Foothills Pipe Lines Ltd. (Foothills)' and [Key Point] in ('Kingsgate','Monchy')) or \
([Corporate Entity] = 'TransCanada PipeLines Limited' and [Key Point] = 'Northern Ontario Line') \
group by [Year],[Month],[Corporate Entity],[Pipeline Name], [Key Point] \
) as gas_cap \
group by [Date] \
) as SourceTable \
pivot \
( \
avg([value]) \
for Point in ([Alliance Pipeline Limited Partnership - Alliance Pipeline - Border], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Kingsgate], \
[Foothills Pipe Lines Ltd. (Foothills) - Foothills System - Monchy], \
[TransCanada PipeLines Limited - Canadian Mainline - Northern Ontario Line], \
[Capacity (1000 m3/d)]) \
) as PivotTable \
where year([Date]) >= '2015' \
order by [Date]"

query_rail_wcs = "select \
rail.Date, \
rail.Units, \
rail.Volume as [Crude by Rail], \
wcs.[WCS Differential] as [WCS-WTI Differential] \
\
from \
( \
\
SELECT \
[Date], \
[Volume], \
[Units] \
\
FROM [EnergyData].[dbo].[NEB_RailExports_Oil] \
where Units in ('bbl per day','m3 per day') \
\
) as rail \
\
left join \
\
( \
SELECT  \
year([SettlementDate]) as [Year], \
month([SettlementDate]) as [Month], \
round(avg([SettlementValue]),2)*-1 as [WCS Differential] \
\
FROM [EnergyData].[dbo].[Net_Energy_Spot] \
\
where Market = 'WCS' \
\
group by year([SettlementDate]),month([SettlementDate]) \
) as wcs \
\
on year(rail.Date) = wcs.Year and month(rail.Date) = wcs.Month \
where year(rail.Date) >= 2015\
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
cast(str([Month])+'-'+str([Date])+'-'+str([Year]) as date) as [Date], \
[Corporate Entity], \
[Pipeline Name], \
[Key Point], \
[Direction of Flow], \
[Trade Type], \
'Natural Gas' as [Product], \
[Capacity (1000 m3/d)], \
[Throughput (1000 m3/d)] \
FROM [EnergyData].[dbo].[Pipelines_Gas] \
where cast(str([Month])+'-'+str([Date])+'-'+str([Year]) as date) >= '2015-01-01' \
order by [Corporate Entity],[Pipeline Name],[Key Point],[Date]"

def readCersei(query,name=None):
    conn,engine = cer_connection()
    df = pd.read_sql_query(query,con=conn)
    if name == 'crude_by_rail_wcs.json':
        #df = pd.melt(df,id_vars=['Date','Units'])
        write_path = os.path.join(os.getcwd(),'Colette/crude_by_rail/',name)
    if name == 'gas_traffic.json':
        df['Date'] = pd.to_datetime(df['Date'])
        write_path = os.path.join(os.getcwd(),'Sara/gas_traffic/',name)
    
    if name != None:
        df.to_json(write_path,orient='records')
    conn.close()
    return df


def readCsv(name):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_csv(read_path)
    df['Period'] = pd.to_datetime(df['Period'])
    df.to_json(name.split('.')[0]+'.json',orient='records')
    return df

def jsTest(name,sheet='pq',flatten=False):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet_name=sheet)
    
    if name == 'natural-gas-liquids-exports-monthly.xlsx':
        df['Period'] = pd.to_datetime(df['Period'])
        write_path = os.path.join(os.getcwd(),'JavaScript Tests/series_creation/',name.split('.')[0]+'.json')
        df_bbl = df[df['Units']=='bbl'].copy()
        write_path_bbl = os.path.join(os.getcwd(),'JavaScript Tests/series_creation/',name.split('.')[0]+'_bbl.json')
        df_bbl.to_json(write_path_bbl,orient='records',force_ascii=False)
        
        if flatten:
            df = pd.melt(df,id_vars=['Period','Product','Region','Units'])
            write_path = os.path.join(os.getcwd(),'JavaScript Tests/series_creation/',name.split('.')[0]+'_flat.json')
            df = df[df['value'].notnull()]
            df = df[df['variable']!='Total']
            df.to_json(write_path,orient='records',force_ascii=False)
    
    df = df.astype(object).where(pd.notnull(df), None)
    df.to_json(write_path,orient='records',force_ascii=False)
    return df

def readExcel(name,sheet='pq',flatten=False):
    read_path = os.path.join(os.getcwd(),'Data/',name)
    df = pd.read_excel(read_path,sheet_name=sheet)
    
    if name == 'Crude_Oil_Production.xlsx':
        df['Year'] = pd.to_numeric(df['Year'])
        #df['Value'] = pd.to_numeric(df['Value'])
        write_path = os.path.join(os.getcwd(),'Kevin/crude_production/',name.split('.')[0]+'.json')
    if name == 'UScrudeoilimports.xlsx':
        df['Attribute'] = [x.strip() for x in df['Attribute']]
        write_path = os.path.join(os.getcwd(),'Kevin/us_imports/',name.split('.')[0]+'.json')
    if name == 'natural-gas-liquids-exports-monthly.xlsx':
        df['Period'] = pd.to_datetime(df['Period'])
        df = df[df['Period'].dt.year >= 2010]
        df = df[df['Units']=='bbl'].copy()
        for delete in ['Units','Total']:
            del df[delete]
        
        for col in ['Pipeline','Railway','Truck','Marine']:
            df[col] = df[col].round(1)
            
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
        write_path = os.path.join(os.getcwd(),'Kevin/crude_exports/',name.split('.')[0]+'.json')
    
    if name == 'UScrudeoilimports.xlsx':
        write_path = os.path.join(os.getcwd(),'Kevin/us_imports/',name.split('.')[0]+'.json')
        df['Value'] = [round(x,2) for x in df['Value']]
    
    if name == 'fgrs-eng.xlsx':
        write_path = os.path.join(os.getcwd(),'Colette/crude_takeaway/',name.split('.')[0]+'.json')
        
        
    #df = df.astype(object).where(pd.notnull(df), None)
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
    
    oil_lines = ['Aurora Pipeline','Enbridge Mainline','Enbridge Norman Wells Pipeline','Express Pipeline','Cochin Pipeline','Milk River Pipeline','Montreal Pipeline','Southern Lights Pipeline','Trans Mountain Pipeline','Keystone Pipeline System','Trans-Northern Pipeline','Wascana','Westspur Pipeline']
    df['Category'] = ['Oil' if x in oil_lines else 'Gas' for x in df['Pipeline']]
    
    write_path = os.path.join(os.getcwd(),'Cassandra/all_pipes/',name.split('.')[0]+'.json')
    df.to_json(write_path,orient='records',force_ascii=False)
   
    if sql:
        conn,engine = cer_connection()
        df.to_sql('Pipeline_Financial_Metrics',con=conn,index=False,if_exists='replace')
        conn.close()
    return df


def readExcelCredit(name,sheet='Credit Ratings'):
    
    df = pd.read_excel(name,sheet)
    df['Value'] = [str(x).strip() for x in df['Value']]
    df['Value'] = df['Value'].replace({'-':None})
    df = df.rename(columns={'Pipeline':'Corporate Entity'})
    del df['Table']
    
    conn,engine = cer_connection()
    df.to_sql('Pipeline_Financial_Ratings',con=conn,index=False,if_exists='replace')
    conn.close()
    
    return df


# def crudeThroughput(name):
#     query = "select [Date],[Corporate Entity],[Pipeline Name],[Key Point],[Direction of Flow],[Trade Type],[Product],[Units],[Throughput] \
#     from \
#     ( \
#     SELECT \
#     cast(cast([Month] as nvarchar(2))+'-'+'1'+'-'+cast([Year] as nvarchar(4)) as date) as [Date],[Corporate Entity],[Pipeline Name],[Key Point],[Direction of Flow],[Trade Type],[Product], \
#     round([Throughput (1000 m3/d)],2) as [1000 m3/d], \
#     round([Throughput (1000 m3/d)]*6.2898,2) as [1000 b/d] \
#     FROM [EnergyData].[dbo].[Pipelines_Throughput_Oil] \
#     ) as unTidy \
#     unpivot \
#     (Throughput FOR Units in ([1000 m3/d],[1000 b/d]) \
#     ) as tidy \
#     order by [Pipeline Name],[Corporate Entity],Product,[Date]"

#     conn,engine = cer_connection()
#     df = pd.read_sql_query(query,con=conn)
#     df.to_json(name.split('.')[0]+'.json',orient='records')
#     conn.close()
    
#     return df


# def crudeCapacity(name):
#     query = "select [Date],[Corporate Entity],[Pipeline Name],[Key Point], \
#     rtrim(ltrim(LEFT([Units], Charindex('(', [Units]) - 1))) as [Capacity Type], \
#     ltrim(Right([Units], Charindex('(', [Units]))) as [Units], \
#     [Capacity] \
#     from( \
#     SELECT \
#     cast(cast([Month] as nvarchar(2))+'-'+'1'+'-'+cast([Year] as nvarchar(4)) as date) as [Date],[Corporate Entity],[Pipeline Name],[Key Point], \
#     round([Nameplate Capacity (1000 m3/d)],2) as [Nameplate Capacity (1000 m3/d)], \
#     round([Available Capacity (1000 m3/d)],2) as [Available Capacity (1000 m3/d)], \
#     round([Nameplate Capacity (1000 m3/d)]*6.2898,2) as [Nameplate Capacity (1000 b/d)], \
#     round([Available Capacity (1000 m3/d)]*6.2898,2) as [Available Capacity (1000 b/d)] \
#     FROM [EnergyData].[dbo].[Pipelines_Capacity_Oil] \
#     where ([Pipeline Name] = 'Canadian Mainline' and [Key Point] in ('ex-Gretna','Into-Sarnia')) or ([Pipeline Name] <> 'Canadian Mainline') \
#     ) as unTidy \
#     unpivot \
#     (Capacity FOR Units in ([Nameplate Capacity (1000 m3/d)],[Available Capacity (1000 m3/d)],[Nameplate Capacity (1000 b/d)],[Available Capacity (1000 b/d)]) \
#     ) as tidy \
#     order by [Pipeline Name],[Corporate Entity],[Key Point],[Date]"

#     conn,engine = cer_connection()
#     df = pd.read_sql_query(query,con=conn)
#     df.to_json(name.split('.')[0]+'.json',orient='records')
#     conn.close()
    
#     return df


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
            
    conn,engine = cer_connection()
    for query in [[query_oil,'keyPointsOil.json'],[query_gas,'keyPointsGas.json']]:
        df = pd.read_sql_query(query[0],con=conn)
        for num in ['Latitude','Longitude']:
            df[num] = pd.to_numeric(df[num])
    
        write_path = os.path.join(os.getcwd(),'Jennifer/throughcap/',query[-1])
        df.to_json(write_path,orient='records')
        
    conn.close()
    return df


def throughcap(query,name):
    
    #TODO: look into grouping this by year/month to reduce the file size
    conn,engine = cer_connection()
    df = pd.read_sql_query(query,con=conn)
    df['Date'] = pd.to_datetime(df['Date'])
    
    if name == 'gas_throughcap.json':
        numeric_cols = ['Capacity (1000 m3/d)','Throughput (1000 m3/d)']
    elif name == 'oil_throughcap.json':
        numeric_cols = ['Available Capacity (1000 m3/d)','Throughput (1000 m3/d)']
    
    for numeric in numeric_cols:
        df[numeric] = pd.to_numeric(df[numeric])
        df[numeric] = df[numeric].round(1)
    
    write_path = os.path.join(os.getcwd(),'Jennifer/throughcap/',name)
    df.to_json(write_path,orient='records')
    conn.close()
    return df

def financialResources(name='NEB_DM_PROD - 1267261 - Financial Resource Types - Data.XLSX'):
    
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
    
    df = pd.read_excel(name,sheet_name='FinRes Types',skiprows=5)
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

if __name__ == '__main__':
    
    #kevin
    #df = readExcel('Crude_Oil_Production.xlsx',sheet='pq')
    #df = readExcel('crude-oil-exports-by-destination-annual.xlsx',sheet='pq')
    #df = readExcel('UScrudeoilimports.xlsx',sheet='pq')
    #df = ne2_wcs_wti(query_ne2)
    
    #colette
    #df = readCersei(query_rail_wcs,'crude_by_rail_wcs.json')
    df = readExcel('fgrs-eng.xlsx',sheet='pq')
    
    #sara
    #df = readCersei(query_gas_traffic,'gas_traffic.json')
    
    #cassandra
    #df = readExcelPipeline('PipelineProfileTables.xlsx',sheet='Data')
    
    #ryan
    #df = readExcel('natural-gas-liquids-exports-monthly.xlsx',flatten=False) #TODO: move save location!
    
    #jennifer
    df_oil = throughcap(query=query_oil_throughcap, name='oil_throughcap.json')
    df_gas = throughcap(query=query_gas_throughcap, name='gas_throughcap.json')
    df_point = keyPoints()
    
    
    #other
    #df = readCsv('ngl_exports.csv')
    #df = readExcelCredit(name='CreditTables.xlsx')
    #df = crudeThroughput(name='oil_throughput.sql')
    #df = crudeCapacity(name='oil_capacity.sql')
    #df = keyPoints()
    #df = financialResources()
    

#%%




