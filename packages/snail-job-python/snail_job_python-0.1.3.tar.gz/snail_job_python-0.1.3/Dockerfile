FROM python:3.10-alpine

WORKDIR /app

# 安装 snail-job-python 依赖
RUN pip install --no-cache-dir -v snail-job-python

# 把代码添加到工作目录
COPY example/*.py ./

CMD [ "python", "main.py" ]
