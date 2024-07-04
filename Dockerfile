# 
FROM python:3.9

# 
WORKDIR /authentication-service

# 
COPY ./requirements.txt /authentication-service/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /authentication-service/requirements.txt

# 
COPY ./app /authentication-service/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "3000"]