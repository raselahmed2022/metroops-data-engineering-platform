# MetroOps — Industrial IoT Data Engineering Platform

**An end-to-end industrial IoT data engineering project built with Python, AWS, Apache Airflow, dbt, Docker, and Terraform.**

MetroOps demonstrates how industrial equipment data can be ingested, validated, transformed, stored in a cloud data lake, and modeled for operational analytics.

The project focuses on compressor sensor readings, equipment faults, maintenance activities, and operational performance.

## Project Overview

Industrial equipment generates large volumes of sensor and maintenance data. Transforming these records into reliable analytics requires data ingestion, quality checks, scalable storage, orchestration, and analytical modeling.

MetroOps implements these components using a medallion-style data architecture, AWS cloud services, and infrastructure as code.

**Key capabilities:**
- Python-based CSV ingestion and Parquet processing
- Chunked processing of approximately 1.52 million expected sensor records
- Bronze, Silver, and Gold data layers
- Amazon S3 storage and AWS Glue data cataloging
- SQL transformations using dbt and Amazon Athena
- Apache Airflow orchestration with Docker
- Data quality and relationship validation
- Terraform infrastructure management
- GitHub Actions CI/CD with AWS OIDC authentication

## Architecture

```text
Industrial IoT CSV Data
          |
          v
   Python Ingestion
          |
          v
  Bronze Layer (Parquet)
          |
          +----------------------+
          |                      |
          v                      v
 Python Transformations     Amazon S3
          |                      |
          v                      v
  Silver Layer (Local)      AWS Glue Crawler
          |                      |
          v                      v
  Gold Layer (Local)        AWS Glue Catalog
                                 |
                                 v
                           Amazon Athena
                                 |
                                 v
                           dbt Models
                                 |
                    +------------+------------+
                    |            |            |
                 Staging     Dimensions     Facts
                                              |
                                              v
                                        Analytics Marts
```

Apache Airflow orchestrates the S3 upload, Glue crawler execution, and dbt build. Terraform manages AWS infrastructure separately.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python, SQL |
| Data processing | pandas, PyArrow, Parquet |
| Cloud | AWS S3, AWS Glue, Amazon Athena |
| Data modeling | dbt Core, dbt-athena |
| Orchestration | Apache Airflow |
| Containers | Docker, Docker Compose |
| Infrastructure as Code | Terraform |
| CI/CD | GitHub Actions |
| Authentication | AWS IAM, AWS OIDC |
| Version control | Git, GitHub |

## Data Pipeline

### 1. Bronze — Data Ingestion

Python scripts ingest CSV files and convert them into Parquet datasets.

The ingestion process adds technical metadata such as source filenames and ingestion timestamps. Large sensor datasets are processed in chunks of 100,000 records.

### 2. Silver — Data Cleaning

Python transformations standardize timestamps and data types, remove duplicates, validate required fields, and apply business rules.

### 3. Gold — Analytical Datasets

The local Gold layer produces analytical datasets such as:
- Maintenance performance
- Fault summaries
- Daily compressor health

These datasets support analysis of maintenance costs, equipment downtime, faults, and sensor behavior.

### 4. AWS Data Lake and dbt

Bronze Parquet files are uploaded to Amazon S3.

An AWS Glue crawler discovers the datasets and updates the Glue Data Catalog. dbt uses Amazon Athena to build staging models, warehouse dimensions and facts, and analytical marts.

Example models include:

- `fct_sensor_daily`
- `fct_faults`
- `fct_maintenance`
- `dim_compressor`
- `dim_facility`
- `dim_technician`
- `mart_compressor_health`
- `mart_maintenance_performance`

## Apache Airflow Orchestration

The `metroops_pipeline` DAG executes the following sequence:

1. Upload Bronze Parquet datasets to Amazon S3.
2. Trigger the AWS Glue crawler.
3. Wait for successful crawler completion.
4. Execute `dbt build`.

The DAG is configured for manual triggering rather than automatic scheduling.

Airflow runs locally through Docker Compose.

## Data Quality

The project includes Python validation scripts and dbt data tests.

Validation covers:
- Expected sensor record counts
- Required fields and null values
- Duplicate identifiers
- Timestamp consistency
- Valid numeric values and date ranges
- Relationships between equipment, faults, work orders, and maintenance records
- dbt uniqueness, not-null, relationship, and accepted-value tests

## Repository Structure

```text
MetroOps_Data_Pipeline/
|
|-- .github/workflows/   # CI and CD workflows
|-- airflow/             # Airflow DAG and Docker configuration
|-- data/                # Local data lake (Git-ignored)
|-- metroops_dbt/        # dbt SQL models and tests
|-- src/
|   |-- ingestion/       # CSV and Parquet ingestion
|   |-- transformation/  # Silver and Gold processing
|   |-- validation/      # Data quality checks
|-- terraform/           # AWS infrastructure and IAM
|-- tests/               # Local test directory
|-- .gitignore
|-- README.md
```

## Running Locally

### Prerequisites

- Python 3.12
- Docker Desktop
- AWS CLI with a configured AWS profile
- Terraform
- dbt Core with the Athena adapter
- Access to the project's source CSV dataset

The raw dataset is not included in the Git repository.

### 1. Install Python dependencies

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pandas pyarrow boto3
```

### 2. Prepare source data

Place the CSV files in:

`data/raw/metro_company_dataset_csv/`

### 3. Run ingestion

```powershell
python src/ingestion/ingest_bronze.py
python src/ingestion/ingest_sensor_bronze.py
```

### 4. Run transformations

```powershell
python src/transformation/transform_silver.py
python src/transformation/transform_sensor_silver.py
python src/transformation/transform_gold.py
```

### 5. Validate data

```powershell
python src/validation/validate_bronze.py
python src/validation/validate_silver.py
python src/validation/validate_gold.py
```

### 6. Run cloud components

Cloud execution requires valid AWS credentials, access to the configured S3 bucket and Glue crawler, and a working dbt Athena profile.

The Airflow Docker Compose configuration also requires local environment setup.

## Infrastructure as Code

Terraform manages the project's AWS resources, including:

- Amazon S3 data lake bucket
- AWS Glue database and crawler
- IAM roles and policies
- GitHub Actions OIDC provider and deployment role

Terraform state is stored remotely in Amazon S3 with state locking enabled.

## CI/CD

### Continuous Integration

The **MetroOps CI** GitHub Actions workflow runs on pushes and pull requests to `main`.

It checks Python syntax, Terraform formatting, and Terraform configuration validity.

### Continuous Deployment

The **MetroOps CD** workflow is triggered manually and deploys Terraform changes to AWS.

It uses:
- GitHub Actions OIDC authentication
- A dedicated AWS IAM deployment role
- GitHub `production` environment approval
- Terraform initialization, validation, planning, and application

**Status:** CI and CD workflows successfully completed on November 5, 2026.

[View GitHub Actions](https://github.com/raselahmed2022/metroops-data-engineering-platform/actions)

## Project Scope

MetroOps is a portfolio-oriented, production-style engineering project. AWS infrastructure deployment is automated through GitHub Actions, while the Airflow data pipeline runs in a local Docker environment.

The project demonstrates practical experience in building data pipelines, modeling analytical datasets, validating data quality, managing cloud infrastructure, and implementing CI/CD.

## Author

**Rasal Miah**

[GitHub](https://github.com/raselahmed2022)