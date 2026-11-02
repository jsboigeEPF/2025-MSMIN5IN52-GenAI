from dataclasses import dataclass
import yaml, random

@dataclass
class Config:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    seed: int = 42
    max_requests: int = 200
    temperature: float = 0.7
    top_p: float = 1.0
    batch_size: int = 8
    max_tokens: int = 300
    prompts_file: str = "src/auditor/prompts/bias_tests.yaml"
    save_run_dir: str = "data/results/runs"
    save_reports_dir: str = "data/results/reports"

def load_config(path: str) -> 'Config':
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    cfg = Config(
        provider=data.get("provider", "openai"),
        model=data.get("model", "gpt-4o-mini"),
        seed=int(data.get("seed", 42)),
        max_requests=int(data.get("max_requests", 200)),
        temperature=float(data.get("temperature", 0.7)),
        top_p=float(data.get("top_p", 1.0)),
        batch_size=int(data.get("batch_size", 8)),
        max_tokens=int(data.get("max_tokens", 300)),
        prompts_file=data.get("prompts_file", "src/auditor/prompts/bias_tests.yaml"),
        save_run_dir=data.get("save", {}).get("run_dir", "data/results/runs"),
        save_reports_dir=data.get("save", {}).get("reports_dir", "data/results/reports"),
    )
    random.seed(cfg.seed)
    return cfg
