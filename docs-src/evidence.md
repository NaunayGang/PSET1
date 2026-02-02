---
title: Evidence & Proof of Functionality
date: 2026-02-01
---

# Evidence & Proof of Functionality

## Docker Build Success

```bash
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose up --build
```

![Docker Build Process](resources/images/docker.png)

## Test Suite Results

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```
![Test Execution Results](resources/images/tests.png)

## Parquet Functionality

![Parquet Upload](resources/images/parquet1.png)

![Uploaded zones](resources/images/parquet2.png)