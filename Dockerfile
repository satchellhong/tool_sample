# FROM python:3.11-slim

# # Install AWS Lambda Runtime Interface Client
# RUN pip install awslambdaric

# # Set working directory
# WORKDIR /var/task

# # Copy AWS credentials
# COPY aws /root/.aws

# # Copy your application code
# COPY . .

# # Install dependencies
# RUN pip3 install pandas pyarrow boto3

# # Make sure run_tool.py is executable
# RUN chmod +x run_tool.py

# # Set up the Lambda handler
# COPY lambda_handler.py .

# # Set the CMD to the Lambda handler
# CMD [ "python", "-m", "awslambdaric", "lambda_handler.handler" ]

# # Add Lambda Runtime Interface Emulator and use it as entrypoint
# ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
# RUN chmod 755 /usr/bin/aws-lambda-rie
# ENTRYPOINT [ "/usr/bin/aws-lambda-rie" ]

FROM public.ecr.aws/lambda/python:3.11

COPY aws /root/.aws
COPY ./public/ ${LAMBDA_TASK_ROOT}/public/
COPY ./src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}
COPY run_tool.py ${LAMBDA_TASK_ROOT}

# Install the function's dependencies
RUN pip install --no-cache-dir pandas pyarrow boto3

RUN mkdir -p /tmp/data/
RUN mkdir -p /tmp/results/
RUN chmod -R 777 /tmp/data/
RUN chmod -R 777 /tmp/results/

# Set the CMD to your handler
CMD [ "lambda_handler.handler" ]