echo Building the backend...
docker build --rm -t backend backend/
echo Building the corenlp server...
docker build --rm -t corenlp corenlp/
echo Building the frontend...
docker build --rm -t frontend frontend/
echo Done!
