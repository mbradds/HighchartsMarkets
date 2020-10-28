import { getUnique, fillDropUpdate, creditsClick } from "../../modules/util.js";

import financialData from "./PipelineProfileTables.json";

export const cassandraAllPipes = () => {
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

    var finPipes = getUnique(data, "Pipeline");
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

    for (const pipe in finPipes) {
      var dataPipe = data.filter((row) => row.Pipeline == finPipes[pipe]);
      var unit = dataPipe[0]["Unit"];
      dataPipe = dataPipe.map((v, i) => {
        var hcRow = {
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

    var yOptions = {};

    if (unit == "%") {
      yOptions.yFormat = "{value}%";
      yOptions.yLabel = "%";
      yOptions.yCall = function () {
        return this.value + "%";
      };
    } else {
      yOptions.yFormat = "{value:,.0f}";
      yOptions.yLabel = "C$ (Millions)";
      yOptions.yCall = function () {
        return this.value / 1000000;
      };
    }

    return [hcData, yOptions];
  };

  var financeFilters = { Category: "All", Type: "Deemed Equity Ratio" };

  var [seriesData, yOptions] = prepareSeriesFinance(
    financialData,
    financeFilters
  );

  fillDropUpdate(
    "select_metric_financial",
    getUnique(financialData, "Type"),
    false,
    "Deemed Equity Ratio"
  );

  const createFinancialChart = (newData, yOptions) => {
    return new Highcharts.chart("container_financial_metrics", {
      chart: {
        type: "line",
        zoomType: "x",
        borderWidth: 1,
        events: {
          load: function () {
            creditsClick(this, "https://apps.cer-rec.gc.ca/REGDOCS/Home/Index");
          },
        },
      },

      credits: {
        text: "Source: CER REGDOCS",
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

      title: {
        text:
          financeFilters.Type + ": " + financeFilters.Category + " pipelines",
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
          text: yOptions.yLabel,
        },
        labels: {
          //format: yOptions.yFormat,
          formatter: yOptions.yCall,
        },
      },

      lang: {
        noData: "No Financial Data",
      },
      series: newData,
    });
  };

  const mainPipeline = () => {
    var chartFinance = createFinancialChart(seriesData, yOptions);
    var selectMetricFinancial = document.getElementById(
      "select_metric_financial"
    );

    selectMetricFinancial.addEventListener(
      "change",
      (selectMetricFinancial) => {
        var metric = selectMetricFinancial.target.value;
        financeFilters.Type = metric;
        chartFinance = graphEvent(financeFilters);
      }
    );

    var selectPipeFinancial = document.getElementById(
      "select_pipelines_financial"
    );

    selectPipeFinancial.addEventListener("change", (selectPipeFinancial) => {
      var pipeGroup = selectPipeFinancial.target.value;
      financeFilters.Category = pipeGroup;
      chartFinance = graphEvent(financeFilters);
    });

    const graphEvent = (filters) => {
      [seriesData, yOptions] = prepareSeriesFinance(financialData, filters);
      return createFinancialChart(seriesData, yOptions);
    };
  };
  mainPipeline();
};
