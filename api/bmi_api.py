from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/hello/{name}")
def hello(name: str):
    return {"你好": name}

@app.get("/bmi")
def bmi(height: float = Query(gt=0), weight: float = Query(gt=0)):
    value = weight / (height ** 2)

    if value < 18.5:
        evaluate = "偏瘦"
    elif value < 24:  # 走到这里,必然已经 ≥18.5
        evaluate = "正常"
    elif value < 28:  # 走到这里,必然已经 ≥24
        evaluate = "超重"
    else:  # 剩下的都是 ≥28
        evaluate = "肥胖"
    return {"bmi": round(value, 2), "评价": evaluate}
