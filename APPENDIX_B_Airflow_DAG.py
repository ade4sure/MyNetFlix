from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from airflow.models.param import Param

# Assuming the original script's functions are encapsulated
from APPENDIX_A_ETL_Script import EXTRACT_DATA, MOVE_DATA_2_STAGING, TRANSFORM_LOAD

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

def extract_data_with_param(**context):
    # Fetch the year from DAGparam conf (passed when triggering the DAG)
    year = context["params"]["year"]
    print(f'Year supplied = {year}')
    EXTRACT_DATA(year)
    

with DAG('etl_f1_data_pipeline',
         default_args=default_args,
         params={"year": Param(2021, type="integer", minimum=2020)},
         schedule_interval='@daily',
         catchup=False) as dag:

    extract_task = PythonOperator(
        task_id='Extract_Data',
        python_callable=extract_data_with_param        
    )

    staging_task = PythonOperator(
        task_id='Stage_Data',
        python_callable=MOVE_DATA_2_STAGING
    )

    transform_load_task = PythonOperator(
        task_id='Transform_and_Load',
        python_callable=TRANSFORM_LOAD
    )
    
    extract_task >> staging_task >> transform_load_task 
