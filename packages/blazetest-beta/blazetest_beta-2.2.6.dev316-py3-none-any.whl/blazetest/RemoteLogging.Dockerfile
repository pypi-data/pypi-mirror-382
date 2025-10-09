ARG PYTHON_VERSION=3.9
FROM railflow/loki-lambda-extension:${PYTHON_VERSION} as layer

# Start with minimal AWS Lambda Python base (no browsers baked in)
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

# Build arguments for browser configuration
ARG BROWSER_TYPE=chrome
ARG BROWSER_VERSION=latest
ARG INSTALL_BROWSER=true
ARG INSTALL_ALLURE=false
ARG BUILD_BACKEND=docker
ARG SELENIUM_VERSION=4.36.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BROWSER_TYPE=${BROWSER_TYPE} \
    BROWSER_VERSION=${BROWSER_VERSION}

# Copy extension layer
COPY --from=layer /opt/ /opt/
RUN chmod +x /opt/extensions/telemetry_extension

# Install Node.js and Allure CLI conditionally (only if Allure reporting is enabled)
RUN if [ "$INSTALL_ALLURE" = "true" ]; then \
        yum install -y nodejs npm && \
        npm install -g allure-commandline --save-dev && \
        yum clean all; \
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

# Install browser at build time (if requested)
COPY .blazetest/scripts/install_browser.sh /tmp/
RUN chmod +x /tmp/install_browser.sh && \
    if [ "$INSTALL_BROWSER" = "true" ]; then \
        /tmp/install_browser.sh ${BROWSER_TYPE} ${BROWSER_VERSION}; \
    else \
        echo "Skipping browser installation (INSTALL_BROWSER=false)"; \
    fi

# Install Selenium at build time
# Note: webdriver-manager removed as Selenium 4.6+ has built-in Selenium Manager
RUN pip install --no-cache-dir selenium==${SELENIUM_VERSION}

# Copy dependency files first for better layer caching
COPY requirements.txt* pyproject.toml* poetry.lock* Pipfile* Pipfile.lock* ${LAMBDA_TASK_ROOT}/ 2>/dev/null || :
COPY .blazetest/scripts/install_dependencies.sh /tmp/

# Install Python deps (this layer will be cached if dependencies don't change)
RUN /usr/bin/bash /tmp/install_dependencies.sh

# Copy project files and tests (this layer changes frequently)
ADD . ${LAMBDA_TASK_ROOT}/
ADD .blazetest/tests_runner_handler ${LAMBDA_TASK_ROOT}/tests_runner_handler

CMD ["tests_runner_handler.handler.run_tests"]
