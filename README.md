# LMNH Plant Health Pipeline

- This is an example project built around a case study.
- The project aims to serve a dashboard and messaging service for the benfit of the key stakeholders in the case study.

## Case Study

- We are a team of data engineers working for **Liverpool Museum of Natural History (LMNH)**.
- LMNH has sensors attached to their plants which outputs data about the plant to an API every minute.
- The team want to store the last 24 hours of data, keep a summary record of all data recorded and view both sets of data in a live dashboard.
- The team would also like to be notified through messaging when a plant has recordings that need tending to e.g. an unhealthy plant.

## Navigating the Repository

- Semantically similiar content ahs been grouped into sub directories of this repository.
- Each sub directory and its content is explained below.

### Project planning

- The `planning` directory stores information to how the project was planned.
- These include:
    - Project Requirements
    - A Work Breakdown Structure
    - A template for documenting python projects

### System Architecture

- The `architecture` directory contains information relating to the design of the cloud architecture and the implementation of that.
- This includes:
    - Scripts and schema for populating a SQL Server Database
    - Terraform config for deploying resources to AWS
    - Design documentation for the architecture

### Pipelines

- The `pipelines` directory contains the two extract, transform, load pipelines used in this project
- They are seperated into two sub directories:
    - `longterm`
        - Loads summary data from the AWS relational database service into the S3 bucket for long term storage
    - `shortterm`
        - Loads all data from LMNH API into AWS relational database service

### Dashboard

- The `dashboard` directory contains the files for serving a streamlit dashboard.

### Report

- The `report` directory contains the files for a report script that notifies an AWS simple notifcation service topic when a plant needs assisstance.

## Using the repository

- These instructions assume you have an RDS instance created for you 
    - If you do not, make that first.
- Each directory as stated above serves a purpose
- To use this repositoryyou must follow the usage instructions in each directory `README` in order:
    - In AWS: 
        - `architecture/database`
        - `architecture/terraform`
    - Local
        - `architecture/database`
        - `pipelines/shortterm`
        - Re run the pipeline multiple times to populate the RDS
        - `pipelines/longterm`
        - Re run the pipeline multiple times to populate the RDS as longterm pipeline clears it and you need the data for dashboard 
        - `pipelines/shortterm`
        - `dashboard`