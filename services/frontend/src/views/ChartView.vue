<script setup>
import {ref, onMounted} from 'vue'
import { getOHLC, getRSI } from '@services/api'
import CombinedChart from "@/components/CimbineChar.vue";

const price = ref([]);
const rsi = ref([]);

async function load(symbol = "GOLD") {
    const ohlc = await getOHLC(symbol);

    price.value = ohlc;

    const closeArray = ohlc.map(c => c.close);

    const rsiResponse = await getRSI(closeArray, 14);

    rsi.value = rsiResponse.values;
}

onMounted(() => {
    load("GOLD");
});
</script>

<template>
    <div>
        <CombinedChart :price="price" :rsi="rsi" />
    </div>
</template>