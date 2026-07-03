from django.db import models
from django.conf import settings  # Tambahkan import ini

STATUS_CHOICES = [
    ('DRAFT', 'Draft'),          # Tambahkan pilihan DRAFT
    ('REPORTED', 'Reported'),
    ('VERIFIED', 'Verified'),
    ('IN_PROGRESS', 'In Progress'),
    ('RESOLVED', 'Resolved'),
]

class Report(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=200)

    # Tambahkan field reporter (Relasi ke CustomUser)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REPORTED'
    )

    # Tambahkan field jejak waktu
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Dibutuhkan oleh test_report_model_str (test_addtional.py)
        return self.title