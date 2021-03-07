# scripts

These scripts have dependencies as seen in the Pipfile (Beautiful Soup, Pandas, and xlsxwriter)


Install the dependencies in a pipenv virtual environment
    1) open a terminal
    2) cd to the "questions" directory (where the Pipfile is)
    3) pip install pipenv
    4) pipenv shell
    5) make sure you are using the correct python interpreter
    6) pipenv sync
    7) Run these Python scripts to generate Excel files in their respective directories:
        python ./python_baby_names/question_1.py
        python ./python_baby_names/question_2.py

        python ./python_fix_logs/question_1.py
        python ./python_fix_logs/question_2.py
