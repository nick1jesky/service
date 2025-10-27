import fastapi
from fastapi import HTTPException, status
from database.database import db
from server.models import AddItemRequest, OrderItemResponse
from server.order_handling import order_handlers



async def lifespan(app: fastapi.FastAPI):
    print("Creating async context manager")
    try:
        await db.connect()
        print("Database connection established")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    print("Closing async context manager")
    try:
        await db.disconnect()
        print("Database connection closed")
    except Exception as e:
        print(f"Error disconnecting from database: {e}")

app = fastapi.FastAPI(
    title="Order service API",
    description="REST API для добавления ордеров в",
    version="1.0.0",
    lifespan=lifespan
)


@app.get(
    path="/healthcheck",
    description="Проверка жизнеспособности сервиса"
)
async def healthcheck():
    try:
        await db.fetch("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


# Управление продуктами в заказе

# Добавление продукта в заказ
@app.post(
    path="/orders/{order_id}/items",
    response_model=OrderItemResponse,
    summary="Add product to order",
    description="Добавление продукта в заказ. В случае наличия увеличение количества."
)
async def add_item_to_order(item: AddItemRequest):
    return await order_handlers.add_item_to_order(item)

# Получение продуктов заказа
@app.get(
    path="/orders/{order_id}/items",
    description="Получение продуктов заказа"
)
async def get_order_items(order_id: int):
    return await order_handlers.get_order_items(order_id)
