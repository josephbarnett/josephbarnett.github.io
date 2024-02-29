docker build --rm -t codeblind.ai/app .
docker run -p 3000:3000 --pid=host codeblind.ai/app