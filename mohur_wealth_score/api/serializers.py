from rest_framework import serializers
from .models import PeerBenchmark, ComponentWeight

class GoalSerializer(serializers.Serializer):
    # for serializing the goals as part of the user input
    goal_name = serializers.CharField(max_length = 100)
    target_amount = serializers.FloatField(min_value = 0)
    target_months = serializers.IntegerField(min_value = 1)
    current_monthly = serializers.FloatField(min_value = 0)


class WealthScoreInputSerializer(serializers.Serializer):
    # serializer for main api input

    city = serializers.CharField(max_length=100)

    monthly_income = serializers.FloatField(min_value=1)

    rent_emi = serializers.FloatField(min_value=0)

    savings_per_month = serializers.FloatField(min_value=0)

    emergency_fund = serializers.FloatField(min_value = 0)

    has_sip = serializers.BooleanField()

    number_of_instruments = serializers.IntegerField(min_value=0)

    goals = GoalSerializer(many=True, allow_empty=True)


    def validate_city(self, value):

        city_capitalized = value.strip().capitalize()
        
        if not PeerBenchmark.objects.filter(city=city_capitalized).exists():
            raise serializers.ValidationError(f"City '{value}' not found in benchmark data.")
        return city_capitalized



class WealthScoreOutputSerializer(serializers.Serializer):


    wealth_fitness_score = serializers.IntegerField()
    peer_rank_percentile = serializers.IntegerField()  

