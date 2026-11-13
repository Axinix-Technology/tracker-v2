import re
import json
import os
from django.utils import timezone
from contributions.models import ContributionCategory

class WorkStatusAIParser:
    """
    Intelligent AI Work Status Parser powered by Amazon Bedrock Mantle / OpenAI SDK.
    Extracts individual activity items from raw, unstructured WhatsApp / Slack updates,
    maps them to Project vs Company scopes, classifies Primary & Secondary Categories,
    and evaluates the 6 Quality Factors with rationale.
    """

    KEYWORD_CATEGORY_MAPPING = [
        (r"\b(architect|architecture|subsystem|populate_core|kernel|engine)\b", "Reusable System Architecture", "Company Contribution", 12.0),
        (r"\b(ci/cd|pipeline|docker|aws|cloud|deploy|server|hosting|godaddy|cloudflare|s3|instance)\b", "DevOps & CI/CD Infrastructure", "Company Contribution", 10.0),
        (r"\b(client acquisition|acquired an order|converted prospect|sales proposal|contract)\b", "Client Acquisition", "Company Contribution", 12.0),
        (r"\b(prospect|business development|lead generation|demo to prospect)\b", "Business Development", "Company Contribution", 10.0),
        (r"\b(bug|fix|fixed|defect|error 500|patch|crash)\b", "Bug Fixing", "Project Contribution", 8.0),
        (r"\b(testing|test cases|qa|regression|verification|verified)\b", "Quality Assurance", "Project Contribution", 7.0),
        (r"\b(api|apis|developed|built|implemented|coding|backend|frontend|react|django|controller)\b", "Development", "Project Contribution", 10.0),
        (r"\b(brs|documentation|knowledge base|docs|guide|manual|specs)\b", "Documentation", "Company Contribution", 6.0),
        (r"\b(training|trained|mentor|guided|guidance|knowledge transfer)\b", "Mentoring & Knowledge Sharing", "Company Contribution", 5.0),
        (r"\b(barcode|barcoding|prn|label printer|catalog|product entry|inward)\b", "Data Preparation & Product Catalog Management", "Project Contribution", 5.0),
    ]

    @classmethod
    def parse_raw_text(cls, raw_text: str, default_member=None, target_date=None):
        if not raw_text or not raw_text.strip():
            return []

        # 1. Attempt Amazon Bedrock LLM Parsing if configured
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("BEDROCK_MODEL", "openai.gpt-oss-120b")

        if api_key and base_url:
            try:
                llm_items = cls._parse_with_bedrock(raw_text, api_key, base_url, model, target_date)
                if llm_items and len(llm_items) > 0:
                    return llm_items
            except Exception as e:
                print(f"[WorkStatusAIParser] Bedrock LLM invocation failed, falling back to heuristic: {e}")

        # 2. Local High-Precision Heuristic Fallback
        return cls._parse_with_heuristics(raw_text, default_member, target_date)

    @classmethod
    def _parse_with_bedrock(cls, raw_text: str, api_key: str, base_url: str, model: str, target_date: str = None):
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)

        # Retrieve available DB categories
        categories = list(ContributionCategory.objects.filter(is_active=True).values("name", "scope", "base_points"))
        cat_names = [c["name"] for c in categories]
        cat_map = {c["name"].lower(): c for c in categories}

        date_str = target_date or timezone.now().date().isoformat()

        prompt = f"""
You are an expert Enterprise Resource Planning (ERP) Contribution & Equity Classifier.
Analyze the following unstructured work status message and extract each discrete activity item.

Available Contribution Categories:
{json.dumps(cat_names)}

For each distinct activity, evaluate the 6 criteria (true or false):
1. factor_effort (20%): Genuine effort and consistency spent on meaningful work.
2. factor_complexity (15%): High difficulty, specialist knowledge, or deep problem solving.
3. factor_deliverable (25%): Fully completed output or working milestone. (Set to FALSE if work is in progress, ongoing, started, on hold, or testing).
4. factor_quality (20%): Clean execution, correctness, and architectural compliance.
5. factor_evidence (10%): Verifiable commits, tickets, client acceptance, or documentation links.
6. factor_outcome (10%): Reusable asset, direct revenue, customer value, or strategic impact.

If factor_deliverable is false, delivery_status should be 'in_progress' or 'on_hold'. If true, delivery_status is 'completed'.

Input Work Status:
\"\"\"
{raw_text}
\"\"\"

Respond strictly with a valid JSON array of objects with the following schema:
[
  {{
    "activity": "clean description of what was done",
    "project_name": "Project or Company name mentioned (default to 'Axinix Technologies' if not specified)",
    "scope": "Company Contribution" or "Project Contribution",
    "category_name": "exact category name from available list",
    "worked_days": float (default 1.0, or extracted if mentioned like 'about 20 working days'),
    "factor_effort": boolean,
    "factor_complexity": boolean,
    "factor_deliverable": boolean,
    "factor_quality": boolean,
    "factor_evidence": boolean,
    "factor_outcome": boolean,
    "delivery_status": "completed" | "in_progress" | "on_hold" | "stalled",
    "ai_reasoning": "1 sentence explanation of why factors and category were chosen"
  }}
]
Do not include any Markdown code fences or extra text, just the raw JSON.
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise JSON-only output assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        content = response.choices[0].message.content.strip()
        # Clean any accidental code fences
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"\n?```$", "", content).strip()

        parsed = json.loads(content)
        items = []

        for p in parsed:
            cat_info = cat_map.get((p.get("category_name") or "").lower())
            base_pts = cat_info["base_points"] if cat_info else 10.0
            scope = cat_info["scope"] if cat_info else p.get("scope", "Company Contribution")

            f_eff = bool(p.get("factor_effort", True))
            f_comp = bool(p.get("factor_complexity", True))
            f_del = bool(p.get("factor_deliverable", True))
            f_qual = bool(p.get("factor_quality", True))
            f_evid = bool(p.get("factor_evidence", True))
            f_out = bool(p.get("factor_outcome", True))

            factor_sum = (
                (20.0 if f_eff else 0.0) +
                (15.0 if f_comp else 0.0) +
                (25.0 if f_del else 0.0) +
                (20.0 if f_qual else 0.0) +
                (10.0 if f_evid else 0.0) +
                (10.0 if f_out else 0.0)
            )

            days = float(p.get("worked_days", 1.0))
            final_points = round((days * base_pts) * (factor_sum / 100.0), 2)

            items.append({
                "activity": p.get("activity", ""),
                "project_name": p.get("project_name", "Axinix Technologies"),
                "scope": scope,
                "category_name": cat_info["name"] if cat_info else p.get("category_name", "Development"),
                "worked_days": days,
                "base_points": base_pts,
                "factor_effort": f_eff,
                "factor_complexity": f_comp,
                "factor_deliverable": f_del,
                "factor_quality": f_qual,
                "factor_evidence": f_evid,
                "factor_outcome": f_out,
                "factor_percentage": factor_sum,
                "final_points": final_points,
                "delivery_status": p.get("delivery_status", "completed" if f_del else "in_progress"),
                "ai_reasoning": p.get("ai_reasoning", "Extracted via Amazon Bedrock AI."),
                "date": date_str,
            })

        return items

    @classmethod
    def _parse_with_heuristics(cls, raw_text: str, default_member=None, target_date=None):
        date_str = target_date or timezone.now().date().isoformat()
        lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]

        current_project = "Axinix Technologies"
        extracted_activities = []

        skip_patterns = [
            r"^@all",
            r"^today['’]?s work status",
            r"^work status",
            r"^daily update",
            r"^hi all",
            r"^hello",
        ]

        for line in lines:
            line_lower = line.lower()
            if any(re.match(p, line_lower) for p in skip_patterns):
                continue

            is_header = False
            clean_candidate = re.sub(r"^[#*\-\s]+", "", line).strip()
            if len(clean_candidate) < 40 and not re.match(r"^\d+[\.\)]", line) and not line.endswith("."):
                if any(k in clean_candidate.lower() for k in ["axinix", "tea shop", "clothing", "client", "project", "technologies", "ar.i.s", "skg", "prospect"]):
                    current_project = clean_candidate
                    is_header = True

            if is_header:
                continue

            clean_activity = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
            clean_activity = re.sub(r"^[\-\*•]\s*", "", clean_activity).strip()

            if len(clean_activity) < 5:
                continue

            scope, category_name, base_points = cls._classify_activity(clean_activity, current_project)
            factors = cls._evaluate_factors(clean_activity)
            days = cls._estimate_days(clean_activity)

            factor_sum = (
                (20.0 if factors["effort"] else 0.0) +
                (15.0 if factors["complexity"] else 0.0) +
                (25.0 if factors["deliverable"] else 0.0) +
                (20.0 if factors["quality"] else 0.0) +
                (10.0 if factors["evidence"] else 0.0) +
                (10.0 if factors["outcome"] else 0.0)
            )
            final_points = round((days * base_points) * (factor_sum / 100.0), 2)

            delivery_status = "completed" if factors["deliverable"] else "in_progress"
            if any(w in clean_activity.lower() for w in ["on hold", "paused"]):
                delivery_status = "on_hold"
            elif any(w in clean_activity.lower() for w in ["blocked", "waiting"]):
                delivery_status = "stalled"

            extracted_activities.append({
                "activity": clean_activity,
                "project_name": current_project,
                "scope": scope,
                "category_name": category_name,
                "worked_days": days,
                "base_points": base_points,
                "factor_effort": factors["effort"],
                "factor_complexity": factors["complexity"],
                "factor_deliverable": factors["deliverable"],
                "factor_quality": factors["quality"],
                "factor_evidence": factors["evidence"],
                "factor_outcome": factors["outcome"],
                "factor_percentage": factor_sum,
                "final_points": final_points,
                "delivery_status": delivery_status,
                "ai_reasoning": factors["reasoning"],
                "date": date_str,
            })

        return extracted_activities

    @classmethod
    def _classify_activity(cls, text: str, project_name: str):
        text_lower = text.lower()
        project_lower = project_name.lower()

        is_company = any(c in project_lower for c in ["axinix", "internal", "ar.i.s", "company"])

        matched_cat = None
        matched_scope = "Company Contribution" if is_company else "Project Contribution"
        base_points = 10.0

        for pattern, cat, scp, pts in cls.KEYWORD_CATEGORY_MAPPING:
            if re.search(pattern, text_lower):
                matched_cat = cat
                matched_scope = scp if is_company else "Project Contribution"
                base_points = pts
                break

        if not matched_cat:
            matched_cat = "Development" if not is_company else "Internal Process Improvement"
            base_points = 10.0 if not is_company else 7.0

        db_cat = ContributionCategory.objects.filter(name__iexact=matched_cat).first()
        if db_cat:
            matched_cat = db_cat.name
            base_points = db_cat.base_points
            matched_scope = db_cat.scope

        return matched_scope, matched_cat, base_points

    @classmethod
    def _evaluate_factors(cls, text: str):
        text_lower = text.lower()
        effort = True
        complexity = True
        if any(w in text_lower for w in ["trivial", "simple rename", "minor typo", "comment update"]):
            complexity = False

        deliverable = True
        reasoning = "Milestone output delivered or verified."
        if any(w in text_lower for w in ["in progress", "started", "started auditing", "under review", "on hold", "planning", "wip", "ongoing"]):
            deliverable = False
            reasoning = "Activity is currently in progress or under review; deliverable completion factor is pending."

        quality = True
        evidence = True
        outcome = True

        return {
            "effort": effort,
            "complexity": complexity,
            "deliverable": deliverable,
            "quality": quality,
            "evidence": evidence,
            "outcome": outcome,
            "reasoning": reasoning,
        }

    @classmethod
    def _estimate_days(cls, text: str):
        text_lower = text.lower()
        match = re.search(r"(\d+(\.\d+)?)\s*(working\s*)?days?", text_lower)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
        return 1.0
