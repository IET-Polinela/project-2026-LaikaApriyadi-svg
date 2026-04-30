import random
from django.core.management.base import BaseCommand
from faker import Faker
from main_app.models import Report # Ganti jika nama app kamu berbeda [cite: 24]

fake = Faker('id_ID') # Set ke Bahasa Indonesia [cite: 26, 27]

class Command(BaseCommand):
    help = 'Generate contextual fake reports for IET City' # [cite: 29]

    def add_arguments(self, parser):
        parser.add_argument('num_records', type=int, help='Jumlah data') # [cite: 30, 31]

    def handle(self, *args, **kwargs):
        num_records = kwargs['num_records'] # [cite: 33]
        context_data = {
            'Jalan Rusak': {
                'titles': ['Lubang Besar di Tengah Jalan', 'Aspal Mengelupas Parah'],
                'desc': 'Ditemukan kerusakan jalan yang cukup dalam.'
            },
            'Sampah': {
                'titles': ['Tumpukan Sampah Liar', 'Bau Menyengat Sampah'],
                'desc': 'Warga mengeluhkan penumpukan sampah.'
            },
            # ... Tambahkan kategori lain: Lampu Mati, Drainase, Keamanan [cite: 34-48]
        }
        status_choices = ['REPORTED', 'VERIFIED', 'IN PROGRESS', 'RESOLVED'] # [cite: 49, 50]

        for _ in range(num_records):
            category = random.choice(list(context_data.keys())) # [cite: 53]
            title_template = random.choice(context_data[category]['titles']) # [cite: 55]
            
            Report.objects.create(
                title=f"{title_template} - {fake.street_name()}", # [cite: 60, 61]
                category=category,
                description=f"{context_data[category]['desc']} Lokasi: {fake.street_address()}", # [cite: 63, 64]
                location=f"Kecamatan {fake.city()}, {fake.address()}", # [cite: 66]
                status=random.choice(status_choices), # [cite: 66]
            )
        self.stdout.write(self.style.SUCCESS(f'Berhasil membuat {num_records} laporan!')) # [cite: 67, 68]