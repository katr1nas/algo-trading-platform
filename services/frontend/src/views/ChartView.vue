<script setup>
import { ref, onMounted } from "vue";
import { getOHLC, getRSI, getRSIStrategy } from "@/services/api";
import CombinedChart from "@/components/CombinedChart.vue";

const price = ref([]);
const rsi = ref([]);
const buySignals = ref([]);
const sellSignals = ref([]);

async function load(symbol = "GOLD") {
  const ohlc = await getOHLC(symbol);
  price.value = ohlc;

  const close = ohlc.map(c => c.close);

  const rsiResp = await getRSI(close, 14);
  rsi.value = rsiResp.values;

  const strategyResp = await getRSIStrategy(rsi.value);
  buySignals.value = strategyResp.signals.filter(s => s.type === "BUY");
  sellSignals.value = strategyResp.signals.filter(s => s.type === "SELL");
}

onMounted(() => {
  load("GOLD");
});
</script>

<template>
  <CombinedChart 
    :price="price" 
    :rsi="rsi"
    :buySignals="buySignals"
    :sellSignals="sellSignals"
  />
</template>
