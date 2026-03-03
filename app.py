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
from textual.widgets import Footer, Header, RichLog, Static

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
    return random.choice([
        f"@{target} are we still on track for {feat} this sprint?",
        f"@{target} quick q \u2014 does {svc} support batch requests yet?",
        f"@{target} have you seen the latest error spike on {svc}?",
        f"@{target} can you take a look at the {feat} spec when you get a sec?",
        f"@{target} what's the status on the {svc} migration?",
        f"@{target} do we have docs for the {feat} API?",
        f"@{target} is {svc} ready for the load test tomorrow?",
        f"@{target} thoughts on the {random.choice(TECH_TOPICS)} approach?",
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

def _t_crossdept(bot: Bot, target: str) -> str:
    feat = random.choice(FEATURES)
    svc = random.choice(SERVICES)
    return random.choice([
        f"@{target} the {feat} mockups are ready for eng review.",
        f"@{target} can we get a sales perspective on the {feat} pricing?",
        f"@{target} legal signed off on the {feat} data handling.",
        f"@{target} support is seeing tickets about {svc}. Is there a known issue?",
        f"@{target} marketing wants to announce {feat} next week \u2014 is it launch-ready?",
        f"@{target} the {feat} docs need a final review from your team.",
        f"@{target} finance approved the budget for {svc} scaling.",
        f"@{target} design handoff for {feat} is in Figma. Let me know if questions.",
        f"@{target} got customer feedback on {feat} from 3 enterprise accounts.",
        f"@{target} the {feat} beta results are in \u2014 NPS at {random.randint(40, 80)}.",
    ])

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

        # Decide message type
        roll = random.random()
        if roll < 0.35:
            text = _t_question(speaker, target.name.split()[0])
            is_mention = True
        elif roll < 0.60:
            text = _t_crossdept(speaker, self._pick_crossdept(speaker).name.split()[0])
            is_mention = True
        elif roll < 0.80:
            text = _t_deploy(speaker)
            is_mention = False
        else:
            text = _t_pr(speaker)
            is_mention = False

        # Create thread with 2-5 participants, 2-6 messages
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
        roll = random.random()
        if roll < 0.35:
            text = _t_social(speaker)
        elif roll < 0.65:
            text = _t_technical(speaker)
        elif roll < 0.85:
            text = _t_sprint(speaker)
        else:
            text = _t_deploy(speaker)

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

    Footer {
        dock: bottom;
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
        yield Footer()

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
