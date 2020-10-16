import {
  cerPalette,
  fillDropUpdate,
  prepareSeriesTidy,
  creditsClick,
  conversions,
} from "../../modules/util.js";

import crudeExportsData from "./crude-oil-exports-by-destination-annual.json";

export const kevinCrudeExports = () => {
  const crudeExportColors = {
    "PADD I": cerPalette["Sun"],
    "PADD II": cerPalette["Night Sky"],
    "PADD III": cerPalette["Ocean"],
    "PADD IV": cerPalette["Forest"],
    "PADD V": cerPalette["Cool Grey"],
    Other: cerPalette["Flame"],
  };

  fillDropUpdate("select_units_crude_exports", ["Mb/d", "m3/d"], false, "Mb/d");

  var units = conversions("Mb/d to m3/d", "Mb/d", "Mb/d");

  var seriesData = prepareSeriesTidy(
    crudeExportsData,
    false,
    units,
    "PADD",
    "Year",
    "Value",
    crudeExportColors
  );

  const mouseOverFunction = (itter, currentSelection) => {
    itter.forEach(function (s) {
      if (s.name != currentSelection) {
        s.setState("inactive");
      } else {
        s.setState("hover");
      }
    });
  };

  const mouseOutFunction = (itter) => {
    itter.forEach(function (s) {
      s.setState("");
    });
  };

  const createPaddMap = () => {
    var paddMap = new Highcharts.mapChart("container_padd_map", {
      chart: {
        type: "map",
        map: "countries/us/custom/us-all-mainland",
        events: {
          load: function () {
            creditsClick(
              this,
              "https://apps.cer-rec.gc.ca/CommodityStatistics/Statistics.aspx?language=english"
            );
          },
        },
      },

      title: {
        text: null,
      },

      credits: {
        text: "Source: CER Commodity Tracking System",
      },

      legend: {
        enabled: false,
      },

      tooltip: {
        formatter: function () {
          return this.series.name;
        },
      },

      plotOptions: {
        map: {
          allAreas: false,
        },
        series: {
          states: {
            inactive: {
              opacity: 0.5,
            },
            hover: {
              brightness: 0,
            },
          },
          events: {
            mouseOver: function () {
              var currentSelection = this.name;
              mouseOverFunction(this.chart.series, currentSelection);
              mouseOverFunction(chartCrudeExports.series, currentSelection);
            },
            mouseOut: function () {
              mouseOutFunction(this.chart.series);
              mouseOutFunction(chartCrudeExports.series);
            },
          },
        },
      },

      series: [
        {
          name: "PADD I",
          data: [
            ["us-me", 1],
            ["us-vt", 1],
            ["us-nh", 1],
            ["us-ma", 1],
            ["us-ct", 1],
            ["us-ri", 1],
            ["us-ny", 1],
            ["us-pa", 1],
            ["us-nj", 1],
            ["us-de", 1],
            ["us-md", 1],
            ["us-wv", 1],
            ["us-va", 1],
            ["us-nc", 1],
            ["us-sc", 1],
            ["us-ga", 1],
            ["us-fl", 1],
          ],
          color: crudeExportColors["PADD I"],
        },
        {
          name: "PADD II",
          data: [
            ["us-nd", 1],
            ["us-sd", 1],
            ["us-ne", 1],
            ["us-ks", 1],
            ["us-ok", 1],
            ["us-mn", 1],
            ["us-ia", 1],
            ["us-mo", 1],
            ["us-wi", 1],
            ["us-il", 1],
            ["us-mi", 1],
            ["us-in", 1],
            ["us-ky", 1],
            ["us-tn", 1],
            ["us-oh", 1],
          ],
          color: crudeExportColors["PADD II"],
        },
        {
          name: "PADD III",
          data: [
            ["us-tx", 1],
            ["us-la", 1],
            ["us-nm", 1],
            ["us-ms", 1],
            ["us-al", 1],
            ["us-ar", 1],
          ],
          color: crudeExportColors["PADD III"],
        },
        {
          name: "PADD IV",
          data: [
            ["us-mt", 1],
            ["us-id", 1],
            ["us-ut", 1],
            ["us-co", 1],
            ["us-wy", 1],
          ],
          color: crudeExportColors["PADD IV"],
        },
        {
          name: "PADD V",
          data: [
            ["us-wa", 1],
            ["us-or", 1],
            ["us-ca", 1],
            ["us-nv", 1],
            ["us-az", 1],
          ],
          color: crudeExportColors["PADD V"],
        },
      ],
    });
    return paddMap;
  };

  const createCrudeExportsChart = (seriesData) => {
    var chartCrudeExports = new Highcharts.chart("container_crude_exports", {
      chart: {
        type: "column",
      },

      title: {
        text: null,
      },

      credits: {
        enabled: false,
      },

      plotOptions: {
        column: {
          stacking: "normal",
          dataLabels: {
            enabled: false,
          },
        },
        series: {
          events: {
            mouseOver: function () {
              var currentSelection = this.name;
              mouseOverFunction(paddMap.series, currentSelection);
            },
            mouseOut: function () {
              mouseOutFunction(paddMap.series);
            },
          },
        },
      },

      yAxis: {
        title: { text: "bbl/d" },
        stackLabels: {
          enabled: true,
        },
      },

      lang: {
        noData: "No Exports",
      },

      series: seriesData,
    });

    return chartCrudeExports;
  };

  var paddMap = createPaddMap();
  var chartCrudeExports = createCrudeExportsChart(seriesData);

  var selectUnitsCrudeExports = document.getElementById(
    "select_units_crude_exports"
  );
  selectUnitsCrudeExports.addEventListener(
    "change",
    (selectUnitsCrudeExports) => {
      units.unitsCurrent = selectUnitsCrudeExports.target.value;
      var seriesData = prepareSeriesTidy(
        crudeExportsData,
        false,
        units,
        "PADD",
        "Year",
        "Value",
        crudeExportColors
      );

      chartCrudeExports.update({
        series: seriesData,
        yAxis: {
          title: { text: units.unitsCurrent },
        },
      });
    }
  );
};
