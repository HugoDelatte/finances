from finances.app import run_app

if __name__ == '__main__':
    project_folder = ('C:/Users/hugo/OneDrive/Documents/SynologyDrive/Administrative/'
                      'Finances/HSBC/Financial Analysis')
    database_name = 'finance.db'
    run_app(project_folder=project_folder, database_name=database_name)
