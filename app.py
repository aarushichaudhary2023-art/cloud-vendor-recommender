from flask import Flask, request, jsonify, redirect, session, url_for, send_from_directory
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
CORS(app)

# Secret key for session
app.secret_key = "your-random-secret-key-change-this"

# Google OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID',
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)
from flask import send_from_directory

@app.route("/")
def index():
    return send_from_directory(".", "index.html")
# ─────────────────────────────────────────────────────────────────────────────
# Vendor knowledge base
# ─────────────────────────────────────────────────────────────────────────────
VENDORS = {
    "aws": {
        "name": "Amazon Web Services",
        "logo": "AWS",
        "color": "#FF9900",
        "strengths": ["Widest service catalog", "Global reach", "Mature ecosystem", "Best ML services"],
        "weaknesses": ["Complex pricing", "Steep learning curve", "Cost management difficult"],
        "pricing": {
            "compute":  {"small": 0.0104, "medium": 0.0416, "large": 0.1664},
            "storage":  0.023,
            "network":  0.09,
            "database": {"small": 0.017, "medium": 0.068, "large": 0.272}
        },
        "features": {
            "regions": 31, "services": 200, "sla_uptime": 99.99,
            "free_tier": True, "ml_services": True, "serverless": True,
            "kubernetes": True, "cdn": True,
            "compliance": ["HIPAA", "PCI-DSS", "SOC2", "ISO27001", "GDPR", "FedRAMP"]
        },
        "scores": {
            "reliability": 9.5, "performance": 9.2, "security": 9.4,
            "support": 8.8, "innovation": 9.6, "documentation": 9.0, "community": 9.5
        }
    },
    "gcp": {
        "name": "Google Cloud Platform",
        "logo": "GCP",
        "color": "#4285F4",
        "strengths": ["Best data analytics", "Kubernetes native", "AI/ML leadership", "Competitive pricing"],
        "weaknesses": ["Fewer enterprise features", "Smaller partner ecosystem", "Less mature support"],
        "pricing": {
            "compute":  {"small": 0.0095, "medium": 0.0380, "large": 0.1520},
            "storage":  0.020,
            "network":  0.08,
            "database": {"small": 0.015, "medium": 0.060, "large": 0.240}
        },
        "features": {
            "regions": 35, "services": 150, "sla_uptime": 99.99,
            "free_tier": True, "ml_services": True, "serverless": True,
            "kubernetes": True, "cdn": True,
            "compliance": ["HIPAA", "PCI-DSS", "SOC2", "ISO27001", "GDPR"]
        },
        "scores": {
            "reliability": 9.3, "performance": 9.4, "security": 9.3,
            "support": 8.5, "innovation": 9.7, "documentation": 8.8, "community": 8.9
        }
    },
    "azure": {
        "name": "Microsoft Azure",
        "logo": "AZ",
        "color": "#0078D4",
        "strengths": ["Best enterprise integration", "Hybrid cloud leader", "Microsoft ecosystem", "Strong compliance"],
        "weaknesses": ["Complex portal", "Inconsistent performance", "Pricing complexity"],
        "pricing": {
            "compute":  {"small": 0.0112, "medium": 0.0448, "large": 0.1792},
            "storage":  0.018,
            "network":  0.087,
            "database": {"small": 0.018, "medium": 0.072, "large": 0.288}
        },
        "features": {
            "regions": 60, "services": 200, "sla_uptime": 99.99,
            "free_tier": True, "ml_services": True, "serverless": True,
            "kubernetes": True, "cdn": True,
            "compliance": ["HIPAA", "PCI-DSS", "SOC2", "ISO27001", "GDPR", "FedRAMP", "DoD CC SRG"]
        },
        "scores": {
            "reliability": 9.2, "performance": 9.0, "security": 9.6,
            "support": 9.1, "innovation": 9.0, "documentation": 9.2, "community": 9.0
        }
    },
    "digitalocean": {
        "name": "DigitalOcean",
        "logo": "DO",
        "color": "#0080FF",
        "strengths": ["Simple pricing", "Developer-friendly", "Excellent docs", "Affordable"],
        "weaknesses": ["Limited enterprise features", "Fewer global regions", "No dedicated ML services"],
        "pricing": {
            "compute":  {"small": 0.007,  "medium": 0.028,  "large": 0.112},
            "storage":  0.010,
            "network":  0.01,
            "database": {"small": 0.015, "medium": 0.060, "large": 0.240}
        },
        "features": {
            "regions": 14, "services": 30, "sla_uptime": 99.99,
            "free_tier": True, "ml_services": False, "serverless": True,
            "kubernetes": True, "cdn": True,
            "compliance": ["SOC2", "ISO27001", "GDPR"]
        },
        "scores": {
            "reliability": 8.8, "performance": 8.5, "security": 8.0,
            "support": 8.7, "innovation": 7.5, "documentation": 9.3, "community": 8.8
        }
    }
}

