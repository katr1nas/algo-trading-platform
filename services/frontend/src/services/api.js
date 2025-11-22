export async function getRSI(close, period) {
  const response = await fetch("http://localhost:8000/api/v1/indicators/rsi", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ close, period })
  });

  return await response.json();
}
