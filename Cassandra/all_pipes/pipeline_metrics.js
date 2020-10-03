const prepareSeriesFinance = (data, filters) => {
  for (const [key, value] of Object.entries(filters)) {
    if (key == "Category") {
      if (value == "Oil") {
        data = data.filter((row) => row.Category == "Oil");
      } else if (value == "Gas") {
        data = data.filter((row) => row.Category == "Gas");
      }
    } else {
      data = data.filter((row) => row[key] == value);
    }
  }

  var finPipes = getUnique((items = data), (filterColumns = "Pipeline"));
  var colors = [
    "#054169",
    "#FFBE4B",
    "#5FBEE6",
    "#559B37",
    "#FF821E",
    "#871455",
    "#8c8c96",
    "#42464B",
  ];
  var hcData = [];

  for (pipe in finPipes) {
    dataPipe = data.filter((row) => row.Pipeline == finPipes[pipe]);
    var unit = dataPipe[0]["Unit"];
    dataPipe = dataPipe.map((v, i) => {
      hcRow = {
        x: v["Year"],
        y: v["Value"],
      };
      return hcRow;
    });

    var completedMetric = {
      name: finPipes[pipe],
      data: dataPipe,
      color: colors[pipe],
    };
    hcData.push(completedMetric);
  }

  if (unit == "%") {
    var yFormat = "{value}%";
    var yLabel = "%";
  } else {
    var yFormat = "{value:,.0f}";
    var yLabel = "CAD ($)";
  }

  return [hcData, yFormat, yLabel];
};

var financeFilters = { Type: "Assets", Category: "All" };
var financialData = JSON.parse(
  JSON.stringify(
    JSON.parse(getData("Cassandra/all_pipes/PipelineProfileTables.json"))
  )
);
[seriesData, yFormat, yLabel] = prepareSeriesFinance(
  financialData,
  financeFilters
);
fillDrop(
  (column = "Type"),
  (dropName = "select_metric_financial"),
  (value = "Assets"),
  (data = financialData)
);

const createFinancialChart = (newData, yFormat, yLabel) => {
  const chart = new Highcharts.chart("container_financial_metrics", {
    chart: {
      type: "line", //line,bar,scatter,area,areaspline
      zoomType: "x", //allows the user to focus in on the x or y (x,y,xy)
      borderColor: "black",
      borderWidth: 1,
      animation: true,
      events: {
        load: function () {
          this.credits.element.onclick = function () {
            window.open(
              "https://apps.cer-rec.gc.ca/REGDOCS/Home/Index",
              "_blank" // <- This is what makes it open in a new window.
            );
          };
        },
      },
    },

    credits: {
      //enabled:false //gets rid of the "Highcharts logo in the bottom right"
      text: "Source: CER REGDOCS"
    },

    plotOptions: {
      series: {
        stickyTracking: false,
        connectNulls: false,
        states: {
          inactive: {
            opacity: 1,
          },
          hover: {
            enabled: false,
          },
        },
      },
    },

    tooltip: {
      animation: true,
      shared: true,
    },

    title: {
      text: financeFilters.Type + ": " + financeFilters.Category + " pipelines",
    },

    colors: [
      "#054169",
      "#FFBE4B",
      "#5FBEE6",
      "#559B37",
      "#FF821E",
      "#871455",
      "#8c8c96",
      "#42464B",
    ],

    yAxis: {
      title: {
        text: yLabel,
      },
      labels: {
        format: yFormat,
      },
    },

    lang: {
      noData: "No Financial Data",
    },
    noData: {
      style: {
        fontWeight: "bold",
        fontSize: "15px",
        color: "#303030",
      },
    },
    series: newData,
  });
};

const chartFinance = createFinancialChart(seriesData, yFormat, yLabel);

var selectMetricFinancial = document.getElementById("select_metric_financial");
selectMetricFinancial.addEventListener("change", (selectMetricFinancial) => {
  var metric = selectMetricFinancial.target.value;
  financeFilters.Type = metric;
  graphEvent(financeFilters);
});

var selectPipeFinancial = document.getElementById("select_pipelines_financial");
selectPipeFinancial.addEventListener("change", (selectPipeFinancial) => {
  var pipeGroup = selectPipeFinancial.target.value;
  financeFilters.Category = pipeGroup;
  graphEvent(financeFilters);
});

const graphEvent = (filters) => {
  [seriesData, yFormat, yLabel] = prepareSeriesFinance(
    financialData,
    financeFilters
  );
  createFinancialChart(seriesData, yFormat, yLabel);
};
