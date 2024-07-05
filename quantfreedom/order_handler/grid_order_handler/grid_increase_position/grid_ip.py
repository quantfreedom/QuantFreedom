from logging import getLogger
from quantfreedom.order_handler.grid_order_handler.grid_order_class.grid_order import GridOrderHandler
from quantfreedom.core.enums import OrderStatus

logger = getLogger()


class GridIncreasePosition(GridOrderHandler):
    def grid_increase_position(
        self,
        order_size: float,
        entry_price: float,
    ):
        try:
            abs_position_size_usd = abs(self.position_size_usd)
            total_position_size_usd = abs_position_size_usd + order_size
            
            position_size_asset = abs_position_size_usd / average_entry
            order_size_asset = order_size / entry_price
            total_asset_size = position_size_asset + order_size_asset

            average_entry = total_position_size_usd / total_asset_size
            
        except ZeroDivisionError:    
            average_entry = entry_price
        
        return average_entry