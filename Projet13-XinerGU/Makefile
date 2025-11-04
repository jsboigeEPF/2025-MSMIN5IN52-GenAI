install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	python -m src.scripts.run_all

report:
	python -m src.scripts.export_report

dashboard:
	streamlit run src/scripts/dashboard.py
