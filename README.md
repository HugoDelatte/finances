# finances

finances is a Python library to save the transactions from your bank account
into a database and analyse them through an interactive app.

## Motivation

At the time of writing, HSBC UK provides personal account statements only in pdf.
This package reads your HSBC statements from pdf, converts and saves them into a local sqlite database in order
to analyse your account transactions and track your spending via a Dash interactive app.
For the moment, only statements from HSBC UK are supported.


## App Demo
![](transactions_analysis.gif)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the package finances:

```bash
pip install finances
```

Install the dependencies using requirement.txt:
```bash
pip install -r requirements.txt  
```

You can also create a virtual environment from the environment.yml file:

```bash
conda env create -f environment.yml
```

## How to use it?

* Choose a location to create your project folder.
This is where the database will be saved with other things like logs and error
files.

* Save all your pdf bank statements in a folder and rename them "statements_yyyy-mm.pdf"

* To save the statements into the database, run the following lines

```bash
from finances.archiver import archive_statements

archive_statements('my_project_folder', 'my_database_name', 'my_statements_folder')
```
 
Each transaction is mapped to an entity from the entity_mapping.csv using keywords.
The mapping algorithm is straightforward.
Their is a trade-off between maximal mapping flexibility and minimal editing.
The entity from the entity_mapping.csv file assigned to the transactions is the one with the keyword of maximum length
that matches the begining of the transaction description.
When no entity is found, the transaction details are saved in the error folder.
In that case, you have to add the missing mapping into the entity_mapping.csv file.

* To use the app, run the following lines

```bash
from finances.app import run_app

run_app('my_project_folder', 'my_database_name')
```

## Examples

You can find mapping and code examples in finances.examples


## License
[MIT](https://choosealicense.com/licenses/mit/)