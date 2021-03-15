# scripts

These scripts have dependencies as seen in the Pipfile (Beautiful Soup, Pandas, and xlsxwriter)


### Install the dependencies in a pipenv virtual environment:
1. open a terminal
1. cd to the directory where the Pipfile file is
1. ```pip install pipenv```
1. ```pipenv shell```
1. Make sure you are using the correct python interpreter
1. ```pipenv sync```


# Option 1
### Run these Python scripts to generate Excel files in their respective directories:
* ```python ./python_baby_names/question_1.py```
* ```python ./python_baby_names/question_2.py```

* ```python ./python_fix_logs/question_1.py```
* ```python ./python_fix_logs/question_2.py```


# Option 2
### Run these ___alternate___ Python scripts to generate Excel files in their respective directories:
#### These use Regular Expressions to generate the same files as Option 1.
1. Make sure you have all the latest dependencies
    ```pipenv sync```

* ```python ./python_baby_names/question_1_v2.py```
* ```python ./python_baby_names/question_2_v2.py```

* ```python ./python_fix_logs/question_1_v2.py```
* ```python ./python_fix_logs/question_2_v2.py```


1. ```exit```
1. ```pipenv --rm```