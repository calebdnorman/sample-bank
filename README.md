Usage:
1. Ensure python, docker, poetry are all installed
2. From the root, run `docker-compose -f ./backend/docker-compose-local.yaml up -d` to establish a local DB instance
3. `poetry run start` will start the application and listen on `http://localhost:8000`
4. To run the test suite, make sure your DB is running and run `pytest backend/tests.py` all the data creation is hadnled in the test setup.
