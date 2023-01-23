aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 307494535005.dkr.ecr.eu-west-2.amazonaws.com

docker tag sleepsaver:latest 307494535005.dkr.ecr.eu-west-2.amazonaws.com/sleepsaver:latest
docker push 307494535005.dkr.ecr.eu-west-2.amazonaws.com/sleepsaver:latest