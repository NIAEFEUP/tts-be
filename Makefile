.PHONY: all clean 

POSTGRES_DATA = ./postgres/sql

all: clean_database
	@echo [EXECUTING] ./scripts/$(EXEC)
	@bash ./scripts/exec.sh

download: clean_fetcher clean_database
	@echo [CREATING] fetcher/data folder 
	@-mkdir ./fetcher/data
	@echo [DOWNLOADING] data from the source... 
	@docker-compose run fetcher python ./update_data/download.py
	@echo [REMOVING] data from postgres... 
	@-rm $(POSTGRES_DATA)/01_data.sql
	@echo [MOVING] data from fetcher to sql... 
	@mv ./fetcher/data/* ./postgres/sql

upload: 
	@echo [UPLOADING] data...
	@docker-compose run fetcher python ./update_data/upload.py

populate:
	@-docker compose down
	@-docker compose build --no-cache
	@-docker volume rm tts_postgres_data || true
	@-docker compose up

clean: clean_fetcher clean_database

clean_fetcher: 
	@echo [CLEANING] Removing folder fetcher/data...
	@-rm -r ./fetcher/data

clean_database:
	@echo [CLEANING] Removing database data...
	@-docker volume rm tts_postgres_data || true
