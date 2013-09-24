from django.db import connection


    
    
def main():
    cursor = connection.cursor()
    cursor.execute('DROP TABLE old_formulae ;')
    cursor.execute("ALTER TABLE haccp_customercomplaint ADD COLUMN conclusion text not null default '';")
    cursor.close()


if __name__ == "__main__":
    main()