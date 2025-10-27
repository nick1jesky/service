from typing import Optional, List, Dict, Any
from .database import db


QUERY_GET_ORDER = "SELECT * FROM orders WHERE id = %s"

class OrderCRUD:
    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        return await db.fetchrow(
            QUERY_GET_ORDER,
            order_id
        )

QUERY_GET_PRODUCT = "SELECT * FROM products WHERE id = %s FOR UPDATE"
QUERY_UPDATE_PRODUCT_QUANTITY = "UPDATE products SET quantity = %s WHERE id = %s"

class ProductCRUD:
    async def get_product_with_lock(self, product_id: int) -> Optional[Dict[str, Any]]:
        return await db.fetchrow(
            QUERY_GET_PRODUCT,
            product_id
        )
    
    async def update_product_quantity(self, product_id: int, new_quantity: int) -> bool:
        count = await db.execute(
            QUERY_UPDATE_PRODUCT_QUANTITY,
            new_quantity, product_id
        )
        return count > 0
      

QUERY_GET_ORDER_ITEM =  "SELECT * FROM order_items WHERE order_id = %s AND product_id = %s"
QUERY_INSERT_ORDER_ITEM = "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)"
QUERY_UPDATE_ORDER_ITEM_QUANTITY = "UPDATE order_items SET quantity = %s WHERE order_id = %s AND product_id = %s"
QUERY_GET_ORDER_ITEMS = """
SELECT oi.*, p.name as product_name, p.price 
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id 
            WHERE oi.order_id = %s
"""

class OrderItemCRUD:
    async def get_order_item(self, order_id: int, product_id: int) -> Optional[Dict[str, Any]]:
        return await db.fetchrow(
           QUERY_GET_ORDER_ITEM,
            order_id, product_id
        )
    
    async def insert_order_item(self, order_id: int, product_id: int, quantity: int) -> bool:
        try:
            count = await db.execute(
                QUERY_INSERT_ORDER_ITEM,
                order_id, product_id, quantity
            )
            return count > 0
        except Exception:
            return False
    
    async def update_order_item_quantity(self, order_id: int, product_id: int, quantity: int) -> bool:
        count = await db.execute(
            QUERY_UPDATE_ORDER_ITEM_QUANTITY,
            quantity, order_id, product_id
        )
        return count > 0
    
    async def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        return await db.fetch(
            QUERY_GET_ORDER_ITEMS,
            order_id
        )

order_crud = OrderCRUD()
product_crud = ProductCRUD()
order_item_crud = OrderItemCRUD()