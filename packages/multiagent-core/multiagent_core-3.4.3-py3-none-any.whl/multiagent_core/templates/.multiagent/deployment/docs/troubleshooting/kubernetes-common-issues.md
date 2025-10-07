# Kubernetes Deployment Common Issues

## Pod Issues

### Issue: Pod stuck in "Pending"
```bash
# Check pod events
kubectl describe pod pod-name

# Common causes:
# - No nodes available with required resources
# - PersistentVolume not available
# - Image pull issues

# Check node resources
kubectl top nodes
kubectl describe nodes
```

### Issue: Pod keeps restarting (CrashLoopBackOff)
```bash
# Check logs
kubectl logs pod-name --previous
kubectl logs pod-name -f

# Common fixes:
# - Fix health check endpoints
# - Increase memory limits
# - Fix startup command
```

### Issue: ImagePullBackOff
```bash
# Check image name and tag
kubectl describe pod pod-name | grep Image

# For private registries, create secret
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass

# Use in deployment
imagePullSecrets:
  - name: regcred
```

## Service/Networking Issues

### Issue: Service not accessible
```bash
# Check service endpoints
kubectl get endpoints
kubectl get svc

# Test from inside cluster
kubectl run test-pod --image=busybox -it --rm -- sh
wget service-name:port

# Check if selector matches pods
kubectl get pods --show-labels
```

### Issue: Ingress not working
```bash
# Check ingress controller is installed
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress

# Common: Add annotation for nginx
annotations:
  kubernetes.io/ingress.class: nginx
```

## ConfigMap/Secret Issues

### Issue: ConfigMap changes not reflecting
```bash
# Pods don't auto-restart on ConfigMap change
# Force rolling update
kubectl rollout restart deployment/my-app

# Or add annotation to force update
kubectl patch deployment my-app -p \
  '{"spec":{"template":{"metadata":{"annotations":{"date":"'$(date)'"}}}}}'
```

### Issue: Secret not mounting
```yaml
# Correct volume mount
volumes:
  - name: secret-volume
    secret:
      secretName: my-secret
volumeMounts:
  - name: secret-volume
    mountPath: /etc/secrets
    readOnly: true
```

## Resource Issues

### Issue: OOMKilled (Out of Memory)
```yaml
# Increase memory limits
resources:
  requests:
    memory: "256Mi"
  limits:
    memory: "512Mi"  # Increase this
```

### Issue: CPU Throttling
```yaml
# Adjust CPU limits
resources:
  requests:
    cpu: "100m"
  limits:
    cpu: "500m"  # Be generous with CPU limits
```

## Storage Issues

### Issue: PersistentVolume not binding
```bash
# Check PV and PVC
kubectl get pv
kubectl get pvc

# Common: StorageClass mismatch
kubectl get storageclass
```

### Issue: Read-only filesystem
```yaml
# Make sure not mounting as read-only
volumeMounts:
  - name: data
    mountPath: /data
    readOnly: false  # Or remove this line
```

## Debugging Commands

```bash
# Get all resources in namespace
kubectl get all -n my-namespace

# Describe everything about a pod
kubectl describe pod pod-name

# Get pod YAML
kubectl get pod pod-name -o yaml

# Execute commands in pod
kubectl exec -it pod-name -- /bin/bash

# Port forward for debugging
kubectl port-forward pod-name 8080:8080

# Check cluster events
kubectl get events --sort-by='.lastTimestamp'

# Debug networking
kubectl run debug --image=nicolaka/netshoot -it --rm

# Check resource usage
kubectl top pods
kubectl top nodes
```

## Helm Issues

### Issue: Helm upgrade fails
```bash
# Rollback
helm rollback my-release

# Force upgrade
helm upgrade my-release ./chart --force

# Delete and reinstall
helm delete my-release
helm install my-release ./chart
```

### Issue: Values not overriding
```bash
# Check computed values
helm get values my-release
helm install my-release ./chart --dry-run --debug
```

## Quick Fixes

### Force pod restart
```bash
kubectl delete pod pod-name
# Or scale down and up
kubectl scale deployment my-app --replicas=0
kubectl scale deployment my-app --replicas=3
```

### Emergency access
```bash
# If app broken, run debug container
kubectl debug pod-name -it --image=busybox
```

### Clean up evicted pods
```bash
kubectl delete pods --field-selector status.phase=Failed
```