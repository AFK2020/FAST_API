from enum import Enum
from fastapi import FastAPI, HTTPException,Depends
from application.models import Employee
from sqlalchemy.orm import Session

from . import crud, models, schemas, database


app = FastAPI()


# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/")
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = crud.create_employee(db=db, employee=employee)
    return db_employee


"""
@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/items/me")
# async def read_item():
#     return {"item : me"}



# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.post("/users/")
def create_user(user: User):
    return {"username": user.username, "email": user.email}













class Category(Enum):
    TOOLS = "tools"
    CONSUMABLES = "consumeables"


class Item(BaseModel):
    name: str
    price : float
    count : int
    id: int
    category: Category

items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="Pliers", price=5.99, count=20, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=1.99, count=100, id=2, category=Category.CONSUMABLES),
}


# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@app.get("/")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}


@app.get("/items/{item_id}")
def query_item_by_id(item_id: int) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} does not exsist.")
    
    return items[item_id]



# Function parameters that are not path parameters can be specified as query parameters in the URL
# Here we can query items like this /items?count=20
Selection = dict[
    str, str | int | float | Category | None
]  # dictionary containing the user's query arguments



@app.get("/items/")
def query_item_by_parameters(
    name: str | None = None,
    price: float | None = None,
    count: int | None = None,
    category: Category | None = None,
) -> dict[str, Selection | list[Item]]:
    def check_item(item: Item):
        # Check if the item matches the query arguments from the outer scope.
        return all(
            (
                name is None or item.name == name,
                price is None or item.price == price,
                count is None or item.count != count,
                category is None or item.category is category,
            )
        )

    selection = [item for item in items.values() if check_item(item)]
    return {
        "query": {"name": name, "price": price, "count": count, "category": category},
        "selection": selection,
    }

    """