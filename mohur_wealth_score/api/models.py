from django.db import models

class PeerBenchmark(models.Model):
    city = models.CharField(max_length=100, primary_key=True)
    tier = models.CharField(max_length=10)
    benchmark_saving_pct = models.FloatField()
    peer_base_percentile = models.FloatField()
    income_low = models.IntegerField()
    income_high = models.IntegerField()
    mean_adj_low = models.FloatField()
    mean_adj_high = models.FloatField()



    def __str__(self):
        return self.city
    


class ComponentWeight(models.Model):
    component = models.CharField(max_length=100, primary_key=True)
    weight_pct = models.FloatField()

    def __str__(self):
        return f"{self.component} ({self.weight_pct * 100}%)"
    

