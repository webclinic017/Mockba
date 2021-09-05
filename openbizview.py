# coding=utf-8
import postgrescon as pg
import psycopg2

# login contraseña
def login_pass(ppassw):
    con = pg.conection()
    record = ""
    try:
        cur = con.cursor()
        cur.callproc('bot_login_pass', ['1', ppassw])       
        for row in cur.fetchall():
            record = row[0]
        cur.close
        con.close    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()  # Cerrando conección
    return record