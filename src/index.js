import { kevinCrudeProduction } from "./Kevin/crude_production/crude_production";
import { kevinCrudeExports } from "./Kevin/crude_exports/crude_exports";
import { kevinUsImports } from "./Kevin/us_imports/us_imports";
import { kevinCrudePrices } from "./Kevin/crude_prices/crude_prices";
import { coletteCrudeByRail } from "./Colette/crude_by_rail/crude_by_rail";
import { coletteCrudeTakeaway } from "./Colette/crude_takeaway/crude_takeaway";
import { saraGasTraffic } from "./Sara/gas_traffic/gas_traffic";
import { cassandraAllPipes } from "./Cassandra/all_pipes/pipeline_metrics";
import { cassandraTolls } from "./Cassandra/tolls/tolls";
import { ryanNglExports } from "./Ryan/ngl_exports/ngl_exports";
//import { mainThroughcap } from "./Jennifer/throughcap/throughcap"
import { jenniferFinResources } from "./Jennifer/financial_instruments/fin_resource";

kevinCrudeProduction();
kevinCrudeExports();
kevinUsImports();
kevinCrudePrices();
coletteCrudeByRail();
coletteCrudeTakeaway();
saraGasTraffic();
cassandraAllPipes();
cassandraTolls();
ryanNglExports();
//mainThroughcap();
jenniferFinResources();
