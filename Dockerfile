FROM python:3.11.4-bookworm

ENV PYTHONBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /code
COPY . /code/
RUN chmod +x /code/start.sh

# Install packages
RUN apt-get update && apt-get install -y graphviz libgraphviz-dev graphviz-dev wget zip
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Chrome has no install candidate on ARM64
# If you plan on running on x86 you can comment this out
# Install Chrome
# RUN apt install chromium-browser
# Install Chromedriver
# ENV CHROMEDRIVER_VERSION=124.0.6367.155
# RUN wget https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip \
#   && unzip chromedriver-linux64.zip && rm -dfr chromedriver_linux64.zip \
#   && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
#   && chmod +x /usr/bin/chromedriver
  
# Install Firefox and Geckodriver
RUN apt-get update && apt-get install -y firefox-esr
# Download the latest Geckodriver and install it
ENV GECKODRIVER_VERSION=latest
RUN wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz
RUN tar -zxf geckodriver.tar.gz -C /usr/bin
RUN chmod +x /usr/bin/geckodriver

# Expose port 8000 for the web server
EXPOSE 8000

ENTRYPOINT [ "/code/start.sh" ]