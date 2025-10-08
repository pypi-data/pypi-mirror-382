FROM railflow/blazetest:PYTHON_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Node.js and Allure CLI (needed for Allure report generation)
RUN yum install -y nodejs npm && \
    npm install -g allure-commandline --save-dev && \
    yum clean all

# Copy dependency files first for better layer caching
COPY requirements.txt* pyproject.toml* poetry.lock* Pipfile* Pipfile.lock* ${LAMBDA_TASK_ROOT}/ 2>/dev/null || :
COPY .blazetest/scripts/install_dependencies.sh /tmp/

# Install Python deps (this layer will be cached if dependencies don't change)
RUN /usr/bin/bash /tmp/install_dependencies.sh

# Copy project files and tests (this layer changes frequently)
ADD . ${LAMBDA_TASK_ROOT}/
ADD .blazetest/tests_runner_handler ${LAMBDA_TASK_ROOT}/tests_runner_handler

CMD ["tests_runner_handler.handler.run_tests"]
