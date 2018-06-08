FROM       python:3.6
MAINTAINER vicalloy "https://github.com/vicalloy"

RUN apt-get update && apt-get install -y \
		npm \
		graphviz libgraphviz-dev \
		pkg-config \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN npm install -g bower
RUN pip install --upgrade pip setuptools
RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN mkdir -p /usr/deploy
WORKDIR /usr/deploy
RUN git clone https://github.com/vicalloy/django-lb-workflow
WORKDIR /usr/deploy/django-lb-workflow
RUN pip install -e .[options]

RUN make wfgen
RUN make reload_test_data
RUN python testproject/manage.py bower_install --allow-root

EXPOSE 9000
CMD ["make", "run"]
