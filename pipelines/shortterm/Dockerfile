FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install unix0DBC
RUN dnf install -y tar gzip unixODBC unixODBC-devel

# Install Microsoft ODBC Drivers
RUN curl https://packages.microsoft.com/config/rhel/7/prod.repo | tee /etc/yum.repos.d/mssql-release.repo
RUN ACCEPT_EULA=Y dnf install -y msodbcsql18
RUN export CFLAGS=”-I/opt/include” && export LDFLAGS=”-L/opt/lib”

COPY extract_short.py .
COPY transform_short.py .
COPY load_short.py .
COPY pipeline_short.py .

CMD [ "pipeline_short.lambda_handler" ]