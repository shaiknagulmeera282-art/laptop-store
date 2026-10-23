
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session


app = FastAPI()


DATABASE_URL = (
    "postgresql+psycopg://postgres:nagul"
    "@localhost:5432/laptop_store;"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductResponse(ProductCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Laptop Store API"}


@app.post("/products", response_model=ProductResponse)
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = ProductDB(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

# 9. Get all laptops
@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db)
):
    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = data.name
    product.price = data.price
    product.quantity = data.quantity

    db.commit()
    db.refresh(product)

    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
