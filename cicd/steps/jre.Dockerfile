# Note: The JRE image should synced with workflow https://bitbucket.org/foundingfathersflo/workflow/src/master/Dockerfile. To be de-duplicated in the future.

FROM eclipse-temurin:17.0.12_7-jre-ubi9-minimal
ARG GIT_COMMIT
ARG BUILD_DATETIME
ARG ARCHIVE
ENV ARCHIVE=$ARCHIVE
ARG SERVICE
ENV SERVICE=$SERVICE


# The container will run using user 1000 in k8s. Validate that this maps to user ubuntu.
RUN if [ $(id -u ubuntu) -ne 1000 ]; then echo "User ubuntu is not 1000" && exit 1; fi;
WORKDIR /home/ubuntu/

RUN wget https://github.com/jattach/jattach/releases/download/v2.2/jattach
RUN chmod +x jattach

COPY --chown=ubuntu:ubuntu $ARCHIVE $SERVICE.jar

ENV GIT_COMMIT=$GIT_COMMIT
ENV BUILD_DATETIME=$BUILD_DATETIME

ENTRYPOINT java -jar ${SERVICE}.jar