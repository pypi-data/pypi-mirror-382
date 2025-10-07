# OS Forge - Kubernetes Deployment

This directory contains all the Kubernetes manifests for deploying OS Forge in a production-ready environment.

## 📁 File Structure

```
k8s/
├── namespace.yaml                    # Namespace, ResourceQuota, LimitRange
├── configmap.yaml                   # Application configuration
├── secret.yaml                      # Sensitive data (secrets, RBAC)
├── persistent-volume.yaml           # Storage classes and PVCs
├── backend-deployment.yaml          # FastAPI backend deployment
├── frontend-deployment.yaml         # Next.js frontend deployment
├── service.yaml                     # Services for backend and frontend
├── ingress.yaml                     # External access and TLS termination
├── horizontal-pod-autoscaler.yaml   # Auto-scaling configuration
├── network-policy.yaml              # Network security policies
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes cluster** (v1.24+)
2. **kubectl** configured to access your cluster
3. **Docker** installed and running
4. **Docker registry** access (Docker Hub, GCR, ECR, etc.)

> **⚠️ Important**: Replace `your-registry` throughout this guide with your actual Docker registry (e.g., `docker.io/yourusername`, `gcr.io/your-project`, `your-account.dkr.ecr.region.amazonaws.com`)

### Step-by-Step Production Deployment

#### Step 1: Build and Push Docker Images

```bash
# Navigate to project root
cd /path/to/policy-guard

# Build backend image
docker build -t policy-guard-backend:latest .

# Build frontend image
docker build -t policy-guard-frontend:latest ./frontend

# Tag images for your registry (replace with your registry)
docker tag policy-guard-backend:latest your-registry/policy-guard-backend:latest
docker tag policy-guard-frontend:latest your-registry/policy-guard-frontend:latest

# Push to registry (replace with your registry)
docker push your-registry/policy-guard-backend:latest
docker push your-registry/policy-guard-frontend:latest
```

#### Step 2: Update Image References

```bash
# Update backend deployment image
sed -i 's|policy-guard-backend:latest|your-registry/policy-guard-backend:latest|g' k8s/backend-deployment.yaml

# Update frontend deployment image
sed -i 's|policy-guard-frontend:latest|your-registry/policy-guard-frontend:latest|g' k8s/frontend-deployment.yaml
```

#### Step 3: Install Required Addons (If Not Already Installed)

```bash
# Install nginx-ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager for TLS certificates
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

#### Step 4: Deploy to Production Cluster

Deploy the manifests in the following order:

```bash
# 1. Create namespace and resource quotas
kubectl apply -f k8s/namespace.yaml

# 2. Create secrets and RBAC
kubectl apply -f k8s/secret.yaml

# 3. Create configuration
kubectl apply -f k8s/configmap.yaml

# 4. Create storage
kubectl apply -f k8s/persistent-volume.yaml

# 5. Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# 6. Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# 7. Create services
kubectl apply -f k8s/service.yaml

# 8. Configure ingress
kubectl apply -f k8s/ingress.yaml

# 9. Enable auto-scaling
kubectl apply -f k8s/horizontal-pod-autoscaler.yaml

# 10. Apply network policies
kubectl apply -f k8s/network-policy.yaml
```

#### Step 5: Configure DNS (Production Only)

```bash
# Get ingress external IP
kubectl get ingress policy-guard-ingress -n policy-guard

# Update your DNS records to point to the external IP:
# policy-guard.example.com -> <EXTERNAL_IP>
# api.policy-guard.example.com -> <EXTERNAL_IP>
```

#### Step 6: Monitor Deployment

```bash
# Watch pods starting up
kubectl get pods -n policy-guard -w

# Check logs if needed
kubectl logs -l app.kubernetes.io/component=backend -n policy-guard
kubectl logs -l app.kubernetes.io/component=frontend -n policy-guard

# Check events for any issues
kubectl get events -n policy-guard --sort-by='.lastTimestamp'
```

#### Step 7: Test Application

```bash
# Get the external IP or use port-forward for testing
kubectl port-forward svc/policy-guard-frontend 3000:3000 -n policy-guard
kubectl port-forward svc/policy-guard-backend 8000:8000 -n policy-guard

# Test in browser:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n policy-guard

# Check pods status
kubectl get pods -n policy-guard

# Check services
kubectl get svc -n policy-guard

# Check ingress
kubectl get ingress -n policy-guard

# Check persistent volumes
kubectl get pv,pvc -n policy-guard

# Check horizontal pod autoscaler
kubectl get hpa -n policy-guard

# Check network policies
kubectl get networkpolicies -n policy-guard
```

## ⚡ Quick Commands for Common Tasks

