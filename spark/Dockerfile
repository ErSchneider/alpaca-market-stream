FROM python:3.9.1

RUN apt-get update && apt-get install -y curl wget

RUN pip install pandas confluent_kafka kafka-python

ENV PATH="/home/jdk-11.0.2/bin/:${PATH}"

RUN DOWNLOAD_URL="https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/openjdk-11.0.2_linux-x64_bin.tar.gz" \
    && mkdir -p "/home/jdk-11.0.2" \
    && tar xzf "${TMP_DIR}/openjdk-11.0.2_linux-x64_bin.tar.gz" -C "/home/jdk-11.0.2" --strip-components=1 \
    && rm -rf "${TMP_DIR}" 

RUN DOWNLOAD_URL_SPARK="https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz" \
    && wget --no-verbose -O apache-spark.tgz "${DOWNLOAD_URL_SPARK}" \
    && mkdir -p /home/spark \
    && tar -xf apache-spark.tgz -C /home/spark --strip-components=1 

ENV PATH="/home/spark/bin/:${PATH}"
ENV PYTHONPATH="/home/spark/python/:$PYTHONPATH"
ENV PYTHONPATH="/home/spark/python/lib/py4j-0.10.9.5-src.zip:$PYTHONPATH"

ADD spark/main.py /
ADD config.py /

CMD [ "python", "./main.py" ]
