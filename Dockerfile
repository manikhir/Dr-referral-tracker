# Base image
FROM ubuntu:14.04

# Add user to run the application
RUN adduser app_user --disabled-password

# Create application directories
RUN mkdir -p /web/static
RUN mkdir -p /web/media
RUN chown -R app_user:app_user /web

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=Dr-referral-tracker
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv/Dr-referral-tracker


# Install packages
#RUN apt-get update
#RUN apt-get install -y python python-dev python-setuptools libpq-dev
#RUN apt-get install -y nginx supervisor vim
#RUN apt-get install -y python-numpy libjpeg-dev libffi-dev

RUN apt-get update && apt-get -y upgrade
#RUN apt-get install -y tar git curl nano wget dialog net-tools
RUN sudo apt-get install -y python3-setuptools
RUN apt-get install -y python3-dev
RUN sudo easy_install3 pip
RUN pip install --upgrade pip

# Install pip
#RUN apt-get install -y python-pip
#RUN pip install --upgrade pip
RUN ln -s /usr/local/bin/pip /usr/bin/pip
RUN apt-get install -y supervisor

# Install Python packages
RUN pip install gunicorn
#RUN pip install Pillow

# Copy over scripts
ADD scripts /root/Dr-referral/Dr-referral-tracker/scripts
RUN chmod 755 /root/Dr-referral/Dr-referral-tracker/scripts/*

# Copy over config
ADD conf /root/Dr-referral/Dr-referral-tracker/conf

# Set up supervisor
RUN sudo ln -s /root/Dr-referral/Dr-referral-tracker/conf/supervisor_app.conf /etc/supervisor/conf.d/

# Set up NGINX
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/*
RUN ln -s /root/Dr-referral/Dr-referral-tracker/conf/nginx_app /etc/nginx/sites-enabled/nginx_app

# Expose port
EXPOSE 80

# Start script
CMD ["/root/Dr-referral/Dr-referral-tracker/scripts/container_start.sh"]

#
# Triggers for sub-builds
#

# Install Python dependencies
ONBUILD ADD requirements.txt /DOCKYARD_SRVPROJ/
ONBUILD RUN pip install -r /DOCKYARD_SRVPROJ/requirements.txt

# Copy over user code
ONBUILD ADD . /root/code/

# Set permissions on user code
ONBUILD RUN chown -R root:root /home/root

