# DevSecOps Learning Guide: Kubernetes & AppSec

I've analyzed your `secure-task-manager-gitops` repository. It is a fantastic starting point for learning GitOps via ArgoCD! However, when looking through a **DevSecOps** and **AppSec** lens, there are several areas in your Kubernetes configuration and Application setup that you should harden.

By addressing the issues below, you will gain hands-on experience with core DevSecOps principles.

---

> [!CAUTION]
> **High Priority: Container Execution Context**
> Currently, your `deployment.yaml` does not specify a `securityContext`. By default, Docker/Kubernetes runs containers as the `root` user unless specified otherwise. This is a critical security vulnerability. 

## 1. Hardening Kubernetes Workloads (The "OpSec" & "DevSec" part)

### A. Apply Security Contexts
Update your `deployment.yaml` to include a `securityContext` to prevent the container from gaining unnecessary privileges:
```yaml
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000  # Ensure the Dockerfile creates a non-root user with ID 1000
      containers:
        - name: secure-task-manager
          image: ezio7223/secure-task-manager:08ca273
          securityContext:
            readOnlyRootFilesystem: true  # Prevents attackers from modifying the container filesystem
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
```

### B. Shift away from `NodePort`
Your `service.yaml` exposes the application via `NodePort`. 
> [!WARNING]
> Exposing NodePorts directly to the external world is not recommended in production. It circumvents load balancing and security policies.

**Action**: Use `ClusterIP` for the Service and configure an `Ingress` controller (like NGINX or Traefik). You have an empty `ingress.yaml` file—this is the perfect place to implement it! An Ingress allows you to set up TLS (HTTPS) termination natively preventing Man-in-the-Middle (MitM) attacks.

### C. Network Policies
Currently, any pod in your Kubernetes cluster can likely talk to your `secure-task-manager` pod. 
**Action**: Create a `NetworkPolicy` to implement **Zero Trust**. Only allow traffic from your Ingress controller to port 8000 on your application pods. Deny all other internal traffic explicitly.

---

## 2. Secrets Management (GitOps Security)

You have an empty `secret.yaml`. 

> [!IMPORTANT]
> Never commit base64-encoded Kubernetes Secrets (like Database passwords or JWT Secret Keys) directly into your Git repository! ArgoCD will read them, but so can anyone else.

**Action**: Learn about Secret Management tools designed for GitOps:
1. **Sealed Secrets (Bitnami)**: You encrypt the secret locally, commit the encrypted YAML, and a controller in K8s decrypts it.
2. **External Secrets Operator**: Pulls secrets automatically from AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault directly into the Pod.

---

## 3. Application Security (AppSec)

Your application uses a hardcoded SQLite Database (`test.db`) and a hardcoded JWT secret (from the previous `auth.py` analysis). 

### A. Environment Injection
Configure your FastAPI application to read these values from Environment Variables. Then, in your K8s `deployment.yaml`, map these environment variables to the Secrets you created above:
```yaml
env:
  - name: SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: secure-task-secrets
        key: jwt-secret
```

### B. Dependency Scanning & Ephemeral File Systems
Because SQLite writes to a local file (`test.db`), setting `readOnlyRootFilesystem: true` in step 1A will break your database unless you mount an `emptyDir` or `PersistentVolumeClaim` specifically for the `/app/test.db` path. This forces you to think deliberately about where your application writes state!

---

## 4. CI/CD Security (The "DevSecOps" Pipeline)

Before the image ever reaches ArgoCD, your GitHub Actions (or CI tool) should verify its integrity.

**Action**: Add these steps to your CI pipeline:
1. **SAST (Static Application Security Testing)**: Run a tool like `Bandit` against your Python code to find vulnerabilities before the Docker image is built.
2. **Container Scanning**: Use `Trivy` or `Grype` in your CI pipeline to scan `ezio7223/secure-task-manager:08ca273` for CVEs (Common Vulnerabilities and Exposures) before pushing it to Docker Hub. Let the pipeline fail if critical vulnerabilities exist.
3. **Image Signing**: Use `Cosign` to cryptographically sign your Docker images. You can configure K8s to strictly reject images without an authentic signature.

## Summary Checklist
- [ ] Create a non-root user in your `Dockerfile` and enforce `securityContext` in `deployment.yaml`.
- [ ] Migrate `service.yaml` to `ClusterIP` and configure `ingress.yaml` with TLS.
- [ ] Setup Bitnami Sealed Secrets and inject them as environment variables.
- [ ] Implement Trivy container scanning in your GitHub Actions.
