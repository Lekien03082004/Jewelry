from django.db import models
from django.utils.text import slugify
from autoslug import AutoSlugField
from my_jewelry.mixins import FileCleanupMixin
import uuid
import os
# Create your models here.

class Product(FileCleanupMixin,models.Model):
    file_fields = ['main_image']
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to='product_images/')
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    material = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug :
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        for image in self.images.all():# images là dựa vào related_name trong ProductImage
            image.delete()  # Gọi FileCleanupMixin.delete() của ProductImage
        super().delete(*args, **kwargs)  # Gọi FileCleanupMixin.delete() của Product
  
  
def product_image_path(instance, filename):
    ext = os.path.splitext(filename)[1] # Lay duoi file
    unique_name = f'{uuid.uuid4().hex}{ext}'
    return f'product_images/gallery/{unique_name}'

class ProductImage(FileCleanupMixin,models.Model):
    file_fields = ['image']
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_path)
    
    
class Category(models.Model):
    
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True) # Cach 2 tu dong tao slug tu name
    description = models.TextField()
    
    def __str__(self):
        return self.name
    