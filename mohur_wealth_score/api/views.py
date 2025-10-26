from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import WealthScoreInputSerializer, WealthScoreOutputSerializer
from .services import WealthScoreCalculator

class WealthScoreView(APIView):
    """
    API endpoint to calculate the Wealth Fitness Score.
    
    Accepts a POST request with user data and returns the score,
    peer rank, and a personalized nudge.
    """
    
    def post(self, request, *args, **kwargs):
        # 1. Validate the input data
        input_serializer = WealthScoreInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = input_serializer.validated_data
        
        try:
            # 2. Pass validated data to the calculation service
            calculator = WealthScoreCalculator(validated_data)
            output_data = calculator.calculate_score()
            
            # 3. Serialize the output data
            output_serializer = WealthScoreOutputSerializer(data=output_data)
            if output_serializer.is_valid():
                # 4. Return the successful response
                return Response(output_serializer.data, status=status.HTTP_200_OK)
            else:
                # This should not happen if the service logic is correct
                return Response(output_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValueError as e:
            # Handle known errors, e.g., missing benchmark data
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle unexpected server errors

            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
