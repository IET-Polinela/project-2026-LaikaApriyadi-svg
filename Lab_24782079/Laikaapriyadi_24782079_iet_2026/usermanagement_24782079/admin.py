from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Menentukan kolom apa saja yang muncul di daftar user
    list_display = ('username', 'email', 'is_admin', 'is_member', 'is_active')
    
    # Menambahkan field kustom agar bisa diedit di dalam detail user
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_admin',)}),
    )
    
    # Menambahkan field kustom saat membuat user baru lewat admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('is_admin',)}),
    )

# Daftarkan model User dengan pengaturan kustom tadi
admin.site.register(User, CustomUserAdmin)