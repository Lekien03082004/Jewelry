from rest_framework import serializers
from .models import Product, ProductImage, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        
class ProductImageSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product']
        
class ProductListSerializer(serializers.ModelSerializer): 
    category = CategorySerializer(read_only=True)      
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'main_image', 'category','material', "description",'created_at', 'updated_at']

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class ProductWriteSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'slug', 'price', 'main_image', 'quantity','images', 'category', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)

        for image in images:
            ProductImage.objects.create(
                product=product,
                image=image
            )

        return product
    
    def update(self, instance, validated_data):
        images = validated_data.pop('images', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if images is not None:
            # Xóa file vật lý trên storage + xóa record trong DB
            old_images = instance.images.all()
            for old_image in old_images:
                old_image.image.delete(save=False)  # xóa file khỏi storage
            old_images.delete()                      # xóa record khỏi DB

            # Tạo ảnh mới
            for image in images:
                ProductImage.objects.create(
                    product=instance,
                    image=image
                )
            
        return instance        

# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, read_only=True)
#     category = CategorySerializer(read_only=True, source='category_id')
#     category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True, source ='category')

#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'description', 'slug', 'price', 'main_image', 'quantity', 'category', 'images', 'category_id', 'created_at', 'updated_at']
        
#         read_only_fields = ['slug']
    
#     def create(self, validated_data):
#         images_data = validated_data.pop('images', [])
#         product = Product.objects.create(**validated_data)
        
#         for image_data in images_data:
#             ProductImage.objects.create(product=product, **image_data)
            
#         return product
    
#     def update(self, instance, validated_data):
#         images_data = validated_data.pop('images', None)
        
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
        
#         if images_data is not None:
#             instance.images.all().delete()
#             for image_data in images_data:
#                 ProductImage.objects.create(product=instance, **image_data)
        
#         return instance