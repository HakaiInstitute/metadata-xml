# Run tests using docker
FROM python:3.13-slim

WORKDIR /repo

RUN apt-get update \
    && apt-get install -y --no-install-recommends libxml2-utils unzip \
    && rm -rf /var/lib/apt/lists/*

COPY validate.sh .
COPY cioos-schema.zip .
RUN unzip -q cioos-schema.zip

COPY pyproject.toml README.md ./
COPY ./metadata_xml ./metadata_xml
COPY sample_records ./sample_records
RUN pip install --no-cache-dir .

RUN python -m metadata_xml -f sample_records/record.yml
# make sure it validates with the schema
RUN sh validate.sh sample_records/record.xml
