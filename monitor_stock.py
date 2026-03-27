import os
import django
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from product.models import Product

def monitor_stock(product_id, duration_seconds=120):
    print(f"Monitoring Product {product_id} for {duration_seconds} seconds...")
    last_stock = None
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        try:
            p = Product.objects.get(id=product_id)
            if p.stock_quantity != last_stock:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Stock changed: {last_stock} -> {p.stock_quantity}")
                last_stock = p.stock_quantity
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(1)
    
    print("Monitoring ended.")

if __name__ == "__main__":
    monitor_stock(6)
