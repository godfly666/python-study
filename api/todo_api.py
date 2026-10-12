from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# 1. 连接数据库:"sqlite:///todos.db" = 本目录下的 todos.db 文件
engine = create_engine("sqlite:///todos.db", connect_args={"check_same_thread": False})

# 2. 所有表都要继承这个基类(固定写法,照抄)
class Base(DeclarativeBase):
    pass

# 3. 用类描述一张表,表名叫 todos
class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)            # 主键:自动编号
    title: Mapped[str] = mapped_column(String(100))              # 普通字段:文字
    done: Mapped[bool] = mapped_column(Boolean, default=False)   # 普通字段:真假,默认 False

# 4. 真去数据库里把表建出来(表已存在就跳过)
Base.metadata.create_all(engine)
print("建表完成:study\\api\\todos.db")

app = FastAPI()                                  # 建应用

SessionLocal = sessionmaker(bind=engine)         # 会话工厂:要动数据库时找它要一个"会话"

class TodoCreate(BaseModel):                     # 规定客户端必须传什么
    title: str                                   # 只收一个 title
class TodoUpdate(BaseModel):      # PUT 要传什么
    title: str
    done: bool                    # 两个字段都要给
@app.post("/todos")                              # POST = 新增
def create_todo(data: TodoCreate):
    db = SessionLocal()                          # 1. 开会话
    todo = Todo(title=data.title)                # 2. 造一条记录(此时还在内存里)
    db.add(todo)                                 # 3. 放进"待保存"篮子
    db.commit()                                  # 4. 真的写进 todos.db
    db.refresh(todo)                             # 5. 从数据库读回来(为了拿到自动分配的 id)
    db.close()                                   # 6. 关会话
    return {"id": todo.id, "title": todo.title, "done": todo.done}

@app.get("/todos")
def list_todos():
    db = SessionLocal()
    todos = db.query(Todo).all()      # 拿到全部记录(一个 Todo 对象的列表)
    db.close()

    result = []                       # 空篮子,准备装结果
    for t in todos:                   # 一条一条拿出来处理
        result.append({               # 把它翻译成字典,扔进篮子
            "id": t.id,
            "title": t.title,
            "done": t.done,
        })
    return result                     # 把装好的列表返回出去
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    db = SessionLocal()
    todo = db.query(Todo).filter(Todo.id == todo_id).first()    # 空1:筛"id 等于几"
    db.close()

    if todo is None:                                        # 没查到
        raise HTTPException(status_code=404, detail="没有这条待办")

    return {                                                # 空2:翻成字典(你写过两遍了)
        "id": todo.id,
        "title": todo.title,
        "done": todo.done,
    }
@app.delete("/todos/{todo_id}")                    # 换成 delete
def delete_todo(todo_id: int):
    db = SessionLocal()
    todo = db.query(Todo).filter(Todo.id == todo_id).first()   # 跟查单条一模一样
    if todo is None:
        db.close()                                 # 先关会话,再抛错
        raise HTTPException(status_code=404, detail="没有这条待办")
    db.delete(todo)                                # 第一步:标记"这条要删"
    db.commit()                                    # 第二步:真的生效(忘了这句就删不掉)
    db.close()
    return {"msg": "已删除", "id": todo_id}         # 回一句确认
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, data: TodoUpdate):
    db = SessionLocal()
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        db.close()
        raise HTTPException(status_code=404, detail="没有这条待办")

    todo.title = data.title      # 改标题
    todo.done = data.done        # 改状态
    db.commit()                  # 提交生效
    db.refresh(todo)             # 提交后属性会"过期",这句从数据库读回来(不加就 500)
    db.close()
    return {"id": todo.id, "title": todo.title, "done": todo.done}