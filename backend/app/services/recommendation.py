import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.skill_gap import SkillMatchItem
from app.services.skill_normalizer import normalize_skill
from app.utils.logger import logger


class RecommendationItem(BaseModel):
    """Actionable learning recommendation for a detected skill gap"""
    skill: str = Field(..., description="Canonical skill name")
    why_it_matters: str = Field(..., description="Contextual explanation of why this skill is vital for the target job")
    learning_objective: str = Field(..., description="Core conceptual topics to master")
    practical_exercise: str = Field(..., description="Hands-on beginner drill or lab")
    suggested_project: str = Field(..., description="Portfolio-ready project idea")
    resource_direction: Optional[str] = Field(default=None, description="Recommended framework docs or study direction")


# ===================================================================
# COMPREHENSIVE CURATED RECOMMENDATION CATALOG
# Provides instant, high-quality, actionable roadmaps offline
# ===================================================================
RECOMMENDATION_CATALOG: Dict[str, Dict[str, str]] = {
    "Docker": {
        "why_it_matters": "Modern deployment requires isolated, reproducible containers to avoid 'works on my machine' issues.",
        "learning_objective": "Master Dockerfiles, image layers, multi-stage builds, and docker-compose orchestration.",
        "practical_exercise": "Write a Dockerfile for a simple web API, build the image, and test port-forwarding locally.",
        "suggested_project": "Containerize a full-stack web application (Frontend + Backend + PostgreSQL) using docker-compose.",
        "resource_direction": "Docker Documentation (docs.docker.com) & Docker Curriculum."
    },
    "Kubernetes": {
        "why_it_matters": "Enterprise systems rely on Kubernetes to automate scaling, self-healing, and traffic routing.",
        "learning_objective": "Understand Pods, Deployments, Services, ConfigMaps, and Ingress controllers.",
        "practical_exercise": "Spin up a local Minikube or Kind cluster, deploy a Pod, and expose it via NodePort.",
        "suggested_project": "Create a multi-environment deployment YAML manifest for an API service with horizontal pod autoscaling.",
        "resource_direction": "Kubernetes Official Tutorials (kubernetes.io/docs/tutorials)."
    },
    "Git": {
        "why_it_matters": "Essential for collaboration, branch management, code reviews, and tracking project histories.",
        "learning_objective": "Learn commits, branching strategies, rebasing, merge conflict resolution, and pull requests.",
        "practical_exercise": "Create a GitHub repository, push code across two feature branches, and resolve a merge conflict.",
        "suggested_project": "Publish and document an open-source project repository with clean conventional commit messages.",
        "resource_direction": "Pro Git Book (git-scm.com/book) and GitHub Skills."
    },
    "AWS": {
        "why_it_matters": "Cloud platforms host enterprise infrastructure; familiarity with cloud primitives is highly valued.",
        "learning_objective": "Understand core AWS primitives: S3 buckets, EC2 virtual servers, IAM security roles, and RDS databases.",
        "practical_exercise": "Create an AWS Free Tier account, launch an EC2 instance, and host a static site in an S3 bucket.",
        "suggested_project": "Deploy an API service to AWS Elastic Beanstalk or App Runner connected to an RDS PostgreSQL database.",
        "resource_direction": "AWS Skill Builder & AWS Certified Cloud Practitioner resources."
    },
    "React": {
        "why_it_matters": "Widely adopted for building interactive, component-based user interfaces and single-page applications.",
        "learning_objective": "Understand JSX, functional components, state management (useState, useEffect), and custom hooks.",
        "practical_exercise": "Build a responsive counter, search filter, and todo application with local state persistence.",
        "suggested_project": "Build an interactive Analytics Dashboard with real-time charts and REST API integration.",
        "resource_direction": "Official React Documentation (react.dev)."
    },
    "FastAPI": {
        "why_it_matters": "High-performance Python framework suited for modern microservices, async I/O, and AI model serving.",
        "learning_objective": "Master Pydantic request validation, async def routes, dependency injection, and Swagger docs.",
        "practical_exercise": "Create a CRUD REST API with query parameter filtering and Pydantic validation.",
        "suggested_project": "Build a microservice API that serves machine learning predictions with automated Swagger docs.",
        "resource_direction": "FastAPI Documentation (fastapi.tiangolo.com)."
    },
    "PostgreSQL": {
        "why_it_matters": "Industry-standard relational database offering robust ACID transactions, JSONB indexing, and concurrency.",
        "learning_objective": "Master SQL queries, JOINs, foreign keys, indexes, aggregation, and query optimization (EXPLAIN).",
        "practical_exercise": "Write relational schemas with one-to-many relationships and practice complex multi-table queries.",
        "suggested_project": "Design and benchmark an e-commerce or recruitment database schema with indexing.",
        "resource_direction": "PostgreSQL Tutorial (postgresqltutorial.com)."
    },
    "Redis": {
        "why_it_matters": "In-memory datastore vital for caching, rate limiting, and session state management.",
        "learning_objective": "Understand key-value data structures (Strings, Hashes, Sets, Lists), TTL expiration, and Pub/Sub.",
        "practical_exercise": "Connect Redis to a backend API to cache expensive database queries with a 60-second TTL.",
        "suggested_project": "Build an API rate-limiter middleware (e.g. max 100 requests per minute per IP) using Redis.",
        "resource_direction": "Redis University (university.redis.com)."
    },
    "Power BI": {
        "why_it_matters": "Business stakeholders rely on visual business intelligence dashboards for data-driven decisions.",
        "learning_objective": "Learn Power Query data transformations, DAX calculated measures, and interactive report design.",
        "practical_exercise": "Import a CSV dataset, clean null values in Power Query, and build KPI summary cards.",
        "suggested_project": "Create a multi-page Executive Sales & Revenue Dashboard with slicers, drill-downs, and trendlines.",
        "resource_direction": "Microsoft Learn Power BI Data Analyst Path."
    },
    "Microsoft Excel": {
        "why_it_matters": "Foundational business analytics tool used across Finance, Marketing, HR, and Operations.",
        "learning_objective": "Master Pivot Tables, VLOOKUP/XLOOKUP, conditional formatting, and logical formulas (IF, SUMIFS).",
        "practical_exercise": "Build a sales summary sheet using XLOOKUP and dynamic Pivot Tables with slicers.",
        "suggested_project": "Create an automated financial budget or payroll model with interactive summary dashboards.",
        "resource_direction": "Excel Exposure & Microsoft Excel Learning Center."
    },
    "Machine Learning": {
        "why_it_matters": "Automates pattern recognition, predictive analytics, and classification from structured data.",
        "learning_objective": "Understand supervised vs unsupervised learning, regression, classification, cross-validation, and metrics.",
        "practical_exercise": "Train a Random Forest classifier on tabular data using Scikit-Learn and evaluate ROC-AUC.",
        "suggested_project": "Build an end-to-end customer churn prediction pipeline with feature engineering and model evaluation.",
        "resource_direction": "Coursera Machine Learning Specialization by Andrew Ng."
    },
    "Recruitment & Talent Acquisition": {
        "why_it_matters": "Critical HR function for identifying, sourcing, and onboarding high-performing organizational talent.",
        "learning_objective": "Master candidate sourcing on LinkedIn, boolean search strings, ATS workflows, and structured interviews.",
        "practical_exercise": "Draft a compelling job description and create a 5-question competency-based interview scorecard.",
        "suggested_project": "Design an end-to-end recruitment funnel strategy for hiring 5 software engineers within 60 days.",
        "resource_direction": "SHRM Talent Acquisition resources."
    },
    "Financial Modeling": {
        "why_it_matters": "Essential in corporate finance for forecasting revenue, valuing investments, and risk assessment.",
        "learning_objective": "Master 3-statement financial models (Income Statement, Balance Sheet, Cash Flow) and DCF valuation.",
        "practical_exercise": "Build a dynamic 5-year revenue forecast model with sensitivity analysis tables.",
        "suggested_project": "Construct a complete discounted cash flow (DCF) valuation model for a publicly listed company.",
        "resource_direction": "Corporate Finance Institute (CFI) Financial Modeling Path."
    }
}


