HOST_PORT = 8086

MAIN_LOC = stocksense/server.py

run-server:
	cd server && fastapi run $(MAIN_LOC) --port $(HOST_PORT)

dev-server:
	cd server && fastapi dev $(MAIN_LOC) --port $(HOST_PORT)

report:
	pdflatex -synctex=1 -interaction=nonstopmode -file-line-error -recorder --extra-mem-bot=10000000 report.tex
