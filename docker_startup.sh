port=${1:-14827}

docker run -it \
-v $(pwd):/workspace \
-p $port:8501 \
--restart unless-stopped \
--name self_trpg \
python:3.10.13-slim \
bash -c "cd workspace && ./startup.sh"