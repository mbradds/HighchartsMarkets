import { generalTheme } from "./modules/themes";
import { instructionsChart } from "./modules/charts";
import { kevinCrudeProduction } from "./Kevin/crude_production/crude_production";
import { kevinCrudeExports } from "./Kevin/crude_exports/crude_exports";
import { kevinUsImports } from "./Kevin/us_imports/us_imports";
import { kevinCrudePrices } from "./Kevin/crude_prices/crude_prices";
import { coletteCrudeMode } from "./Colette/crude_export_mode/crude_export_mode";
import { coletteCrudeByRail } from "./Colette/crude_by_rail/crude_by_rail";
import { coletteMarine } from "./Colette/marine_exports/marine_exports";
import { coletteCrudeTakeaway } from "./Colette/crude_takeaway/crude_takeaway";
import { rebeccaGasProd } from "./Rebecca/gas_production/gas_production";
import { rebeccaGasTrade } from "./Rebecca/gas_trade/gas_trade";
import { rebeccaGasPrices } from "./Rebecca/gas_prices/gas_prices";
import { saraGasTraffic } from "./Sara/gas_traffic/gas_traffic";
import { saraMnp } from "./Sara/st_stephen/st_stephen";
import { sara2019 } from "./Sara/gas_2019/gas_2019";
import { ryanNglProduction } from "./Ryan/ngl_production/ngl_production";
import { ryanNglExports } from "./Ryan/ngl_exports/ngl_exports";
import { ryanNglDestination } from "./Ryan/ngl_exports/ngl_destination";
import { cassandraSettlements } from "./Cassandra/negotiated_settlements/settlements";
import { cassandraTolls } from "./Cassandra/tolls/tolls";
import { jenniferFinResources } from "./Jennifer/financial_instruments/fin_resource";
import { jenniferAbandonment } from "./Jennifer/abandonment_funding/abandonment";
import { cassandraAllPipes } from "./Cassandra/all_pipes/pipeline_metrics";
import { jenniferRatingsCross } from "./Jennifer/credit_ratings_cross_section/credit_ratings_cross";
import { jenniferRatingsMulti } from "./Jennifer/credit_ratings/creditRatingsMultiple";
import eng from "./modules/eng.json";
import justWhy from "ie-gang";
try {
  let warningParams = {
    message: eng.ieWarnMessage,
    type: "alert",
    title: eng.ieWarnTitle,
    applyIE: false,
  };
  justWhy.ieWarn(warningParams);
} catch (err) {
  console.log("ieWarn error");
}

generalTheme();

async function loadAllCharts(eng) {
  console.time(`chart loading`);
  let arrayOfCharts = [
    instructionsChart(eng.instructionsChart),
    kevinCrudeProduction(eng.crudeProduction, eng.shared),
    kevinCrudeExports(eng.crudeExports),
    kevinCrudePrices(eng.crudePrices),
    kevinUsImports(eng.crudeImports),
    coletteCrudeMode(eng.crudeMode),
    coletteCrudeByRail(eng.crudeByRail),
    coletteMarine(eng.marineCrudeExports),
    coletteCrudeTakeaway(eng.crudeTakeaway),
    rebeccaGasProd(eng.gasProduction, eng.shared),
    rebeccaGasTrade(eng.gasTrade),
    rebeccaGasPrices(eng.gasPrices),
    saraGasTraffic(eng.gasTraffic),
    saraMnp(eng.gasMnp),
    sara2019(eng.gas2019),
    ryanNglProduction(eng.nglProduction, eng.shared),
    ryanNglExports(eng.nglExports),
    ryanNglDestination(eng.nglDestination),
    cassandraSettlements(eng.settlements),
    cassandraTolls(eng.tolls),
    jenniferFinResources(eng.finResource),
    jenniferAbandonment(eng.abandon),
    cassandraAllPipes(eng.finance),
    jenniferRatingsCross(eng.ratingsCross, false),
    jenniferRatingsMulti(eng.ratingsMultiple, false),
  ];
  Promise.allSettled(arrayOfCharts).then((value) => {
    console.timeEnd(`chart loading`);
  });
}
loadAllCharts(eng);
