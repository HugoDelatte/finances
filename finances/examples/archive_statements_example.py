from finances.archiver import archive_statements

if __name__ == '__main__':
    project_folder = 'my_project_folder'
    database_name = 'finance.db'
    statements_folder = 'my_statement_folder'
    archive_statements(project_folder, database_name, statements_folder)
