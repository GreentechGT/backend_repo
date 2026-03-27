from product.models import Product
from subscriptions.models import Subscription

def update_data():
    # Find a product
    p = Product.objects.filter(name_en__icontains='Milk').first()
    if not p:
        p = Product.objects.first()
    
    if not p:
        print("No products found.")
        return

    # Clear existing to avoid confusion (optional, but cleaner for testing)
    # Subscription.objects.all().delete()

    plans = [
        {
            'plan_name_en': 'Monthly Basic',
            'plan_name_hi': 'मासिक बेसिक',
            'plan_name_mr': 'मासिक बेसिक',
            'plan_name_ur': 'ماہانہ بنیادی',
            'desc_en': 'Essential milk delivery for small families',
            'desc_hi': 'छोटे परिवारों के लिए आवश्यक दूध वितरण',
            'desc_mr': 'लहान कुटुंबांसाठी आवश्यक दूध वितरण',
            'desc_ur': 'چھوٹے خاندانوں کے لیے ضروری دودھ کی فراہمی',
            'category': 'Monthly Essentials',
            'is_best_value': False,
            'original_price': 1500,
            'total_amount': 1200,
            'unit': 'Monthly',
            'frequency': 'monthly',
        },
        {
            'plan_name_en': 'Monthly Organic',
            'plan_name_hi': 'मासिक ऑर्गेनिक',
            'plan_name_mr': 'मासिक सेंद्रिय',
            'plan_name_ur': 'ماہانہ آرگینک',
            'desc_en': 'Pure organic milk for health-conscious users',
            'desc_hi': 'स्वास्थ्य के प्रति जागरूक उपयोगकर्ताओं के लिए शुद्ध जैविक दूध',
            'desc_mr': 'आरोग्याबद्दल जागरूक वापरकर्त्यांसाठी शुद्ध सेंद्रिय दूध',
            'desc_ur': 'صحت سے آگاہ صارفین کے لیے خالص نامیاتی دودھ',
            'category': 'Monthly Organic',
            'is_best_value': True,
            'original_price': 2200,
            'total_amount': 1800,
            'unit': 'Monthly',
            'frequency': 'monthly',
            'discount': '15% OFF'
        },
        {
            'plan_name_en': 'Yearly Family Premium',
            'plan_name_hi': 'वार्षिक फैमिली प्रीमियम',
            'plan_name_mr': 'वार्षिक फॅमिली प्रीमियम',
            'plan_name_ur': 'سالانہ فیملی پریمیم',
            'desc_en': 'Best value for big families. Save more annually!',
            'desc_hi': 'बड़े परिवारों के लिए सबसे अच्छा मूल्य। सालाना अधिक बचत करें!',
            'desc_mr': 'मोठ्या कुटुंबांसाठी सर्वोत्तम मूल्य. वार्षिक अधिक बचत करा!',
            'desc_ur': 'بڑے خاندانوں کے لیے بہترین قیمت۔ سالانہ مزید بچت کریں!',
            'category': 'Yearly Family Packs',
            'is_best_value': True,
            'original_price': 18000,
            'total_amount': 15000,
            'unit': 'Yearly',
            'frequency': 'yearly',
            'discount': '20% OFF'
        },
        {
            'plan_name_en': 'Daily Fresh Trial',
            'plan_name_hi': 'दैनिक ताजा ट्रायल',
            'plan_name_mr': 'दैनिक ताजे ट्रायल',
            'plan_name_ur': 'روزانہ تازہ ٹرائل',
            'desc_en': 'One week trial of fresh milk',
            'desc_hi': 'ताजा दूध का एक सप्ताह का परीक्षण',
            'desc_mr': 'ताजे दूध दररोज पोहोचवले जाते',
            'desc_ur': 'تازہ دودھ کا ایک ہفتہ کا ٹرائل',
            'category': 'Monthly Essentials',
            'is_best_value': False,
            'original_price': 350,
            'total_amount': 300,
            'unit': 'Weekly',
            'frequency': 'daily',
        }
    ]

    for plan_data in plans:
        Subscription.objects.update_or_create(
            plan_name_en=plan_data['plan_name_en'],
            defaults={
                'product': p,
                **plan_data
            }
        )
        print(f"Synced plan: {plan_data['plan_name_en']}")

if __name__ == "__main__":
    update_data()
