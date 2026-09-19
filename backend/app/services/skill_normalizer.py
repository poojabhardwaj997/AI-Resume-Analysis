import re
from typing import List, Dict, Set, Optional

# ===================================================================
# CANONICAL SKILL TAXONOMY & SYNONYM DICTIONARY
# Keys are normalized lookup tokens (lowercase, stripped of punctuation)
# Values are standardized professional display names
# ===================================================================
SKILL_SYNONYMS: Dict[str, str] = {
    # Programming Languages & Scripting
    "python": "Python",
    "python3": "Python",
    "python 3": "Python",
    "python programming": "Python",
    "python development": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "es6": "JavaScript",
    "ecmascript": "JavaScript",
    "vanilla js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "java": "Java",
    "core java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c sharp": "C#",
    "c": "C",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "html": "HTML/CSS",
    "html5": "HTML/CSS",
    "css": "HTML/CSS",
    "css3": "HTML/CSS",
    "html/css": "HTML/CSS",
    "html css": "HTML/CSS",

    # Web & Application Frameworks
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "react native": "React Native",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "next js": "Next.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "tailwindcss": "Tailwind CSS",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "bootstrap 5": "Bootstrap",

    # Databases & Caching
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "postgre sql": "PostgreSQL",
    "mysql": "MySQL",
    "sql": "SQL",
    "structured query language": "SQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "supabase": "Supabase",
    "firebase": "Firebase",

    # DevOps, Cloud & Version Control
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    "version control": "Git",
    "docker": "Docker",
    "docker containers": "Docker",
    "containerization": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "google cloud platform": "Google Cloud Platform",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "linux": "Linux",
    "unix": "Linux",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "graphql": "GraphQL",

    # Data Science & AI/ML
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "scikitlearn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "excel": "Microsoft Excel",
    "ms excel": "Microsoft Excel",
    "microsoft excel": "Microsoft Excel",
    "ms-excel": "Microsoft Excel",
    "advanced excel": "Microsoft Excel",
    "data analysis": "Data Analysis",
    "statistics": "Statistics",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "llm": "Large Language Models",
    "llms": "Large Language Models",
    "large language models": "Large Language Models",
    "openai": "OpenAI API",
    "openai api": "OpenAI API",

    # Management, HR & Business
    "human resources": "Human Resources",
    "hr": "Human Resources",
    "recruitment": "Recruitment & Talent Acquisition",
    "talent acquisition": "Recruitment & Talent Acquisition",
    "talent sourcing": "Recruitment & Talent Acquisition",
    "payroll": "Payroll Management",
    "employee engagement": "Employee Engagement",
    "project management": "Project Management",
    "agile": "Agile / Scrum",
    "scrum": "Agile / Scrum",
    "jira": "Jira",
    "communication": "Communication Skills",
    "negotiation": "Negotiation Skills",

    # Finance & Accounts
    "accounting": "Accounting",
    "financial modeling": "Financial Modeling",
    "auditing": "Auditing",
    "taxation": "Taxation",
    "gst": "Taxation",
    "tally": "Tally ERP",
    "tally erp": "Tally ERP",
    "quickbooks": "QuickBooks"
}

# ===================================================================
# RELATED & TRANSFERABLE SKILL CLUSTERS
# Maps a canonical skill to interchangeable or adjacent competencies
# ===================================================================
RELATED_SKILL_CLUSTERS: Dict[str, Set[str]] = {
    "FastAPI": {"Django", "Flask", "Express.js", "Python"},
    "Django": {"FastAPI", "Flask", "Python"},
    "Flask": {"FastAPI", "Django", "Python"},
    "React": {"Vue.js", "Angular", "Next.js", "JavaScript"},
    "Vue.js": {"React", "Angular", "JavaScript"},
    "Angular": {"React", "Vue.js", "TypeScript"},
    "PostgreSQL": {"MySQL", "SQLite", "SQL"},
    "MySQL": {"PostgreSQL", "SQL"},
    "MongoDB": {"Cassandra", "Firebase"},
    "Docker": {"Kubernetes", "CI/CD"},
    "Kubernetes": {"Docker", "AWS"},
    "AWS": {"Microsoft Azure", "Google Cloud Platform"},
    "Microsoft Azure": {"AWS", "Google Cloud Platform"},
    "Power BI": {"Tableau", "Microsoft Excel"},
    "Tableau": {"Power BI", "Microsoft Excel"},
    "Scikit-Learn": {"PyTorch", "TensorFlow", "Pandas"},
    "PyTorch": {"TensorFlow", "Deep Learning"},
    "TensorFlow": {"PyTorch", "Deep Learning"},
    "JavaScript": {"TypeScript"},
    "TypeScript": {"JavaScript"}
}

