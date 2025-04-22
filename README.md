---

```markdown
# ENTSOE Day-Ahead Electricity Prices ETL Pipeline

This project implements a robust ETL pipeline to fetch day-ahead electricity prices from ENTSOE (European Network of Transmission System Operators for Electricity), transform the data, and store it in a PostgreSQL database. The pipeline uses Apache Airflow and is deployable locally via Docker or on Azure Kubernetes Service (AKS) with GitHub Actions for CI/CD.

---

## 🧩 Project Features

- **ETL Pipeline** with dynamic task mapping for historical and daily ingestion.
- **Dockerized Development** with easy local setup using Docker Compose.
- **Azure Deployment** via AKS + Azure File Share for DAG synchronization.
- **CI/CD** using GitHub Actions for streamlined cloud deployment.

---

## 🖥️ Local Development

### Prerequisites

- Docker & Docker Compose

### Run Locally

```bash
docker-compose up -d
```

Visit Airflow UI at [http://localhost:8080](http://localhost:8080)

---

## ☁️ Azure Deployment

### Infrastructure

- **AKS** (Azure Kubernetes Service)
- **Azure Container Registry**
- **Azure File Share** (to mount DAGs directory)

### Steps

1. GitHub Actions CI/CD handles the following:

   - Builds and pushes Docker images to Azure Container Registry (ACR)
   - Deploys to AKS using kubectl and Helm
   - Mounts Azure File Share for DAGs

2. **First Time DAG Upload**
   Make sure to create a small dummy change (like a log statement or comment) in your DAG Python file to trigger syncing on the first upload:

   ```python
   # Dummy change to ensure sync on Azure File Share mount
   print("Initial DAG sync")
   ```

3. Monitor the deployment in GitHub Actions and AKS Dashboard.

---

## 🛠️ Technologies Used

- Python
- Apache Airflow
- Docker & Docker Compose
- Azure Kubernetes Service (AKS)
- Azure File Share
- Azure Container Registry (ACR)
- PostgreSQL
- GitHub Actions (CI/CD)

---

## 📜 License

MIT License

```

---
```
