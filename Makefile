build:
	docker build -t  retrieve_names .
bash:
	docker run -it -p 5010:5010 --rm --name retrieve_names retrieve_names bash 
interactive:
	docker run -it -p 5010:5010 --rm --name retrieve_names retrieve_names sh /retrieve_names/run_server.sh
server:
	docker run -itd -p 5010:5010 --rm --name retrieve_names retrieve_names sh /retrieve_names/run_server.sh
