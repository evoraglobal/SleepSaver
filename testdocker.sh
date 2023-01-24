


docker run --rm --name SLEEPSAVER -d -p 9000:8080  -e REGIONLIST=eu-west-2 -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e  AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN      sleepsaver

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"event":"STOP"}'