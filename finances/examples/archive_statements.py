from finances.archiver import archive_statements

if __name__ == '__main__':
    project_folder = ('C:/Users/hugo/OneDrive/Documents/SynologyDrive/Administrative/'
                      'Finances/HSBC/Financial Analysis')
    database_name = 'finance.db'
    statements_folder = project_folder + '/Statments/'

    archive_statements(project_folder, database_name, statements_folder)
