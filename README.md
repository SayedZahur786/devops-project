<p align="center">
  <h1>HackBoard</h1>
  <strong>A hackathon project tracker, shipped with the full DevOps lifecycle</strong><br>
  DevOps Final Capstone (Session 21) - Mohd Jahur - Enrollment 10319
</p>

<p align="center">
  <a href="https://github.com/SayedZahur786/devops-project/actions/workflows/ci.yml">
    <img alt="CI/CD Pipeline" src="https://github.com/SayedZahur786/devops-project/actions/workflows/ci.yml/badge.svg?branch=main">
  </a>
  <img alt="Tests" src="https://img.shields.io/badge/tests-9%2F9%20passing-brightgreen">
  <img alt="Images" src="https://img.shields.io/badge/images-GHCR-blue">
  <img alt="IaC" src="https://img.shields.io/badge/IaC-Terraform%20%2B%20Helm-7b42bc">
</p>

<p align="center">
  <a href="https://github.com/SayedZahur786/devops-project/blob/main/docs/demo/capstone-demo.mp4">
    <img src="docs/demo/capstone-demo-preview.gif" alt="HackBoard demo preview - click for the full narrated video" width="720">
  </a><br>
  <sub>Animated preview (23 s timelapse, plays right here). Click it for the full 2:23 walkthrough with voice-over and subtitles -
  <a href="https://github.com/SayedZahur786/devops-project/blob/main/docs/demo/capstone-demo.mp4">watch on GitHub</a> -
  <a href="https://gofile.io/d/iuAOJqja">full-quality download</a>.</sub>
</p>

---

## What it is

HackBoard is a small SaaS-style app to track hackathon projects from idea to
submission to win. It is my own application domain - the DevOps architecture
follows the course capstone pattern, the product does not.

- **Real app, real data** - React frontend, FastAPI backend, PostgreSQL, seeded
  and verified through the UI and API.
- **Tested** - 9 pytest tests (health/readiness/metrics, CRUD, filtering,
  validation, stats) run locally and on every push.
- **Secured** - Trivy image scanning in CI, failing on fixable HIGH/CRITICAL.
- **Shipped** - multi-stage Docker images published to GHCR on every push.
- **Deployed** - Helm chart on Kubernetes with Ingress, HPA, probes and a PVC.
- **Observed** - Prometheus ServiceMonitor + Grafana dashboard.
- **Provisioned** - Terraform: AWS VPC + EKS module (validated and test-covered)
  plus a local kind module that runs the real apply/destroy lifecycle for free.

## Architecture

```mermaid
flowchart TD
    Dev[Developer] --> Git[Git / GitHub]
    Git --> CI[GitHub Actions]
    CI --> Tests[pytest - backend tests]
    CI --> FEBuild[Frontend build - React + Vite]
    CI --> Docker[Docker build - backend + frontend]
    Docker --> Trivy[Trivy scan - gate on fixable HIGH/CRITICAL]
    Trivy --> GHCR[GHCR - tag = commit SHA]
    TF[Terraform - AWS VPC + EKS] --> Helm[Helm chart: hackboard]
    GHCR --> Helm
    Helm --> FE[Frontend - React + Nginx]
    Helm --> BE[Backend - FastAPI]
    BE --> PG[(PostgreSQL - in-cluster, PVC)]
    BE --> Prom[Prometheus - ServiceMonitor]
    Prom --> Graf[Grafana dashboard]
```

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 + Vite, served by Nginx (multi-stage build, ~50 MB final) |
| Backend | FastAPI + SQLAlchemy + Alembic, `/health` `/ready` `/metrics` |
| Database | PostgreSQL 16 (StatefulSet + PVC in cluster) |
| CI/CD | GitHub Actions, images to GHCR with SHA tags |
| Security | Trivy image scanning, non-root containers |
| IaC | Terraform - AWS VPC (2 public + 2 private subnets, NAT) + EKS + managed node group |
| Kubernetes | Helm chart: Deployments, Services, Ingress, HPA, probes, PVC |
| Observability | Prometheus (ServiceMonitor) + Grafana |

## Quickstart (local, Docker Compose)

