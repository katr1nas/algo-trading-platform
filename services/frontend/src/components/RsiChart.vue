<script setup>
import { defineProps } from 'vue';
import VChart from 'vue-echarts';

const props = defineProps({
    rsi: {
        type: Array,
        default: () => []
    }
});

const option = computed(() => ({
    tooltip: {trigger: "axis"},
    xAxis: {
        type: "category",
        data: props.rsi.map((_, i) => i)
    },
    yAxis: {type: "valies"},
    series: [
        {
            type: 'line',
            data: props.rsi
        }
    ]
}));
</script>

<template>
    <v-chart :option="option" autoresize/>
</template>