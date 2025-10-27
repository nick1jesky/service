from server.models import AddItemRequest, OrderItemResponse
from server.order_processing import order_processor
from fastapi import HTTPException, status

class OrderHandlers:
    def __init__(self):
        pass
    
    async def add_item_to_order(self, item: AddItemRequest) -> OrderItemResponse:
        try:
            message = await order_processor.process_add_item_to_order(
                item.order_id, item.product_id, item.quantity
            )
            
            return OrderItemResponse(
                order_id=item.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                message=message
            )
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    async def get_order_items(self, order_id: int) -> dict:
        try:
            return await order_processor.get_order_details(order_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

order_handlers = OrderHandlers()
