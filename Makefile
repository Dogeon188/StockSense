HOST_PORT = 8086

SERVER_LOC = stocksense/server.py

.PHONY: setup run-server dev-server run-client dev-client report

setup:
	pip install -r requirements.txt

run-server:
	fastapi run $(SERVER_LOC) --port $(HOST_PORT)

dev-server:
	fastapi dev $(SERVER_LOC) --port $(HOST_PORT)

run-client:
	cd client && npm run build && npm run preview

dev-client:
	cd client && npm run dev

report:
	pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -recorder --extra-mem-bot=10000000 report.tex
