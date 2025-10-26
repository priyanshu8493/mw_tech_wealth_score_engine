import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from api.models import PeerBenchmark, ComponentWeight

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')

class Command(BaseCommand):
    help = 'Loads static data from CSV files into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data load...'))

        # Load PeerBenchmarks
        self.load_peer_benchmarks()
        
        # Load ComponentWeights
        self.load_component_weights()
        
        # Removed call to load_nudge_rules()

        self.stdout.write(self.style.SUCCESS('Data load complete!'))

    def load_peer_benchmarks(self):
        file_path = os.path.join(DATA_DIR, 'PeerBenchmarks.csv')
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
            
        self.stdout.write('Loading PeerBenchmarks...')
        PeerBenchmark.objects.all().delete() # Clear existing data
        
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            benchmarks = []
            for row in reader:
                try:
                    benchmarks.append(PeerBenchmark(
                        city=row['City'].strip().capitalize(),
                        tier=row['Tier'],
                        benchmark_saving_pct=float(row['BenchmarkSavingPct']),
                        peer_base_percentile=float(row['PeerBasePercentile']),
                        income_low=int(row['IncomeLow']),
                        income_high=int(row['IncomeHigh']),
                        mean_adj_low=float(row['MeanAdjLow']),
                        mean_adj_high=float(row['MeanAdjHigh']),
                    ))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error processing row: {row}. Error: {e}'))
            
            PeerBenchmark.objects.bulk_create(benchmarks)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(benchmarks)} peer benchmarks.'))

    def load_component_weights(self):
        file_path = os.path.join(DATA_DIR, 'Weights.csv')
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')

        self.stdout.write('Loading ComponentWeights...')
        ComponentWeight.objects.all().delete()
        
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            weights = []
            for row in reader:
                weights.append(ComponentWeight(
                    component=row['Component'],
                    weight_pct=float(row['WeightPct']),
                ))
            ComponentWeight.objects.bulk_create(weights)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(weights)} component weights.'))



