from django.core.management.base import BaseCommand
from promotion.models import Banner

class Command(BaseCommand):
    help = 'Load mock banner data into the database'

    def handle(self, *args, **kwargs):
        banners_data = [
            {
                'id': 1,
                'title_en': "Fresh Milk Daily",
                'title_hi': "ताज़ा दूध रोज़ाना",
                'title_mr': "दररोज ताजे दूध",
                'title_ur': "روزانہ تازہ دودھ",
                'subtitle_en': "Subscribe & Save 10% Every Month",
                'subtitle_hi': "सब्सक्राइब करें और हर महीने 10% बचाएं",
                'subtitle_mr': "सबस्क्राइब करा आणि दरमहा १०% वाचवा",
                'subtitle_ur': "سبسکرائب کریں اور ہر ماہ 10% بچائیں",
                'color': "bg-blue-600",
                'image': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=400&q=80',
                'product_ids': [1, 2, 3]
            },
            {
                'id': 2,
                'title_en': "Traditional Ghee",
                'title_hi': "पारंपरिक घी",
                'title_mr': "पारंपारिक तूप",
                'title_ur': "روایتی گھی",
                'subtitle_en': "The Purity of Bilona Method",
                'subtitle_hi': "बिलोना विधि की शुद्धता",
                'subtitle_mr': "बिलोना पद्धतीची शुद्धता",
                'subtitle_ur': "بلونا طریقہ کی پاکیزگی",
                'color': "bg-orange-500",
                'image': 'https://images.unsplash.com/photo-1625944525335-473db7a5f4c5?auto=format&fit=crop&w=600&h=600&q=80',
                'product_ids': [7]
            },
            {
                'id': 3,
                'title_en': "Breakfast Essentials",
                'title_hi': "नाश्ते की ज़रूरी चीज़ें",
                'title_mr': "नाश्त्याच्या आवश्यक वस्तू",
                'title_ur': "ناشتے کی ضروریات",
                'subtitle_en': "Eggs & Butter Delivered by 7 AM",
                'subtitle_hi': "अंडे और मक्खन सुबह 7 बजे तक पहुँचाए जाएँगे",
                'subtitle_mr': "अंडी आणि लोणी सकाळी ७ वाजेपर्यंत पोहोचवले जातील",
                'subtitle_ur': "انڈے اور مکھن صبح 7 بجے تک پہنچا دیے جائیں گے",
                'color': "bg-green-600",
                'image': "https://images.unsplash.com/photo-1506976785307-8732e854ad03?auto=format&fit=crop&w=800&q=80",
                'product_ids': [6, 8]
            },
            {
                'id': 4,
                'title_en': "Summer Chills",
                'title_hi': "गर्मियों की ठंडक",
                'title_mr': "उन्हाळ्यातील थंडावा",
                'title_ur': "گرمیوں کی ٹھنڈک",
                'subtitle_en': "Refreshing Beverages & Yogurts",
                'subtitle_hi': "ताज़ा पेय और दही",
                'subtitle_mr': "ताजेतवाने पेये आणि दही",
                'subtitle_ur': "فرحت بخش مشروبات اور دہی",
                'color': "bg-purple-500",
                'image': "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=800&q=80",
                'product_ids': [9, 10]
            },
        ]

        for data in banners_data:
            banner_id = data.pop('id')
            product_ids = data.pop('product_ids', [])
            banner, created = Banner.objects.update_or_create(id=banner_id, defaults=data)
            
            # Set many-to-many relationship (only for existing products)
            if product_ids:
                from product.models import Product
                existing_product_ids = Product.objects.filter(id__in=product_ids).values_list('id', flat=True)
                banner.products.set(existing_product_ids)
                if len(existing_product_ids) < len(product_ids):
                    self.stdout.write(self.style.WARNING(f'Linked {len(existing_product_ids)}/{len(product_ids)} products for banner {banner_id} (some products missing)'))

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(banners_data)} banners'))
