from fastapi import APIRouter

router = APIRouter()

@router.post("/rsi-strategy")
def rsi_strategy(rsi: list[float]):
    signals = []

    for i, value in enumerate(rsi):
        if value < 30:
            signals.append({"index" :i, "type": 'buy'})
        elif value > 70:
            signals.append({"index": i, "type": "sell"})
    
    return {"signals": signals}
