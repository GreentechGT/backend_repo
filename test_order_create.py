"""
Quick diagnostic script to test multi-vendor order creation.
Run: python test_order_create.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from orders.serializers import OrderSerializer
from orders.models import MainOrder, Order, OrderItem
from product.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("MULTI-VENDOR ORDER CREATION DIAGNOSTIC")
print("=" * 60)

user = User.objects.first()
if not user:
    print("ERROR: No user found in DB")
    sys.exit(1)
print(f"User: {user.email}")

products = list(Product.objects.exclude(vendor_id=None).all()[:3])
print(f"Products available: {len(products)}")
for p in products:
    print(f"  -> id={p.id}, name={p.name_en}, vendor_id={p.vendor_id}, price={p.price}")

if len(products) < 1:
    print("ERROR: No products with vendor_id found")
    sys.exit(1)

# --- TEST 1: Single vendor ---
print("\n--- TEST 1: Single vendor (should trigger Razorpay) ---")
data_single = {
    'items': [{'product_id': products[0].id, 'quantity': 1, 'price': str(products[0].price)}],
    'full_name': 'Test User',
    'phone': '9999999999',
    'address': '1 Test St',
    'city': 'Mumbai',
    'pincode': '400001',
    'payment_method': 'online',
}
s = OrderSerializer(data=data_single)
if s.is_valid():
    try:
        o = s.save(user=user)
        print(f"  SUCCESS -> SubOrder id={o.id}, vendor={o.vendor_id}")
        print(f"  MainOrder id={o.main_order.id}, is_multi_vendor={o.main_order.is_multi_vendor}, status={o.main_order.status}")
    except Exception as e:
        import traceback
        print(f"  FAILED: {e}")
        traceback.print_exc()
else:
    print(f"  VALIDATION ERROR: {s.errors}")

# --- TEST 2: Multi vendor ---
if len(products) >= 2:
    # Get 2 products with different vendors
    p1 = products[0]
    p2 = next((p for p in products[1:] if p.vendor_id != p1.vendor_id), None)

    if p2:
        print(f"\n--- TEST 2: Multi-vendor (vendors: {p1.vendor_id} + {p2.vendor_id}) ---")
        data_multi = {
            'items': [
                {'product_id': p1.id, 'quantity': 1, 'price': str(p1.price)},
                {'product_id': p2.id, 'quantity': 1, 'price': str(p2.price)},
            ],
            'full_name': 'Multi Vendor User',
            'phone': '8888888888',
            'address': '2 Vendor St',
            'city': 'Delhi',
            'pincode': '110001',
            'payment_method': 'cod',
        }
        s2 = OrderSerializer(data=data_multi)
        if s2.is_valid():
            try:
                o2 = s2.save(user=user)
                print(f"  SUCCESS -> SubOrder id={o2.id}, vendor={o2.vendor_id}")
                print(f"  MainOrder id={o2.main_order.id}, is_multi_vendor={o2.main_order.is_multi_vendor}, status={o2.main_order.status}")
                all_sub = Order.objects.filter(main_order=o2.main_order)
                print(f"  Total sub-orders created: {all_sub.count()}")
                for sub in all_sub:
                    print(f"    SubOrder id={sub.id}, vendor={sub.vendor_id}, total={sub.total_amount}")
            except Exception as e:
                import traceback
                print(f"  FAILED: {e}")
                traceback.print_exc()
        else:
            print(f"  VALIDATION ERROR: {s2.errors}")
    else:
        print("\n--- TEST 2: SKIPPED (all products have same vendor_id) ---")
        print("  All products belong to same vendor, cannot test multi-vendor")
else:
    print("\n--- TEST 2: SKIPPED (need at least 2 products) ---")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
