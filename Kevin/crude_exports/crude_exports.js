const prepareSeriesExports = (data,units) => {

    const colors = ['#054169', '#FFBE4B', '#5FBEE6', '#559B37', '#FF821E', '#871455', '#8c8c96', '#42464B']
    seriesData = []
    data = data.filter(row => row.Unit == units)
    data = data.filter(row => row.PADD !== 'Total')
    const padds = getUnique(data,'PADD')
    
    padds.map((v,iPadds) => {
        hcData = []
        const padd = data.filter(row => row.PADD == v)
        padd.map((r,i) => {
            hcRow = {
                x: r.Year,
                y: r.Value
            }
            hcData.push(hcRow)
        })

        seriesData.push({
            name: v,
            data: hcData,
            color: colors[iPadds]
        })

    })

    return seriesData

}
const crudeExportColors = {'PADD 1':'#FFBE4B',
'PADD 2':'#054169',
'PADD 3':'#5FBEE6',
'PADD 4':'#559B37',
'PADD 5':'#42464B'}

const crudeExportsData = JSON.parse(JSON.stringify(JSON.parse(getData('Kevin/crude_exports/crude-oil-exports-by-destination-annual.json'))));
console.log(crudeExportsData)
fillDrop('Unit','select_units_crude_exports','bbl/d',crudeExportsData)
var seriesData = prepareSeriesExports(crudeExportsData,'bbl/d')
const createCrudeExportsChart = (seriesData) => {


const chartCrudeExports = new Highcharts.chart('container_crude_exports', {

    chart: {
        type: 'column', //line,bar,scatter,area,areaspline
        zoomType: 'x', //allows the user to focus in on the x or y (x,y,xy)
        borderColor: 'black',
        borderWidth: 1,
        animation: true,
        events: {
            load: function () {
                this.credits.element.onclick = function () {
                    window.open(
                        'https://www.cer-rec.gc.ca/index-eng.html',
                        '_blank' // <- This is what makes it open in a new window.
                    );
                }
            }
        }
    },

    title: {
        text: null
    },

    credits: {
        //enabled:false //gets rid of the "Highcharts logo in the bottom right"
        text: 'Canada Energy Regulator',
        href: 'https://www.cer-rec.gc.ca/index-eng.html'
    },

    plotOptions: {
        column: {
            stacking: 'normal',
            dataLabels: {
                enabled: false
            }
        }
    },

    tooltip: {
        animation: true,
        //shared: true,
    },

    // title: { text: 'Canada Propane Exports' },

    // xAxis: {
    // },

    yAxis: {
        title: { text: 'Thousand bbl/day' },
        stackLabels: {
            enabled: true,
            style: {
                fontWeight: 'bold',
                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
            }
        }
    },

    lang: {
        noData: "No Exports"
    },

    noData: {
        style: {
            fontWeight: 'bold',
            fontSize: '15px',
            color: '#303030'
        }
    },
    series: seriesData
});

return chart
}

var chartCrudeExports = createCrudeExportsChart(seriesData)

var selectUnitsCrudeExports = document.getElementById('select_units_crude_exports');
selectUnitsCrudeExports.addEventListener('change', (selectUnitsCrudeExports) => {
    var units = selectUnitsCrudeExports.target.value;
    var seriesData = prepareSeriesExports(crudeExportsData,units)
    chartCrudeExports = createCrudeExportsChart(seriesData)
});








