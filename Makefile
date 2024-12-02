HOST_PORT = 8086

SERVER_LOC = stocksense/server.py

.PHONY: run-server dev-server

setup:
	pip install -r requirements.txt

run-server:
	cd server && fastapi run $(SERVER_LOC) --port $(HOST_PORT)

dev-server:
	cd server && fastapi dev $(SERVER_LOC) --port $(HOST_PORT)

report:
	pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -recorder --extra-mem-bot=10000000 report.tex