VALID_SIZES      = {"small", "medium", "large"}
VALID_COMPLIANCE = {"HIPAA", "PCI-DSS", "SOC2", "ISO27001", "GDPR", "FedRAMP", "DoD CC SRG"}


# ─────────────────────────────────────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────────────────────────────────────

def validate_request(data):
    errors = []
    workload = data.get("workload", {})
    if not isinstance(workload, dict):
        errors.append("'workload' must be a JSON object.")
        return errors
    if workload.get("compute_size", "medium") not in VALID_SIZES:
        errors.append(f"compute_size must be one of {sorted(VALID_SIZES)}.")
    for key in ("compute_hours", "storage_gb", "network_gb"):
        val = workload.get(key, 1)
        if not isinstance(val, (int, float)) or val < 0:
            errors.append(f"workload.{key} must be a non-negative number.")
    if workload.get("compute_hours", 730) > 744:
        errors.append("compute_hours cannot exceed 744.")
    budget = data.get("max_budget", 1000)
    if not isinstance(budget, (int, float)) or budget <= 0:
        errors.append("max_budget must be a positive number.")
    unknown = set(data.get("required_compliance", [])) - VALID_COMPLIANCE
    if unknown:
        errors.append(f"Unknown compliance standards: {sorted(unknown)}.")
    return errors


def calculate_monthly_cost(vendor_key, workload):
    p = VENDORS[vendor_key]["pricing"]
    size     = workload.get("compute_size", "medium")
    hours    = workload.get("compute_hours", 730)
    stor_gb  = workload.get("storage_gb", 100)
    net_gb   = workload.get("network_gb", 50)
    db_inst  = workload.get("db_instances", 1)
    db_size  = workload.get("db_size", "small")
    compute  = p["compute"].get(size, p["compute"]["medium"]) * hours
    storage  = p["storage"] * stor_gb
    network  = p["network"] * net_gb
    database = p["database"].get(db_size, p["database"]["small"]) * hours * db_inst
    return round(compute + storage + network + database, 2)


def score_vendor(vendor_key, requirements):
    """
    Multi-Criteria Decision Analysis (MCDA) scorer.
    Returns (total_score, monthly_cost, breakdown_dict).

    v2 changes:
      - Hard compliance gate (0 if any required standard missing)
      - Feature penalty (-1.0 ML, -0.8 K8s, -0.5 serverless) when required but absent
      - AHP normalisation: weights always sum to 1.0
      - Full per-criterion breakdown returned
    """
    vendor   = VENDORS[vendor_key]
    scores   = vendor["scores"]
    features = vendor["features"]
    workload = requirements.get("workload", {})

    # 1. Normalise weights
    rw = {
        "reliability": max(0, requirements.get("reliability_weight", 0.20)),
        "performance": max(0, requirements.get("performance_weight", 0.15)),
        "security":    max(0, requirements.get("security_weight",    0.15)),
        "cost":        max(0, requirements.get("cost_weight",        0.20)),
        "support":     max(0, requirements.get("support_weight",     0.10)),
        "innovation":  max(0, requirements.get("innovation_weight",  0.10)),
        "compliance":  max(0, requirements.get("compliance_weight",  0.10)),
    }
    tw = sum(rw.values()) or 1.0
    w  = {k: v / tw for k, v in rw.items()}

    # 2. Cost score
    monthly_cost = calculate_monthly_cost(vendor_key, workload)
    max_budget   = max(1, requirements.get("max_budget", 1000))
    cost_score   = max(0.0, min(10.0, 10.0 - (monthly_cost / max_budget) * 5.0))

    # 3. Compliance score — HARD GATE
    req_compliance = requirements.get("required_compliance", [])
    if req_compliance:
        missing = [c for c in req_compliance if c not in features["compliance"]]
        compliance_score = 0.0 if missing else 10.0
    else:
        compliance_score = 8.0

    # 4. Feature adjustments (bonus if present, penalty if required but absent)
    feat_adj = 0.0
    if requirements.get("needs_ml"):
        feat_adj += 0.5 if features.get("ml_services") else -1.0
    if requirements.get("needs_kubernetes"):
        feat_adj += 0.3 if features.get("kubernetes") else -0.8
    if requirements.get("needs_serverless"):
        feat_adj += 0.2 if features.get("serverless") else -0.5

    # 5. Weighted sum + breakdown
    breakdown = {
        "reliability": round(scores["reliability"] * w["reliability"], 3),
        "performance": round(scores["performance"] * w["performance"], 3),
        "security":    round(scores["security"]    * w["security"],    3),
        "cost":        round(cost_score            * w["cost"],        3),
        "support":     round(scores["support"]     * w["support"],     3),
        "innovation":  round(scores["innovation"]  * w["innovation"],  3),
        "compliance":  round(compliance_score      * w["compliance"],  3),
    }
    raw   = sum(breakdown.values()) + feat_adj
    total = round(min(10.0, max(0.0, raw)), 2)
    return total, monthly_cost, breakdown


