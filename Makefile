.PHONY: all clean 

MYSQL_DATA = ./mysql/sql

all: clean_database
	@echo [EXECUTING] ./scripts/$(EXEC)
	@bash ./scripts/exec.sh

download: clean_fetcher clean_database
	@echo [CREATING] fetcher/data folder 
	@-mkdir ./fetcher/data
	@echo [DOWNLOADING] data from the source... 
	@docker-compose run fetcher python ./update_data/download.py
	@echo [REMOVING] data from mysql... 
	@-rm $(MYSQL_DATA)/1_faculty.sql
	@-rm $(MYSQL_DATA)/2_course.sql
	@-rm $(MYSQL_DATA)/3_course_unit.sql
	@-rm $(MYSQL_DATA)/4_schedule.sql
	@echo [MOVING] data from fetcher to sql... 
	@mv ./fetcher/data/* ./mysql/sql

upload: 
	@echo [UPLOADING] data...
	@docker-compose run fetcher python ./update_data/upload.py

clean: clean_fetcher clean_database

clean_fetcher: 
	@echo [CLEANING] Removing folder fetcher/data...
	@-rm -r ./fetcher/data

clean_database:
	@echo [CLEANING] Removing folder mysql/data...
	@-rm -r ./mysql/data/
