from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UniversalSignUpForm(UserCreationForm):
    # Menambahkan pilihan Role di halaman pendaftaran
    ROLE_CHOICES = [
        ('False', 'Citizen (Akses Lihat Saja)'),
        ('True', 'Admin (Akses CRUD Laporan)'),
    ]
    
    is_admin_choice = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Daftar Sebagai",
        help_text="Pilih 'Admin' jika Anda ingin memiliki hak akses untuk menambah/mengubah laporan."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # field is_admin_choice akan diproses manual di views