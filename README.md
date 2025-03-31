# tool_merge

## 참고할 부분
run_tool.py에서 파일을 어떻게 s3에서 lambda로 가져오는지 부분만 참고하시면 될 것 같습니다.

## docker build

```sh
docker build -t tool_sample -f Dockerfile .
```

## test run

### local env (코드 테스트)

#### docker 빌드 후

```sh
docker run -it -v `pwd`:/mnt/ --rm --entrypoint /bin/bash --name tool_adme --cpus 8 --memory 16384m tool_sample
```

#### docker container 내에서
```sh
cd /mnt/
./test.sh
```

### lambda env (인프라 테스트)

#### docker 빌드 후

```sh
./run_local_server.sh
./invoke_local.sh
```


## AS-IS
1. input은 data, output은 results 파일에...
2. row-by-row로 합칠 수 있도록 하여야함 df merge를 이용하면 메모리 리소스 오버로딩 발생 가능성 있음
3. merge시에 각자 다른 툴에서 나온 결과는 column명의 prefix를 정형화 한다든지 하여 합쳐야 나중에 합쳐졌을 때, 어느 툴에서 나온 결과인지 확인 할 수 있음
