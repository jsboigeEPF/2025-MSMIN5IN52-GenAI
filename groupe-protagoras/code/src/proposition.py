from dataclasses import dataclass


@dataclass
class Proposition:
    texte_original: str
    formule_logique: str
    type: str  # "premise" | "conclusion"
