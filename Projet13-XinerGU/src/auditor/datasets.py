import yaml, itertools, hashlib, json

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

def load_prompt_sets(path: str):
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    tasks = []
    for task in doc.get("tasks", []):
        name, template = task["name"], task["template"]
        variables = task.get("variables", {})
        keys, groups = list(variables.keys()), list(variables.values())
        for combo in itertools.product(*groups):
            mapping = dict(zip(keys, combo))
            prompt = template.format(**mapping)
            uid = _hash(name + json.dumps(mapping, ensure_ascii=False))
            tasks.append({
                "task": name,
                "mapping": mapping,
                "prompt": prompt,
                "uid": uid,
                "group": "|".join(str(v) for v in mapping.values())
            })
    return tasks
