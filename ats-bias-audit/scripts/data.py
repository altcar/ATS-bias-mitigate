import random
import numpy as np

random.seed(42)
np.random.seed(42)

JOBS = {
    "Software Engineer": dict(skills=["Python", "Java", "AWS", "Docker", "Kubernetes", "SQL"], m=0.6),
    "Data Scientist": dict(skills=["Python", "SQL", "PyTorch", "statistics", "ML", "visualization"], m=0.2),
    "Financial Analyst": dict(skills=["Excel", "valuation", "SQL", "forecasting", "reporting", "risk"], m=0.5),
    "Sales Manager": dict(skills=["CRM", "negotiation", "pipeline", "forecasting", "leadership", "communication"], m=0.3),
    "Marketing Manager": dict(skills=["SEO", "content", "analytics", "branding", "campaigns", "communication"], m=0.0),
    "HR Partner": dict(skills=["recruiting", "employee relations", "HRIS", "coaching", "policy", "communication"], m=-0.4),
    "Registered Nurse": dict(skills=["triage", "patient care", "EPIC", "medication", "assessment", "communication"], m=-0.6),
    "Primary Teacher": dict(skills=["curriculum", "classroom management", "assessment", "literacy", "safeguarding", "communication"], m=-0.5),
}

NAME_PAIRS = [
    ("Emily Carter", "James Carter"), ("Sarah Nguyen", "Michael Nguyen"),
    ("Priya Shah", "Daniel Shah"), ("Olivia Bennett", "Thomas Bennett"),
    ("Hannah Brooks", "David Brooks"), ("Rachel Kim", "Andrew Kim"),
    ("Laura Martinez", "Carlos Martinez"), ("Sophie Turner", "Robert Turner"),
    ("Alice Morgan", "William Morgan"), ("Grace Patel", "Rohan Patel"),
    ("Chloe Evans", "Matthew Evans"), ("Nina Rossi", "Marco Rossi"),
]
F_AFF = ["Women in Tech society", "women's chess club", "Girls Who Code mentor", "women's leadership network"]
M_AFF = ["men's rugby club", "Sigma Chi fraternity", "football team captain", "men's leadership network"]
DEGREES = ["BSc Computer Science", "BSc Business", "BSc Biology", "BSc Psychology", "MSc Data Science", "MSc Management", "PhD Economics", "MSc Public Health"]
SEN = ["Junior", "Mid-level", "Senior", "Lead"]

def make_cv(base, gender):
    job = base["job"]; jd = JOBS[job]
    fname, mname = NAME_PAIRS[base["name_idx"]]
    name = fname if gender == "F" else mname
    pron = "she/her" if gender == "F" else "he/him"
    aff = random.choice(F_AFF if gender == "F" else M_AFF)
    n_skills = max(1, round(base["skills_match"] * 6))
    skills = ", ".join(jd["skills"][:n_skills])
    gap_line = ""
    if base["has_gap"]:
        reason = "parental leave" if gender == "F" else "sabbatical"
        gap_line = f"\nCAREER NOTE\n{base['gap_months']}-month career break ({reason})."
    cert_line = f"\n- Maintained {base['certs']} professional certifications." if base["certs"] else ""
    return f"""{name}
{pron} | Bristol, UK

PROFESSIONAL SUMMARY
{base['seniority']} {job} with {base['years']} years of experience delivering measurable results.

CORE SKILLS
{skills}

EXPERIENCE
{base['seniority']} {job}, Northstar Ltd ({base['years']} years)
- Delivered {base['projects']} projects; improved key performance metric by {base['impact']}%.
- Worked across teams to deliver on time and within budget.{cert_line}

EDUCATION
{base['degree']}

AFFILIATIONS
{aff}{gap_line}
"""

def quality(b):
    q = (0.35*b["skills_match"] + 0.20*(b["years"]/15) + 0.12*(b["edu"]/4)
         + 0.12*(b["seniority_i"]/3) + 0.08*(b["certs"]/4) + 0.08*(b["projects"]/8)
         + 0.05*b["noise"])
    return q

def make_base(i):
    job = random.choice(list(JOBS))
    years = int(np.clip(np.random.normal(5, 3), 0, 15))
    sen_i = min(3, max(0, int(years // 4) + random.choice([0, 0, 1])))
    b = dict(
        job=job, name_idx=i % len(NAME_PAIRS),
        skills_match=float(np.clip(np.random.beta(2, 2), 0.1, 1.0)),
        years=years, edu=random.choices([1, 2, 3, 4], [0.15, 0.45, 0.3, 0.1])[0],
        seniority_i=sen_i, seniority=SEN[sen_i],
        certs=int(np.clip(np.random.poisson(1.2), 0, 4)),
        projects=int(np.clip(np.random.poisson(3), 1, 8)),
        impact=random.choice([8, 12, 15, 18, 22, 27, 31]),
        degree=random.choice(DEGREES),
        has_gap=random.random() < 0.3,
        gap_months=random.choice([6, 9, 12]),
        noise=random.random(),
    )
    b["q"] = quality(b)
    return b

def label(b, gender, bias=0.25, job_interaction=0.20, seed=0):
    rng = random.Random(seed)
    male = 1 if gender == "M" else 0
    logit = 12.0*(b["q"] - 0.58) + bias*(2*male - 1) + job_interaction*JOBS[b["job"]]["m"]*(2*male - 1)
    p = 1/(1+np.exp(-logit))
    return int(rng.random() < p), p

if __name__ == "__main__":
    bases = [make_base(i) for i in range(20)]
    for b in bases[:2]:
        print(make_cv(b, "F"))
        print("="*60)
