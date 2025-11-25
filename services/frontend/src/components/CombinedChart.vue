<script setup>
import PriceChart from './PriceChart.vue';
import RsiChart from './RsiChart.vue';

const props = defineProps({
    price: Array,
    rsi: Array
});
</script>

<template>
    <div>
        <div> style="height:400px; margin-bottomo:20px;">
            <PriceChart 
            :data="price" 
            :buySignals="buySignals"
            :sellSignals="sellSignals"/>
        </div>

        <div style="height:200px;">
            <RsiChart :rsi="rsi" />
        </div>
    </div>
</template>