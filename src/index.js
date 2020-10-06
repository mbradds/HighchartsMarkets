import { kevinCrudeProduction } from "./Kevin/crude_production/crude_production.js";
import { kevinCrudeExports } from "./Kevin/crude_exports/crude_exports.js";
import { kevinUsImports } from "./Kevin/us_imports/us_imports.js";
import { kevinCrudePrices } from "./Kevin/crude_prices/crude_prices.js";
import { coletteCrudeByRail } from "./Colette/crude_by_rail/crude_by_rail.js";
import { coletteCrudeTakeaway } from "./Colette/crude_takeaway/crude_takeaway.js";
import { saraGasTraffic } from "./Sara/gas_traffic/gas_traffic.js";
import { cassandraAllPipes } from "./Cassandra/all_pipes/pipeline_metrics.js";
import { ryanNglExports } from "./Ryan/ngl_exports/ngl_exports.js";

kevinCrudeProduction();
kevinCrudeExports();
kevinUsImports();
kevinCrudePrices();
coletteCrudeByRail();
coletteCrudeTakeaway();
saraGasTraffic();
cassandraAllPipes();
ryanNglExports();