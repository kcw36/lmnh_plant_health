# Extract
## Installation
- ODBC Driver for SQL from Mac
```bash
brew install unixodbc
```
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18
```