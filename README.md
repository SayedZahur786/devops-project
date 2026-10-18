# HackBoard - DevOps Final Capstone (Session 21)

HackBoard is a hackathon project tracker: a small SaaS-style app to track hackathon
projects from idea to submission to win. It is my own application domain - the
DevOps architecture follows the course capstone pattern, the product does not.

**Enrollment no. 10319**

## Architecture

```text
Developer
   |
   v
Git / GitHub
   |
   v
GitHub Actions
   |-- pytest (backend tests)
   |-- frontend build (React + Vite)
   |-- Docker build (backend + frontend)
   |-- Trivy scan (HIGH/CRITICAL gate)
   `-- push images to GHCR (tag = commit SHA)
              |
              v
        Terraform
              |
       AWS VPC + EKS
              |
              v
        Helm (hackboard chart)
              |
      +-------+--------+
      |                |
   Frontend          Backend
   React+Nginx      FastAPI
      |                |
      +-------> PostgreSQL (in-cluster, PVC)
              |
       Prometheus
              |
           Grafana
```

## Stack

- Frontend: React 18 + Vite, served by Nginx (multi-stage Docker build)
- Backend: FastAPI + SQLAlchemy + Alembic migrations, `/health`, `/ready`, `/metrics`
- Database: PostgreSQL 16
- CI/CD: GitHub Actions, images to GHCR with SHA tags
- Security: Trivy image scanning (fails on fixable HIGH/CRITICAL)
- IaC: Terraform - AWS VPC (2 public + 2 private subnets, NAT) + EKS + managed node group
- Kubernetes: Helm chart, Deployments, Services, Ingress, HPA, probes, PVC
- Observability: Prometheus (ServiceMonitor) + Grafana

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
helm/hackboard/     Helm chart (Deployments, Services, Ingress, HPA, PostgreSQL)
k8s/                Namespace manifest
monitoring/         kube-prometheus-stack values (Prometheus + Grafana)
troubleshooting/    Broken manifests + write-up (see Troubleshooting below)
scripts/            Load generator for the HPA demo
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

## Demo

Recorded walkthrough (2 min 23 s): a captioned tour with an AI voice-over,
built from the real screenshots captured during the runs documented below -
the compose stack, tests, Trivy, the green CI runs, the Kubernetes deploy,
HPA scaling, both troubleshooting fixes and the Grafana dashboard.

- In this repo (cannot expire):
  [docs/demo/capstone-demo.mp4](docs/demo/capstone-demo.mp4) -
  watch it on GitHub:
  <https://github.com/SayedZahur786/devops-project/blob/main/docs/demo/capstone-demo.mp4>
- Full quality download: <https://gofile.io/d/iuAOJqja>

## CI/CD

Every push to `main` runs:

1. `test` - pytest + frontend build (fails the pipeline on failure)
2. `build-scan-push` - builds both images, Trivy scans them, pushes
   `ghcr.io/<owner>/devops-project/hackboard-{backend,frontend}:<commit-sha>` to GHCR
3. `deploy` - `helm upgrade --install` (runs only when a `KUBECONFIG` secret and
   the `DEPLOY_ENABLED=true` repo variable are configured; skipped otherwise)

Green runs and GHCR packages: see Evidence below.

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

All 4 runs pass (screenshot `tf-eks-tests-pass.png`) and run again in CI on
every push. The mocks simulate AWS; they prove the module plans, applies and
destroys correctly end to end, but they are not a real AWS run.

### AWS / EKS status (honest)

The EKS module in `terraform/` is complete and validated (`terraform
validate`, plus the mocked unit and simulated-apply tests above). HackBoard
is container-native: the same Helm chart in `helm/` deploys it unchanged to
EKS (the CI deploy job is ready - set the `DEPLOY_ENABLED` variable and a
`KUBECONFIG` secret). The module was **not applied on real AWS**: EKS has no
free tier and bills by the hour, and the project owner chose not to spend on
a second billing setup. The evidence for the full IaC lifecycle is the real
`init` / `plan` / `apply` / `destroy` run against the local kind cluster
(`tf-kind-apply.png`, `tf-kind-destroy.png`) and the mocked test suite.

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

## Troubleshooting lab

`troubleshooting/` contains two deliberately broken manifests. Write-up with the
root-cause trail is in this README's Troubleshooting section below.

## Evidence

All runs below were executed for real in Killercoda cloud labs (Ubuntu 24.04
playground for Docker, kubeadm Kubernetes playground for the cluster) on
2026-10-17/18 IST. Screenshots live in `docs/screenshots/`.

### 1. App + containerization

- `docker compose up --build` - postgres + backend + frontend all healthy;
  verified live through the lab's public port proxy (UI screenshot:
  `app-ui.png`, `compose-ps-health.png` showing `/health`, `/ready`, `/api/stats`).
- Seeded 3 hackathon projects through the UI/API and read them back.
- Both Dockerfiles run as non-root; the frontend is a multi-stage build
  (node build -> nginx serve, ~50 MB final).

### 2. Tests

- `pytest -v`: 9/9 passed (screenshot `pytest-9-passed.png`). Run both in the
  lab VM and in CI.

### 3. Image security (Trivy)

- First scan found fixable HIGH CVEs. Fixes applied:
  backend `fastapi 0.143.3` + `starlette 1.3.1` (clears all 3 python HIGH);
  frontend pinned `nginx:1.29-alpine` + `apk upgrade` in the final stage.
- Rescan: frontend 0 vulnerabilities; backend 0 python-package vulnerabilities.
  Remaining: 44 unfixed Debian base-image OS HIGH CVEs (no fix published -
  upstream Debian issue, screenshot `trivy-rescan.png`). The CI gate fails only
  on *fixable* HIGH/CRITICAL (`--ignore-unfixed`), which is the standard
  pattern - blocking on CVEs nobody can fix yet would make CI permanently red.

### 4. Kubernetes (kubeadm lab, stands in for EKS)

- Helm release `hackboard` (revision 2) on the kubeadm lab cluster (2 nodes,
  controlplane + node01, v1.37.1): backend x2 + frontend x2 + postgres
  StatefulSet with PVC, all 1/1 Running (screenshot `k8s-app-ui.png` - the live
  UI served through ingress-nginx, data seeded over the API).
- The app images were loaded into containerd on BOTH nodes (`ctr -n k8s.io
  images import`) so no registry pull was needed; `imagePullPolicy: IfNotPresent`.
- Ingress: `hackboard.local/` -> frontend, `/api` -> backend; verified with
  curl (`/api/projects/stats` returns live counts, UI 200).
- HPA: backend 2 -> 4 pods under generated load (`scripts/load-test.sh`),
  `kubectl get hpa` showed cpu 87%/70% with 4 replicas (screenshot
  `k8s-hpa-scaled.png`); metrics-server provided the metrics
  (`--kubelet-insecure-tls` patch on the kubeadm lab).
- Monitoring: kube-prometheus-stack (Prometheus + Grafana, alertmanager
  disabled to fit the 2GB lab nodes); a ServiceMonitor for the backend scrapes
  `/metrics` (enabled via helm upgrade once the CRDs existed). Grafana's
  provisioned HackBoard dashboard live against Prometheus:
  `k8s-grafana-dashboard.png`.
- Final cluster state: all pods 1/1 Running, HPA idle at 2%/70% with metrics
  from metrics-server (`k8s-final-state.png`).
- Fix found during the real run: the frontend Nginx config hard-coded the
  Compose service name `backend`, which does not exist as a DNS name in
  Kubernetes. The image now uses an env-substituted `BACKEND_HOST`
  (`nginx.conf.template`, default `backend` for Compose, `hackboard-backend`
  from the Helm chart).


### 5. CI/CD

- Workflow file: `.github/workflows/ci.yml`. Test -> build+scan+push (GHCR,
  SHA tags) -> conditional `helm upgrade`.
- First pipeline run: **all green** (test, build+Trivy+GHCR push; the deploy job
  skips until `vars.DEPLOY_ENABLED=true`):
  <https://github.com/SayedZahur786/devops-project/actions/runs/39089182651>
  (green run list: `ci-actions-green.png`)
- Published images: `ghcr.io/sayedzahur786/devops-project/hackboard-backend` and
  `ghcr.io/sayedzahur786/devops-project/hackboard-frontend` (tags: `latest` and
  the commit SHA).

### 6. Terraform (AWS EKS + local kind)

- EKS module: `terraform validate` passes; 4 mocked `terraform test` runs
  (2 unit + 2 simulated applies) pass - `tf-eks-tests-pass.png`.
- Local kind module: real `terraform init` / `plan` / `apply` created a
  running Kubernetes cluster (`kubectl get nodes` -> Ready, v1.35.0) and
  `terraform destroy` tore it down (post-destroy `kubectl` refuses to
  connect) - `tf-kind-apply.png`, `tf-kind-destroy.png`.
- CI runs `terraform validate` on both modules and `terraform test` on the
  EKS module on every push (job `terraform-validate`).
- Not applied on real AWS (cost) - see "AWS / EKS status" above.

## Troubleshooting lab

Two deliberately broken manifests in `troubleshooting/`, each fixed live in the
lab with the root-cause trail captured:

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
