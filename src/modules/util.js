export const cerPalette = {
  "Night Sky": "#054169",
  Sun: "#FFBE4B",
  Ocean: "#5FBEE6",
  Forest: "#559B37",
  Flame: "#FF821E",
  Aubergine: "#871455",
  "Dim Grey": "#8c8c96",
  "Cool Grey": "#42464B",
  hcBlue: "#7cb5ec",
  hcGreen: "#90ed7d",
  hcPink: "#f15c80",
  hcRed: "#f45b5b",
  hcAqua: "#2b908f",
  hcPurple: "#8085e9",
  hcLightBlue: "#91e8e1",
  Forecast: "#F0F8FF",
};

export const numberFormat = (value) => {
  return Highcharts.numberFormat(value, 0, ".", ",");
};

export const dateFormat = (value, format = "%b %d, %Y") => {
  return Highcharts.dateFormat(format, value);
};

export const conversions = (conv, current, base) => {
  var cerConversions = {
    "m3/d to b/d": { conversion: 6.2898, type: "*" },
    "b/d to m3/d": { conversion: 0.159, type: "*" },
    "Mb/d to m3/d": { conversion: 159, type: "*" },
    "MMb/d to Mm3/d": { conversion: 0.0062898, type: "/" },
    "Bcf/d to Mm3/d": { conversion: 0.0000353, type: "*" },
    "Bcf/d to Million m3/d": { conversion: 28.32, type: "*" },
    "Million m3/d to Bcf/d": { conversion: 1 / 28.32, type: "*" },
  };
  var units = cerConversions[conv];
  units.unitsCurrent = current;
  units.unitsBase = base;
  return units;
};

export const sortJson = (obj) => {
  return obj.slice().sort((a, b) => b.value - a.value);
};

export const sortObj = (obj) => {
  return Object.fromEntries(Object.entries(obj).sort(([, a], [, b]) => a - b));
};

//takes in a json object and checks if the column has data
export const checkIfValid = (data) => {
  let valid = false;
  for (var t = 0; t < data.length; t++) {
    if (data[t]["y"] != null && data[t]["y"] != 0) {
      valid = true;
      break;
    }
  }
  return valid;
};

//gets the unique regions to populate the dropdown
export const getUnique = (items, filterColumns) => {
  var lookup = {};
  var result = [];
  for (var item, i = 0; (item = items[i++]); ) {
    var name = item[filterColumns];
    if (!(name in lookup)) {
      lookup[name] = 1;
      result.push(name);
    }
  }

  return result;
};

export const filterData = (data, filters) => {
  if (filters !== false) {
    for (const [key, value] of Object.entries(filters)) {
      if (!Array.isArray(value)) {
        data = data.filter((row) => row[key] == value);
      } else {
        value.map((filterValue) => {
          data = data.filter((row) => row[key] == filterValue);
        });
      }
    }
  }
  return data;
};

const yHigherOrder = (units, roundPoints) => {
  if (!units || units.unitsCurrent == units.unitsBase) {
    //The dataset has no unit conversions, and the data is already rounded
    if (roundPoints == 1) {
      const y = (row, col, units, round) => {
        if (row[col] == null) {
          return null;
        } else {
          return row[col];
        }
      };
      return y;
    } else {
      const y = (row, col, units, round) => {
        if (row[col] == null) {
          return null;
        } else {
          return +row[col].toFixed(round);
        }
      };
      return y;
    }
  } else {
    if (units.type == "*") {
      const y = (row, col, units, round) => {
        if (row[col] == null) {
          return null;
        } else {
          return +(row[col] * units.conversion).toFixed(round);
        }
      };
      return y;
    } else if (units.type == "/") {
      const y = (row, col, units, round) => {
        if (row[col] == null) {
          return null;
        } else {
          return +(row[col] / units.conversion).toFixed(round);
        }
      };
      return y;
    }
  }
};

const tidyOperation = (
  dataRaw,
  filters,
  units,
  variableCol,
  xCol,
  yCol,
  colors,
  decimals,
  xName
) => {
  const dataFiltered = filterData(dataRaw, filters);
  const variableColumn = getUnique(dataFiltered, variableCol);
  const seriesData = [];
  const yH = yHigherOrder(units, decimals);
  variableColumn.map((v, iVar) => {
    const hcData = [];
    const variableSeries = dataFiltered.filter((row) => row[variableCol] == v);
    variableSeries.map((r) => {
      hcData.push({
        [xName]: r[xCol],
        y: yH(r, yCol, units, decimals),
      });
    });

    seriesData.push({
      name: v,
      data: hcData,
      color: colors[v],
    });
  });

  return seriesData;
};

