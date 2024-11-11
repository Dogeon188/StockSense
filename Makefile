HOST_PORT = 8086

MAIN_LOC = stocksense/server.py

run-server:
	cd server && fastapi run $(MAIN_LOC) --port $(HOST_PORT)

dev-server:
	cd server && fastapi dev $(MAIN_LOC) --port $(HOST_PORT)