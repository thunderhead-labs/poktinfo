FROM python3
ADD . .
RUN python3 -m pip install -r ./requirements.txt
ENTRYPOINT ["python3 run_cache_service.py"]