```bash
# Scale deployment
kubectl scale deployment policy-guard-backend --replicas=3 -n policy-guard

# Update image
kubectl set image deployment/policy-guard-backend policy-guard-backend=your-registry/policy-guard-backend:v2.0 -n policy-guard

# View logs
kubectl logs -f deployment/policy-guard-backend -n policy-guard

# Execute into pod
kubectl exec -it deployment/policy-guard-backend -n policy-guard -- /bin/bash

# Check resource usage
kubectl top pods -n policy-guard
kubectl top nodes

# Restart deployment
kubectl rollout restart deployment/policy-guard-backend -n policy-guard

# Check rollout status
kubectl rollout status deployment/policy-guard-backend -n policy-guard

# Rollback deployment
kubectl rollout undo deployment/policy-guard-backend -n policy-guard
```

## 🔧 Configuration

### Environment Variables

The application is configured through ConfigMaps and Secrets:

**ConfigMap (`policy-guard-config`):**
- Database configuration
- API settings
- Security settings
- Feature flags

**Secret (`policy-guard-secrets`):**
- Database credentials
- API keys
- JWT secrets
- TLS certificates

### Storage

Three types of persistent storage:

1. **Database Storage** (5Gi, ReadWriteOnce)
   - SQLite database files
   - Mounted at `/app/data`

2. **Reports Storage** (2Gi, ReadWriteMany)
   - PDF and HTML reports
   - Mounted at `/app/reports`

3. **Backups Storage** (10Gi, ReadWriteOnce)
   - Database backups
   - Mounted at `/app/backups`

## 🔒 Security Features

### Network Policies
- **Default deny** all traffic
- **Selective allow** for required communication
- **Ingress controller** access
- **Monitoring** access
- **DNS resolution** allowed

### Pod Security
- **Non-root** containers
- **Read-only** root filesystem
- **Security contexts** configured
- **Capabilities** dropped

### RBAC
- **Service account** for application
- **Minimal permissions** principle
- **Role-based access** control

## 📊 Monitoring & Scaling

### Auto-scaling
- **HPA** for horizontal scaling (2-10 backend, 2-8 frontend)
- **VPA** for vertical scaling (optional)
- **CPU/Memory** based scaling
- **Custom metrics** support

### Resource Limits
- **Backend**: 100m-500m CPU, 256Mi-512Mi memory
- **Frontend**: 50m-200m CPU, 128Mi-256Mi memory
- **Storage**: 5Gi-20Gi depending on type

## 🌐 Ingress Configuration

### Domains
- **Main app**: `policy-guard.example.com`
- **API**: `api.policy-guard.example.com`
- **Internal**: `policy-guard.local`

### TLS
- **Automatic certificates** via cert-manager
- **Let's Encrypt** integration
- **Force HTTPS** redirect

### Security Headers
- **X-Frame-Options**: DENY
- **X-Content-Type-Options**: nosniff
- **X-XSS-Protection**: 1; mode=block
- **Content-Security-Policy**: Strict policy

## 🔄 Updates & Maintenance

### Rolling Updates
- **Zero-downtime** deployments
- **Rolling update** strategy
- **Pod disruption budgets**

### Health Checks
- **Liveness probes**: `/health` endpoint
- **Readiness probes**: `/ready` endpoint
- **Startup probes**: Initial health check

### Backup Strategy
- **Persistent volumes** for data
- **Database backups** automated
- **Configuration backups** via Git

## 🧹 Cleanup

### Complete Cleanup

```bash
# Delete everything
kubectl delete namespace policy-guard

# Or delete specific resources
kubectl delete -f k8s/network-policy.yaml
kubectl delete -f k8s/horizontal-pod-autoscaler.yaml
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/frontend-deployment.yaml
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/persistent-volume.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
kubectl delete -f k8s/namespace.yaml
```

### Docker Cleanup

```bash
# Remove unused Docker images
docker system prune -a --volumes -f

# Remove specific images
docker rmi policy-guard-backend:latest policy-guard-frontend:latest
```

## 🐛 Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n policy-guard
   kubectl logs <pod-name> -n policy-guard
   ```

2. **Storage issues**
   ```bash
   kubectl get pv,pvc -n policy-guard
   kubectl describe pvc <pvc-name> -n policy-guard
   ```

3. **Network connectivity**
   ```bash
   kubectl get networkpolicies -n policy-guard
   kubectl describe networkpolicy <policy-name> -n policy-guard
   ```

4. **Ingress not working**
   ```bash
   kubectl get ingress -n policy-guard
   kubectl describe ingress policy-guard-ingress -n policy-guard
   ```

### Logs
```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -n policy-guard

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend -n policy-guard

# All logs
kubectl logs -l app.kubernetes.io/name=policy-guard -n policy-guard
```

## 🚨 Production Considerations

### Before Going Live

1. **Update secrets** with production values
2. **Configure TLS certificates** properly
3. **Set up monitoring** (Prometheus/Grafana)
4. **Configure backup** strategy
5. **Test disaster recovery** procedures
6. **Review resource limits** and scaling
7. **Configure log aggregation**
8. **Set up alerting**

### Security Checklist

- [ ] All secrets updated with production values
- [ ] TLS certificates configured
- [ ] Network policies reviewed
- [ ] RBAC permissions minimized
- [ ] Pod security contexts configured
- [ ] Resource limits set appropriately
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Ingress Controller Setup](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager Setup](https://cert-manager.io/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
