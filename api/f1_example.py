# /docs 页面 = FastAPI 根据代码自动生成的接口文档(Swagger UI),
# 点 "Try it out" 就能在网页上直接调接口——它就是图形化的"调用程序"。
from fastapi import FastAPI, Query

app = FastAPI()


# 示例 1:路径参数 —— 值写在网址"路"里
# 浏览器打开:http://127.0.0.1:8000/hello/李安杰
@app.get("/hello/{name}")
def hello(name: str):
    return {"你好": name}


# 示例 2:查询参数 + 自动校验 —— 值写在问号后面,负数会被 FastAPI 挡掉(自动返回 422)
# 浏览器打开:http://127.0.0.1:8000/area?r=3
@app.get("/area")
def area(r: float = Query(gt=0, description="半径,必须大于 0")):
    s = 3.14159 * r * r
    return {"半径": r, "面积": round(s, 2)}
