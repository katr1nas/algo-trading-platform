<script setup>
import {defineProps, computed} from 'vue';
import VChart from 'vue-echarts';
import { use } from "echarts/core";
import { CandlestickChart, GridComponent, TooltipComponent } from "echarts/components";
import {CanvasRenderer} from "echarts/renderers"; 


use([CandlestickChart, GridComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps({
    data: {
        type: Array,
        default: () => []
    }
})

const option = computed(() => ({
    tooltip: { trigger: "axis" },
    xAxis: {
        type: "category",
        data: props.data.map(i => i.time)
    },
    yAxis: {type: "value"},
    series: [
        {
            type: "candlestick",
            data: props.data.map(i => [i.open, i.close, i.low, i.high])
        }
    ]
}))
</script>

<template>
    <v-chart :option="option" autoresize />
</template>