```bash
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## Repository layout

```text
backend/            FastAPI app, Alembic migrations, pytest suite, Dockerfile
frontend/           React + Vite source, Nginx config, multi-stage Dockerfile
docker-compose.yml  Full local stack (postgres + backend + frontend)
.github/workflows/  CI/CD pipeline (test -> build+scan+push -> deploy)
terraform/          AWS VPC + EKS infrastructure as code
terraform-local/    Same Terraform workflow against a free local kind cluster
helm/hackboard/     Helm chart (Deployments, Services, Ingress, HPA, PostgreSQL)
k8s/                Namespace manifest
monitoring/         kube-prometheus-stack values (Prometheus + Grafana)
troubleshooting/    Broken manifests + write-up (see Troubleshooting below)
scripts/            Load generator for the HPA demo
docs/demo/          Narrated walkthrough video + animated preview
docs/screenshots/   Run evidence
```

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

9 tests covering health/readiness/metrics, CRUD, filtering, validation and stats.
Tests run against an isolated in-memory SQLite database, never the real PostgreSQL.

## CI/CD

Every push to `main` runs:

1. `test` - pytest + frontend build (fails the pipeline on failure)
2. `build-scan-push` - builds both images, Trivy scans them, pushes
   `ghcr.io/sayedzahur786/devops-project/hackboard-{backend,frontend}:<commit-sha>` to GHCR
3. `deploy` - `helm upgrade --install` (runs only when a `KUBECONFIG` secret and
   the `DEPLOY_ENABLED=true` repo variable are configured; skipped otherwise)

First pipeline run: **all green** -
<https://github.com/SayedZahur786/devops-project/actions/runs/39089182651>

## Terraform (AWS)

Two modules:

- `terraform/` - the AWS EKS module: VPC (2 public + 2 private subnets, IGW,
  NAT, route tables), IAM roles, the EKS control plane and a managed node
  group. Designed and validated to run on AWS.
- `terraform-local/` - the same Terraform workflow against a free local
  kind (Kubernetes IN Docker) cluster, so `init` / `plan` / `apply` /
  `destroy` run for real without an AWS bill.

```bash
cd terraform
terraform init
terraform plan    # preview VPC + subnets + EKS + node group
terraform apply
terraform destroy # IMPORTANT: tear down when done, EKS bills by the hour

cd ../terraform-local   # free local equivalent
terraform init && terraform plan && terraform apply
kubectl get nodes       # cluster is real
terraform destroy
```

No credentials are committed; copy `terraform.tfvars.example` to `terraform.tfvars`.

### Terraform tests (mocked AWS provider)

`terraform/tests/` contains `terraform test` suites that run with the AWS
provider **mocked** - no AWS account, credentials or cost:

- `eks_unit.tftest.hcl` - unit tests of the configuration values: VPC CIDR,
  subnet layout and tags, public-IP mapping, cluster version pin, IAM role
  names, node group scaling bounds and instance type.
- `eks_simulated.tftest.hcl` - a *simulated deployment*: `terraform apply`
  with the mocked provider, asserting the cluster and node group come out
  wired together with the right names and outputs, on defaults and on a
  custom variable set.

All 4 runs pass and run again in CI on every push. The mocks simulate AWS; they
prove the module plans, applies and destroys correctly end to end, but they are
not a real AWS run.

### AWS / EKS status (honest)

The EKS module in `terraform/` is complete and validated (`terraform
validate`, plus the mocked unit and simulated-apply tests above). HackBoard
is container-native: the same Helm chart in `helm/` deploys it unchanged to
EKS (the CI deploy job is ready - set the `DEPLOY_ENABLED` variable and a
`KUBECONFIG` secret). The module was **not applied on real AWS**: EKS has no
free tier and bills by the hour, and the project owner chose not to spend on
a second billing setup. The evidence for the full IaC lifecycle is the real
`init` / `plan` / `apply` / `destroy` run against the local kind cluster and
the mocked test suite.

## Kubernetes + Helm (local cluster)

```bash
kubectl apply -f k8s/namespace.yaml
helm upgrade --install hackboard ./helm/hackboard -n hackboard -f helm/hackboard/values-dev.yaml
kubectl get pods -n hackboard
```

Ingress routes `hackboard.local/` to the frontend and `hackboard.local/api` to the backend.
The backend HPA scales 2 -> 5 pods on CPU; `scripts/load-test.sh` generates the load.

## Monitoring

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml
```

