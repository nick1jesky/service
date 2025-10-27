from database.crud import order_crud, product_crud, order_item_crud
from database.database import db
from fastapi import HTTPException, status
from typing import Dict, Any

class OrderProcessor:
    def __init__(self):
        pass

    async def check_order_existence(self, order_id: int) -> Dict[str, Any]:
        order = await order_crud.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )
        return order

    async def check_order_not_closed(self, order: Dict[str, Any]) -> None:
        if order.get('closed_at') is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add items to closed order"
            )

    async def check_product_availability(self, product_id: int, requested_quantity: int) -> Dict[str, Any]:
        product = await product_crud.get_product_with_lock(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        if product['quantity'] < requested_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient product quantity. Available: {product['quantity']}, requested: {requested_quantity}"
            )
        
        return product

    async def add_or_update_order_item(self, order_id: int, product_id: int, quantity: int) -> str:
        existing_item = await order_item_crud.get_order_item(order_id, product_id)
        
        if existing_item:
            new_quantity = existing_item['quantity'] + quantity
            success = await order_item_crud.update_order_item_quantity(order_id, product_id, new_quantity)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update order item"
                )
            return f"Product quantity updated to {new_quantity}"
        else:
            success = await order_item_crud.insert_order_item(order_id, product_id, quantity)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add product to order"
                )
            return "Product added to order"

    async def update_product_inventory(self, product_id: int, current_quantity: int, sold_quantity: int) -> None:
        new_quantity = current_quantity - sold_quantity
        success = await product_crud.update_product_quantity(product_id, new_quantity)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update product inventory"
            )

    async def process_add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> str:
        async with db.transaction(): 
            order = await self.check_order_existence(order_id)
            await self.check_order_not_closed(order)
            product = await self.check_product_availability(product_id, quantity)
            message = await self.add_or_update_order_item(order_id, product_id, quantity)
            await self.update_product_inventory(product_id, product['quantity'], quantity)
        return message

    async def get_order_details(self, order_id: int) -> Dict[str, Any]:
        order = await self.check_order_existence(order_id)
        items = await order_item_crud.get_order_items(order_id)
        
        return {
            "order": order,
            "items": items
        }

order_processor = OrderProcessor()