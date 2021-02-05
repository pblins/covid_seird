test:
	coverage run --source=./covid_seird -m unittest -v tests/test_covid_accessor.py 
	coverage report -m