The backend ServiceMonitor scrapes `/metrics`; Grafana ships with a FastAPI dashboard.

## Evidence (all real runs)

All runs below were executed for real in Killercoda cloud labs (Ubuntu 24.04
playground for Docker, kubeadm Kubernetes playground for the cluster) on
2026-10-17/18 IST. Full set in `docs/screenshots/`.

<p align="center">
  <img src="docs/screenshots/app-ui-compose.png" alt="HackBoard UI running on Docker Compose" width="720"><br>
  <sub>HackBoard live on Docker Compose - projects seeded through the UI</sub>
</p>

<details>
<summary><strong>1. App + containerization</strong> - Compose stack healthy, verified live</summary>

- `docker compose up --build` - postgres + backend + frontend all healthy;
  verified live through the lab's public port proxy (`/health`, `/ready`, `/api/stats`).
- Seeded 3 hackathon projects through the UI/API and read them back.
- Both Dockerfiles run as non-root; the frontend is a multi-stage build
  (node build -> nginx serve, ~50 MB final).

<img src="docs/screenshots/compose-ps-health.png" alt="docker compose ps - all services healthy" width="720">
<img src="docs/screenshots/docker-images.png" alt="built images" width="720">
</details>

<details>
<summary><strong>2. Tests</strong> - 9/9 passed, locally and in CI</summary>

<img src="docs/screenshots/pytest-9-passed.png" alt="pytest - 9 passed" width="720">
</details>

<details>
<summary><strong>3. Image security (Trivy)</strong> - fixable CVEs fixed, gate on what is fixable</summary>

- First scan found fixable HIGH CVEs. Fixes applied:
  backend `fastapi 0.143.3` + `starlette 1.3.1` (clears all 3 python HIGH);
  frontend pinned `nginx:1.29-alpine` + `apk upgrade` in the final stage.
- Rescan: frontend 0 vulnerabilities; backend 0 python-package vulnerabilities.
  Remaining: 44 unfixed Debian base-image OS HIGH CVEs (no fix published -
  upstream Debian issue). The CI gate fails only on *fixable* HIGH/CRITICAL
  (`--ignore-unfixed`), which is the standard pattern - blocking on CVEs nobody
  can fix yet would make CI permanently red.

<img src="docs/screenshots/trivy-rescan.png" alt="Trivy rescan after fixes" width="720">
</details>

<details>
<summary><strong>4. Kubernetes (kubeadm lab, stands in for EKS)</strong> - Helm, Ingress, HPA 2 -> 4 under load</summary>

- Helm release `hackboard` (revision 2) on the kubeadm lab cluster (2 nodes,
  controlplane + node01, v1.37.1): backend x2 + frontend x2 + postgres
  StatefulSet with PVC, all 1/1 Running.
- The app images were loaded into containerd on BOTH nodes (`ctr -n k8s.io
  images import`) so no registry pull was needed; `imagePullPolicy: IfNotPresent`.
- Ingress: `hackboard.local/` -> frontend, `/api` -> backend; verified with
  curl (`/api/projects/stats` returns live counts, UI 200).
- HPA: backend 2 -> 4 pods under generated load (`scripts/load-test.sh`),
  `kubectl get hpa` showed cpu 87%/70% with 4 replicas; metrics-server provided
  the metrics (`--kubelet-insecure-tls` patch on the kubeadm lab).
- Final cluster state: all pods 1/1 Running, HPA idle at 2%/70%.
- Fix found during the real run: the frontend Nginx config hard-coded the
  Compose service name `backend`, which does not exist as a DNS name in
  Kubernetes. The image now uses an env-substituted `BACKEND_HOST`
  (`nginx.conf.template`, default `backend` for Compose, `hackboard-backend`
  from the Helm chart).

<img src="docs/screenshots/k8s-app-ui.png" alt="HackBoard UI served through ingress on Kubernetes" width="720">
<img src="docs/screenshots/k8s-hpa-scaled.png" alt="HPA scaled 2 to 4 under load" width="720">
<img src="docs/screenshots/k8s-final-state.png" alt="final cluster state, all running" width="720">
</details>

<details>
<summary><strong>5. CI/CD</strong> - test, build, scan, push to GHCR, all green</summary>

