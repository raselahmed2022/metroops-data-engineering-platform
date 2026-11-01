import time

import boto3
import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator


AWS_PROFILE = "metroops-admin"
AWS_REGION = "eu-central-1"
GLUE_CRAWLER_NAME = "metroops-bronze-crawler"


def get_glue_client():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION,
    )

    return session.client("glue")


def start_glue_crawler():
    glue = get_glue_client()

    try:
        glue.start_crawler(
            Name=GLUE_CRAWLER_NAME
        )

        print(
            f"Started Glue crawler: {GLUE_CRAWLER_NAME}"
        )

    except glue.exceptions.CrawlerRunningException:
        print(
            f"Glue crawler {GLUE_CRAWLER_NAME} is already running."
        )

    # Make sure the crawler actually enters RUNNING state
    for _ in range(30):

        crawler = glue.get_crawler(
            Name=GLUE_CRAWLER_NAME
        )["Crawler"]

        state = crawler["State"]

        print(f"Glue crawler state: {state}")

        if state == "RUNNING":
            print("Glue crawler is now running.")
            return

        time.sleep(2)

    raise RuntimeError(
        "Glue crawler did not enter RUNNING state."
    )


def wait_for_glue_crawler():
    glue = get_glue_client()

    while True:

        crawler = glue.get_crawler(
            Name=GLUE_CRAWLER_NAME
        )["Crawler"]

        state = crawler["State"]

        print(f"Glue crawler state: {state}")

        if state == "READY":

            last_crawl = crawler.get("LastCrawl")

            if not last_crawl:
                raise RuntimeError(
                    "Glue crawler finished but no LastCrawl information was found."
                )

            crawl_status = last_crawl.get("Status")

            print(
                f"Last Glue crawl status: {crawl_status}"
            )

            if crawl_status == "SUCCEEDED":
                print(
                    "Glue crawler completed successfully."
                )
                return

            raise RuntimeError(
                f"Glue crawler finished with status: {crawl_status}"
            )

        time.sleep(10)


with DAG(
    dag_id="metroops_pipeline",
    description="End-to-end orchestration of the MetroOps AWS data pipeline",
    start_date=pendulum.datetime(
        2026,
        10,
        29,
        tz="Europe/Berlin",
    ),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 1,
    },
    tags=[
        "metroops",
        "data-engineering",
        "aws",
        "dbt",
    ],
) as dag:

    upload_bronze_to_s3 = BashOperator(
        task_id="upload_bronze_to_s3",
        bash_command=(
            "python "
            "src/ingestion/upload_bronze_to_s3.py"
        ),
        cwd="/opt/metroops",
    )

    trigger_glue_crawler = PythonOperator(
        task_id="trigger_glue_crawler",
        python_callable=start_glue_crawler,
    )

    wait_for_glue_crawler = PythonOperator(
        task_id="wait_for_glue_crawler",
        python_callable=wait_for_glue_crawler,
    )

    run_dbt_build = BashOperator(
        task_id="run_dbt_build",
        bash_command=(
            "dbt build "
            "--project-dir /opt/metroops/metroops_dbt "
            "--profiles-dir /home/airflow/.dbt"
        ),
        cwd="/opt/metroops/metroops_dbt",
    )

    (
        upload_bronze_to_s3
        >> trigger_glue_crawler
        >> wait_for_glue_crawler
        >> run_dbt_build
    )