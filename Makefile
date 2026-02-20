docker-super:
	./scripts/docker-super.sh

docker-super-detach:
	./scripts/docker-super.sh -d

docker-clean:
	docker compose down -v --rmi local