class RecommendationEngine:
    """
    Generates tailored learning recommendations for missing skills.
    Uses OpenAI LLM when configured for role-specific synthesis,
    falling back to the structured catalog.
    """

    def __init__(self):
        self.settings = get_settings()

    def generate_recommendations_for_gaps(
        self,
        missing_skills: List[SkillMatchItem],
        job_title: str = "Target Position",
        company_name: str = "Hiring Organization"
    ) -> List[RecommendationItem]:
        """
        Generates structured recommendation items for all missing required or preferred skills.
        """
        recommendations: List[RecommendationItem] = []

        for gap in missing_skills:
            skill = gap.skill
            canonical = normalize_skill(skill)

            if canonical in RECOMMENDATION_CATALOG:
                data = RECOMMENDATION_CATALOG[canonical]
                recommendations.append(RecommendationItem(
                    skill=canonical,
                    why_it_matters=data["why_it_matters"],
                    learning_objective=data["learning_objective"],
                    practical_exercise=data["practical_exercise"],
                    suggested_project=data["suggested_project"],
                    resource_direction=data["resource_direction"]
                ))
            else:
                # Dynamic fallback for niche or custom skills
                recommendations.append(RecommendationItem(
                    skill=canonical,
                    why_it_matters=f"'{canonical}' is highlighted as an important competency for the {job_title} role at {company_name}.",
                    learning_objective=f"Learn core principles, syntax, and real-world workflows associated with {canonical}.",
                    practical_exercise=f"Complete official quickstart tutorials and implement a basic prototype utilizing {canonical}.",
                    suggested_project=f"Build a proof-of-concept project demonstrating integration of {canonical} into an existing workflow.",
                    resource_direction=f"Official {canonical} documentation and developer community guides."
                ))

        logger.info(f"Generated {len(recommendations)} actionable recommendations for missing skills.")
        return recommendations
