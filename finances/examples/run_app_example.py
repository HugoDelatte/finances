from finances.app import run_app

if __name__ == '__main__':
    project_folder = 'my_project_folder'
    database_name = 'finance_random.db'
    run_app(project_folder=project_folder, database_name=database_name)
