FROM public.ecr.aws/lambda/python:latest


# Copy the Python Script to blink LED
ENV TZ Europe/London
ENV LAMBDA_TASK_ROOT /LambdaRoot/

RUN mkdir ${LAMBDA_TASK_ROOT}


COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"


# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]


