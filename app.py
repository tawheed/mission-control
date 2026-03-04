"""Mission Control — 124 AI agents running your startup so you don't have to."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, RichLog, Static

# ---------------------------------------------------------------------------
# Bot definitions
# ---------------------------------------------------------------------------

DEPARTMENTS = {
    "Engineering Backend": {"color": "cyan", "short": "Backend"},
    "Engineering Frontend": {"color": "dodger_blue1", "short": "Frontend"},
    "Infrastructure": {"color": "dark_cyan", "short": "Infra/DevOps"},
    "QA": {"color": "medium_purple", "short": "QA"},
    "Product": {"color": "green", "short": "Product"},
    "Design": {"color": "magenta", "short": "Design"},
    "Data & ML": {"color": "bright_yellow", "short": "Data/ML"},
    "Marketing": {"color": "orange1", "short": "Marketing"},
    "Sales": {"color": "bright_green", "short": "Sales"},
    "Support": {"color": "sky_blue1", "short": "Support"},
    "HR & People": {"color": "plum2", "short": "People"},
    "Finance & Legal": {"color": "grey70", "short": "Finance"},
    "Executive": {"color": "gold1", "short": "Exec"},
    "Security": {"color": "red", "short": "Security"},
    "IT": {"color": "grey50", "short": "IT"},
}


@dataclass
class Bot:
    name: str
    role: str
    department: str
    personality: str  # brief trait for flavor
    chattiness: float = 0.5  # 0.0-1.0, affects how often they talk
    status: str = "online"  # online, busy, away


# fmt: off
BOT_DEFS: list[dict] = [
    # Engineering Backend (18)
    {"name": "Aria Chen", "role": "Staff Engineer", "department": "Engineering Backend", "personality": "precise, thorough", "chattiness": 0.8},
    {"name": "Marcus Webb", "role": "Senior Backend", "department": "Engineering Backend", "personality": "pragmatic, fast", "chattiness": 0.7},
    {"name": "Priya Sharma", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "curious, methodical", "chattiness": 0.6},
    {"name": "Jun Tanaka", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "quiet, deep thinker", "chattiness": 0.3},
    {"name": "Olumide Adeyemi", "role": "Senior Backend", "department": "Engineering Backend", "personality": "mentor, patient", "chattiness": 0.6},
    {"name": "Sofia Rodriguez", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "energetic, fast learner", "chattiness": 0.7},
    {"name": "Liam O'Connor", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "systems thinker", "chattiness": 0.5},
    {"name": "Mei Lin", "role": "Principal Engineer", "department": "Engineering Backend", "personality": "architect, big picture", "chattiness": 0.4},
    {"name": "Dmitri Volkov", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "performance obsessed", "chattiness": 0.6},
    {"name": "Amara Obi", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "detail oriented", "chattiness": 0.5},
    {"name": "Henrik Larsson", "role": "Senior Backend", "department": "Engineering Backend", "personality": "clean code advocate", "chattiness": 0.5},
    {"name": "Yuki Sato", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "testing enthusiast", "chattiness": 0.4},
    {"name": "Carlos Mendez", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "database guru", "chattiness": 0.5},
    {"name": "Fatima Al-Hassan", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "API design focused", "chattiness": 0.6},
    {"name": "Nikhil Patel", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "microservices expert", "chattiness": 0.5},
    {"name": "Ewa Kowalski", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "pragmatic debugger", "chattiness": 0.4},
    {"name": "Tomás Silva", "role": "Junior Backend", "department": "Engineering Backend", "personality": "eager, asks questions", "chattiness": 0.7},
    {"name": "Aisha Mohammed", "role": "Backend Engineer", "department": "Engineering Backend", "personality": "distributed systems", "chattiness": 0.5},
    # Engineering Frontend (14)
    {"name": "Devon Park", "role": "Senior Frontend", "department": "Engineering Frontend", "personality": "UI perfectionist", "chattiness": 0.8},
    {"name": "Zara Hussain", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "animation wizard", "chattiness": 0.7},
    {"name": "Lucas Bergström", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "accessibility first", "chattiness": 0.6},
    {"name": "Ines Moreau", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "component architect", "chattiness": 0.5},
    {"name": "Ryan Kim", "role": "Senior Frontend", "department": "Engineering Frontend", "personality": "performance tuner", "chattiness": 0.6},
    {"name": "Chioma Eze", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "design system lead", "chattiness": 0.5},
    {"name": "Oscar Nilsson", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "state management nerd", "chattiness": 0.4},
    {"name": "Maya Johansson", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "rapid prototyper", "chattiness": 0.7},
    {"name": "Ravi Krishnan", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "testing advocate", "chattiness": 0.5},
    {"name": "Elena Popescu", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "CSS wizard", "chattiness": 0.6},
    {"name": "Kenji Watanabe", "role": "Junior Frontend", "department": "Engineering Frontend", "personality": "eager learner", "chattiness": 0.6},
    {"name": "Aaliya Bashir", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "mobile-first thinker", "chattiness": 0.5},
    {"name": "Nils Andersen", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "build tooling expert", "chattiness": 0.4},
    {"name": "Leila Santos", "role": "Frontend Engineer", "department": "Engineering Frontend", "personality": "i18n specialist", "chattiness": 0.5},
    # Infrastructure (10)
    {"name": "Kai Okafor", "role": "SRE Lead", "department": "Infrastructure", "personality": "calm under pressure", "chattiness": 0.7},
    {"name": "Ingrid Haugen", "role": "DevOps Engineer", "department": "Infrastructure", "personality": "automation first", "chattiness": 0.6},
    {"name": "André Costa", "role": "Platform Engineer", "department": "Infrastructure", "personality": "Kubernetes whisperer", "chattiness": 0.5},
    {"name": "Wei Zhang", "role": "SRE", "department": "Infrastructure", "personality": "monitoring obsessed", "chattiness": 0.6},
    {"name": "Nadia Petrov", "role": "DevOps Engineer", "department": "Infrastructure", "personality": "CI/CD expert", "chattiness": 0.5},
    {"name": "Omar Farouk", "role": "Cloud Engineer", "department": "Infrastructure", "personality": "cost optimizer", "chattiness": 0.4},
    {"name": "Sven Eriksson", "role": "Platform Engineer", "department": "Infrastructure", "personality": "infra-as-code purist", "chattiness": 0.5},
    {"name": "Thandiwe Moyo", "role": "SRE", "department": "Infrastructure", "personality": "incident commander", "chattiness": 0.6},
    {"name": "Jakub Nowak", "role": "DevOps Engineer", "department": "Infrastructure", "personality": "pipeline builder", "chattiness": 0.4},
    {"name": "Rosa Martinez", "role": "Cloud Engineer", "department": "Infrastructure", "personality": "network specialist", "chattiness": 0.5},
    # QA (8)
    {"name": "Hana Yamamoto", "role": "QA Lead", "department": "QA", "personality": "breaks everything", "chattiness": 0.7},
    {"name": "Ivan Sokolov", "role": "QA Engineer", "department": "QA", "personality": "edge case finder", "chattiness": 0.6},
    {"name": "Grace Okonkwo", "role": "QA Engineer", "department": "QA", "personality": "automation builder", "chattiness": 0.5},
    {"name": "Leo Fischer", "role": "QA Engineer", "department": "QA", "personality": "regression hunter", "chattiness": 0.5},
    {"name": "Deepa Nair", "role": "QA Engineer", "department": "QA", "personality": "performance tester", "chattiness": 0.4},
    {"name": "Sam Taylor", "role": "QA Engineer", "department": "QA", "personality": "exploratory tester", "chattiness": 0.6},
    {"name": "Marta Kovic", "role": "QA Engineer", "department": "QA", "personality": "spec reader", "chattiness": 0.4},
    {"name": "Tariq Hassan", "role": "QA Engineer", "department": "QA", "personality": "mobile QA", "chattiness": 0.5},
    # Product (8)
    {"name": "Sam Rivera", "role": "VP Product", "department": "Product", "personality": "visionary, decisive", "chattiness": 0.7},
    {"name": "Nora Lindqvist", "role": "Senior PM", "department": "Product", "personality": "data-driven", "chattiness": 0.7},
    {"name": "James Oduya", "role": "Product Manager", "department": "Product", "personality": "user advocate", "chattiness": 0.6},
    {"name": "Chloe Dumont", "role": "Product Manager", "department": "Product", "personality": "feature prioritizer", "chattiness": 0.6},
    {"name": "Rajan Gupta", "role": "Product Manager", "department": "Product", "personality": "metrics obsessed", "chattiness": 0.5},
    {"name": "Vera Johansson", "role": "Product Analyst", "department": "Product", "personality": "insight miner", "chattiness": 0.5},
    {"name": "Daniel Asante", "role": "Product Manager", "department": "Product", "personality": "stakeholder wrangler", "chattiness": 0.5},
    {"name": "Lina Cho", "role": "Associate PM", "department": "Product", "personality": "curious, organized", "chattiness": 0.6},
    # Design (7)
    {"name": "Freya Andersson", "role": "Design Lead", "department": "Design", "personality": "pixel perfect", "chattiness": 0.6},
    {"name": "Kofi Mensah", "role": "Senior Designer", "department": "Design", "personality": "systems thinker", "chattiness": 0.5},
    {"name": "Yuna Park", "role": "UX Designer", "department": "Design", "personality": "research driven", "chattiness": 0.6},
    {"name": "Marco Rossi", "role": "UI Designer", "department": "Design", "personality": "brand guardian", "chattiness": 0.5},
    {"name": "Suki Patel", "role": "UX Designer", "department": "Design", "personality": "prototype queen", "chattiness": 0.6},
    {"name": "Emil Strand", "role": "Motion Designer", "department": "Design", "personality": "animation nerd", "chattiness": 0.5},
    {"name": "Adaeze Umeh", "role": "UX Researcher", "department": "Design", "personality": "empathy first", "chattiness": 0.5},
    # Data & ML (8)
    {"name": "Dr. Lena Virtanen", "role": "ML Lead", "department": "Data & ML", "personality": "model architect", "chattiness": 0.6},
    {"name": "Kwame Asante", "role": "Data Engineer", "department": "Data & ML", "personality": "pipeline builder", "chattiness": 0.5},
    {"name": "Anya Kuznetsova", "role": "ML Engineer", "department": "Data & ML", "personality": "experiment runner", "chattiness": 0.6},
    {"name": "Raj Malhotra", "role": "Data Scientist", "department": "Data & ML", "personality": "stats purist", "chattiness": 0.5},
    {"name": "Birgit Holm", "role": "Data Engineer", "department": "Data & ML", "personality": "ETL specialist", "chattiness": 0.4},
    {"name": "Chen Wei", "role": "ML Engineer", "department": "Data & ML", "personality": "GPU whisperer", "chattiness": 0.5},
    {"name": "Olu Bankole", "role": "Data Analyst", "department": "Data & ML", "personality": "dashboard creator", "chattiness": 0.5},
    {"name": "Mika Virtanen", "role": "ML Engineer", "department": "Data & ML", "personality": "NLP focused", "chattiness": 0.5},
    # Marketing (10)
    {"name": "Jordan Ellis", "role": "VP Marketing", "department": "Marketing", "personality": "brand storyteller", "chattiness": 0.7},
    {"name": "Anika Desai", "role": "Growth Lead", "department": "Marketing", "personality": "funnel optimizer", "chattiness": 0.7},
    {"name": "Pierre Dubois", "role": "Content Lead", "department": "Marketing", "personality": "wordsmith", "chattiness": 0.6},
    {"name": "Sade Williams", "role": "Marketing Manager", "department": "Marketing", "personality": "campaign runner", "chattiness": 0.6},
    {"name": "Viktor Novak", "role": "SEO Specialist", "department": "Marketing", "personality": "keyword hunter", "chattiness": 0.5},
    {"name": "Li Jing", "role": "Paid Ads Manager", "department": "Marketing", "personality": "ROAS focused", "chattiness": 0.6},
    {"name": "Rachel Foster", "role": "Social Media", "department": "Marketing", "personality": "trend spotter", "chattiness": 0.7},
    {"name": "Mateo Vargas", "role": "Marketing Ops", "department": "Marketing", "personality": "MarTech stack", "chattiness": 0.5},
    {"name": "Fiona MacLeod", "role": "Events Manager", "department": "Marketing", "personality": "logistics queen", "chattiness": 0.5},
    {"name": "Dayo Adebayo", "role": "Community Manager", "department": "Marketing", "personality": "people connector", "chattiness": 0.7},
    # Sales (8)
    {"name": "Tanya Brooks", "role": "VP Sales", "department": "Sales", "personality": "closer, direct", "chattiness": 0.7},
    {"name": "Kyle Morrison", "role": "AE Lead", "department": "Sales", "personality": "quota crusher", "chattiness": 0.7},
    {"name": "Amina Diallo", "role": "Account Executive", "department": "Sales", "personality": "relationship builder", "chattiness": 0.6},
    {"name": "Benny Zhao", "role": "SDR Lead", "department": "Sales", "personality": "outbound machine", "chattiness": 0.6},
    {"name": "Natasha Ivanova", "role": "Account Executive", "department": "Sales", "personality": "enterprise focus", "chattiness": 0.5},
    {"name": "Jake Sullivan", "role": "SDR", "department": "Sales", "personality": "cold call king", "chattiness": 0.6},
    {"name": "Esi Owusu", "role": "Sales Ops", "department": "Sales", "personality": "CRM perfectionist", "chattiness": 0.5},
    {"name": "Luis Romero", "role": "Solutions Engineer", "department": "Sales", "personality": "demo artist", "chattiness": 0.5},
    # Support (8)
    {"name": "Claire Beaumont", "role": "Support Lead", "department": "Support", "personality": "empathetic, thorough", "chattiness": 0.6},
    {"name": "Tunde Okafor", "role": "Support Engineer", "department": "Support", "personality": "patient explainer", "chattiness": 0.6},
    {"name": "Hannah Gruber", "role": "Support Engineer", "department": "Support", "personality": "docs writer", "chattiness": 0.5},
    {"name": "Arjun Mehta", "role": "Support Engineer", "department": "Support", "personality": "escalation handler", "chattiness": 0.6},
    {"name": "Kira Johansson", "role": "Support Engineer", "department": "Support", "personality": "bug reproducer", "chattiness": 0.5},
    {"name": "Felix Braun", "role": "Support Engineer", "department": "Support", "personality": "workaround finder", "chattiness": 0.5},
    {"name": "Wanjiku Kamau", "role": "Support Engineer", "department": "Support", "personality": "customer champion", "chattiness": 0.6},
    {"name": "Pablo Reyes", "role": "Support Engineer", "department": "Support", "personality": "ticket triager", "chattiness": 0.4},
    # HR & People (6)
    {"name": "Morgan Bailey", "role": "VP People", "department": "HR & People", "personality": "culture builder", "chattiness": 0.6},
    {"name": "Aiko Tanaka", "role": "HR Manager", "department": "HR & People", "personality": "process optimizer", "chattiness": 0.5},
    {"name": "David Osei", "role": "Recruiter", "department": "HR & People", "personality": "talent scout", "chattiness": 0.6},
    {"name": "Simone Bernard", "role": "People Ops", "department": "HR & People", "personality": "benefits expert", "chattiness": 0.4},
    {"name": "Erik Holm", "role": "L&D Manager", "department": "HR & People", "personality": "growth mindset", "chattiness": 0.5},
    {"name": "Zuri Ndlovu", "role": "DEI Lead", "department": "HR & People", "personality": "inclusive by default", "chattiness": 0.5},
    # Finance & Legal (6)
    {"name": "Rebecca Sterling", "role": "CFO", "department": "Finance & Legal", "personality": "numbers sharp", "chattiness": 0.5},
    {"name": "Akio Mori", "role": "Controller", "department": "Finance & Legal", "personality": "audit ready", "chattiness": 0.4},
    {"name": "Nkem Achebe", "role": "Financial Analyst", "department": "Finance & Legal", "personality": "model builder", "chattiness": 0.5},
    {"name": "Laura Schmidt", "role": "General Counsel", "department": "Finance & Legal", "personality": "risk assessor", "chattiness": 0.4},
    {"name": "Hassan El-Amin", "role": "Legal Counsel", "department": "Finance & Legal", "personality": "contract reviewer", "chattiness": 0.4},
    {"name": "Cindy Tran", "role": "Accounting", "department": "Finance & Legal", "personality": "detail oriented", "chattiness": 0.3},
    # Executive (5)
    {"name": "Alex Reeves", "role": "CEO", "department": "Executive", "personality": "visionary, brief", "chattiness": 0.4},
    {"name": "Priya Kapoor", "role": "CTO", "department": "Executive", "personality": "technical, strategic", "chattiness": 0.5},
    {"name": "Michael Obi", "role": "COO", "department": "Executive", "personality": "operations focused", "chattiness": 0.4},
    {"name": "Sarah Lindgren", "role": "CPO", "department": "Executive", "personality": "customer obsessed", "chattiness": 0.5},
    {"name": "Ben Nakamura", "role": "VP Engineering", "department": "Executive", "personality": "builder, enabler", "chattiness": 0.5},
    # Security (4)
    {"name": "Zain Abdullah", "role": "Security Lead", "department": "Security", "personality": "threat aware", "chattiness": 0.5},
    {"name": "Katya Petrova", "role": "Security Engineer", "department": "Security", "personality": "pen tester", "chattiness": 0.4},
    {"name": "Nate Collins", "role": "Security Engineer", "department": "Security", "personality": "compliance focused", "chattiness": 0.4},
    {"name": "Amira Khoury", "role": "Security Analyst", "department": "Security", "personality": "log analyst", "chattiness": 0.5},
    # IT (4)
    {"name": "Doug Carpenter", "role": "IT Manager", "department": "IT", "personality": "helpful, organized", "chattiness": 0.5},
    {"name": "Yemi Adebisi", "role": "IT Support", "department": "IT", "personality": "troubleshooter", "chattiness": 0.5},
    {"name": "Mila Novak", "role": "IT Support", "department": "IT", "personality": "endpoint manager", "chattiness": 0.4},
    {"name": "Roy Taniguchi", "role": "Sys Admin", "department": "IT", "personality": "infrastructure keeper", "chattiness": 0.4},
]
# fmt: on

# ---------------------------------------------------------------------------
# Message template pools
# ---------------------------------------------------------------------------

SERVICES = [
    "auth-service", "user-service", "billing-api", "notification-worker",
    "search-index", "analytics-pipeline", "payment-gateway", "email-sender",
    "cdn-proxy", "rate-limiter", "feature-flags", "webhook-relay",
    "cache-layer", "audit-log", "media-processor", "config-service",
    "identity-provider", "data-sync", "event-bus", "api-gateway",
]

VERSIONS = [
    "v2.3.1", "v1.8.0", "v3.0.0-rc1", "v2.14.2", "v1.12.5",
    "v4.1.0", "v2.0.3", "v3.2.1", "v1.5.7", "v2.9.0",
]

FEATURES = [
    "SSO integration", "dark mode", "bulk export", "real-time collab",
    "webhook retry logic", "rate limiting v2", "search autocomplete",
    "dashboard redesign", "onboarding wizard", "API key rotation",
    "multi-tenant isolation", "audit trail", "custom fields",
    "email templates", "usage analytics", "role-based access",
    "batch processing", "PDF generation", "Slack integration",
    "mobile push notifications", "2FA enrollment flow",
]

ENVIRONMENTS = ["staging", "production", "dev", "canary", "preview"]

ERRORS = [
    "ConnectionTimeout", "RateLimitExceeded", "AuthTokenExpired",
    "SchemaValidationError", "DeadlockDetected", "OutOfMemoryError",
    "CertificateExpired", "DNSResolutionFailed", "PermissionDenied",
    "CircuitBreakerOpen", "QueueOverflow", "CacheMiss",
]

METRICS = [
    "p99 latency", "error rate", "throughput", "CPU usage", "memory",
    "queue depth", "cache hit rate", "connection pool", "disk I/O",
    "request count", "GC pause time", "thread count",
]

TECH_TOPICS = [
    "GraphQL vs REST", "event sourcing", "CQRS pattern", "gRPC migration",
    "edge caching", "zero-trust auth", "canary deployments", "feature flags",
    "trunk-based development", "observability", "chaos engineering",
    "schema migrations", "blue-green deploys", "service mesh",
]

PR_NUMBERS = list(range(1234, 1320))

MARKETING_CAMPAIGNS = [
    "Spring Launch", "Product Hunt Day", "Enterprise Push Q2",
    "Dev Conference Blitz", "Year-End Wrap", "Customer Stories",
    "ABM Pilot", "Rebrand 2025", "Holiday Promo", "Webinar Series",
]
MARKETING_CHANNELS = [
    "organic search", "paid social", "email nurture", "LinkedIn ads",
    "Google Ads", "content syndication", "partner co-marketing",
    "podcast sponsorship", "YouTube pre-roll", "Reddit community",
]
SALES_STAGES = [
    "Discovery", "Qualification", "Demo Scheduled", "Proposal Sent",
    "Negotiation", "Verbal Commit", "Closed Won", "Closed Lost",
]
CUSTOMERS = [
    "Acme Corp", "Globex Industries", "Initech", "Umbrella LLC",
    "Massive Dynamic", "Soylent Corp", "Wonka Enterprises",
    "Sterling Cooper", "Dunder Mifflin", "Pied Piper",
    "Hooli", "Stark Industries", "Wayne Enterprises",
]
TICKET_TOPICS = [
    "SSO login loop", "CSV export timeout", "webhook not firing",
    "missing email notifications", "dashboard loading slow",
    "permission denied on admin page", "API rate limit confusion",
    "password reset broken", "billing charge disputed", "2FA lockout",
]
HR_TOPICS = [
    "onboarding checklist", "benefits enrollment", "performance review cycle",
    "PTO policy update", "engagement survey", "L&D budget",
    "hiring pipeline", "diversity report", "offboarding process",
    "comp benchmarking",
]
LEGAL_TOPICS = [
    "DPA review", "vendor contract", "NDA renewal", "SOC 2 compliance",
    "privacy policy update", "terms of service revision", "IP assignment",
    "export control check", "GDPR data request", "insurance renewal",
]
DESIGN_SCREENS = [
    "onboarding flow", "settings page", "dashboard v2", "pricing page",
    "checkout flow", "user profile", "notification center", "admin panel",
    "search results", "mobile nav", "empty states", "error pages",
]
DATA_MODELS = [
    "churn prediction", "lead scoring", "recommendation engine",
    "anomaly detection", "demand forecasting", "NLP classifier",
    "embedding model", "time-series forecast", "clustering pipeline",
    "A/B test analyzer",
]

# Template functions — each returns a message string

def _t_deploy(bot: Bot) -> str:
    svc = random.choice(SERVICES)
    ver = random.choice(VERSIONS)
    env = random.choice(ENVIRONMENTS)
    return random.choice([
        f"Just deployed {svc} {ver} to {env}. All green.",
        f"Pushed {svc} {ver} to {env} \u2014 rolling out now.",
        f"{svc} {ver} is live on {env}. No alerts so far.",
        f"Deploy complete: {svc} {ver} \u2192 {env}. Monitoring.",
        f"Shipped {svc} {ver} to {env}. Build time: {random.randint(45, 180)}s.",
    ])

def _t_pr(bot: Bot) -> str:
    pr = random.choice(PR_NUMBERS)
    feat = random.choice(FEATURES)
    return random.choice([
        f"Merged PR #{pr} \u2014 {feat}. Ready for review in staging.",
        f"PR #{pr} ({feat}) is up. Would love a review.",
        f"Just opened PR #{pr} for {feat}. Pretty clean diff, ~{random.randint(40, 300)} lines.",
        f"Closed PR #{pr} \u2014 {feat} shipped!",
        f"Rebased PR #{pr} onto main. {feat} looking solid.",
    ])

def _t_sprint(bot: Bot) -> str:
    return random.choice([
        f"Sprint velocity looking good \u2014 {random.randint(28, 52)} points this week.",
        "Updated the board. We're on track for the sprint goal.",
        f"Moved {random.randint(3, 8)} tickets to Done today.",
        "Standup notes posted in the wiki.",
        f"Backlog groomed \u2014 {random.randint(12, 30)} stories estimated.",
        "Retro action items from last sprint are all resolved.",
        "Sprint demo at 3pm \u2014 everyone welcome.",
    ])

def _t_question(bot: Bot, target: str) -> str:
    svc = random.choice(SERVICES)
    feat = random.choice(FEATURES)
    dept = bot.department
    if dept in ("Engineering Backend", "Engineering Frontend"):
        return random.choice([
            f"@{target} are we still on track for {feat} this sprint?",
            f"@{target} does {svc} support batch requests yet?",
            f"@{target} have you seen the error spike on {svc}?",
            f"@{target} what's the status on the {svc} migration?",
            f"@{target} is {svc} ready for the load test tomorrow?",
            f"@{target} can you review the {feat} API spec?",
            f"@{target} thoughts on the {random.choice(TECH_TOPICS)} approach?",
            f"@{target} did the schema migration for {svc} land?",
        ])
    if dept == "Infrastructure":
        return random.choice([
            f"@{target} are the {svc} pods healthy after the rollout?",
            f"@{target} do we have monitoring for the new {svc} endpoint?",
            f"@{target} what's the current cost for {svc} infra?",
            f"@{target} can we get staging access for {svc} load testing?",
            f"@{target} is the {svc} Terraform state locked by someone?",
            f"@{target} when is the next maintenance window?",
            f"@{target} should we set up a canary deploy for {feat}?",
        ])
    if dept == "QA":
        return random.choice([
            f"@{target} do we have a test environment for {feat}?",
            f"@{target} what are the acceptance criteria for {feat}?",
            f"@{target} is the {svc} regression suite up to date?",
            f"@{target} can I get test data for {feat}?",
            f"@{target} should we block release for the {svc} flaky tests?",
            f"@{target} are there known issues with {feat} on mobile?",
        ])
    if dept == "Product":
        return random.choice([
            f"@{target} what's the ETA on {feat}?",
            f"@{target} do we have usage data for {feat}?",
            f"@{target} can we scope down {feat} for the MVP?",
            f"@{target} how are customers reacting to {feat}?",
            f"@{target} should we prioritize {feat} over the {svc} work?",
            f"@{target} is the {feat} PRD finalized?",
        ])
    if dept == "Design":
        return random.choice([
            f"@{target} can you check the {random.choice(DESIGN_SCREENS)} implementation against the mocks?",
            f"@{target} are the {random.choice(DESIGN_SCREENS)} designs final?",
            f"@{target} do we need a new component for {feat}?",
            f"@{target} what's the interaction pattern for {feat}?",
            f"@{target} can we schedule a usability review for {random.choice(DESIGN_SCREENS)}?",
            f"@{target} is the design system token for this approved?",
        ])
    if dept == "Data & ML":
        model = random.choice(DATA_MODELS)
        return random.choice([
            f"@{target} is the training data for {model} ready?",
            f"@{target} what's the expected latency for {model} inference?",
            f"@{target} can we get more compute for the {model} training run?",
            f"@{target} are there data quality issues in the {svc} pipeline?",
            f"@{target} should we A/B test the new {model} against baseline?",
            f"@{target} what metrics should we track for {model}?",
        ])
    if dept == "Sales":
        customer = random.choice(CUSTOMERS)
        return random.choice([
            f"@{target} does {feat} work for {customer}'s use case?",
            f"@{target} can we get a demo environment for {customer}?",
            f"@{target} what's our positioning against {random.choice(['Competitor A','Competitor B'])}?",
            f"@{target} is {feat} ready for enterprise customers?",
            f"@{target} can we expedite the {customer} contract?",
            f"@{target} when can I tell {customer} that {feat} ships?",
        ])
    if dept == "Support":
        topic = random.choice(TICKET_TOPICS)
        return random.choice([
            f"@{target} is the {topic} issue a known bug?",
            f"@{target} do we have a workaround for {topic}?",
            f"@{target} should I escalate the {topic} tickets to eng?",
            f"@{target} when is the fix for {topic} shipping?",
            f"@{target} can we update the KB article for {topic}?",
            f"@{target} are other customers seeing {topic} too?",
        ])
    if dept == "Marketing":
        campaign = random.choice(MARKETING_CAMPAIGNS)
        return random.choice([
            f"@{target} is {feat} ready for the '{campaign}' announcement?",
            f"@{target} can we get a quote for the {feat} case study?",
            f"@{target} what's the messaging for {feat}?",
            f"@{target} do we have assets for the '{campaign}' launch?",
            f"@{target} when does the blog post for {feat} go live?",
            f"@{target} can we feature {feat} in the newsletter?",
        ])
    if dept == "HR & People":
        return random.choice([
            f"@{target} is the job description for the {random.choice(['backend','frontend','product','design'])} role approved?",
            f"@{target} when are performance reviews due?",
            f"@{target} can we schedule the team building event for next month?",
            f"@{target} what's the status on the new hire onboarding?",
            f"@{target} do we have budget for the L&D program?",
            f"@{target} is the engagement survey ready to send?",
        ])
    if dept == "Finance & Legal":
        return random.choice([
            f"@{target} is the {random.choice(LEGAL_TOPICS)} signed off?",
            f"@{target} do we have budget approval for the {svc} project?",
            f"@{target} when is the next audit deadline?",
            f"@{target} can we expedite the vendor payment?",
            f"@{target} is the contract for {random.choice(CUSTOMERS)} ready for review?",
            f"@{target} what's the burn rate looking like this month?",
        ])
    if dept == "Executive":
        return random.choice([
            f"@{target} can we get an update on {feat} for the board deck?",
            f"@{target} what's the team's capacity for next quarter?",
            f"@{target} how are the OKRs tracking?",
            f"@{target} can we discuss the {feat} strategy?",
            f"@{target} what's the hiring plan for {random.choice(list(DEPARTMENTS.keys()))}?",
            f"@{target} should we reprioritize given the {random.choice(['market shift','customer feedback','competitor move'])}?",
        ])
    if dept == "Security":
        return random.choice([
            f"@{target} is {svc} compliant with the new security policy?",
            f"@{target} when is the pen test for {svc} scheduled?",
            f"@{target} did we patch the latest CVE on {svc}?",
            f"@{target} can we review the access controls for {svc}?",
            f"@{target} is the security incident playbook up to date?",
            f"@{target} should we rotate the {svc} API keys?",
        ])
    if dept == "IT":
        return random.choice([
            f"@{target} did the new laptops ship?",
            f"@{target} is the SSO integration with {random.choice(['Okta','Google Workspace','Azure AD'])} working?",
            f"@{target} can we reclaim the unused software licenses?",
            f"@{target} when is the VPN maintenance window?",
            f"@{target} should we upgrade the office WiFi?",
            f"@{target} is the new employee provisioning script ready?",
        ])
    # Fallback
    return random.choice([
        f"@{target} are we still on track for {feat} this sprint?",
        f"@{target} quick q \u2014 does {svc} support batch requests yet?",
        f"@{target} can you take a look at the {feat} spec?",
        f"@{target} what's the status on the {svc} migration?",
    ])

def _t_reply_agree(bot: Bot, target: str) -> str:
    return random.choice([
        f"@{target} +1, looks good to me.",
        f"@{target} agreed. Ship it.",
        f"@{target} LGTM, ship it.",
        f"@{target} yep, that matches what I had in mind.",
        f"@{target} makes sense. Let's go with that.",
        f"@{target} nice work on that!",
        f"@{target} solid approach. I'm on board.",
    ])

def _t_reply_discuss(bot: Bot, target: str) -> str:
    topic = random.choice(TECH_TOPICS)
    svc = random.choice(SERVICES)
    return random.choice([
        f"@{target} hmm, what about the {topic} angle? Might be simpler.",
        f"@{target} one concern \u2014 this could affect {svc} latency.",
        f"@{target} have we considered the {topic} tradeoffs here?",
        f"@{target} I see your point, but the {svc} team might push back.",
        f"@{target} interesting. Let me prototype something and share.",
        f"@{target} let's sync on this after standup. I have some ideas.",
        f"@{target} worth checking with the {random.choice(list(DEPARTMENTS.keys())).split()[0]} team first.",
    ])

def _t_technical(bot: Bot) -> str:
    svc = random.choice(SERVICES)
    metric = random.choice(METRICS)
    err = random.choice(ERRORS)
    return random.choice([
        f"{svc} {metric} is at {random.randint(1, 99)}{'ms' if 'latency' in metric else '%'}. Looks normal.",
        f"Seeing intermittent {err} on {svc}. Investigating.",
        f"Fixed the {err} in {svc} \u2014 was a config issue.",
        f"FYI: {svc} {metric} spiked to {random.randint(200, 800)}ms. Back to normal now.",
        f"Profiled {svc} \u2014 the bottleneck is in the DB layer. {metric} doubled after the schema change.",
        f"Heads up: {svc} is at {random.randint(60, 95)}% {metric}. Scaling up.",
        f"Added alerting for {svc} {metric}. Threshold: {random.randint(100, 500)}ms.",
        f"The {err} on {svc} was a flaky test. Disabled it for now.",
        f"Config update: {svc} connection pool bumped from {random.randint(10, 30)} to {random.randint(40, 80)}.",
    ])

def _t_social(bot: Bot) -> str:
    return random.choice([
        "Anyone up for lunch at the new ramen place?",
        "Happy Friday everyone!",
        "WFH today \u2014 plumber coming. Online all day though.",
        "Coffee run in 10 if anyone wants to join.",
        "Reminder: team outing next Thursday!",
        "Just hit my 1-year anniversary here! Time flies.",
        "Shoutout to the team for an amazing Q4. We crushed it.",
        "Who broke the office playlist? I'm hearing polka.",
        "Heads up: I'll be OOO next Monday. Ping me on Slack if urgent.",
        f"Happy birthday to our very own {random.choice(['Aria', 'Marcus', 'Devon', 'Sam', 'Kai'])}!",
        "New coffee machine in the kitchen. Life changing.",
        "Anyone watching the game tonight?",
        "Starting a book club if anyone's interested. DM me.",
        "The office dog is back today. Productivity may vary.",
        "Wrapping up early today \u2014 kids' school play. Back online at 8pm.",
    ])

def _t_backend(bot: Bot) -> str:
    svc = random.choice(SERVICES)
    return random.choice([
        f"Optimized the {svc} query \u2014 down from {random.randint(200,800)}ms to {random.randint(15,60)}ms.",
        f"Added pagination to the {svc} list endpoint. Was returning 10k rows unbounded.",
        f"Schema migration for {svc} is ready \u2014 adding {random.choice(['indexes','partitioning','a new column','foreign keys'])}.",
        f"Refactored {svc} to use connection pooling. Pool size: {random.randint(20,60)}.",
        f"The {svc} N+1 query is fixed. Went from {random.randint(80,200)} queries to {random.randint(2,5)}.",
        f"Wrote a data backfill script for {svc}. ~{random.randint(1,8)}M rows, should take {random.randint(10,45)} min.",
        f"Added {random.choice(['Redis caching','write-behind cache','read replicas'])} to {svc}. Latency cut in half.",
        f"API versioning on {svc} is done \u2014 v1 stays, v2 is the new default.",
    ])

def _t_frontend(bot: Bot) -> str:
    feat = random.choice(FEATURES)
    return random.choice([
        f"Lighthouse score for {feat} page: {random.randint(88,100)} performance, {random.randint(90,100)} a11y.",
        f"Bundle size after tree-shaking {feat}: {random.randint(40,180)}KB (down from {random.randint(200,450)}KB).",
        f"New {feat} component is in Storybook. All variants documented.",
        f"Fixed the layout shift on {feat} \u2014 CLS down to {random.uniform(0.01, 0.08):.3f}.",
        f"Keyboard navigation for {feat} is fully working now. Tab order makes sense.",
        f"Migrated {feat} from class components to hooks. Much cleaner.",
        f"Added skeleton loaders to {feat}. Perceived load time feels instant.",
        f"i18n strings for {feat} extracted \u2014 {random.randint(30,120)} keys ready for translation.",
    ])

def _t_infra(bot: Bot) -> str:
    svc = random.choice(SERVICES)
    return random.choice([
        f"Scaled {svc} pods from {random.randint(3,8)} to {random.randint(10,24)}. Traffic spike handled.",
        f"Terraform plan for {svc}: {random.randint(3,12)} resources to add, {random.randint(0,3)} to change.",
        f"TLS cert for {svc} renewed. Expires in {random.randint(60,365)} days.",
        f"CI pipeline for {svc} optimized \u2014 build time from {random.randint(8,20)}min to {random.randint(2,6)}min.",
        f"AWS cost for {svc} last month: ${random.randint(800,5000)}. Found {random.randint(1,4)} idle resources to kill.",
        f"Migrated {svc} to arm64 nodes. ~{random.randint(15,35)}% cost savings.",
        f"New Grafana dashboard for {svc} is live. Alert thresholds tuned.",
        f"Disaster recovery test passed for {svc}. RTO: {random.randint(5,30)} min.",
    ])

def _t_qa(bot: Bot) -> str:
    svc = random.choice(SERVICES)
    feat = random.choice(FEATURES)
    return random.choice([
        f"Found a race condition in {svc} under concurrent load. Opened a bug.",
        f"Test coverage for {feat}: {random.randint(72,95)}%. Still missing edge cases for error paths.",
        f"Regression suite passed \u2014 {random.randint(180,500)} tests, {random.randint(0,2)} flaky.",
        f"Exploratory testing on {feat} done. Filed {random.randint(2,7)} bugs, {random.randint(1,3)} are P1.",
        f"Load test results: {svc} handles {random.randint(500,3000)} RPS before degradation.",
        f"The {feat} flow breaks on Safari when using a screen reader. Logging accessibility bug.",
        f"Automated the {feat} smoke tests. Runs in {random.randint(30,180)}s now.",
        f"Signed off on {feat} for release. All acceptance criteria met.",
    ])

def _t_product(bot: Bot) -> str:
    feat = random.choice(FEATURES)
    return random.choice([
        f"PRD for {feat} is ready for eng review. Scope is tight this time.",
        f"A/B test results on {feat}: variant B won with {random.randint(5,25)}% lift in conversions.",
        f"NPS for {feat} is {random.randint(35,72)}. Top complaint: {random.choice(['complexity','speed','discoverability'])}.",
        f"Roadmap updated \u2014 {feat} moved to {random.choice(['this sprint','next sprint','Q3','backlog'])}.",
        f"Customer interview takeaway: {feat} is the #1 requested capability.",
        f"Prioritization done \u2014 cutting {random.randint(2,5)} items to make room for {feat}.",
        f"Usage data shows {random.randint(8,40)}% of users engage with {feat} weekly.",
        f"Feature flag plan for {feat}: 5% rollout \u2192 25% \u2192 100% over 2 weeks.",
    ])

def _t_design(bot: Bot) -> str:
    screen = random.choice(DESIGN_SCREENS)
    return random.choice([
        f"Figma file for {screen} is ready. {random.randint(3,8)} screens, all states covered.",
        f"Usability test on {screen}: {random.randint(4,6)}/5 participants completed the task unaided.",
        f"Design system update: new {random.choice(['button variants','spacing tokens','color ramp','icon set'])} pushed.",
        f"Prototype for {screen} is in Figma. Interactive, ready for stakeholder review.",
        f"Accessibility audit on {screen}: contrast ratio issues on {random.randint(2,6)} elements. Fixing now.",
        f"Mobile designs for {screen} adapted. Breakpoints at 375px and 768px.",
        f"Design QA on {screen} \u2014 found {random.randint(3,10)} pixel discrepancies vs implementation.",
        f"User flow diagram for {screen} updated. Added {random.randint(2,4)} edge case paths.",
    ])

def _t_data(bot: Bot) -> str:
    model = random.choice(DATA_MODELS)
    return random.choice([
        f"{model} training run #{random.randint(12,99)} complete. AUC: 0.{random.randint(82,97)}.",
        f"ETL pipeline processed {random.randint(5,50)}M rows overnight. No failures.",
        f"Feature importance analysis for {model} done \u2014 top 3 features explain {random.randint(60,85)}%.",
        f"A/B experiment #{random.randint(100,300)} concluded: {random.choice(['significant','not significant','borderline'])} at p<0.05.",
        f"Data quality check: {random.randint(0,3)}% null rate on key columns. Within threshold.",
        f"New {model} outperforms baseline by {random.randint(3,15)}%. Ready for shadow mode.",
        f"Airflow DAG for {model} retrained on schedule. Next run in {random.randint(4,24)}h.",
        f"Dashboard for {model} metrics is live. Stakeholders have access.",
    ])

def _t_marketing(bot: Bot) -> str:
    campaign = random.choice(MARKETING_CAMPAIGNS)
    channel = random.choice(MARKETING_CHANNELS)
    return random.choice([
        f"'{campaign}' campaign launched on {channel}. Early CTR: {random.uniform(1.5, 6.0):.1f}%.",
        f"SEO update: organic traffic up {random.randint(5,30)}% MoM. Top keyword ranking improved.",
        f"Email nurture sequence open rate: {random.randint(22,45)}%. Click-through: {random.randint(3,12)}%.",
        f"Content calendar for next month is finalized \u2014 {random.randint(8,20)} pieces planned.",
        f"'{campaign}' ROI so far: {random.randint(2,8)}x. {channel} is the top performer.",
        f"Blog post on {random.choice(TECH_TOPICS)} published. Targeting featured snippet.",
        f"Social engagement up {random.randint(10,60)}% this week. That LinkedIn post went viral.",
        f"MQL count this month: {random.randint(80,300)}. Pipeline attribution looks healthy.",
    ])

def _t_sales(bot: Bot) -> str:
    customer = random.choice(CUSTOMERS)
    stage = random.choice(SALES_STAGES)
    return random.choice([
        f"{customer} deal moved to {stage}. ACV: ${random.randint(20,200)}K.",
        f"Pipeline this quarter: ${random.randint(500,3000)}K. {random.randint(60,95)}% to target.",
        f"Demo with {customer} went well. They want a follow-up with their CTO.",
        f"Win/loss analysis: lost {customer} to {random.choice(['pricing','missing feature','competitor','timing'])}.",
        f"Renewal for {customer} is up next month. Health score: {random.choice(['green','yellow','at risk'])}.",
        f"Booked {random.randint(3,10)} demos this week. SDR team is crushing it.",
        f"Competitive intel: {random.choice(['Competitor A','Competitor B'])} dropped their price by {random.randint(10,30)}%.",
        f"{customer} asked about {random.choice(FEATURES)}. Logging as a feature request.",
    ])

def _t_support(bot: Bot) -> str:
    topic = random.choice(TICKET_TOPICS)
    return random.choice([
        f"Ticket volume today: {random.randint(30,120)}. Top issue: {topic}.",
        f"CSAT this week: {random.randint(85,98)}%. Slight dip from {topic} tickets.",
        f"Escalated {topic} to engineering \u2014 {random.randint(5,20)} customers affected.",
        f"KB article for '{topic}' updated. Should reduce repeat tickets.",
        f"Median first response time: {random.randint(4,30)} min. Under SLA.",
        f"Created a canned response for {topic}. Will save ~{random.randint(2,5)} min per ticket.",
        f"Customer {random.choice(CUSTOMERS)} flagged as churn risk \u2014 multiple {topic} tickets.",
        f"Resolved {random.randint(15,50)} tickets today. Backlog down to {random.randint(10,40)}.",
    ])

def _t_hr(bot: Bot) -> str:
    topic = random.choice(HR_TOPICS)
    return random.choice([
        f"{topic.capitalize()} is finalized. Rolling out to all teams next week.",
        f"Hiring update: {random.randint(3,12)} open roles, {random.randint(10,50)} candidates in pipeline.",
        f"Engagement survey results: {random.randint(72,92)}% favorable. Action items being drafted.",
        f"New onboarding cohort: {random.randint(3,8)} people starting Monday.",
        f"L&D budget approved \u2014 ${random.randint(500,2000)} per head for training.",
        f"Updated the {topic} process. Docs in Notion.",
        f"Retention rate this quarter: {random.randint(92,99)}%. Exit interviews show no red flags.",
        f"Offer extended to a strong candidate for the {random.choice(['backend','frontend','product','design'])} role.",
    ])

def _t_finance(bot: Bot) -> str:
    topic = random.choice(LEGAL_TOPICS)
    return random.choice([
        f"Monthly burn rate: ${random.randint(200,800)}K. Runway: {random.randint(14,36)} months.",
        f"{topic.capitalize()} review is done \u2014 no blockers.",
        f"Q{random.randint(1,4)} audit prep is {random.randint(70,100)}% complete.",
        f"Budget approval for {random.choice(SERVICES)} scaling \u2014 ${random.randint(5,50)}K/mo.",
        f"Vendor invoice from {random.choice(CUSTOMERS)} processed. Net-30 terms.",
        f"Updated the financial model \u2014 new ARR projection: ${random.randint(2,20)}M.",
        f"Contract for {random.choice(['AWS','GCP','Datadog','Snowflake','Slack'])} renewal is under review.",
        f"Expense reports deadline is Friday. {random.randint(5,20)} still outstanding.",
    ])

def _t_executive(bot: Bot) -> str:
    return random.choice([
        f"Board deck for Q{random.randint(1,4)} is ready. Key theme: {random.choice(['growth','efficiency','expansion','profitability'])}.",
        "All-hands agenda is set. Main topics: roadmap update and team wins.",
        f"Strategic initiative '{random.choice(FEATURES)}' kicked off. Exec sponsor assigned.",
        f"Investor update sent. ARR growth: {random.randint(20,80)}% YoY.",
        f"Leadership offsite planned for {random.choice(['next month','Q3','early Q4'])}. Focus: org structure.",
        f"Headcount plan approved \u2014 adding {random.randint(5,20)} roles across {random.randint(2,4)} teams.",
        f"Customer NPS trending up. Overall score: {random.randint(45,75)}.",
        f"OKRs for next quarter drafted. {random.randint(3,5)} company-level objectives.",
    ])

def _t_security(bot: Bot) -> str:
    svc = random.choice(SERVICES)
    return random.choice([
        f"Vuln scan on {svc} complete \u2014 {random.randint(0,5)} findings, {random.randint(0,2)} critical.",
        f"Pen test report for {svc} is in. {random.randint(1,4)} medium-severity issues to fix.",
        f"New CVE affecting {random.choice(['OpenSSL','log4j','curl','nginx'])} \u2014 patching across all services.",
        f"SOC 2 evidence collection: {random.randint(70,100)}% complete. Audit starts next month.",
        f"WAF rules updated \u2014 blocked {random.randint(500,5000)} malicious requests last week.",
        f"Security awareness training completion: {random.randint(75,98)}%. Sending reminders.",
        f"Rotated API keys for {svc}. Old keys expire in 24h.",
        f"Incident response drill scheduled for Thursday. Tabletop exercise on {random.choice(['data breach','ransomware','DDoS'])}.",
    ])

def _t_it(bot: Bot) -> str:
    return random.choice([
        f"Provisioned {random.randint(3,10)} new laptops for the incoming cohort.",
        f"SSO integration with {random.choice(['Okta','Google Workspace','Azure AD'])} updated. No downtime.",
        f"Software license audit: {random.randint(5,20)} unused {random.choice(['Figma','Notion','Jira','Slack'])} seats. Reclaiming.",
        f"VPN capacity increased \u2014 peak concurrent users was hitting {random.randint(60,95)}% of limit.",
        f"MDM policy pushed to all devices. {random.randint(2,8)} non-compliant machines flagged.",
        f"New printer on floor {random.randint(2,5)} is set up. Driver link is in #it-help.",
        f"Resolved {random.randint(5,20)} IT tickets today. Most common: password reset.",
        f"Office WiFi upgraded \u2014 new AP on floor {random.randint(2,5)}. Speed test: {random.randint(200,600)}Mbps.",
    ])

def _t_crossdept(bot: Bot, target: str) -> str:
    feat = random.choice(FEATURES)
    svc = random.choice(SERVICES)
    dept = bot.department
    if dept in ("Engineering Backend", "Engineering Frontend"):
        return random.choice([
            f"@{target} can product confirm the {feat} spec is final?",
            f"@{target} design review needed for the {feat} PR.",
            f"@{target} QA \u2014 {feat} is in staging, ready for your pass.",
            f"@{target} support is reporting issues with {svc}. We're investigating.",
            f"@{target} infra \u2014 do we need to scale {svc} before launch?",
            f"@{target} security \u2014 can you review the auth changes in {svc}?",
        ])
    if dept == "Infrastructure":
        return random.choice([
            f"@{target} engineering \u2014 {svc} needs a config change for the new infra.",
            f"@{target} security \u2014 cert rotation for {svc} is scheduled tonight.",
            f"@{target} finance \u2014 cloud costs for {svc} need budget approval.",
            f"@{target} heads up, the {svc} deployment pipeline has a new gate.",
            f"@{target} can someone from eng verify {svc} after the migration?",
        ])
    if dept == "QA":
        return random.choice([
            f"@{target} engineering \u2014 found a blocker in {feat}. Details in the bug.",
            f"@{target} product \u2014 acceptance criteria for {feat} need clarification.",
            f"@{target} design \u2014 the {feat} flow doesn't match the latest mocks.",
            f"@{target} release is blocked until the {svc} regression passes.",
            f"@{target} support \u2014 heads up, {feat} has a known edge case. Workaround in the ticket.",
        ])
    if dept == "Product":
        return random.choice([
            f"@{target} engineering \u2014 what's the effort estimate for {feat}?",
            f"@{target} design \u2014 can we get mocks for {feat} by end of week?",
            f"@{target} marketing \u2014 {feat} is launching soon, let's sync on messaging.",
            f"@{target} sales \u2014 any customer feedback on the {feat} beta?",
            f"@{target} data \u2014 can we get usage metrics for {feat}?",
            f"@{target} support \u2014 what's the top complaint related to {feat}?",
        ])
    if dept == "Design":
        return random.choice([
            f"@{target} engineering \u2014 the {feat} handoff is in Figma. Let me know if questions.",
            f"@{target} product \u2014 need requirements clarified for the {random.choice(DESIGN_SCREENS)} redesign.",
            f"@{target} frontend \u2014 can you check the {random.choice(DESIGN_SCREENS)} implementation?",
            f"@{target} marketing \u2014 brand assets for {feat} are ready.",
            f"@{target} research session for {random.choice(DESIGN_SCREENS)} is scheduled. Want to observe?",
        ])
    if dept == "Data & ML":
        model = random.choice(DATA_MODELS)
        return random.choice([
            f"@{target} engineering \u2014 the {model} API needs a new endpoint for scoring.",
            f"@{target} product \u2014 {model} results show interesting user segments.",
            f"@{target} infra \u2014 we need more GPU quota for {model} training.",
            f"@{target} the experiment results for {feat} are ready for review.",
            f"@{target} marketing \u2014 the {model} data supports the campaign targeting.",
        ])
    if dept == "Sales":
        customer = random.choice(CUSTOMERS)
        return random.choice([
            f"@{target} engineering \u2014 {customer} needs a demo environment for {feat}.",
            f"@{target} product \u2014 {customer} is asking for {feat}. Can we fast-track?",
            f"@{target} legal \u2014 the {customer} contract needs a custom clause.",
            f"@{target} support \u2014 {customer} is at risk. Can we prioritize their tickets?",
            f"@{target} marketing \u2014 can we get a case study from {customer}?",
        ])
    if dept == "Support":
        topic = random.choice(TICKET_TOPICS)
        return random.choice([
            f"@{target} engineering \u2014 escalating {topic}. {random.randint(5,20)} customers affected.",
            f"@{target} product \u2014 {topic} is the #1 support driver this week.",
            f"@{target} sales \u2014 heads up, {random.choice(CUSTOMERS)} is frustrated about {topic}.",
            f"@{target} QA \u2014 can we reproduce {topic} in staging?",
            f"@{target} docs for {topic} need updating \u2014 getting repeat questions.",
        ])
    if dept == "Marketing":
        campaign = random.choice(MARKETING_CAMPAIGNS)
        return random.choice([
            f"@{target} product \u2014 is {feat} launch-ready? '{campaign}' goes live Monday.",
            f"@{target} design \u2014 need visuals for the '{campaign}' campaign.",
            f"@{target} sales \u2014 '{campaign}' leads are coming in. Ready to follow up?",
            f"@{target} engineering \u2014 can we get a technical blog post for {feat}?",
            f"@{target} exec \u2014 '{campaign}' results deck is ready for review.",
        ])
    if dept == "HR & People":
        return random.choice([
            f"@{target} hiring update: {random.randint(3,8)} candidates in pipeline for your team.",
            f"@{target} reminder: engagement survey closes Friday.",
            f"@{target} the new {random.choice(HR_TOPICS)} policy is live. Please review.",
            f"@{target} onboarding for your new hire is scheduled. Calendar invite sent.",
            f"@{target} L&D budget for your team is approved. Details in email.",
        ])
    if dept == "Finance & Legal":
        return random.choice([
            f"@{target} budget for the {svc} project is approved.",
            f"@{target} the {random.choice(LEGAL_TOPICS)} is signed. You're unblocked.",
            f"@{target} need receipts for last month's expenses by Friday.",
            f"@{target} vendor contract for {random.choice(['AWS','Datadog','Snowflake'])} renewal is ready for signatures.",
            f"@{target} Q{random.randint(1,4)} financial review is scheduled. Please prep your team's numbers.",
        ])
    if dept == "Executive":
        return random.choice([
            f"@{target} let's discuss the {feat} strategy in the leadership sync.",
            f"@{target} the board wants an update on {random.choice(['growth','ARR','headcount','product roadmap'])}.",
            f"@{target} great work on {feat} \u2014 calling it out at all-hands.",
            f"@{target} we need to align on priorities for next quarter.",
            f"@{target} investor meeting next week \u2014 can you prep the {random.choice(['product','engineering','growth'])} slides?",
        ])
    if dept == "Security":
        return random.choice([
            f"@{target} engineering \u2014 {svc} needs the latest security patch applied.",
            f"@{target} IT \u2014 we need to rotate credentials for {random.randint(3,8)} services.",
            f"@{target} legal \u2014 the SOC 2 evidence package is ready for review.",
            f"@{target} infra \u2014 the WAF rules for {svc} need updating.",
            f"@{target} please complete the security training by end of week.",
        ])
    if dept == "IT":
        return random.choice([
            f"@{target} your team has {random.randint(2,6)} unused software licenses to reclaim.",
            f"@{target} the SSO migration is complete for your department.",
            f"@{target} new laptops for your team's hires are ready for pickup.",
            f"@{target} VPN maintenance tonight 10pm-2am. Plan accordingly.",
            f"@{target} security \u2014 can we review the MDM policy exceptions?",
        ])
    # Fallback
    return random.choice([
        f"@{target} the {feat} update is ready for your review.",
        f"@{target} can we sync on {feat}? Need your team's input.",
        f"@{target} heads up \u2014 {svc} changes may affect your workflow.",
    ])

# ---------------------------------------------------------------------------
# Department template mappings
# ---------------------------------------------------------------------------

DEPT_TEMPLATE_FN = {
    "Engineering Backend": _t_backend,
    "Engineering Frontend": _t_frontend,
    "Infrastructure": _t_infra,
    "QA": _t_qa,
    "Product": _t_product,
    "Design": _t_design,
    "Data & ML": _t_data,
    "Marketing": _t_marketing,
    "Sales": _t_sales,
    "Support": _t_support,
    "HR & People": _t_hr,
    "Finance & Legal": _t_finance,
    "Executive": _t_executive,
    "Security": _t_security,
    "IT": _t_it,
}

# (func, weight) pairs — dept-specific dominates, shared templates fill in
_eng_standalone = lambda fn: [
    (fn, 35), (_t_deploy, 15), (_t_pr, 15), (_t_technical, 15),
    (_t_sprint, 10), (_t_social, 10),
]
_noneng_standalone = lambda fn: [
    (fn, 50), (_t_sprint, 15), (_t_social, 20),
    (_t_deploy, 5), (_t_pr, 5), (_t_technical, 5),
]

DEPT_STANDALONE = {
    "Engineering Backend": _eng_standalone(_t_backend),
    "Engineering Frontend": _eng_standalone(_t_frontend),
    "Infrastructure": _eng_standalone(_t_infra),
    "QA": _eng_standalone(_t_qa),
    "Security": _eng_standalone(_t_security),
    "Product": [(_t_product, 45), (_t_sprint, 20), (_t_social, 15), (_t_technical, 10), (_t_deploy, 5), (_t_pr, 5)],
    "Design": _noneng_standalone(_t_design),
    "Data & ML": [(_t_data, 40), (_t_technical, 15), (_t_sprint, 15), (_t_social, 15), (_t_deploy, 8), (_t_pr, 7)],
    "Marketing": _noneng_standalone(_t_marketing),
    "Sales": _noneng_standalone(_t_sales),
    "Support": _noneng_standalone(_t_support),
    "HR & People": _noneng_standalone(_t_hr),
    "Finance & Legal": _noneng_standalone(_t_finance),
    "Executive": [(_t_executive, 50), (_t_social, 20), (_t_sprint, 15), (_t_technical, 5), (_t_deploy, 5), (_t_pr, 5)],
    "IT": _noneng_standalone(_t_it),
}

# Thread start behavior weights: (type_key, weight)
_eng_thread = [("question", 25), ("crossdept", 15), ("deploy", 25), ("pr", 20), ("dept_specific", 15)]
_noneng_thread = [("question", 20), ("crossdept", 35), ("dept_specific", 35), ("deploy", 5), ("pr", 5)]

DEPT_THREAD_START = {
    "Engineering Backend": _eng_thread,
    "Engineering Frontend": _eng_thread,
    "Infrastructure": _eng_thread,
    "QA": [("question", 25), ("crossdept", 20), ("dept_specific", 30), ("deploy", 10), ("pr", 15)],
    "Security": [("question", 20), ("crossdept", 25), ("dept_specific", 35), ("deploy", 10), ("pr", 10)],
    "Product": [("question", 25), ("crossdept", 30), ("dept_specific", 30), ("deploy", 5), ("pr", 10)],
    "Design": [("question", 20), ("crossdept", 30), ("dept_specific", 40), ("deploy", 5), ("pr", 5)],
    "Data & ML": [("question", 25), ("crossdept", 20), ("dept_specific", 30), ("deploy", 10), ("pr", 15)],
    "Marketing": _noneng_thread,
    "Sales": [("question", 15), ("crossdept", 40), ("dept_specific", 35), ("deploy", 5), ("pr", 5)],
    "Support": [("question", 20), ("crossdept", 35), ("dept_specific", 35), ("deploy", 5), ("pr", 5)],
    "HR & People": _noneng_thread,
    "Finance & Legal": _noneng_thread,
    "Executive": [("question", 20), ("crossdept", 30), ("dept_specific", 40), ("deploy", 5), ("pr", 5)],
    "IT": _noneng_thread,
}

# ---------------------------------------------------------------------------
# Conversation threading
# ---------------------------------------------------------------------------

@dataclass
class Thread:
    participants: list[Bot]
    messages_remaining: int
    last_speaker: Optional[Bot] = None
    topic: str = ""


# ---------------------------------------------------------------------------
# Simulated clock
# ---------------------------------------------------------------------------

@dataclass
class SimClock:
    base_time: datetime
    _offset: float = 0.0

    def now(self) -> datetime:
        return self.base_time + timedelta(seconds=self._offset)

    def advance(self, seconds: float) -> None:
        self._offset += seconds

    def format(self) -> str:
        return self.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Message engine
# ---------------------------------------------------------------------------

@dataclass
class ChatMessage:
    timestamp: str
    bot: Bot
    text: str
    is_mention: bool = False
    mention_target: str = ""


class MessageEngine:
    """Generates messages, manages threads, tracks state."""

    def __init__(self, bots: list[Bot]) -> None:
        self.bots = bots
        self.active_threads: list[Thread] = []
        self.message_count = 0
        self.token_count = random.randint(1_200_000, 1_800_000)
        self.clock = SimClock(
            base_time=datetime.now().replace(
                hour=random.randint(9, 10),
                minute=random.randint(0, 30),
                second=0,
                microsecond=0,
            )
        )
        self._dept_bots: dict[str, list[Bot]] = {}
        for b in bots:
            self._dept_bots.setdefault(b.department, []).append(b)

    def _available_bots(self) -> list[Bot]:
        return [b for b in self.bots if b.status != "away"]

    def _pick_speaker(self, pool: list[Bot] | None = None) -> Bot:
        candidates = pool or self._available_bots()
        # Busy bots speak at 25% rate
        weighted = []
        for b in candidates:
            if b.status == "busy":
                if random.random() > 0.25:
                    continue
            weighted.append(b)
        if not weighted:
            weighted = candidates
        # Weight by chattiness
        weights = [b.chattiness for b in weighted]
        return random.choices(weighted, weights=weights, k=1)[0]

    def _pick_other(self, exclude: Bot) -> Bot:
        pool = [b for b in self._available_bots() if b is not exclude]
        return random.choice(pool) if pool else exclude

    def _pick_crossdept(self, speaker: Bot) -> Bot:
        other_depts = [d for d in self._dept_bots if d != speaker.department]
        dept = random.choice(other_depts)
        pool = [b for b in self._dept_bots[dept] if b.status != "away"]
        return random.choice(pool) if pool else self._pick_other(speaker)

    def generate(self) -> ChatMessage:
        """Generate one message, advancing the sim clock."""
        self.clock.advance(random.uniform(0.5, 3.0))
        roll = random.random()

        # 70% continue thread, 20% new thread, 10% standalone
        if self.active_threads and roll < 0.70:
            msg = self._continue_thread()
        elif roll < 0.90:
            msg = self._start_thread()
        else:
            msg = self._standalone()

        self.message_count += 1
        word_count = len(msg.text.split())
        self.token_count += int(word_count * 1.3) + random.randint(2, 8)

        # Prune dead threads
        self.active_threads = [t for t in self.active_threads if t.messages_remaining > 0]
        # Cap concurrent threads
        if len(self.active_threads) > 5:
            self.active_threads = self.active_threads[-5:]

        return msg

    def _continue_thread(self) -> ChatMessage:
        thread = random.choice(self.active_threads)
        # Pick someone other than last speaker from participants
        pool = [b for b in thread.participants if b is not thread.last_speaker]
        if not pool:
            pool = thread.participants
        speaker = self._pick_speaker(pool)
        target = thread.last_speaker or thread.participants[0]

        if random.random() < 0.6:
            text = _t_reply_agree(speaker, target.name.split()[0])
        else:
            text = _t_reply_discuss(speaker, target.name.split()[0])

        thread.last_speaker = speaker
        thread.messages_remaining -= 1

        return ChatMessage(
            timestamp=self.clock.format(),
            bot=speaker,
            text=text,
            is_mention=True,
            mention_target=target.name.split()[0],
        )

    def _start_thread(self) -> ChatMessage:
        speaker = self._pick_speaker()
        target = self._pick_other(speaker)

        _fallback = [("question", 30), ("crossdept", 25), ("deploy", 20), ("pr", 15), ("dept_specific", 10)]
        behaviors = DEPT_THREAD_START.get(speaker.department, _fallback)
        keys, weights = zip(*behaviors)
        choice = random.choices(keys, weights=weights, k=1)[0]

        if choice == "question":
            text = _t_question(speaker, target.name.split()[0])
            is_mention = True
        elif choice == "crossdept":
            text = _t_crossdept(speaker, self._pick_crossdept(speaker).name.split()[0])
            is_mention = True
        elif choice == "deploy":
            text = _t_deploy(speaker)
            is_mention = False
        elif choice == "pr":
            text = _t_pr(speaker)
            is_mention = False
        else:  # dept_specific
            dept_fn = DEPT_TEMPLATE_FN.get(speaker.department, _t_technical)
            text = dept_fn(speaker)
            is_mention = False

        # Create thread with 2-5 participants, 1-5 follow-up messages
        participants = [speaker, target]
        for _ in range(random.randint(0, 3)):
            extra = self._pick_other(speaker)
            if extra not in participants:
                participants.append(extra)

        thread = Thread(
            participants=participants,
            messages_remaining=random.randint(1, 5),
            last_speaker=speaker,
            topic=text[:40],
        )
        self.active_threads.append(thread)

        return ChatMessage(
            timestamp=self.clock.format(),
            bot=speaker,
            text=text,
            is_mention=is_mention,
            mention_target=target.name.split()[0] if is_mention else "",
        )

    def _standalone(self) -> ChatMessage:
        speaker = self._pick_speaker()
        _fallback = [(_t_social, 25), (_t_technical, 30), (_t_sprint, 25), (_t_deploy, 20)]
        templates = DEPT_STANDALONE.get(speaker.department, _fallback)
        funcs, weights = zip(*templates)
        text = random.choices(funcs, weights=weights, k=1)[0](speaker)
        return ChatMessage(timestamp=self.clock.format(), bot=speaker, text=text)

    def generate_history(self, count: int = 25) -> list[ChatMessage]:
        """Pre-generate history messages."""
        messages = []
        for _ in range(count):
            messages.append(self.generate())
        return messages

    def cycle_statuses(self) -> list[tuple[Bot, str, str]]:
        """Randomly change 2-3 bot statuses. Returns list of (bot, old, new)."""
        changes = []
        for _ in range(random.randint(2, 3)):
            bot = random.choice(self.bots)
            old = bot.status
            if old == "online":
                new = random.choice(["busy", "away"])
            elif old == "busy":
                new = random.choice(["online", "away"])
            else:
                new = random.choice(["online", "busy"])
            bot.status = new
            changes.append((bot, old, new))
        return changes


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

SPEED_LABELS = {0.5: "0.5x", 1.0: "1x", 2.0: "2x", 4.0: "4x"}
SPEED_CYCLE = [1.0, 2.0, 4.0, 0.5]


class PresenceSidebar(Static):
    """Department-grouped bot presence list."""

    def render_sidebar(self, bots: list[Bot]) -> str:
        dept_bots: dict[str, list[Bot]] = {}
        for b in bots:
            dept_bots.setdefault(b.department, []).append(b)

        lines: list[str] = []
        dept_order = list(DEPARTMENTS.keys())
        for dept in dept_order:
            members = dept_bots.get(dept, [])
            if not members:
                continue
            info = DEPARTMENTS[dept]
            color = info["color"]
            short = info["short"]

            # Sort: online first, then busy, then away
            order = {"online": 0, "busy": 1, "away": 2}
            members.sort(key=lambda b: (order.get(b.status, 3), b.name))

            online = sum(1 for b in members if b.status == "online")
            lines.append(f"[bold {color}]{short}[/] [dim]({online}/{len(members)})[/]")

            for b in members:
                if b.status == "online":
                    dot = "[green]\u25cf[/]"
                elif b.status == "busy":
                    dot = "[yellow]\u25d0[/]"
                else:
                    dot = "[dim]\u25cb[/]"
                first = b.name.split()[0]
                lines.append(f" {dot} [dim]{first}[/]")
            lines.append("")

        return "\n".join(lines)


class StatsBar(Static):
    """Bottom status bar with token count and bot status."""

    def render_stats(self, engine: MessageEngine, speed: float) -> str:
        online = sum(1 for b in engine.bots if b.status == "online")
        busy = sum(1 for b in engine.bots if b.status == "busy")
        away = sum(1 for b in engine.bots if b.status == "away")
        tokens = f"{engine.token_count:,}"
        msgs = f"{engine.message_count:,}"

        return (
            f"  Tokens Consumed: [bold]{tokens}[/]  |  "
            f"Messages: [bold]{msgs}[/]  |  "
            f"[green]\u25cf {online}[/]  [yellow]\u25d0 {busy}[/]  [dim]\u25cb {away}[/]"
            f"  |  [dim]q Quit[/]"
        )


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


def _format_message(msg: ChatMessage) -> str:
    """Format a ChatMessage for display in the RichLog."""
    dept_info = DEPARTMENTS.get(msg.bot.department, {"color": "white"})
    color = dept_info["color"]
    name = msg.bot.name
    role = msg.bot.role
    ts = msg.timestamp

    return (
        f"[dim]{ts}[/]  "
        f"[bold {color}]{name}[/] [dim]({role})[/]\n"
        f"  {msg.text}"
    )


class ChatroomApp(App):
    """Mission Control \u2014 124 AI agents running your startup."""

    TITLE = "Mission Control \u2014 #general"

    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }

    #main-area {
        height: 1fr;
    }

    #chat-log {
        width: 3fr;
        border: solid $primary;
        margin: 0 0 0 1;
        padding: 0 1;
    }

    #sidebar-scroll {
        width: 28;
        border: solid $accent;
        margin: 0 1 0 0;
        padding: 0 1;
    }

    #sidebar-title {
        text-style: bold;
        text-align: center;
        padding: 0 0 1 0;
        color: $text;
    }

    #presence {
        width: 100%;
    }

    #stats-bar {
        height: 1;
        dock: bottom;
        background: $boost;
        padding: 0 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "cycle_speed", "Speed", show=False),
        Binding("space", "scroll_bottom", "Scroll Down", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._bots = [Bot(**d) for d in BOT_DEFS]
        # Randomize initial statuses: 75% online, 15% busy, 10% away
        for b in self._bots:
            r = random.random()
            if r < 0.75:
                b.status = "online"
            elif r < 0.90:
                b.status = "busy"
            else:
                b.status = "away"
        self._engine = MessageEngine(self._bots)
        self._speed = 1.0
        self._running = True

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-area"):
            yield RichLog(
                id="chat-log",
                max_lines=2000,
                markup=True,
                wrap=True,
                auto_scroll=True,
            )
            with VerticalScroll(id="sidebar-scroll"):
                yield Static("[bold]TEAM (124)[/]", id="sidebar-title")
                yield PresenceSidebar(id="presence")
        yield StatsBar(id="stats-bar")

    def on_mount(self) -> None:
        # Pre-fill history
        history = self._engine.generate_history(25)
        log = self.query_one("#chat-log", RichLog)
        for msg in history:
            log.write(_format_message(msg))

        # Update sidebar + stats
        self._update_sidebar()
        self._update_stats()

        # Start the message worker
        self._run_messages()

    @work(thread=True, exclusive=True, group="message-loop")
    def _run_messages(self) -> None:
        """Background message generation loop."""
        status_timer = time.monotonic()
        status_interval = random.uniform(30, 60)

        while self._running:
            # Determine interval for this tick
            roll = random.random()
            if roll < 0.15:
                # Burst: 3-5 messages fast
                burst_count = random.randint(3, 5)
                for _ in range(burst_count):
                    if not self._running:
                        break
                    msg = self._engine.generate()
                    self.call_from_thread(self._append_chat_message, msg)
                    time.sleep(random.uniform(0.1, 0.3) / self._speed)
            elif roll < 0.25:
                # Quiet pause
                time.sleep(random.uniform(3.0, 8.0) / self._speed)
                continue
            else:
                # Normal message
                msg = self._engine.generate()
                self.call_from_thread(self._append_chat_message, msg)

            # Base interval between ticks
            time.sleep(random.uniform(0.5, 1.2) / self._speed)

            # Periodic status cycling
            now = time.monotonic()
            if now - status_timer > status_interval / self._speed:
                self._engine.cycle_statuses()
                self.call_from_thread(self._update_sidebar)
                status_timer = now
                status_interval = random.uniform(30, 60)

    def _append_chat_message(self, msg: ChatMessage) -> None:
        try:
            log = self.query_one("#chat-log", RichLog)
            log.write(_format_message(msg))
            self._update_stats()
        except Exception:
            pass

    def _update_sidebar(self) -> None:
        try:
            sidebar = self.query_one("#presence", PresenceSidebar)
            sidebar.update(sidebar.render_sidebar(self._bots))
            total = len(self._bots)
            online = sum(1 for b in self._bots if b.status == "online")
            title = self.query_one("#sidebar-title", Static)
            title.update(f"[bold]TEAM ({online}/{total})[/]")
        except Exception:
            pass

    def _update_stats(self) -> None:
        try:
            bar = self.query_one("#stats-bar", StatsBar)
            bar.update(bar.render_stats(self._engine, self._speed))
        except Exception:
            pass

    # Actions
    def action_cycle_speed(self) -> None:
        idx = SPEED_CYCLE.index(self._speed) if self._speed in SPEED_CYCLE else 0
        self._speed = SPEED_CYCLE[(idx + 1) % len(SPEED_CYCLE)]
        self._update_stats()

    def action_scroll_bottom(self) -> None:
        try:
            log = self.query_one("#chat-log", RichLog)
            log.scroll_end()
        except Exception:
            pass

    def action_quit(self) -> None:
        self._running = False
        self.exit()


if __name__ == "__main__":
    app = ChatroomApp()
    app.run()
