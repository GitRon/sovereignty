### STAGE 1: Build ###

# We label our stage as 'builder'
FROM node:14-alpine as builder

# build backend
ADD package.json /tmp/package.json
ADD yarn.lock /tmp/yarn.lock
RUN cd /tmp && yarn install
RUN mkdir -p /backend-app && cp -a /tmp/node_modules /backend-app

### STAGE 2: Setup ###
FROM python:3.9

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV PRJ_SRC=.
# Directory in container for all project files
ENV PRJ_SRVHOME=/srv
# Directory in container for project source files
ENV PRJ_SRVPROJ=/srv/ai-portal/

# Create application subdirectories
WORKDIR $PRJ_SRVPROJ
RUN mkdir media static staticfiles logs

# Move pipfiles to project
COPY Pipfile Pipfile.lock $PRJ_SRVPROJ
RUN pip install -U pip pipenv
RUN pipenv install --system --deploy

# make folders available for other containers
VOLUME ["$PRJ_SRVHOME/media/", "$PRJ_SRVHOME/logs/"]

# Copy application source code to SRCDIR
COPY $PRJ_SRC $PRJ_SRVPROJ

COPY --from=builder /backend-app/node_modules $PRJ_SRVPROJ/node_modules

# Create empty env-file to avoid warnings
RUN touch $PRJ_SRVPROJ/apps/config/.env

# Copy entrypoint script into the image
WORKDIR $PRJ_SRVPROJ

# Run collectstatic for whitenoise
RUN python ./manage.py collectstatic --noinput

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000

CMD ["./run_web.sh"]
