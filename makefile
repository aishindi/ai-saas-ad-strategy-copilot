.PHONY: install seed run-backend run-ui run-tests eval

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

seed:
	python database/seed_data.py

run-backend:
	uvicorn app:app --reload --host 127.0.0.1 --port 8000

run-ui:
	streamlit run ui/streamlit_app.py

run-tests:
	python evaluation/run_evaluation.py

eval:
	python evaluation/run_evaluation.py