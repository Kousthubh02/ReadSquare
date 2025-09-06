from django.contrib import admin
from django.utils.html import format_html
from .models import Category , Author , Book , Customer,Cart,CartItem,Wishlist,Review 

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active','created_at']
    search_fields=['name','description']
    prepopulated_fields={'slug':('name',)}
    list_editable=['is_active']
    
    def book_count(self,obj):
        return obj.books.count()
    book_count.short_description='Books'
    
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display=['name','book_count','created_at']
    search_fields=['name','bio']
    prepopulated_fields={'slug':('name',)}
    
    def book_count(self,obj):
        return obj.books.count()
    book_count.short_description='Books'
    
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display=['title','author','category','format','price','stock_quantity','is_active','is_featured']
    list_filter=['is_active','is_featured','format','category','author','created_at']
    search_fields=['title','isbn','description','author__name']
    prepopulated_fields={'slug':('title',)}
    list_editable=['price','stock_quantity','is_active','is_featured']
    readonly_fields=['created_at','updated_at','average_rating']
    fieldsets=(
        ('Basic Information',{
            'fields':('title','slug','author','category','description')
        }),
        ('Publication Details',{
            'fields':('isbn''publication_date','pages','format')
        }),  
        ('Pricing & Inventory',{
            'fields': ('price','original_price','stock_quantity')
        }),
        ('Image',{
            'fields':('cover_image',)
        }),
        ('Status',{
            'fields':('is_active','is_featured')
        }),
        ('Info',{
            'fields':('average_rating','created_at','updated_at'),
            'classes':('collapse',)
        }),
        )
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=['full_name','user_email','phone','city','created_at']
    search_fields=['user_username','user_email','user_first_name','user_last_name','phone']
    readonly_fields=['created_at']
    
    def user_email(self,obj):
        return obj.user.email
    user_email.short_description='Email'
    
class CartItemInLine(admin.TabularInline):
    model=CartItem
    extra=0
    readonly_fields=['total_price']
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=['customer_name','total_items','total_price','created_at']
    list_filter=['created_at']
    search_fields=['customer__user__username','session_key']
    inLines=[CartItemInLine]
    readonly_fields=['total_items','total_price',]
    
    def customer_name(self,obj):
        if obj.customer:
            return obj.customer.user.username
        return f"Anonymous ({obj.session_key})"
    customer_name.short_description='Customer'
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display=['cart_customer','book','quantity','total_price','created_at']
    list_filter=['created_at']
    search_fields=['cart__customer__user__username','book__title']
    readonly_fields=['total_price']
    
    def cart_customer(self,obj):
        if obj.cart.customer:
            return obj.cart.customer.user.username
        return f"Anonymous"
    cart_customer.short_description='Customer'
    
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display=['customer','book','created_at']
    list_filter=['created_at']
    search_fields=['customer__user__username','book__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['book','customer','rating','is_approved','created_at']
    list_filter=['rating','is_approved','created_at']
    search_fields=['book__title','customer__user__username','comment']
    list_editable=['is_approved']
    readonly_fields=['created_at']
    
    
    
    