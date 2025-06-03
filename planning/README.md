# Project Planning

Directory containing the planning documents used to drive the project.

## Requirements

### List of project requirements

- Cloud hosted pipeline
- Use required tech stack
    - Terraform
    - Docker
    - AWS
    - Python
    - SQL Server
- Extract module
    - Queries API at https://sigma-labs-bot.herokuapp.com/api/plants/\<plant-id\>
    - Data fecthed every minute
    - Data fetched for every plant
    - Supports minimum 50 plants
- Transform module
    - Verifies data
    - Cleans data
    - Fully normalises data for database
- Load
    - Short term storage
        - Some database
        - 24 hour retention
    - Long term storage
        - Fed by short term
        - Recieved summary of 24 hour data
        - Cost efficient
        - Easily accessible
- Display
    - See live data of daily readings
        - Latest temperature
        - Latest moisture
        - Real time
    - See key facts from historical data
- Reporting
    - Make botanist aware when failure occurs with plants
    - Project demo
        - Video presentation
        - Slides for display
    - Project board
    - Links to deployed code
    - Project documentation

### List of project considerations

- CTO preference
    - OOP
    - TDD