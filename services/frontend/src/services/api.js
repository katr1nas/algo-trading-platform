import axios from "axios";


const api = axios.create({
    baseURL: "http://localhost:8000/api/v1",
    headers: {"Content-Type": "application/json"}
});


export async function getRSI(close, period) {
  const {data} = await api.post("/indicators/rsi", { close, period});
  return data;
}

export async function getOHLC(symbol, timeframe="1h") {
    const { data } = await api.get("/price", {
        params: {symbol, timeframe}
    });
    return data;
}

export async function gerRSIStrategy(rsi) {
    const { data } = await api.post("/strategies/rsi-strategy", { rsi });
    return data;
}