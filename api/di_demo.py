"""
依赖注入(Dependency Injection / Depends)入门 —— 阶段 B 收尾项

回顾关 F2 的 todo_api.py:每个接口都手写了一遍
    db = SessionLocal()
    ... 干活 ...
    db.close()
6 个接口写 6 遍。写第 7 个的时候忘了 close() 会怎样?不会有任何报错,
只是连接慢慢泄漏 —— 又是那种"不报错的 bug"。

FastAPI 的 Depends 就是来消灭这种重复的:
    "我只在参数里声明我需要什么,FastAPI 负责在我被调用前准备好、调用完收尾。"

一句话:依赖 = 这个接口运行前必须先准备好的东西;
       注入 = 由框架塞进参数,而不是你自己 new / 自己 close。

运行(必须在 api 目录下启动,否则会新建一个空库):
    python -m uvicorn di_demo:app --reload
然后打开 http://127.0.0.1:8000/docs 挨个点 Try it out
"""
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy import create_engine, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

# ---------------- 数据库(和 todo_api.py 同一套写法) ----------------
engine = create_engine(
    "sqlite:///di_demo.db",
    connect_args={"check_same_thread": False},  # FastAPI 用线程池跑同步函数,SQLite 默认禁止连接跨线程
)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    done: Mapped[bool] = mapped_column(Boolean, default=False)


Base.metadata.create_all(engine)  # 只在表不存在时建表
SessionLocal = sessionmaker(bind=engine)


# ---------------- 依赖 1:数据库会话(最常用的一种依赖) ----------------
def get_db():
    """yield 之前 = 开工前的准备;yield 之后 = 用完后的收尾。

    FastAPI 会在调用接口函数**之前**执行到 yield,把 db 交给接口;
    接口返回后(哪怕中间抛了异常)再回来执行 finally。
    所以"忘记 close()"这个错误从此不可能发生 —— 这就是依赖注入最实际的价值。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- 依赖 2:公共查询参数(很多接口都要的分页条件) ----------------
def common_params(
    limit: int = Query(10, gt=0, le=100, description="最多返回几条"),
    offset: int = Query(0, ge=0, description="跳过前几条"),
):
    """依赖不一定和数据库有关:任何"每个接口都要先算一遍"的东西都能做成依赖。"""
    return {"limit": limit, "offset": offset}


app = FastAPI(title="依赖注入入门", description="关 F2 的重复代码,用 Depends 消掉")


# ---------------- 用法:在参数里写 Depends(谁),FastAPI 就把结果塞进来 ----------------
@app.get("/items", summary="列表(带分页)")
def list_items(p: dict = Depends(common_params), db: Session = Depends(get_db)):
    rows = db.query(Item).offset(p["offset"]).limit(p["limit"]).all()
    return [{"id": r.id, "name": r.name, "done": r.done} for r in rows]


@app.post("/items", summary="新增一条")
def add_item(name: str, db: Session = Depends(get_db)):
    item = Item(name=name)
    db.add(item)          # 草稿箱
    db.commit()           # 点发送
    db.refresh(item)      # 从数据库把 id 拿回来(不 refresh 就读不到 id)
    return {"id": item.id, "name": item.name, "done": item.done}


@app.put("/items/{item_id}", summary="改完成状态")
def update_item(item_id: int, done: bool, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="没有这条记录")  # 这行需要 from fastapi import HTTPException
    item.done = done
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "done": item.done}


@app.delete("/items/{item_id}", summary="删除")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="没有这条记录")
    db.delete(item)       # 参数是"记录对象",不是类
    db.commit()           # 不 commit 不报错,但数据还在
    return {"deleted": item_id}


# ---------------- 留给你的练习 ----------------
# 1) 把 todo_api.py 也改成用上面这个 get_db:删掉 6 个接口里重复的
#    db = SessionLocal() / db.close(),改成 db: Session = Depends(get_db)。
#    改完刷新 /docs —— 接口的行为应该一模一样,但代码短了一截。
# 2) 想一个你自己项目里的重复代码(比如"每个接口都要先检查 API Key"),
#    它能不能也变成一个依赖?
#
# 面试自问:
#   ① 依赖注入解决什么问题?(答:把"准备工作/收尾工作"从每个接口里抽出来,只写一次,靠框架保证执行)
#   ② get_db 里为什么要用 yield 而不是 return?(答:yield 才能把"收尾"写在后面并保证一定执行)
