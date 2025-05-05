from playwright.async_api import async_playwright
from ..base_providers import OrderExecutionProvider
from typing import Dict, Any
import time
import random

class PlaywrightOrderProvider(OrderExecutionProvider):
    def __init__(self, playwright, headless: bool = True):
        self.headless = headless
        self.playwright = playwright
        self.browser = self.playwright.chromium.launch(headless=headless)
        
    def execute_order(self, product_info: Dict[str, Any], quantity: int) -> Dict[str, Any]:
        """Execute order using browser automation."""
        try:
            page = self.browser.new_page()
            
            # Navigate to product page
            page.goto(product_info['url'])
            
            # Wait for page to load
            page.wait_for_load_state("networkidle")
            
            # Find and fill quantity
            quantity_input = page.locator("input[type='number']").first
            if quantity_input:
                quantity_input.fill(str(quantity))
            
            # Find and click add to cart
            add_to_cart = page.locator("button:has-text('Add to Cart')").first
            if add_to_cart:
                add_to_cart.click()
            
            # Wait for cart to update
            time.sleep(2)
            
            # Generate order tracking info
            order_id = f"ORD-{random.randint(10000, 99999)}"
            tracking_number = f"TRK-{random.randint(1000000, 9999999)}"
            
            # Close browser
            page.close()
            
            return {
                "order_id": order_id,
                "product": product_info['title'],
                "price": product_info['price'],
                "quantity": quantity,
                "status": "Order placed successfully",
                "tracking_number": tracking_number,
                "estimated_delivery": self._generate_estimated_delivery()
            }
            
        except Exception as e:
            print(f"Error in order execution: {str(e)}")
            return {
                "status": "Order failed",
                "error": str(e)
            }
    
    def _generate_estimated_delivery(self) -> str:
        from datetime import datetime, timedelta
        delivery_days = random.randint(3, 14)
        delivery_date = datetime.now() + timedelta(days=delivery_days)
        return delivery_date.strftime("%Y-%m-%d")
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop() 