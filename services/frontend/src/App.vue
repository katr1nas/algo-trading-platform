<script setup>
import { ref } from "vue";
import { getRSI } from "./services/api.js";

const closeData = ref("");
const period = ref(14);
const rsiValues = ref([]);    // <= точно создаём реактивное значение

async function computeRSI() {
  const arr = closeData.value.split(",").map(Number);
  try {
    const result = await getRSI(arr, period.value);
    rsiValues.value = result.rsi;   // <= присваиваем корректно
  } catch (e) {
    console.error("RSI fetch error:", e);
  }
}
</script>

<template>
  <div>
    <h1>RSI Calculator</h1>

    <label>Close prices:</label>
    <input v-model="closeData" />

    <label>Period:</label>
    <input type="number" v-model="period" />

    <button @click="computeRSI">Compute</button>

    <div v-if="rsiValues && rsiValues.length">
      <pre>{{ rsiValues }}</pre>
    </div>
  </div>
</template>

