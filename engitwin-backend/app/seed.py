"""
One-time seed data so the app isn't an empty shell on first run.

Creates the subject categories your landing page shows (Physics,
Electrical, Computer Networks, DBMS) each with a starter Lab, and - most
importantly - a real Experiment under Electrical whose
simulation_config marks it as the DSO bench (dso_lab.py), so
"Electrical -> DSO" works immediately without a teacher having to set
anything up first.

Only runs if the labs table is empty, so it never overwrites real data.
"""
from app import models


DEFAULT_CATEGORIES = [
    {
        "category": "Electrical",
        "lab_title": "Electrical Engineering Lab",
        "lab_description": "Circuits, measurement instruments, and signal analysis.",
        "experiments": [
            {
                "title": "Digital Storage Oscilloscope & Function Generator",
                "description": (
                    "Connect a function generator to a virtual DSO, learn the "
                    "controls through a guided tutorial, then take your own "
                    "readings (frequency, Pk-Pk, High-Z vs 50Ω loading, etc.)."
                ),
                # This is what tells the Simulation page to render the real
                # dso_lab.py bench instead of a "coming soon" placeholder.
                "simulation_config": {"bench": "dso"},
                "max_score": 100.0,
            },
        ],
    },
    {
        "category": "Physics",
        "lab_title": "Physics Lab",
        "lab_description": "Mechanics, optics, waves, and general physics experiments.",
        "experiments": [],
    },
    {
        "category": "Computer Networks",
        "lab_title": "Computer Networks Lab",
        "lab_description": "Protocols, packet analysis, and network configuration.",
        "experiments": [],
    },
    {
        "category": "DBMS",
        "lab_title": "Database Management Systems Lab",
        "lab_description": "SQL, schema design, transactions, and query optimization.",
        "experiments": [],
    },
]


def seed_default_data(db):
    if db.query(models.Lab).first():
        return  # already has data - never overwrite

    for entry in DEFAULT_CATEGORIES:
        lab = models.Lab(
            title=entry["lab_title"],
            description=entry["lab_description"],
            category=entry["category"],
            created_by_id=None,  # system-seeded, no owning user
        )
        db.add(lab)
        db.flush()  # get lab.id

        for exp in entry["experiments"]:
            db.add(models.Experiment(
                lab_id=lab.id,
                title=exp["title"],
                description=exp["description"],
                simulation_config=exp["simulation_config"],
                max_score=exp["max_score"],
            ))

    db.commit()
