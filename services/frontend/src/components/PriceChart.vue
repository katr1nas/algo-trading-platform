<script setup>
import { defineProps, computed } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { 
  CandlestickChart, 
  GridComponent, 
  TooltipComponent, 
  ScatterChart 
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([CandlestickChart, ScatterChart, GridComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps({
  data: Array,
  buySignals: Array,
  sellSignals: Array
});

// ⚠️ ВОТ СЮДА — в option — вставляется твой series
const option = computed(() => ({
  tooltip: { trigger: "axis" },

  xAxis: {
    type: "category",
    data: props.data.map(i => i.time)
  },

  yAxis: { type: "value" },

  series: [
    {
      type: "candlestick",
      data: props.data.map(i => [i.open, i.close, i.low, i.high])
    },
    {
      type: "scatter",
      data: props.buySignals.map(sig => [
        props.data[sig.index].time,
        props.data[sig.index].close
      ]),
      symbol: "triangle",
      symbolSize: 15,
      symbolRotate: 180,
      itemStyle: { color: "green" }
    },
    {
      type: "scatter",
      data: props.sellSignals.map(sig => [
        props.data[sig.index].time,
        props.data[sig.index].close
      ]),
      symbol: "triangle",
      symbolSize: 15,
      itemStyle: { color: "red" }
    }
  ]
}));
</script>

<template>
  <v-chart :option="option" autoresize />
</template>
