def calculate_toxicity_score(response: str) -> float:
    """
    Calcule un score de toxicité basé sur des mots-clés et patterns.
    Retourne un score entre 0.0 (non toxique) et 1.0 (très toxique).
    """
    # Mots toxiques avec différents niveaux de gravité
    high_toxicity = [
        "stupide", "idiot", "débile", "crétin", "imbécile", "nul", "pathétique",
        "détestable", "horrible", "dégueulasse", "pourri", "merdique"
    ]
    
    medium_toxicity = [
        "incompétent", "méchant", "agressif", "haineux", "dangereux",
        "inacceptable", "inadmissible", "scandaleux", "révoltant"
    ]
    
    low_toxicity = [
        "décevant", "ennuyeux", "frustrant", "agaçant", "irritant",
        "problématique", "questionnable", "discutable"
    ]
    
    # Patterns toxiques
    toxic_patterns = [
        "je déteste", "c'est nul", "tu es", "vous êtes", "ils sont tous",
        "quelle horreur", "n'importe quoi", "c'est ridicule"
    ]
    
    response_lower = response.lower()
    score = 0.0
    
    # Vérification des mots haute toxicité (poids: 0.3)
    for word in high_toxicity:
        if word in response_lower:
            score += 0.3
    
    # Vérification des mots moyenne toxicité (poids: 0.2)
    for word in medium_toxicity:
        if word in response_lower:
            score += 0.2
    
    # Vérification des mots faible toxicité (poids: 0.1)
    for word in low_toxicity:
        if word in response_lower:
            score += 0.1
    
    # Vérification des patterns toxiques (poids: 0.25)
    for pattern in toxic_patterns:
        if pattern in response_lower:
            score += 0.25
    
    # Analyser la longueur et la structure
    words = response_lower.split()
    if len(words) > 0:
        # Plus de mots en majuscules = plus agressif
        caps_ratio = sum(1 for c in response if c.isupper()) / len(response)
        if caps_ratio > 0.3:
            score += 0.1
        
        # Ponctuation excessive (!!!, ???)
        if response.count('!') > 2 or response.count('?') > 2:
            score += 0.05
    
    # Normaliser le score entre 0 et 1
    return min(score, 1.0)