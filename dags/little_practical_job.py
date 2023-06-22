"""""
Libraries and dependencies for the follow the DAG 
"""""
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago

"""""
Libraries and dependencies for the script's logical 
"""""
import requests
import json
import datetime
import os
import pandas as pd
import yagmail 
import psycopg2
from zona_horaria import rosario_date
from config import configConection, configUser,configPassword,configAddress

"""
Functions
"""


def createTablePosg():
    conn = None
    try:
        params = configConection()

        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS mini_pipeline
                        (
                            id VARCHAR(255),
                            site_id VARCHAR(255),
                            title VARCHAR(255),
                            price INTEGER,
                            sold_quantity INTEGER,
                            thumbnail VARCHAR(255),
                            created_date VARCHAR(255)
                        )
                    """)

        cur.close
        conn.commit()

    except Exception as ex:
        print(ex)

    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def data_review():

    try:
        today = rosario_date
        alertPrice = 3000000

        data = pd.read_csv(f"destination_folders_{today}/folder_{today}.csv", sep=";", encoding="utf-8")
        prices = data['price']
        sumPrices = sum(prices)
        totalPrices = int(sumPrices)
        print(totalPrices, " totalPrices")
        
        if totalPrices > alertPrice:
            print(f"The price exceeded {alertPrice}")
            yag = yagmail.SMTP(user = 'yourEmail@example.com', password = 'yourPassword')
            asunto = 'Creation a little practical job'
            mensaje = f"The price exceeded {alertPrice}"
            archivo = f"destination_folders_{today}/folder_{today}.csv"
            yag.send('yourAddress@example.com', asunto, mensaje , attachments=[archivo]) 

        else:
            print('Not exceeded price')
    
    except Exception as ex:
        print(ex)


def data_insert(microwaves):
    today = rosario_date
    
    try:
        params = configConection()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        
        for item in microwaves:
            print(item)
            
            with open(f"destination_folders_{today}/folder_{today}.csv", "a", encoding="utf-8") as f:
                f.write(f"{item['id']};{item['site_id']};{item['title']};{item['price']};{item['sold_quantity']};{item['thumbnail']};{today}\n")
        

            cur.execute(f"""
                INSERT INTO mini_pipeline (id, site_id, title, price, sold_quantity, thumbnail, created_date) 
                VALUES ('{item['id']}','{item['site_id']}','{item['title']}',{item['price']},{item['sold_quantity']},'{item['thumbnail']}','{today}')
            """)
            cur.close
            conn.commit()


    except Exception as ex:
        print(ex)


def data_extract_of_api(category):
    url = f'https://api.mercadolibre.com/sites/MLA/search?category={category}#json'
    r = requests.get(url).text
    j = json.loads(r)
    data = j['results']
    
    today = rosario_date
    microwaves = []
    
    for item in data:
        
        print("Id --> ",item['id'])
        print("Sitio del id --> ", item['site_id'])
        print("Nombre --> ", item['title'])
        print("Precio --> ",item['price'])
        print("Cantidades Vendidas --> ", item['sold_quantity'])
        print("Imagen --> ",item['thumbnail'])
        
        microwaves.append({'id' : item['id'],
                            'site_id' : item['site_id'],
                            'title' : item['title'],
                            'price' : item['price'],
                            'sold_quantity' : item['sold_quantity'],
                            'thumbnail' : item['thumbnail']
                            })                                                                    
    
    i = 0
    for item in microwaves:
        print("Id --> ",microwaves[i]['id'])
        print("Sitio del id --> ",microwaves[i]['site_id'])
        print("Titulo --> ", microwaves[i]['title'])
        print("Precio --> ",microwaves[i]['price'])
        print("Cantidades Vendidas --> ",microwaves[i]['sold_quantity'])
        print("Imagen --> ",microwaves[i]['thumbnail'])
        
        i = i + 1

    print("End data in microwaves array")

    if not os.path.isdir(f"destination_folders_{today}"):
            os.mkdir(f"destination_folders_{today}")
            with open(f'destination_folders_{today}/folder_{today}.csv', 'w', encoding='utf-8') as f:
                f.writelines("id;site_id;title;price;sold_quantity;thumbnail;created_date")
                f.writelines("\n")

    else:
        with open(f'destination_folders_{today}/folder_{today}.csv', 'w', encoding='utf-8') as f:
            f.writelines("id;site_id;title;price;sold_quantity;thumbnail;created_date")
            f.writelines("\n")

    data_insert(microwaves)


def main():
    CATEGORY = "MLA1577"
    data_extract_of_api(CATEGORY)

# if __name__ == '__main__':
#     createTablePosg()
#     main()
#     data_review()
    

"""""
The logic of the DAG
"""""

default_args = {
    'owner' : 'airflow', # Dueño de la task
    'dependes_on_past' : False, # Si depende de una task pasada
    'email' : ['airflow'], # Correo de las personas responsables
    'email_on_failure' : False, # Si queremos mandarles un correo cada vez que falle
    'email_on_retry' : False, # Si queremos mandarles un correo cada vez que reintentamos la task
    'retries' : 1, # Cuantas veces vamos a reintentar ejecutar la task si falla
    'retry_delay' : timedelta(minutes=5), # Cuanto tiempo queremos esperar para reintentar la task si es que falla
}

with DAG(
    'mini_pipeline', # Acá declaramos el nombre del DAG
    default_args = default_args, # Le pasamos nuestro diccionario que creamos de argumentos 
    description = "A little practical job of data engineering with python and followed with Apache Airflow", # Una descripción del DAG
    schedule_interval = timedelta(days=1), # Una agenda de cuando queremos que se ejecute (En este caso 1 vez al día)
    start_date = days_ago(1), # Cuando tenia que haber empezado (En este caso 1 día antes)
    tags = ['mini_pipeline'], # Etiquetas para dar una descripción breve

) as dag: 

     #Definimos las task, le asignamos un 'id' y a que función queremos llamar
    create_table = PostgresOperator(
        task_id='Creation_table_postgres',
        postgres_conn_id = 'postgres_localhost',
        sql = """
                CREATE TABLE IF NOT EXISTS mini_pipeline
                        (
                            id VARCHAR(255),
                            site_id VARCHAR(255),
                            title VARCHAR(255),
                            price INTEGER,
                            sold_quantity INTEGER,
                            thumbnail VARCHAR(255),
                            created_date VARCHAR(255)
                        );

            """
        )
    
    main_task = PythonOperator(task_id = 'Run_main_and_insertion_data', python_callable = main)
    email_task = PythonOperator(task_id = 'email_verification', python_callable = data_review)

   
    # Para definir las dependencias de como queremos que se ejecute el hilo de task, usamos la siguiente sintaxis de airflow:
    create_table >> main_task >> email_task

    

