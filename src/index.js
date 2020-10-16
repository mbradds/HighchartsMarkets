const generalTheme = () => {
  Highcharts.transportation = {
    chart: {
      borderColor: "black",
      animation: true,
    },
    yAxis: {
      stackLabels: {
        style: {
          fontWeight: "bold",
          color: (Highcharts.theme && Highcharts.theme.textColor) || "gray",
        },
      },
    },

    noData: {
      style: {
        fontWeight: "bold",
        fontSize: "15px",
        color: "#303030",
      },
    },

    title: {
      style: {
        color: "#000",
        font: 'bold 16px "Trebuchet MS", Verdana, sans-serif',
      },
    },
    legend: {
      itemStyle: {
        font: "12pt Arial",
        color: "black",
      },
    },
  };
  Highcharts.setOptions(Highcharts.transportation);
};

generalTheme();

import { kevinCrudeProduction } from "./Kevin/crude_production/crude_production";
import { kevinCrudeExports } from "./Kevin/crude_exports/crude_exports";
import { kevinUsImports } from "./Kevin/us_imports/us_imports";
import { kevinCrudePrices } from "./Kevin/crude_prices/crude_prices";
import { coletteCrudeByRail } from "./Colette/crude_by_rail/crude_by_rail";
import { coletteCrudeTakeaway } from "./Colette/crude_takeaway/crude_takeaway";
import { saraGasTraffic } from "./Sara/gas_traffic/gas_traffic";
import { sara2019 } from "./Sara/gas_2019/gas_2019";
import { cassandraAllPipes } from "./Cassandra/all_pipes/pipeline_metrics";
import { cassandraTolls } from "./Cassandra/tolls/tolls";
import { ryanNglExports } from "./Ryan/ngl_exports/ngl_exports";
import { jenniferThroughcap } from "./Jennifer/throughcap/throughcap";
import { jenniferFinResources } from "./Jennifer/financial_instruments/fin_resource";

kevinCrudeProduction();
kevinCrudeExports();
kevinUsImports();
kevinCrudePrices();
coletteCrudeByRail();
coletteCrudeTakeaway();
saraGasTraffic();
sara2019();
cassandraAllPipes();
cassandraTolls();
ryanNglExports();
jenniferThroughcap();
jenniferFinResources();
