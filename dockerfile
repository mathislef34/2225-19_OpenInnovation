FROM n8nio/n8n

USER root

RUN apk add --no-cache bash python3 py3-pip py3-virtualenv curl

WORKDIR /app

COPY requirements.txt generate_network.py main.py network_input.json /app/

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY workflows/ /home/node/workflows/

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV PATH="/opt/venv/bin:$PATH"
ENV N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
ENV N8N_RUNNERS_ENABLED=true

USER node

ENTRYPOINT ["/start.sh"]
