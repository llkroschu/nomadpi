ARG ARCH=linux/arm64/v8
ARG NODE_VERSION=21
ARG OS=bookworm
ARG BUILD_DATE="$(date +"%Y-%m-%dT%H:%M:%SZ")"
ARG NODE_RED_VERSION=3.1.3
ARG TAG_SUFFIX=default

#### Stage BASE ########################################################################################################
FROM --platform=${ARCH} node:${NODE_VERSION}-${OS} AS base

# Install base tools FIRST
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    tzdata \
    curl \
    nano \
    wget \
    git \
    openssl \
    openssh-client \
    ca-certificates \
    # Add sudo here, needed for group membership checks later potentially
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create directories, groups, user, and set initial permissions separately
RUN mkdir -p /usr/src/node-red /data && \
    groupadd -f -g 997 gpio || true && \
    groupadd -f dialout || true && \
    (deluser --remove-home node || true) && \
    useradd --home-dir /usr/src/node-red --uid 1000 -G dialout,gpio,sudo node-red && \
    chown -R node-red:dialout /data && chmod -R g+rwX /data && \
    chown -R node-red:dialout /usr/src/node-red && chmod -R g+rwX /usr/src/node-red && \
    # Allow sudo without password for node-red user INSIDE container (if needed later)
    echo "node-red ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Copy scripts needed early
COPY scripts/*.sh /tmp/

# Set work directory
WORKDIR /usr/src/node-red

# Setup SSH known_hosts file
COPY known_hosts.sh .
RUN ./known_hosts.sh /etc/ssh/ssh_known_hosts && rm /usr/src/node-red/known_hosts.sh
RUN echo "PubkeyAcceptedKeyTypes +ssh-rsa" >> /etc/ssh/ssh_config

# Copy package files and entrypoint
COPY package.json .
# COPY flows.json /data # flows.json is often better mounted as a volume
COPY scripts/entrypoint.sh .

#### Stage BUILD #######################################################################################################
FROM base AS build

# Install Build tools
RUN apt-get update && apt-get install -y build-essential python3-pip && \
    npm install --unsafe-perm --no-update-notifier --no-fund --only=production && \
    npm uninstall node-red-node-gpio && \
    cp -R node_modules prod_node_modules

#### Stage RELEASE #####################################################################################################
FROM base AS RELEASE
ARG BUILD_DATE
ARG BUILD_VERSION
ARG BUILD_REF
ARG NODE_RED_VERSION
ARG ARCH
ARG TAG_SUFFIX=default

LABEL org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.docker.dockerfile=".docker/Dockerfile.debian" \
    org.label-schema.license="Apache-2.0" \
    org.label-schema.name="Node-RED" \
    org.label-schema.version=${BUILD_VERSION} \
    org.label-schema.description="Low-code programming for event-driven applications." \
    org.label-schema.url="https://nodered.org" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vcs-type="Git" \
    org.label-schema.vcs-url="https://github.com/node-red/node-red-docker" \
    org.label-schema.arch=${ARCH} \
    authors="Dave Conway-Jones, Nick O'Leary, James Thomas, Raymond Mouthaan"

COPY --from=build /usr/src/node-red/prod_node_modules ./node_modules

# Chown, install devtools & Clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libdbus-glib-1-dev \
        libgirepository1.0-dev \
        python3-dev \
        python3 \
        python3-pip \
        bluez \
        usbutils \
        # python3-lgpio HIER ENTFERNEN
        # Abhängigkeiten für lgpio (sollten meist schon da sein)
        libgpiod2 \
        && \
    # Chown node_modules AFTER installing build tools
    chown -R node-red:root /usr/src/node-red/node_modules && \
    # Clean up apt cache and temp files
    rm -rf /var/lib/apt/lists/* && \
    rm -r /tmp/*


RUN pip3 install --break-system-packages \
    lgpio \
    argparse \
    pexpect \
    jc

# Die nächsten RUN Befehle bleiben wie sie waren
RUN npm config set cache /data/.npm --global
RUN rm /usr/lib/python3.11/EXTERNALLY-MANAGED 


# Renogy BT Python library
RUN git clone https://github.com/cyrils/renogy-bt.git /lib/renogy-bt && \
    pip3 install -r /lib/renogy-bt/requirements.txt

USER node-red

# Env variables
ENV NODE_RED_VERSION=$NODE_RED_VERSION \
    NODE_PATH=/usr/src/node-red/node_modules:/data/node_modules \
    PATH=/usr/src/node-red/node_modules/.bin:${PATH} \
    FLOWS=flows.json

# ENV NODE_RED_ENABLE_SAFE_MODE=true    # Uncomment to enable safe start mode (flows not running)
# ENV NODE_RED_ENABLE_PROJECTS=true     # Uncomment to enable projects option

# Expose the listening port of node-red
EXPOSE 1880

# Add a healthcheck (default every 30 secs)
# HEALTHCHECK CMD curl http://localhost:1880/ || exit 1

# switch back to default user
USER node-red

ENTRYPOINT ["./entrypoint.sh"]
