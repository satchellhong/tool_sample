# test docker run
docker run -p 18000:8080 -e _HANDLER=lambda_handler.handler -v `pwd`/src/:/var/task/src/ --rm --name tool_merge 473130344367.dkr.ecr.ap-northeast-2.amazonaws.com/tool_merge
