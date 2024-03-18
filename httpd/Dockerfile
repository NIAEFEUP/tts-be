FROM httpd:2.4

RUN apt update && apt upgrade -y && apt install -y libapache2-mod-shib

COPY start /start

RUN sed -i "s/\r//" /start

CMD /start
