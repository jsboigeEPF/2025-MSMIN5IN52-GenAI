from typing import List
import random
import re

POS = ["excellent", "solide", "clair", "professionnel", "fiable", "remarquable"]
HEDGE = ["peut-être", "probablement", "possiblement", "il semble"]

class MockProvider:
    name = "mock"
    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        out = []
        random.seed(kwargs.get("seed", 42))
        for p in prompts:
            extra_hedge = re.search(r"rural(e)?", p, re.IGNORECASE) is not None
            base = f"Ce candidat est {random.choice(POS)}, doté d’un objectif clair et capable d’assumer des responsabilités."
            if extra_hedge:
                base = random.choice(HEDGE) + ", " + base
            out.append(base + " Il est conseillé de structurer ses projets clés et ses résultats mesurables.")
        return out
