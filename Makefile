.PHONY: test
test:
	poetry run pytest

.PHONY: server
server:
	FLASK_APP=project/app.py poetry run flask run

requirements.txt: poetry.lock
	poetry export --format requirements.txt --output requirements.txt