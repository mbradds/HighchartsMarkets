import { cerPalette, creditsClick } from "../../modules/util.js";

import settlementsData from "./settlements.json";

export const cassandraSettlements = () => {
  const legendNames = {
    company: {
      name: "Active settlement(s)",
      color: cerPalette["Night Sky"],
    },
    end: {
      name: "Settlements with fixed end date",
      color: cerPalette["Ocean"],
    },
    noEnd: {
      name: "Settlements without fixed end date",
      color: cerPalette["Cool Grey"],
    },
  };

  const legendColors = {
    "Active settlement(s)": cerPalette["Night Sky"],
    "Settlements with fixed end date": cerPalette["Ocean"],
    "Settlements without fixed end date": cerPalette["Cool Grey"],
  };

  const filters = { Commodity: "All" };

  const setTitle = (figure_title, filters) => {
    if (filters.Commodity == "All") {
      figure_title.innerText = "Figure 15: Negotiated Settlement Timelines";
    } else {
      figure_title.innerText = `Figure 15: Negotiated Settlement Timelines - ${filters.Commodity} Companies`;
    }
  };

  const currentDate = () => {
    var today = new Date(),
      day = 1000 * 60 * 60 * 24;
    today.setUTCHours(0);
    today.setUTCMinutes(0);
    today.setUTCSeconds(0);
    today.setUTCMilliseconds(0);
    return today.getTime();
  };

  var today = currentDate();

  const getEndDate = (date) => {
    if (date === null) {
      return [today, cerPalette["Cool Grey"]];
    } else {
      return [date, cerPalette["Ocean"]];
    }
  };

  const settlementSeries = (data, filters) => {
    var seriesTracker = {};
    var seriesSettle = [];
    var dates = [];

    if (filters.Commodity !== "All") {
      data = data.filter((row) => row.Commodity == filters.Commodity);
    }

    data.map((row, rowNum) => {
      dates.push(row["Start Date"]);
      dates.push(row["End Date"]);
      var [endDate, seriesColor] = getEndDate(row["End Date"]);

      if (seriesTracker.hasOwnProperty(row.Company)) {
        //the parent company is already in the series, add the sub settlement
        seriesTracker[row.Company].startDate.push(row["Start Date"]);
        seriesTracker[row.Company].endDate.push(endDate);
        seriesSettle.push({
          name: row["Settlement Name"],
          id: row["Settlement Name"],
          parent: row.Company,
          color: seriesColor,
          start: row["Start Date"],
          end: endDate,
        });
      } else {
        //A new company is added to the series as the parent, and the current settlement is also added
        seriesTracker[row.Company] = {
          startDate: [row["Start Date"]],
          endDate: [endDate],
        };
        seriesSettle.push({
          name: row.Company,
          collapsed: true,
          color: cerPalette["Night Sky"],
          id: row.Company,
          start: row["Start Date"],
          end: endDate,
        });
        seriesSettle.push({
          name: row["Settlement Name"],
          id: row["Settlement Name"],
          parent: row.Company,
          color: seriesColor,
          start: row["Start Date"],
          end: endDate,
        });
      }
    });
    
    //get the start and end date for each company across all settlements
    for (const company in seriesTracker) {
      seriesTracker[company].startDate = Math.min(
        ...seriesTracker[company].startDate
      );
      seriesTracker[company].endDate = Math.max(
        ...seriesTracker[company].endDate
      );
    }

    seriesSettle.map((s, seriesNum) => {
      if (seriesTracker.hasOwnProperty(s.name)) {
        s.start = seriesTracker[s.name].startDate;
        s.end = seriesTracker[s.name].endDate;
      }
    });

    dates = dates.filter((row) => row !== null);

    return [seriesSettle, seriesTracker, dates];
  };
  var [seriesSettle, seriesTracker, dates] = settlementSeries(
    settlementsData,
    filters
  );

  const createSettlements = (seriesSettle) => {
    return Highcharts.ganttChart("container_settlements", {
      chart: {
        type: "gantt",
        borderWidth: 1,
        events: {
          load: function () {
            creditsClick(this, "https://www.cer-rec.gc.ca/en/index.html");
          },
        },
      },
      credits: {
        text: "Source: CER",
      },
      plotOptions: {
        series: {
          states: {
            hover: {
              enabled: false,
            },
          },
          events: {
            legendItemClick: function (e) {
              e.preventDefault();
            },
            checkboxClick: function (e) {
              console.log(e);
            },
          },
        },
      },
      legend: {
        enabled: true,
        symbolPadding: 0,
        symbolWidth: 0,
        symbolHeight: 0,
        squareSymbol: false,
        useHTML: true,
        title: {
          text:
            "Legend: (Click on a company name above to view all negotiated settlements)",
          style: {
            fontStyle: "italic",
          },
        },
        labelFormatter: function () {
          return (
            '<span style="font-weight:bold; color:' +
            legendColors[this.name] +
            '">' +
            this.name +
            "</span>"
          );
        },
      },
      xAxis: [
        {
          min: Math.min(...dates),
          max: Math.max(...dates),
          currentDateIndicator: {
            width: 2,
            color: "black",
            label: {
              format: "%Y-%m-%d",
            },
          },
        },
      ],

      tooltip: {
        xDateFormat: "%Y-%m-%d",
        formatter: function () {
          if (this.color == cerPalette["Cool Grey"]) {
            var endText = "No set end date";
          } else {
            var endText = Highcharts.dateFormat("%Y-%m-%d", this.point.end);
          }

          if (this.point.parent == null) {
            return (
              "<b>" +
              this.key +
              "</b> <br> Active settlement(s) start: " +
              Highcharts.dateFormat("%Y-%m-%d", this.point.start) +
              "<br> Active settlement(s) end: " +
              Highcharts.dateFormat("%Y-%m-%d", this.point.end)
            );
          } else {
            return (
              "<b>" +
              this.point.parent +
              " - " +
              this.key +
              "</b> <br> Start: " +
              Highcharts.dateFormat("%Y-%m-%d", this.point.start) +
              "<br> End: " +
              endText
            );
          }
        },
      },
      series: [
        {
          name: legendNames["company"].name,
          data: seriesSettle,
          color: legendNames["company"].color,
        },
        {
          name: legendNames["end"].name,
          data: null,
          color: legendNames["end"].color,
        },
        {
          name: legendNames["noEnd"].name,
          data: null,
          color: legendNames["noEnd"].color,
        },
      ],
    });
  };
  const mainSettlements = () => {
    var figure_title = document.getElementById("settle_title");
    setTitle(figure_title, filters);
    var settlementChart = createSettlements(seriesSettle);
    var selectSettle = document.getElementById("select_commodity_settle");
    selectSettle.addEventListener("change", (selectSettle) => {
      filters.Commodity = selectSettle.target.value;
      setTitle(figure_title, filters);
      var [seriesSettle, seriesTracker, dates] = settlementSeries(
        settlementsData,
        filters
      );
      settlementChart = createSettlements(seriesSettle);
    });
  };
  mainSettlements();
};