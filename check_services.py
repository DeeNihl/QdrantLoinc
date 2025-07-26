import docker

client = docker.from_env()

def is_container_running(name):
    try:
        container = client.containers.get(name)
        return container.status == 'running'
    except docker.errors.NotFound:
        return False

if not is_container_running('qdrant'):
    print("Starting qdrant container...")
    client.containers.run(
        'qdrant/qdrant',
        name='qdrant',
        ports={'6333/tcp': 6333},
        volumes={
            '/home/deenihl/git/ohdsi/QdrantLoinc/data': {'bind': '/qdrant/storage', 'mode': 'rw'},
        },
        detach=True
    )

if not is_container_running('ollama-medcpt'):
    print("Starting ollama-medcpt container...")
    client.containers.run(
        'deenihl/ollama-medcpt',
        name='ollama-medcpt',
        ports={'11434/tcp': 11434},
        detach=True
    )

print("All services are running.")