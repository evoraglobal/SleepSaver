


docker run -p 9000:8080 <image name>
In a separate terminal, you can then locally invoke the function using cURL:

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"payload":"hello world!"}'