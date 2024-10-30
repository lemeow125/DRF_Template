FROM python:3.13.0-bullseye

ENV PYTHONBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /code
COPY . /code/
ADD . /code/
COPY scripts/ /code/scripts/
RUN chmod +x /code/scripts/start.sh

# Install packages
RUN apt update && apt install -y graphviz libgraphviz-dev graphviz-dev wget zip chromium chromium-driver firefox-esr
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# (Firefox) Download the latest Geckodriver and install it
ENV GECKODRIVER_VERSION=latest
RUN wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz
RUN tar -zxf geckodriver.tar.gz -C /usr/bin
RUN chmod +x /usr/bin/geckodriver

# Expose port 8000 for the web server
EXPOSE 8000

ENTRYPOINT [ "/code/scripts/start.sh" ]