# CockroachDB Benchmark

## Prerequisite

- Docker
- Cockroach CLI (macos: `brew install cockroachdb/tap/cockroach`)

## Instruction

One-time configuration
```
bash cdb_bench/configure.sh
```

Example: to spin up 5 nodes
```
bash cdb_bench/cdb_start.sh 5
```

Start HAProxy
```
bash cdb_bench/haproxy_start.sh
```

Generate workload (https://www.cockroachlabs.com/docs/stable/cockroach-workload.html). Workload choices are `bank`, `intro`, `kv`, `movr`, `startrek`, `tpcc`, `yscb`.
```
WORKLOAD=yscb
cockroach workload init ${WORKLOAD} 'postgresql://root@127.0.01:26257?sslmode=disable'
cockroach workload run ${WORKLOAD} --duration=5m 'postgresql://root@127.0.01:26257?sslmode=disable'
```


To stop HAProxy
```
bash cdb_bench/haproxy_stop.sh
```

To stop those 5 nodes
```
bash cdb_bench/cdb_stop.sh 5
```

## TODOs

- [ ] Edit and select HAProxy configuration
- [ ] Select any HAProxy image (local or dockerhub)
- [ ] Add other load balancers
- [ ] Output parser for convenience
- [ ] Grand master experiment script

________________________________________________________________________________

## Development Notes

### CockroachDB-HAProxy Tutorial

Source: https://www.scaleway.com/en/docs/tutorials/setup-cockroachdb-cluster/

#### CockroachDB Cluster Setup

Install CockroachDB on each instance
```
wget -qO- https://binaries.cockroachdb.com/cockroach-latest.linux-amd64.tgz | tar  xvz
cp -i cockroach-latest.linux-amd64/cockroach /usr/local/bin
```

Create certificates
```
mkdir certs
mkdir cr-keys
cockroach cert create-ca --certs-dir=certs --ca-key=cr-keys/ca.key
cockroach cert create-client root --certs-dir=certs --ca-key=cr-keys/ca.key
```

Send certs to each node
```
cockroach cert create-node <node1 internal IP address> <node1 external IP address> <node1 public FQDN> --certs-dir=certs --ca-key=cr-keys/ca.key
ssh <username>@<node1 address> "mkdir certs"
scp certs/ca.crt certs/node.crt certs/node.key <username>@<node1 ip address>:~/certs
rm certs/node.crt certs/node.key
```

Start CockroachDB on all instances
```
cockroach start --certs-dir=certs --host=<node1 address> --join=<node1 ip address>:26257,<node2 ip address>:26257,<node3 ip address>:26257 --cache=25% --max-sql-memory=25% --background
```

Initialize cluster
```
cockroach init --certs-dir=certs --host=<address of any node>
```

Setup time synchronization
```
sudo apt-get install ntp
sudo service ntp stop

# Remove lines starting with "server" or "pool" and add:
#     server ntp.int.scaleway.com iburst
#     server ntp.ubuntu.com iburst
vim /etc/ntp.conf

sudo service ntp start
sudo ntpq -p
```

To test with sql prompt,
```
cockroach sql --certs-dir=certs --host=<address of node1>
```

#### HAProxy Deployment

Generate HAProxy configuration and send to HAProxy node
```
cockroach gen haproxy --certs-dir=certs --host=<address of the primary node> --port=26257
scp haproxy.cfg <username>@<haproxy ip address>:~/
```

```
haproxy -f haproxy.cfg
```

### Dockerized CockroachDB Tutorial

Source: https://www.cockroachlabs.com/docs/stable/start-a-local-cluster-in-docker-mac.html

Setup bridge network
```
docker network create -d bridge roachnet
```

Spin up containers
```
docker volume create roach1
docker volume create roach2
docker volume create roach3
docker run -d --name=roach1 --hostname=roach1 --net=roachnet -p 26257:26257 -p 8080:8080  -v "roach1:/cockroach/cockroach-data" --platform linux/amd64  cockroachdb/cockroach:v22.1.9 start --insecure --join=roach1,roach2,roach3
docker run -d --name=roach2 --hostname=roach2 --net=roachnet -v "roach2:/cockroach/cockroach-data" --platform linux/amd64 cockroachdb/cockroach:v22.1.9 start --insecure --join=roach1,roach2,roach3
docker run -d --name=roach3 --hostname=roach3 --net=roachnet -v "roach3:/cockroach/cockroach-data" --platform linux/amd64 cockroachdb/cockroach:v22.1.9 start --insecure --join=roach1,roach2,roach3
docker exec -it roach1 ./cockroach init --insecure
docker exec -it roach1 grep 'node starting' cockroach-data/logs/cockroach.log -A 11
```

To test with sql prompt,
```
docker exec -it roach1 ./cockroach sql --insecure

CREATE DATABASE bank;
CREATE TABLE bank.accounts (id INT PRIMARY KEY, balance DECIMAL);
INSERT INTO bank.accounts VALUES (1, 1000.50);
SELECT * FROM bank.accounts;
```

Run sample workload
```
docker exec -it roach1 ./cockroach workload init movr 'postgresql://root@roach1:26257?sslmode=disable'
docker exec -it roach1 ./cockroach workload run movr --duration=5m 'postgresql://root@roach1:26257?sslmode=disable'
```

Tear down
```
docker stop roach1 roach2 roach3
docker rm roach1 roach2 roach3
docker volume rm roach1 roach2 roach3
```