# ===================================================================
# DOMAIN CATEGORIES
# ===================================================================
SKILL_CATEGORIES: Dict[str, str] = {
    "Python": "Programming Language",
    "JavaScript": "Programming Language",
    "TypeScript": "Programming Language",
    "Java": "Programming Language",
    "C++": "Programming Language",
    "FastAPI": "Backend Framework",
    "Django": "Backend Framework",
    "Flask": "Backend Framework",
    "React": "Frontend Framework",
    "Next.js": "Frontend Framework",
    "Vue.js": "Frontend Framework",
    "Node.js": "Runtime Environment",
    "PostgreSQL": "Database",
    "MySQL": "Database",
    "MongoDB": "NoSQL Database",
    "Redis": "Caching & In-Memory Store",
    "Docker": "DevOps & Containers",
    "Kubernetes": "Container Orchestration",
    "AWS": "Cloud Computing",
    "Microsoft Azure": "Cloud Computing",
    "Git": "Version Control",
    "Machine Learning": "Data Science & AI",
    "Deep Learning": "Data Science & AI",
    "Pandas": "Data Science & Analytics",
    "Power BI": "Business Intelligence",
    "Tableau": "Business Intelligence",
    "Microsoft Excel": "Business Analytics",
    "Recruitment & Talent Acquisition": "Human Resources",
    "Human Resources": "Human Resources",
    "Financial Modeling": "Finance & Accounting",
    "Accounting": "Finance & Accounting",
    "Project Management": "Management",
    "Agile / Scrum": "Management Methodology"
}


def clean_skill_string(skill: str) -> str:
    """Strips punctuation, trailing symbols, and trims whitespace"""
    if not skill:
        return ""
    # Normalize internal spaces, strip punctuation like commas, parentheses
    clean = re.sub(r'[\(\)\[\],;:]', ' ', skill)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def normalize_skill(skill: str) -> str:
    """
    Standardizes any raw candidate or job skill into its canonical form.
    E.g.:
    - 'JS', 'Javascript', 'ES6' -> 'JavaScript'
    - 'MS Excel', 'Excel' -> 'Microsoft Excel'
    - 'Python 3', 'Python Programming' -> 'Python'
    - 'K8s' -> 'Kubernetes'
    """
    if not skill or not skill.strip():
        return ""

    raw_clean = clean_skill_string(skill)
    lookup_key = raw_clean.lower()

    # 1. Exact alias / synonym match
    if lookup_key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[lookup_key]

    # 2. Check stripped version (e.g. without hyphens or dots)
    stripped_key = re.sub(r'[\.\-_]', '', lookup_key)
    if stripped_key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[stripped_key]

    # 3. If no dictionary alias matches, title-case the cleaned string
    return raw_clean.title()


def normalize_skills_list(skills: List[str]) -> List[str]:
    """
    Normalizes a list of skills and removes duplicates while preserving order.
    """
    seen: Set[str] = set()
    normalized_list: List[str] = []

    for raw in skills:
        canon = normalize_skill(raw)
        if canon and canon not in seen:
            seen.add(canon)
            normalized_list.append(canon)

    return normalized_list


def get_skill_category(skill: str) -> str:
    """Returns the high-level category of a skill"""
    canon = normalize_skill(skill)
    return SKILL_CATEGORIES.get(canon, "General Competency")


def get_related_skills(skill: str) -> List[str]:
    """
    Returns related or transferable skills for a given canonical skill.
    E.g. FastAPI -> ['Django', 'Flask', 'Express.js', 'Python']
    """
    canon = normalize_skill(skill)
    return list(RELATED_SKILL_CLUSTERS.get(canon, set()))
