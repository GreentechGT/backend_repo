import os
import sys
import django

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk_delivery_backend.settings')
django.setup()

from promotion.models import Banner

BANNERS = [
    {
        "title": "Fresh Milk Daily",
        "subtitle": "Subscribe & Save 10% Every Month",
        "color": "bg-blue-600",
        "image": 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=400&q=80',
    },
    {
        "title": "Traditional Ghee",
        "subtitle": "The Purity of Bilona Method",
        "color": "bg-orange-500",
        "image": 'https://images.unsplash.com/photo-1625944525335-473db7a5f4c5?auto=format&fit=crop&w=600&h=600&q=80',
    },
    {
        "title": "Breakfast Essentials",
        "subtitle": "Eggs & Butter Delivered by 7 AM",
        "color": "bg-green-600",
        "image": "https://images.unsplash.com/photo-1506976785307-8732e854ad03?auto=format&fit=crop&w=800&q=80",
    },
    {
        "title": "Summer Chills",
        "subtitle": "Refreshing Beverages & Yogurts",
        "color": "bg-purple-500",
        "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=800&q=80",
    },
]

def upload_banners():
    print("Starting banner upload...")
    for i, data in enumerate(BANNERS):
        banner, created = Banner.objects.get_or_create(
            title=data['title'],
            defaults={
                'subtitle': data['subtitle'],
                'color': data['color'],
                'image': data['image'],
                'order': i,
                'is_active': True
            }
        )
        if created:
            print(f"Created banner: {banner.title}")
        else:
            print(f"Banner already exists: {banner.title}")
            # Update fields anyway to match mock data
            banner.subtitle = data['subtitle']
            banner.color = data['color']
            banner.image = data['image']
            banner.order = i
            banner.save()
            print(f"Updated banner: {banner.title}")
    print("Banner upload complete!")

if __name__ == "__main__":
    upload_banners()
