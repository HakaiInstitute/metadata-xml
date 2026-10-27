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

RUN python -m pip install --no-cache-dir "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"
RUN pip install --no-cache-dir .

RUN python -m metadata_xml -f sample_records/record.yml
# make sure it validates with the schema
RUN sh validate.sh sample_records/record.xml
