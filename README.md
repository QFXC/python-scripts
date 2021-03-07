# scripts

These scripts have dependencies as seen in the Pipfile (Beautiful Soup, Pandas, and xlsxwriter)


### Install the dependencies in a pipenv virtual environment
    1. open a terminal
    1. cd to the "questions" directory (where the Pipfile is)
    1. ```pip install pipenv```
    1. ```pipenv shell```
    1. Make sure you are using the correct python interpreter
    1. ```pipenv sync```
    1. Run these Python scripts to generate Excel files in their respective directories:
        * ```python ./python_baby_names/question_1.py```
        * ```python ./python_baby_names/question_2.py```

        * ```python ./python_fix_logs/question_1.py```
        * ```python ./python_fix_logs/question_2.py```
    1. type:
        * ```exit```
