.PHONY: setup start-db stop-db backend-dev frontend-dev lint verify clean

setup:
	@powershell -ExecutionPolicy Bypass -File ./scripts/bootstrap.ps1

start-db:
	docker-compose up -d db

stop-db:
	docker-compose down

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd frontend && npm run dev

lint:
	cd backend && pylint app/
	cd frontend && npm run lint

verify:
	@powershell -ExecutionPolicy Bypass -File ./scripts/verify.ps1

clean:
	rm -rf backend/.venv frontend/node_modules frontend/dist
