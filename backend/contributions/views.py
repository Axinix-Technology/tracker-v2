import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from contributions.ai_parser import WorkStatusAIParser

class WorkStatusAIParseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        data = request.data or {}
        raw_text = data.get("text", "")
        target_date = data.get("date")
        member_id = data.get("member_id")

        if not raw_text or not raw_text.strip():
            return Response({"success": False, "error": "No work status text provided."}, status=400)

        items = WorkStatusAIParser.parse_raw_text(
            raw_text=raw_text,
            default_member=member_id,
            target_date=target_date
        )

        return Response({
            "success": True,
            "count": len(items),
            "items": items
        })

