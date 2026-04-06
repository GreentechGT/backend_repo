from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        phone = extra_fields.get('phone')
        if not email and not phone:
            raise ValueError('Either Email or Phone must be set')
        if email:
            email = self.normalize_email(email)
            # Real email provided - not verified yet (requires OTP)
            extra_fields.setdefault('email_verified', False)
        else:
            # Phone-only registration: auto-generate placeholder email
            email = f"{phone}@noemail.local"
            # Phone was used to register - mark it as verified
            extra_fields.setdefault('phone_verified', True)
            extra_fields.setdefault('email_verified', False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # Remove username field
    first_name = None
    last_name = None

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]

    email = models.EmailField(unique=True, blank=True, null=True)
    user_id = models.CharField(max_length=50, unique=True, blank=True, null=True, db_index=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Verification status
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    # Push notification token
    push_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class Customer(models.Model):
    cust_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255) # Stored as raw/hashed temporarily
    
    # Verification fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.cust_id:
            import random
            from datetime import datetime
            prefix = f"CUST-{datetime.now().year}-"
            random_suffix = random.randint(1000, 9999)
            self.cust_id = f"{prefix}{random_suffix}"
            
            while Customer.objects.filter(cust_id=self.cust_id).exists():
                random_suffix = random.randint(1000, 9999)
                self.cust_id = f"{prefix}{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cust_id} - {self.name}"

class Address(models.Model):
    # ... (Address remains unchanged)
    ADDRESS_TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Office', 'Office'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=50, default='Home')

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_type}: {self.address}"

class Vendor(models.Model):
    vendor_id = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    
    # Personal Info
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    personal_id_proof = models.ImageField(upload_to='vendors/personal_ids/', blank=True, null=True)
    
    # Shop Info
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    shop_location = models.CharField(max_length=255)
    shop_id_proof = models.ImageField(upload_to='vendors/shop_ids/', blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    banner_image = models.ImageField(upload_to='vendors/banners/', blank=True, null=True)
    logo_image = models.ImageField(upload_to='vendors/logos/', blank=True, null=True)
    
    # Business Info
    business_name = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    fssai_license = models.CharField(max_length=14, blank=True, null=True)
    
    # Bank Info
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    account_type = models.CharField(max_length=20, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    
    # Verification
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate vendor_id on creation
        if not self.vendor_id:
            import datetime
            import random
            year = datetime.datetime.now().year
            prefix = f"VEN-{year}-"
            random_suffix = random.randint(1000, 9999)
            self.vendor_id = f"{prefix}{random_suffix}"
            
            while Vendor.objects.filter(vendor_id=self.vendor_id).exists():
                random_suffix = random.randint(1000, 9999)
                self.vendor_id = f"{prefix}{random_suffix}"

        # Handle Account Creation on Verification
        is_new = self.pk is None
        old_verified = False
        if not is_new:
            try:
                old_verified = Vendor.objects.get(pk=self.pk).verified
            except Vendor.DoesNotExist:
                pass

        # If it's new and verified, or if verified status just changed to True
        if (is_new and self.verified) or (not is_new and self.verified and not old_verified):
            print(f"DEBUG: Vendor {self.vendor_id} is being verified. Attempting user creation...")
            from django.db.models import Q
            existing_user = User.objects.filter(Q(email=self.email) | Q(phone=self.phone)).first()
            
            if not existing_user:
                try:
                    User.objects.create_user(
                        email=self.email,
                        phone=self.phone,
                        full_name=self.name,
                        password=self.password,
                        role='vendor',
                        user_id=self.vendor_id
                    )
                    print(f"DEBUG: Successfully created new User for vendor {self.vendor_id}")
                except Exception as e:
                    print(f"DEBUG: Error creating User for vendor {self.vendor_id}: {str(e)}")
            else:
                # Update existing user role to vendor and link vendor_id
                try:
                    existing_user.role = 'vendor'
                    existing_user.user_id = self.vendor_id
                    existing_user.save()
                    print(f"DEBUG: Updated existing User ({existing_user.email}) role to vendor and linked vendor_id")
                except Exception as e:
                    print(f"DEBUG: Error updating existing User: {str(e)}")

        super().save(*args, **kwargs)

        # Sync Shop details automatically when verified
        if self.verified and getattr(self, 'vendor_id', None):
            try:
                from product.models import ShopDetail
                ShopDetail.objects.update_or_create(
                    vendor=self,
                    defaults={
                        'shop_name_en': self.shop_name,
                        'address_en': self.shop_address,
                    }
                )
            except Exception as e:
                print(f"DEBUG: Error auto-syncing ShopDetail for vendor {self.vendor_id}: {str(e)}")

    def __str__(self):
        return f"{self.vendor_id} - {self.shop_name} ({self.name})"
