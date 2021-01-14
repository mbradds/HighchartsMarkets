import {
  cerPalette,
  creditsClick,
  prepareSeriesPie,
  numberFormat,
  setTitle,
} from "../../modules/util.js";
import { errorChart } from "../../modules/charts.js";
import crudeModeData from "./crude_mode.json";

const createChart = () => {
  const crudeModeFilters = { Year: 2019 };
  const crudeModeColors = {
    Pipeline: cerPalette["Night Sky"],
    Marine: cerPalette["Ocean"],
    Rail: cerPalette["Sun"],
  };

  const createCrudeModeChart = (seriesData, filters) => {
    return new Highcharts.chart("container_crude_mode", {
      chart: {
        borderWidth: 1,
        type: "pie",
        events: {
          load: function () {
            creditsClick(
              this,
              "https://apps.cer-rec.gc.ca/CommodityStatistics/Statistics.aspx?language=english"
            );
          },
        },
      },
      credits: {
        text: "Source: CER Commodity Tracking System",
      },
      tooltip: {
        useHTML: true,
        formatter: function () {
          var toolText = `<table><b>${this.key} - ${filters.Year}</b>`;
          toolText += `<tr><td> Percent of total: </td><td style="padding:0"><b>${this.point.percentage.toFixed(
            0
          )} %</b></td></tr>`;
          toolText += `<tr><td> Export volume: </td><td style="padding:0"><b>${numberFormat(
            this.y.toFixed(1)
          )} bbl/day</b></td></tr>`;
          toolText += `<tr><td></td><td style="padding:0"><b><i>${numberFormat(
            (this.y / 6.2898).toFixed(1)
          )} m3/day</b></i></td></tr>`;
          toolText += `</table>`;
          return toolText;
        },
      },
      accessibility: {
        point: {
          valueSuffix: "%",
        },
      },
      plotOptions: {
        pie: {
          cursor: "pointer",
          size: "80%",
          dataLabels: {
            enabled: true,
            format: "<b>{point.name}</b>: {point.percentage:.1f} %",
          },
          showInLegend: true,
        },
      },
      series: seriesData,
    });
  };
  try {
    var figure_title = document.getElementById("crude_mode_title");
    setTitle(
      figure_title,
      "5",
      crudeModeFilters.Year,
      "Crude Oil Exports by Mode"
    );

    const seriesData = prepareSeriesPie(
      crudeModeData,
      crudeModeFilters,
      "Crude Exports by Mode",
      "Mode",
      "Volume (bbl/d)",
      crudeModeColors
    );

    const crudeModePie = createCrudeModeChart(seriesData, crudeModeFilters);

    $("#crude-exp-mode button").on("click", function () {
      $(".btn-crude-mode > .btn").removeClass("active");
      $(this).addClass("active");
      var thisBtn = $(this);
      var btnText = thisBtn.text();
      var btnValue = thisBtn.val();
      $("#selectedVal").text(btnValue);
      crudeModeFilters.Year = btnText;
      setTitle(
        figure_title,
        "5",
        crudeModeFilters.Year,
        "Crude Oil Exports by Mode"
      );
      crudeModePie.update({
        series: prepareSeriesPie(
          crudeModeData,
          crudeModeFilters,
          "Crude Exports by Mode",
          "Mode",
          "Volume (bbl/d)",
          crudeModeColors
        ),
      });
    });
  } catch (err) {
    errorChart("container_crude_mode");
  }
};

export function coletteCrudeMode() {
  return new Promise((resolve) => {
    setTimeout(() => resolve(createChart()), 0);
  });
}
