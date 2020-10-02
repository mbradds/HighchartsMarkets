const cerPalette = {
    'Night Sky':'#054169',
    'Sun':'#FFBE4B',
    'Ocean':'#5FBEE6',
    'Forest':'#559B37',
    'Flame':'#FF821E',
    'Aubergine':'#871455',
    'Dim Grey':'#8c8c96',
    'Cool Grey':'#42464B',
    'White':'#FFFFFF'
}

const getData = (Url) => {
    var Httpreq = new XMLHttpRequest(); // a new request
    Httpreq.open("GET", Url, false);
    Httpreq.send(null);
    return Httpreq.responseText;
};

const dynamicDropDown = (id,optionsArray) => {

    function addOption(id,text,select){
        select.options[select.options.length] = new Option(text);
    }

    var select = document.getElementById(id);
    //select.options.length = 0;

    for (var i = 0; i < optionsArray.length; i++) {
        addOption (id, optionsArray[i],select);
    }

}

//gets the unique regions to populate the dropdown
const getUnique = (items, filterColumns) => {
    if (Array.isArray(filterColumns)) {
        var lookup = [];
        var result = {};

        for (f in filterColumns) {
            lookup.push({})
            result[filterColumns[f]] = []
        }

        for (var item, i = 0; item = items[i++];) {
            for (f in filterColumns) {
                var name = item[filterColumns[f]];
                if (!(name in lookup[f])) {
                    lookup[f][name] = 1;
                    result[filterColumns[f]].push(name);
                }
            }
        }
        return result

    } else {
        var lookup = {};
        var result = [];
        for (var item, i = 0; item = items[i++];) {
            var name = item[filterColumns];
            if (!(name in lookup)) {
                lookup[name] = 1;
                result.push(name);
            }
        }
        return result
    }
}


const fillDrop = (column,dropName,value,data) => {
    const drop = getUnique(data, filterColumns = column)
    dynamicDropDown(dropName, drop.sort())
    document.getElementById(dropName).value = value;
}

const prepareSeriesNonTidy = (data,filters,valueVars,xCol,colors) => {
    
    seriesData = {}
    colTotals = {}

    if (filters !== false){

        for (const [key, value] of Object.entries(filters)) {
            data = data.filter(row => row[key] == value )
        }

    }

    //initialize each series with an empty list
    valueVars.map((col,colNum) => {
        seriesData[col] = []
        colTotals[col] = 0
    })

    data.map((row,rowNum) => {
        valueVars.map((col,colNum) => {
            seriesData[col].push({
                x: row[xCol],
                y: row[col]
            })
            colTotals[col] = colTotals[col]+row[col]
        })
    })

    seriesResult = []

    for (const [key, value] of Object.entries(seriesData)) {
        if (colTotals[key] !== 0) {
            seriesResult.push({
                name: key,
                data: value,
                color: colors[key]
            })
        }
    }

    return seriesResult
}

const prepareSeriesNonTidyUnits = (data,filters,unitsCurrent,baseUnits,conversion,convType,valueVars,xCol,colors) => {

    seriesData = {}
    colTotals = {}

    if (filters !== false){
        for (const [key, value] of Object.entries(filters)) {
            data = data.filter(row => row[key] == value )
        }
    }

    //initialize each series with an empty list
    valueVars.map((col,colNum) => {
        seriesData[col] = []
        colTotals[col] = 0
    })

    if (unitsCurrent == baseUnits) {

        data.map((row,rowNum) => {
            valueVars.map((col,colNum) => {
                seriesData[col].push({
                    x: row[xCol],
                    y: row[col]
                })
                colTotals[col] = colTotals[col]+row[col]
            })
        })

    } else if (unitsCurrent !== baseUnits && convType == '/') {

        data.map((row,rowNum) => {
            valueVars.map((col,colNum) => {
                seriesData[col].push({
                    x: row[xCol],
                    y: +(row[col]/conversion).toFixed(1)
                })
                colTotals[col] = colTotals[col]+row[col]
            })
        })

    } else if (unitsCurrent !== baseUnits && convType == '*') {

        data.map((row,rowNum) => {
            valueVars.map((col,colNum) => {
                seriesData[col].push({
                    x: row[xCol],
                    y: +(row[col]*conversion).toFixed(1)
                })
                colTotals[col] = colTotals[col]+row[col]
            })
        })
        
    }

    seriesResult = []

    for (const [key, value] of Object.entries(seriesData)) {
        if (colTotals[key]>0) {
            seriesResult.push({
                name: key,
                data: value,
                color: colors[key]
            })
        }
    }

    return seriesResult
}

const prepareSeriesTidy = (data,filters,variableCol,xCol,yCol,colors) => {

    seriesData = []

    for (const [key, value] of Object.entries(filters)) {
        data = data.filter(row => row[key] == value )
    }

    const variableColumn = getUnique(data,variableCol)
    
    variableColumn.map((v,iVar) => {
        hcData = []
        const variableSeries = data.filter(row => row[variableCol] == v)
        variableSeries.map((r,i) => {
            hcRow = {
                x: r[xCol],
                y: r[yCol]
            }
            hcData.push(hcRow)
        })
        
        seriesData.push({
            name: v,
            data: hcData,
            color: colors[v]
        })

    })

    return seriesData

}