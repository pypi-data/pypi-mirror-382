FROM railflow/loki-lambda-extension:PYTHON_VERSION as layer

# Start with minimal AWS Lambda Python base (no browsers baked in)
FROM public.ecr.aws/lambda/python:PYTHON_VERSION

# Build arguments for browser configuration
ARG BROWSER_TYPE=chrome
ARG BROWSER_VERSION=latest
ARG INSTALL_BROWSER=true

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BROWSER_TYPE=${BROWSER_TYPE} \
    BROWSER_VERSION=${BROWSER_VERSION}

# Copy extension layer
COPY --from=layer /opt/ /opt/
RUN chmod +x /opt/extensions/telemetry_extension

# Install Node.js and Allure CLI (needed for Allure report generation)
RUN yum install -y nodejs npm && \
    npm install -g allure-commandline --save-dev && \
    yum clean all

# Install browser at build time (if requested)
COPY .blazetest/scripts/install_browser.sh /tmp/
RUN chmod +x /tmp/install_browser.sh && \
    if [ "$INSTALL_BROWSER" = "true" ]; then \
        /tmp/install_browser.sh ${BROWSER_TYPE} ${BROWSER_VERSION}; \
    else \
        echo "Skipping browser installation (INSTALL_BROWSER=false)"; \
    fi

# Install Selenium and WebDriver Manager at build time (not baked in)
RUN pip install --no-cache-dir selenium==4.16.0 webdriver-manager==4.0.1

# Copy dependency files first for better layer caching
COPY requirements.txt* pyproject.toml* poetry.lock* Pipfile* Pipfile.lock* ${LAMBDA_TASK_ROOT}/ 2>/dev/null || :
COPY .blazetest/scripts/install_dependencies.sh /tmp/

# Install Python deps (this layer will be cached if dependencies don't change)
RUN /usr/bin/bash /tmp/install_dependencies.sh

# Copy project files and tests (this layer changes frequently)
ADD . ${LAMBDA_TASK_ROOT}/
ADD .blazetest/tests_runner_handler ${LAMBDA_TASK_ROOT}/tests_runner_handler

CMD ["tests_runner_handler.handler.run_tests"]
