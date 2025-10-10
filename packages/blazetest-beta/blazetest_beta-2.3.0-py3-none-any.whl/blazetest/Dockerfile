# Start with minimal AWS Lambda Python base (no browsers baked in)
ARG PYTHON_VERSION=3.9
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

# Build arguments for browser configuration
ARG BROWSER_TYPE=chrome
ARG BROWSER_VERSION=latest
ARG INSTALL_BROWSER=true
ARG INSTALL_ALLURE=false
ARG BUILD_BACKEND=docker
ARG SELENIUM_VERSION=4.36.0
ARG DEPENDENCIES_HASH=unknown

# Store dependencies hash as label for smart cache invalidation
LABEL blazetest.dependencies_hash=${DEPENDENCIES_HASH}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BROWSER_TYPE=${BROWSER_TYPE} \
    BROWSER_VERSION=${BROWSER_VERSION} \
    CHROME_FLAGS="--remote-debugging-port=9222 --user-data-dir=/tmp/chrome-user-data --data-path=/tmp/chrome-data --disk-cache-dir=/tmp/chrome-cache --homedir=/tmp" \
    SELENIUM_CHROME_ARGS="--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu --single-process --disable-setuid-sandbox --disable-software-rasterizer --disable-extensions"

# Install OpenSSL 1.1 (required by Selenium Manager binary)
# Amazon Linux 2023 comes with OpenSSL 3.x, but Selenium Manager needs 1.1
# Note: Amazon Linux 2023 Lambda images use microdnf (not dnf/yum)
# Note: openssl11-libs package doesn't exist in AL2023 - testing with OpenSSL 3.x
# RUN microdnf install -y openssl11-libs && microdnf clean all

# Install Node.js and Allure CLI conditionally (only if Allure reporting is enabled)
RUN if [ "$INSTALL_ALLURE" = "true" ]; then \
        microdnf install -y nodejs npm && \
        npm install -g allure-commandline --save-dev && \
        microdnf clean all; \
    else \
        echo "Skipping Node.js and Allure installation (INSTALL_ALLURE=false)"; \
    fi

# Install depot CLI conditionally (only if build backend is depot)
RUN if [ "$BUILD_BACKEND" = "depot" ]; then \
        curl -L https://depot.dev/install-cli.sh | sh; \
    else \
        echo "Skipping depot CLI installation (BUILD_BACKEND=${BUILD_BACKEND})"; \
    fi

# Install namespace CLI conditionally (only if build backend is namespace)
RUN if [ "$BUILD_BACKEND" = "namespace" ]; then \
        curl -fsSL https://get.namespace.so/install.sh | sh; \
    else \
        echo "Skipping namespace CLI installation (BUILD_BACKEND=${BUILD_BACKEND})"; \
    fi

# ============================================================================
# BROWSER INSTALLATION (COMMENTED OUT FOR TESTING)
# ============================================================================
# Testing Lambda parallel execution without browser complexity
# Uncomment these sections when ready to add browser support back

# # Install browser at build time (if requested)
# # Force cache invalidation when BROWSER_VERSION changes by echoing it
# RUN echo "Browser configuration: ${BROWSER_TYPE} version ${BROWSER_VERSION}"
# COPY .blazetest/scripts/install_browser.sh /tmp/
# RUN chmod +x /tmp/install_browser.sh && \
#     if [ "$INSTALL_BROWSER" = "true" ]; then \
#         /tmp/install_browser.sh ${BROWSER_TYPE} ${BROWSER_VERSION}; \
#     else \
#         echo "Skipping browser installation (INSTALL_BROWSER=false)"; \
#     fi

# # Install Selenium at build time
# # Note: webdriver-manager removed as Selenium 4.6+ has built-in Selenium Manager
# RUN pip install --no-cache-dir selenium==${SELENIUM_VERSION}

# Copy project files and dependency files
# Note: We copy everything in one layer since Docker BuildKit doesn't support
# optional wildcard COPY (files might not exist in all projects)
ADD . ${LAMBDA_TASK_ROOT}/
ADD .blazetest/tests_runner_handler ${LAMBDA_TASK_ROOT}/tests_runner_handler
COPY .blazetest/scripts/install_dependencies.sh /tmp/

# Install Python deps
RUN /usr/bin/bash /tmp/install_dependencies.sh

CMD ["tests_runner_handler.handler.run_tests"]