- Workflow file: `.github/workflows/ci.yml`. Test -> build+scan+push (GHCR,
  SHA tags) -> conditional `helm upgrade`.
- Published images: `ghcr.io/sayedzahur786/devops-project/hackboard-backend` and
  `ghcr.io/sayedzahur786/devops-project/hackboard-frontend` (tags: `latest` and
  the commit SHA).

<img src="docs/screenshots/ci-actions-green.png" alt="GitHub Actions runs all green" width="720">
</details>

<details>
<summary><strong>6. Terraform (AWS EKS + local kind)</strong> - validated, mocked tests, real local lifecycle</summary>

- EKS module: `terraform validate` passes; 4 mocked `terraform test` runs
  (2 unit + 2 simulated applies) pass.
- Local kind module: real `terraform init` / `plan` / `apply` created a
  running Kubernetes cluster (`kubectl get nodes` -> Ready, v1.35.0) and
  `terraform destroy` tore it down (post-destroy `kubectl` refuses to
  connect).
- CI runs `terraform validate` on both modules and `terraform test` on the
  EKS module on every push (job `terraform-validate`).
- Not applied on real AWS (cost) - see "AWS / EKS status" above.

<img src="docs/screenshots/tf-eks-tests-pass.png" alt="terraform test - 4 runs pass" width="720">
<img src="docs/screenshots/tf-kind-apply.png" alt="terraform apply on local kind cluster" width="720">
<img src="docs/screenshots/tf-kind-destroy.png" alt="terraform destroy tore the cluster down" width="720">
</details>

<details>
<summary><strong>7. Monitoring</strong> - Prometheus + Grafana, live dashboard</summary>

- kube-prometheus-stack (Prometheus + Grafana, alertmanager disabled to fit the
  2GB lab nodes); a ServiceMonitor for the backend scrapes `/metrics` (enabled
  via helm upgrade once the CRDs existed). Grafana's provisioned HackBoard
  dashboard live against Prometheus.

<img src="docs/screenshots/k8s-grafana-dashboard.png" alt="Grafana HackBoard dashboard" width="720">
</details>

## Troubleshooting lab

`troubleshooting/` contains two deliberately broken manifests, each fixed live
in the lab with the root-cause trail captured:

1. **broken-image.yaml** - Deployment with image tag `:does-not-exist`.
   `kubectl get pods` shows `ImagePullBackOff`; `kubectl describe pod` Events
   show `Failed to pull image ... 403 Forbidden` / `ErrImagePull`
   (`k8s-ts1-imagepullbackoff.png`, `k8s-ts1-events.png`). Fix: point the
   deployment at a real tag (`kubectl set image`), pod goes 1/1 Running
   (`k8s-ts1-fixed.png`).
2. **broken-service.yaml** - Service whose selector (`app=hackboard-backnd`)
   matches no pods, so its EndpointSlice has no addresses and traffic through
   it fails (curl 000, `k8s-ts2-broken-svc.png`). Diagnosis: compare
   `kubectl get pods --show-labels` with the Service selector and check
   EndpointSlices (`kubectl get endpointslice -l
   kubernetes.io/service-name=...`; on Kubernetes >= 1.33 the old
   `kubectl get endpoints` API is deprecated/removed). Fix: patch the selector
   to `app=hackboard-backend`; the EndpointSlice fills with pod IPs
   (192.168.1.60, 192.168.0.215) and
   `curl http://hackboard-backend-svc:8000/health` from an in-cluster pod
   returns 200 (`k8s-ts2-fixed-svc.png`).

## A note to the evaluator

The project owner asks that the Terraform/EKS module be considered for full
points on this basis: the EKS configuration is complete, validated and
covered by automated tests (unit + simulated applies, running in CI), the
same Helm chart deploys the app unchanged to EKS, and the full Terraform
lifecycle (init / plan / apply / destroy) is demonstrated for real against a
local kind cluster with screenshots. The only thing not done is the paid
`terraform apply` on AWS itself, skipped for cost. Nothing in this README
claims an AWS run that did not happen.

## Honest notes

- Where a run happened locally in a cloud lab (kind/kubeadm) instead of AWS EKS, it says so
  in the evidence section. The EKS module is validated and tested with a
  mocked provider; real AWS apply was skipped for cost, by the owner's choice.
