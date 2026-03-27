import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from product.models import Product, ShopDetail
from users.models import User

def debug_vendor_products():
    # Try to find a vendor user
    vendor_user = User.objects.filter(role='vendor').first()
    if not vendor_user:
        print("No vendor user found.")
        return

    print(f"Testing for user: {vendor_user.email}, user_id: {vendor_user.user_id}")
    
    vendor_id = vendor_user.user_id
    try:
        shop_detail = ShopDetail.objects.get(vendor__vendor_id=vendor_id)
        print(f"Shop Detail found: {shop_detail.shop_name_en}")
        products = Product.objects.filter(shop_detail=shop_detail).select_related('category', 'shop_detail')
        print(f"Products count: {products.count()}")
        for p in products:
            print(f" - {p.name_en} (Stock: {p.stock_quantity})")
    except ShopDetail.DoesNotExist:
        print("ShopDetail.DoesNotExist for this vendor_id")
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vendor_products()
