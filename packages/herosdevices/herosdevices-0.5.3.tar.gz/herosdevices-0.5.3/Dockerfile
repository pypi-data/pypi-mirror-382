# #########################################################################################
# Build image with everything required to run HEROS devices via BOSS/HEROS
# #########################################################################################

# -------- Builder Stage --------
FROM python:3 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends swig wget git libtool autoconf pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install wheel-building tools
RUN pip install --break-system-packages --upgrade pip setuptools wheel

# Build and install the lg C library
RUN git clone https://github.com/joan2937/lg.git /opt/lg && \
    cd /opt/lg && \
    make && \
    make install

# Set up wheel build directory
WORKDIR /build

# build older version of libgpiod
RUN wget https://mirrors.edge.kernel.org/pub/software/libs/libgpiod/libgpiod-1.6.3.tar.xz && \
    tar -xvf ./libgpiod-1.6.3.tar.xz && \
    cd ./libgpiod-1.6.3/ && \
    ./configure --enable-tools && \
    make

# get libftd3xx
RUN curl https://ftdichip.com/wp-content/uploads/2024/07/libftd3xx-linux-x86_64-1.0.16.tgz > d3xx.tgz && \
   tar -xzf d3xx.tgz && \
   rm d3xx.tgz

# Download and build necessary wheels
RUN pip wheel lgpio rpi-gpio gpiod spidev sysv_ipc -w /build/wheels

# -------- Final Stage --------
FROM registry.gitlab.com/atomiq-project/boss AS final

# Copy the contents of the repository into the image
WORKDIR /git
COPY . herosdevices

# Copy libftd3xx from the builder stage
COPY --from=builder /build/linux-x86_64/libftd3xx.so* /usr/lib/from-builder/

# Copy lgpio libraries
COPY --from=builder /opt/lg/liblgpio.so* /usr/lib/from-builder/

# Copy libgpiod libraries
COPY --from=builder /build/libgpiod-1.6.3/lib/.libs/libgpiod.so* /usr/lib/from-builder/

# Add lib path
ENV LD_LIBRARY_PATH="/usr/lib/from-builder:${LD_LIBRARY_PATH}"

# Install lgpio deps
RUN apt-get update && apt-get install -y --no-install-recommends swig libgpiod3 && \
    rm -rf /var/lib/apt/lists/*

# Copy the built wheels from the builder stage
COPY --from=builder /build/wheels /wheels

# Install all prebuilt wheels
RUN pip install --break-system-packages /wheels/*.whl

# Install herosdevices in editable mode
RUN pip install --break-system-packages -e herosdevices