const nonTidyOperation = (
  dataRaw,
  filters,
  units,
  valueVars,
  xCol,
  colors,
  decimals,
  xName
) => {
  const seriesData = {};
  const colTotals = {};
  const dataFiltered = filterData(dataRaw, filters);
  const yH = yHigherOrder(units, decimals);

  valueVars.map((col) => {
    seriesData[col] = [];
    colTotals[col] = 0;
  });

  dataFiltered.map((row) => {
    valueVars.map((col) => {
      seriesData[col].push({
        [xName]: row[xCol],
        y: yH(row, col, units, decimals),
      });
      colTotals[col] = colTotals[col] + row[col];
    });
  });

  const seriesResult = [];

  for (const [key, value] of Object.entries(seriesData)) {
    if (colTotals[key] !== 0) {
      seriesResult.push({
        name: key,
        data: value,
        color: colors[key],
      });
    }
  }

  return seriesResult;
};

export const prepareSeriesNonTidy = (
  dataRaw,
  filters,
  units,
  valueVars,
  xCol,
  colors,
  decimals = 1,
  xName = "x"
) => {
  return nonTidyOperation(
    dataRaw,
    filters,
    units,
    valueVars,
    xCol,
    colors,
    decimals,
    xName
  );
};

export const prepareSeriesTidy = (
  dataRaw,
  filters,
  units,
  variableCol,
  xCol,
  yCol,
  colors,
  decimals = 1,
  xName = "x"
) => {
  return tidyOperation(
    dataRaw,
    filters,
    units,
    variableCol,
    xCol,
    yCol,
    colors,
    decimals,
    xName
  );
};

export const prepareSeriesPie = (
  dataRaw,
  filters,
  seriesName,
  nameCol,
  yCol,
  colors,
  colorByPoint = true
) => {
  const data = filterData(dataRaw, filters)[0];
  const series = { name: seriesName, colorByPoint: colorByPoint, data: [] };
  for (const [key, value] of Object.entries(data)) {
    if (key !== "Year") {
      series.data.push({
        name: key,
        y: value,
        color: colors[key],
      });
    }
  }
  return [series];
};

export const creditsClick = (chart, link) => {
  chart.credits.element.onclick = function () {
    window.open(link, "_blank");
  };
};

export const mouseOverFunction = (
  itter,
  currentSelection,
  newColor = false
) => {
  itter.forEach(function (s) {
    if (newColor && s.name == currentSelection) {
      s.update({
        color: newColor,
      });
    } else if (newColor == false) {
      if (s.name != currentSelection) {
        s.setState("inactive");
      } else {
        s.setState("hover");
      }
    }
  });
};

export const mouseOutFunction = (itter, oldColor = false) => {
  itter.forEach(function (s) {
    s.setState("");
    if (oldColor) {
      s.update({
        color: oldColor,
      });
    }
  });
};

const symbolHTML = (symbolName) => {
  var symbols = {
    circle: "&#9679",
    diamond: "&#9670",
    square: "&#9632",
    triangle: "&#9650",
    "triangle-down": "&#9660",
  };

  return symbols[symbolName];
};

export const tooltipPoint = (unitsCurrent) => {
  return `<tr><td> <span style="color: {series.color}">&#9679</span> {series.name}: </td><td style="padding:0"><b>{point.y} ${unitsCurrent}</b></td></tr>`;
};

export const tooltipSymbol = (
  event,
  unitsCurrent,
  shared = true,
  showY = true
) => {
  if (showY) {
    var y = event.point.y;
  } else {
    var y = "";
  }
  if (shared) {
    return `<tr><td> <span style="color: ${event.series.color}">${symbolHTML(
      event.point.graphic.symbolName
    )}</span> ${
      event.series.name
    }: </td><td style="padding:0"><b>${y} ${unitsCurrent}</b></td></tr>`;
  }
};

export const setTitle = (
  figure_title,
  figure_number,
  filter_value,
  title_text
) => {
  figure_title.innerText = `Figure ${figure_number}: ${String(
    filter_value
  ).trim()} ${title_text}`;
};
