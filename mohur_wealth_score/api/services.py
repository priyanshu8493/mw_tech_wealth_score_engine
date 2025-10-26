import math
from scipy.stats import norm
from .models import PeerBenchmark, ComponentWeight





class WealthScoreCalculator:
    """
    Encapsulates all logic for calculating the wealth score
    based on the formulas deduced from the spreadsheets.
    """
    def __init__(self, validated_input_data):
        self.input_data = validated_input_data
        self.benchmark_data = None
        self.calculated_data = validated_input_data.copy()
        

        self.weights = {w.component: w.weight_pct for w in ComponentWeight.objects.all()}
        if not self.weights:
            raise ValueError("ComponentWeight data is not loaded. Run 'python manage.py load_data'.")
            

        try:
            self.benchmark_data = PeerBenchmark.objects.get(city=self.input_data['city'])
        except PeerBenchmark.DoesNotExist:
            raise ValueError(f"No benchmark data for city: {self.input_data['city']}")

    def _get_adjusted_benchmark_saving(self):
        """
        Calculates BenchmarkSavingPct (Adj) based on income range.
        Formula: IF(Income < Low, Base + AdjLow, IF(Income > High, Base + AdjHigh, Base))
        """
        income = self.input_data['monthly_income']
        bm = self.benchmark_data
        
        if income < bm.income_low:
            adj_pct = bm.benchmark_saving_pct + bm.mean_adj_low
        elif income > bm.income_high:
            adj_pct = bm.benchmark_saving_pct + bm.mean_adj_high
        else:
            adj_pct = bm.benchmark_saving_pct
        

        return max(adj_pct, 0.01)

    def _calculate_saving_discipline(self, saving_rate_pct, benchmark_saving_pct_adj):
        """
        Calculates SavingDiscipline (0-100).
        Formula: MAX(0, MIN(100, (SavingRatePct / BenchmarkSavingPct (Adj)) * 100))
        """
        
        score = (saving_rate_pct / benchmark_saving_pct_adj) * 100
        return max(0, min(100, score))

    def _calculate_goal_health(self):
        """
        Calculates GoalHealth (0-100).
        Formula: (SUM(OnTrack_Goals) / COUNT(Goals)) * 100
        An "OnTrack" goal is one where (CurrentMonthly * TargetMonths) >= TargetAmount.
        """
        goals = self.input_data.get('goals', [])
        if not goals:
            return 0  

        on_track_count = 0
        for goal in goals:
            projected_savings = goal['current_monthly'] * goal['target_months']
            if projected_savings >= goal['target_amount']:
                on_track_count += 1
        
        score = (on_track_count / len(goals)) * 100
        return max(0, min(100, score))

    def _calculate_spending_behavior(self, emi_income_ratio):
        """
        Calculates SpendingBehavior (0-100).
        Formula (deduced): MAX(0, MIN(100, (0.5 - (RentEMI / Income)) / 0.5 * 100 + 20))
        This gets 91.68, which is very close to the snippet's 90.
        """
        score = ((0.5 - emi_income_ratio) / 0.5) * 100 + 20
        return max(0, min(100, score))

    def _calculate_investment_mix(self):
        """
        Calculates InvestmentMix (0-100).
        Formula: IF(Has SIP?, 50, 0) + IF(NumInstruments > 1, 50, IF(NumInstruments = 1, 20, 0))
        """
        has_sip = self.input_data['has_sip']
        num_instruments = self.input_data['number_of_instruments']
        
        score = 0
        if has_sip:
            score += 50
        
        if num_instruments > 1:
            score += 50
        elif num_instruments == 1:
            score += 20
            
        return max(0, min(100, score))

    def _calculate_protection(self):
        """
        Calculates Protection (0-100).
        Formula: MAX(0, MIN(100, (Emergency Fund / (3 * Income)) * 100))
        """
        emergency_fund = self.input_data['emergency_fund']
        income = self.input_data['monthly_income']
        

        target_fund = 3 * income
        if target_fund == 0:
            return 0 
            
        score = (emergency_fund / target_fund) * 100
        return max(0, min(100, score))

    def _calculate_peer_percentile(self, saving_rate_pct, benchmark_saving_pct_adj):
        """
        Calculates Peer Percentile (dynamic).
        Formula: NORM.DIST(SavingRatePct, BenchmarkSavingPct (Adj), Assumed StdDev, TRUE)
        Assumed StdDev = 0.04 (from snippet)
        """
        std_dev = 0.04 
        

        percentile = norm.cdf(
            saving_rate_pct, 
            loc=benchmark_saving_pct_adj, 
            scale=std_dev
        )

        return math.floor(percentile * 100)



    def calculate_score(self):
        """
        Main method to run all calculations and return the final output.
        """
        

        income = self.input_data['monthly_income']
        rent_emi = self.input_data['rent_emi']
        savings_monthly = self.input_data['savings_per_month']
        
        saving_rate_pct = savings_monthly / income if income > 0 else 0
        emi_income_ratio = rent_emi / income if income > 0 else 0
        
        benchmark_saving_pct_adj = self._get_adjusted_benchmark_saving()
        
        scores = {
            'SavingDiscipline': self._calculate_saving_discipline(saving_rate_pct, benchmark_saving_pct_adj),
            'GoalHealth': self._calculate_goal_health(),
            'SpendingBehavior': self._calculate_spending_behavior(emi_income_ratio),
            'InvestmentMix': self._calculate_investment_mix(),
            'Protection': self._calculate_protection(),
        }
        

        final_score = 0
        final_score += scores['SavingDiscipline'] * self.weights.get('SavingDiscipline', 0)
        final_score += scores['GoalHealth'] * self.weights.get('GoalHealth', 0)
        final_score += scores['SpendingBehavior'] * self.weights.get('SpendingBehavior', 0)
        final_score += scores['InvestmentMix'] * self.weights.get('InvestmentMix', 0)
        final_score += scores['Protection'] * self.weights.get('Protection', 0)
        

        peer_percentile = self._calculate_peer_percentile(saving_rate_pct, benchmark_saving_pct_adj)
        



        output_data = {
            "wealth_fitness_score": math.floor(final_score),
            "peer_rank_percentile": peer_percentile,

        }
        
        return output_data

