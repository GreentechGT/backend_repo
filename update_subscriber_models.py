import os

file_path = r'c:\Users\ARKAN\React Native\milk_delivery\backend\subscriptions\models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace MonthlySubscriber part
old_monthly = """                from orders.notifications import notify_subscription_status_change
                notify_subscription_status_change(self)"""
new_monthly = """                from orders.notifications import notify_subscription_status_change, notify_vendor_dashboard_refresh
                notify_subscription_status_change(self)
                # Also notify Vendor to refresh dashboard
                if self.plan and self.plan.vendor_id:
                    notify_vendor_dashboard_refresh(self.plan.vendor_id)"""

content = content.replace(old_monthly, new_monthly)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated MonthlySubscriber and YearlySubscriber (if matched).")
