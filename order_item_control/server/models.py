from pydantic import BaseModel, Field

class AddItemRequest(BaseModel):
    order_id: int = Field(gt=0, description="order_id")
    product_id: int = Field(gt=0, description="product id")
    quantity: int = Field(gt=0, description="quantity")

class OrderItemResponse(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    message: str
    