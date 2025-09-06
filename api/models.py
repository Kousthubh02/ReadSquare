from wsgiref.validate import validator
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
from django.urls import reverse
from decimal import Decimal 

class Category(models.Model):
    name=models.CharField(max_length=100, unique=True)
    slug=models.SlugField(max_length=100, unique=True)
    description=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural="Categories"
        ordering=['name']
        
    def __str__(self):
        return self.name 
    
class Author(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(max_length=100, unique=True)
    bio=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['name']
    
    def __str__(self):
        return self.name
    
class Book(models.Model):
    BOOK_FORMATS=[
        ('HARDCOVER','Hardcover'),
        ('PAPERBACK','Paperback'),
        ('EBOOK','eBook'),
    ]
    
    title=models.CharField(max_length=200)
    slug=models.SlugField(max_length=200, unique=True)
    isbn=models.CharField(max_length=13, unique=True,blank=True,null=True)
    
    author=models.ForeignKey(Author , on_delete=models.CASCADE, related_name='books')
    category=models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='books')
  
    description=models.TextField(blank=True)
    pages=models.PositiveIntegerField(null=True,blank=True)
    publication_date=models.DateField()
    format=models.CharField(max_length=20, choices=BOOK_FORMATS)
    
    cover_image=models.ImageField(upload_to='books/covers/',null=True,blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    
    is_active=models.BooleanField(default=True)
    is_featured=models.BooleanField(default=False)
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    
    
    class Meta:
        ordering=['-created_at']
        
    def __str__(self):
        return self.title
    def get__absolute_url(self):
        return reverse('book_detail',args=[self.slug])
    
    
    @property
    def discount_percentage(self):
        if self.original_price and self.original_price>self.price:
            return int(((self.original_price - self.price)/self.original_price)*100)
        return 0
    
    @property
    def is_in_stock(self):
        return self.stock_quantity>0
    
    @property
    def average_rating(self):
        reviews=self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'],1)
        return None
    
class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=15,blank=True,null=True)
    address=models.TextField(blank=True,null=True)
    city=models.CharField(max_length=100,blank=True)
    postal_code=models.CharField(max_length=20,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class Cart(models.Model):
    customer=models.OneToOneField(Customer,on_delete=models.CASCADE,null=True,blank=True)
    session_key=models.CharField(max_length=40,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.customer:
            return f"{self.customer.user.get_full_name()}'s Cart"
        return f"Anonymous Cart {self.session_key}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE, related_name='items')
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=['cart','book']
        
    def __str__(self):
        return f"{self.quantity} of {self.book.title}"
    
    @property
    def total_price(self):
        return self.quantity*self.book.price
    
class Wishlist(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='wishlists')
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
        
    class Meta:
        unique_together=['customer','book']
            
    def __str__(self):
        return f"{self.customer.user.get_full_name()}'s Wishlist Item: {self.book.title }"
    
    
class Review(models.Model):
    book=models.ForeignKey(Book,on_delete=models.CASCADE,related_name='reviews')
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='reviews')
    rating=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.TextField(blank=True)
    is_approved=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=['book','customer']
        ordering=['-created_at']
        
    def __str__(self):
        return f"Review of {self.book.title} by {self.customer.user.get_full_name()}"