def run_recommendation(requirements):
    results = []
    for vk, vendor in VENDORS.items():
        score, cost, breakdown = score_vendor(vk, requirements)
        results.append({
            "vendor": vk, "name": vendor["name"], "logo": vendor["logo"],
            "color": vendor["color"], "score": score, "monthly_cost": cost,
            "breakdown": breakdown, "strengths": vendor["strengths"],
            "weaknesses": vendor["weaknesses"], "features": vendor["features"],
            "scores": vendor["scores"],
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    results[0]["recommended"] = True
    return results


def generate_analysis(results, requirements):
    top, runner_up = results[0], results[1]
    reasoning, trade_offs = [], []
    if requirements.get("needs_ml"):
        reasoning.append("ML/AI requirement: GCP and AWS receive a bonus; absent vendors are penalised.")
    if requirements.get("cost_weight", 0) > 0.25:
        reasoning.append("High cost weight: DigitalOcean offers the lowest compute rates for small workloads.")
    if requirements.get("security_weight", 0) >= 0.2:
        reasoning.append("Elevated security weight: Azure leads with the broadest compliance portfolio.")
    if requirements.get("required_compliance"):
        reasoning.append(
            f"Hard compliance gate applied for: {', '.join(requirements['required_compliance'])}. "
            "Vendors missing any standard received compliance score = 0."
        )
    if not reasoning:
        reasoning.append("Balanced weights applied across all seven criteria.")
    if top["score"] - runner_up["score"] < 0.5:
        trade_offs.append(
            f"{runner_up['name']} is a close alternative "
            f"(score: {runner_up['score']}/10, ${runner_up['monthly_cost']:.0f}/mo)."
        )
    return {
        "summary": f"{top['name']} is the best fit — score {top['score']}/10, "
                   f"est. ${top['monthly_cost']:.2f}/month.",
        "reasoning": reasoning,
        "trade_offs": trade_offs,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Baseline methods
# ─────────────────────────────────────────────────────────────────────────────

def baseline_cheapest(workload):
    costs = {vk: calculate_monthly_cost(vk, workload) for vk in VENDORS}
    return min(costs, key=costs.get)

def baseline_highest_rated(_req):
    def avg(vk):
        s = VENDORS[vk]["scores"]
        return sum(s.values()) / len(s)
    return max(VENDORS.keys(), key=avg)

def baseline_random(_req):
    return random.choice(list(VENDORS.keys()))


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation engine
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_scenarios(scenarios):
    methods = {
        "proposed":      lambda req: run_recommendation(req)[0]["vendor"],
        "cheapest":      lambda req: baseline_cheapest(req.get("workload", {})),
        "highest_rated": lambda req: baseline_highest_rated(req),
        "random":        lambda req: baseline_random(req),
    }
    stats      = {m: {"tp": 0, "fp": 0, "fn": 0} for m in methods}
    per_sc     = []

    for sc in scenarios:
        req, expected = sc["requirements"], sc["expected_vendor"]
        row = {"id": sc["id"], "name": sc["name"],
               "expected": expected, "predictions": {}}
        for method, fn in methods.items():
            predicted = fn(req)
            correct   = predicted == expected
            row["predictions"][method] = {"vendor": predicted, "correct": correct}
            if correct:
                stats[method]["tp"] += 1
            else:
                stats[method]["fp"] += 1
                stats[method]["fn"] += 1
        per_sc.append(row)

    n = len(scenarios)
    aggregate = {}
    for method, s in stats.items():
        tp, fp, fn = s["tp"], s["fp"], s["fn"]
        acc  = round(tp / n, 4) if n else 0
        prec = round(tp / (tp + fp), 4) if (tp + fp) else 0
        rec  = round(tp / (tp + fn), 4) if (tp + fn) else 0
        f1   = round(2 * prec * rec / (prec + rec), 4) if (prec + rec) else 0
        aggregate[method] = {
            "accuracy": acc, "precision": prec,
            "recall": rec,   "f1_score": f1,
            "correct": tp,   "total": n,
        }
    return per_sc, aggregate


# ─────────────────────────────────────────────────────────────────────────────
# Test scenario suite  (15 scenarios with expert-labelled ground truth)
# ─────────────────────────────────────────────────────────────────────────────
TEST_SCENARIOS = [
    {
        "id": 1, "name": "Healthcare Startup — HIPAA + FedRAMP",
        "description": "Small healthcare startup; must comply with HIPAA and FedRAMP; high security priority.",
        "expected_vendor": "azure",
        "rationale": "Azure is the only vendor with both HIPAA and FedRAMP; its security score (9.6) is highest.",
        "requirements": {
            "workload": {"compute_size":"small","compute_hours":730,"storage_gb":50,"network_gb":20,"db_instances":1,"db_size":"small"},
            "max_budget":200,"required_compliance":["HIPAA","FedRAMP"],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":False,
            "cost_weight":0.10,"reliability_weight":0.10,"performance_weight":0.05,
            "security_weight":0.45,"support_weight":0.10,"innovation_weight":0.05,"compliance_weight":0.15,
        }
    },
    {
        "id": 2, "name": "AI / ML Research Lab",
        "description": "University research team running large GPU training jobs; innovation and ML services are paramount.",
        "expected_vendor": "gcp",
        "rationale": "GCP leads in AI/ML innovation (9.7); innovation_weight=0.50 decisively favours GCP.",
        "requirements": {
            "workload": {"compute_size":"large","compute_hours":500,"storage_gb":500,"network_gb":100,"db_instances":1,"db_size":"medium"},
            "max_budget":2000,"required_compliance":[],
            "needs_ml":True,"needs_kubernetes":True,"needs_serverless":False,
            "cost_weight":0.05,"reliability_weight":0.10,"performance_weight":0.20,
            "security_weight":0.05,"support_weight":0.05,"innovation_weight":0.50,"compliance_weight":0.05,
        }
    },
    {
        "id": 3, "name": "Budget Developer Portfolio",
        "description": "Solo developer hosting a personal portfolio; cost is overwhelmingly the primary concern.",
        "expected_vendor": "digitalocean",
        "rationale": "DigitalOcean has the lowest compute and storage rates; cost_weight=0.70 makes it decisive.",
        "requirements": {
            "workload": {"compute_size":"small","compute_hours":730,"storage_gb":20,"network_gb":10,"db_instances":0,"db_size":"small"},
            "max_budget":30,"required_compliance":[],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":False,
            "cost_weight":0.70,"reliability_weight":0.10,"performance_weight":0.05,
            "security_weight":0.05,"support_weight":0.05,"innovation_weight":0.03,"compliance_weight":0.02,
        }
    },
    {
        "id": 4, "name": "Enterprise SAP Migration",
        "description": "Large enterprise migrating SAP workloads; needs hybrid connectivity and enterprise support.",
        "expected_vendor": "azure",
        "rationale": "Azure's support score (9.1) is highest; support_weight=0.35 rewards enterprise support quality.",
        "requirements": {
            "workload": {"compute_size":"large","compute_hours":730,"storage_gb":2000,"network_gb":500,"db_instances":3,"db_size":"large"},
            "max_budget":5000,"required_compliance":["SOC2","ISO27001"],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":False,
            "cost_weight":0.05,"reliability_weight":0.20,"performance_weight":0.10,
            "security_weight":0.20,"support_weight":0.35,"innovation_weight":0.05,"compliance_weight":0.05,
        }
    },
    {
        "id": 5, "name": "E-Commerce Platform — PCI-DSS",
        "description": "Mid-size e-commerce platform handling card payments; PCI-DSS mandatory; high traffic spikes.",
        "expected_vendor": "aws",
        "rationale": "AWS leads in reliability (9.5); reliability_weight=0.40 rewards its 99.99% uptime track record.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":300,"network_gb":200,"db_instances":2,"db_size":"medium"},
            "max_budget":1000,"required_compliance":["PCI-DSS","SOC2"],
            "needs_ml":False,"needs_kubernetes":True,"needs_serverless":True,
            "cost_weight":0.10,"reliability_weight":0.40,"performance_weight":0.20,
            "security_weight":0.15,"support_weight":0.05,"innovation_weight":0.05,"compliance_weight":0.05,
        }
    },
    {
        "id": 6, "name": "Big Data Analytics Pipeline",
        "description": "Data engineering team running Spark pipelines; performance and innovation are key.",
        "expected_vendor": "gcp",
        "rationale": "GCP's performance (9.4) and innovation (9.7) lead; innovation_weight=0.40 favours GCP.",
        "requirements": {
            "workload": {"compute_size":"large","compute_hours":400,"storage_gb":5000,"network_gb":300,"db_instances":1,"db_size":"large"},
            "max_budget":3000,"required_compliance":["GDPR"],
            "needs_ml":True,"needs_kubernetes":True,"needs_serverless":False,
            "cost_weight":0.05,"reliability_weight":0.10,"performance_weight":0.30,
            "security_weight":0.05,"support_weight":0.05,"innovation_weight":0.40,"compliance_weight":0.05,
        }
    },
    {
        "id": 7, "name": "Government Defence App — FedRAMP + DoD",
        "description": "US government contractor; FedRAMP and DoD CC SRG mandatory.",
        "expected_vendor": "azure",
        "rationale": "Azure is the only vendor with DoD CC SRG; hard compliance gate eliminates all others.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":200,"network_gb":100,"db_instances":2,"db_size":"medium"},
            "max_budget":2000,"required_compliance":["FedRAMP","DoD CC SRG"],
            "needs_ml":False,"needs_kubernetes":True,"needs_serverless":False,
            "cost_weight":0.05,"reliability_weight":0.15,"performance_weight":0.10,
            "security_weight":0.40,"support_weight":0.10,"innovation_weight":0.05,"compliance_weight":0.15,
        }
    },
    {
        "id": 8, "name": "Startup MVP — Speed & Cost",
        "description": "Early-stage startup building an MVP; minimal cost is the overwhelming priority.",
        "expected_vendor": "digitalocean",
        "rationale": "DigitalOcean is cheapest for small workloads; cost_weight=0.60 makes this decisive.",
        "requirements": {
            "workload": {"compute_size":"small","compute_hours":730,"storage_gb":50,"network_gb":30,"db_instances":1,"db_size":"small"},
            "max_budget":80,"required_compliance":[],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":True,
            "cost_weight":0.60,"reliability_weight":0.10,"performance_weight":0.10,
            "security_weight":0.05,"support_weight":0.10,"innovation_weight":0.03,"compliance_weight":0.02,
        }
    },
    {
        "id": 9, "name": "Global SaaS — High Reliability",
        "description": "SaaS serving 50 countries; reliability and global reach are paramount.",
        "expected_vendor": "aws",
        "rationale": "AWS leads in reliability (9.5); reliability_weight=0.50 decisively rewards its global uptime.",
        "requirements": {
            "workload": {"compute_size":"large","compute_hours":730,"storage_gb":1000,"network_gb":500,"db_instances":3,"db_size":"large"},
            "max_budget":8000,"required_compliance":["SOC2","GDPR"],
            "needs_ml":False,"needs_kubernetes":True,"needs_serverless":True,
            "cost_weight":0.05,"reliability_weight":0.50,"performance_weight":0.15,
            "security_weight":0.15,"support_weight":0.10,"innovation_weight":0.03,"compliance_weight":0.02,
        }
    },
    {
        "id": 10, "name": "European Fintech — GDPR + PCI-DSS",
        "description": "European fintech; GDPR and PCI-DSS mandatory; cost-sensitive; high performance.",
        "expected_vendor": "gcp",
        "rationale": "GCP passes compliance gate and has the best performance score; cost_weight=0.35 favours its lower pricing.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":150,"network_gb":80,"db_instances":1,"db_size":"medium"},
            "max_budget":400,"required_compliance":["GDPR","PCI-DSS"],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":True,
            "cost_weight":0.35,"reliability_weight":0.15,"performance_weight":0.20,
            "security_weight":0.10,"support_weight":0.05,"innovation_weight":0.10,"compliance_weight":0.05,
        }
    },
    {
        "id": 11, "name": "IoT Platform — Serverless Events",
        "description": "IoT platform processing millions of sensor events; serverless and performance are key.",
        "expected_vendor": "aws",
        "rationale": "AWS Lambda and IoT Core are the most mature; reliability+performance weights favour AWS.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":400,"storage_gb":200,"network_gb":150,"db_instances":1,"db_size":"small"},
            "max_budget":600,"required_compliance":[],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":True,
            "cost_weight":0.10,"reliability_weight":0.30,"performance_weight":0.30,
            "security_weight":0.10,"support_weight":0.10,"innovation_weight":0.07,"compliance_weight":0.03,
        }
    },
    {
        "id": 12, "name": "Media Streaming — High Bandwidth",
        "description": "Video streaming startup; 5 TB/month egress; cost is the primary constraint.",
        "expected_vendor": "digitalocean",
        "rationale": "DigitalOcean egress = /bin/sh.01/GB vs AWS /bin/sh.09/GB — 9x cheaper; cost_weight=0.75 is decisive.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":500,"network_gb":5000,"db_instances":1,"db_size":"small"},
            "max_budget":500,"required_compliance":[],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":False,
            "cost_weight":0.75,"reliability_weight":0.10,"performance_weight":0.07,
            "security_weight":0.03,"support_weight":0.03,"innovation_weight":0.01,"compliance_weight":0.01,
        }
    },
    {
        "id": 13, "name": "Kubernetes-Native Microservices",
        "description": "Engineering team building cloud-native microservices; Kubernetes and innovation are priorities.",
        "expected_vendor": "gcp",
        "rationale": "GKE is the original K8s; innovation_weight=0.37 + needs_kubernetes bonus decisively favours GCP.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":200,"network_gb":100,"db_instances":2,"db_size":"small"},
            "max_budget":800,"required_compliance":[],
            "needs_ml":False,"needs_kubernetes":True,"needs_serverless":True,
            "cost_weight":0.05,"reliability_weight":0.15,"performance_weight":0.30,
            "security_weight":0.05,"support_weight":0.05,"innovation_weight":0.37,"compliance_weight":0.03,
        }
    },
    {
        "id": 14, "name": "Enterprise Microsoft 365 Integration",
        "description": "Enterprise app deeply integrated with Teams, Active Directory, and Power BI.",
        "expected_vendor": "azure",
        "rationale": "Azure has the highest support score (9.1); support_weight=0.40 rewards enterprise integration depth.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":300,"network_gb":100,"db_instances":2,"db_size":"medium"},
            "max_budget":1500,"required_compliance":["SOC2"],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":True,
            "cost_weight":0.05,"reliability_weight":0.15,"performance_weight":0.10,
            "security_weight":0.20,"support_weight":0.40,"innovation_weight":0.05,"compliance_weight":0.05,
        }
    },
    {
        "id": 15, "name": "Balanced General-Purpose Workload",
        "description": "Mid-size company with no special requirements; wants the most well-rounded provider.",
        "expected_vendor": "aws",
        "rationale": "AWS scores highest overall when reliability and support are weighted moderately; broadest service catalog.",
        "requirements": {
            "workload": {"compute_size":"medium","compute_hours":730,"storage_gb":100,"network_gb":50,"db_instances":1,"db_size":"small"},
            "max_budget":500,"required_compliance":[],
            "needs_ml":False,"needs_kubernetes":False,"needs_serverless":False,
            "cost_weight":0.15,"reliability_weight":0.25,"performance_weight":0.15,
            "security_weight":0.15,"support_weight":0.15,"innovation_weight":0.10,"compliance_weight":0.05,
        }
    },
]

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json or {}
    errors = validate_request(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400
    results = run_recommendation(data)
    return jsonify({
        "success": True,
        "recommendations": results,
        "top_pick": results[0]["vendor"],
        "analysis": generate_analysis(results, data)
    })

@app.route("/api/evaluate", methods=["GET"])
def evaluate():
    per_sc, aggregate = evaluate_scenarios(TEST_SCENARIOS)
    return jsonify({"per_scenario": per_sc, "aggregate": aggregate})

@app.route("/api/scenarios", methods=["GET"])
def scenarios():
    return jsonify({"scenarios": TEST_SCENARIOS, "count": len(TEST_SCENARIOS)})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "2.0.0"})
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/auth/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    user  = token.get("userinfo")
    if user:
        session["user"] = {
            "name":    user["name"],
            "email":   user["email"],
            "picture": user["picture"],
        }
    return redirect("/")

@app.route("/auth/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/auth/user")
def get_user():
    user = session.get("user")
    if user:
        return jsonify({"logged_in": True, "user": user})
    return jsonify({"logged_in": False})
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)