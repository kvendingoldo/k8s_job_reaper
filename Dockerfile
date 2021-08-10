FROM python:3-slim

RUN mkdir -p "/app/src"
COPY resources/requirements.txt "/app"
COPY src/ "/app/src/"

RUN pip3 install -r "/app/requirements.txt" \
 && chmod +x "/app/src/reaper.py"

WORKDIR "/app"
ENTRYPOINT ["python3", "src/reaper.py"]
