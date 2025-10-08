# AWS Deployment Common Issues

## AWS Elastic Beanstalk

### Issue: Application Won't Start
```bash
# Check EB logs
eb logs
eb logs --all

# Common fixes
eb setenv PORT=8000
eb setenv PYTHONPATH=/opt/python/current/app
```

### Issue: Health Check Failing
```yaml
# .ebextensions/healthcheck.config
option_settings:
  aws:elasticbeanstalk:application:
    Application Healthcheck URL: /health
  aws:elasticbeanstalk:environment:process:default:
    HealthCheckPath: /health
    HealthCheckInterval: 30
    HealthCheckTimeout: 10
```

### Issue: Database Connection Refused
```bash
# Add security group rule for RDS
eb setenv DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxx
```

## AWS ECS/Fargate

### Issue: Task Fails to Start
```bash
# Check task logs
aws ecs describe-tasks --cluster my-cluster --tasks task-arn
aws logs get-log-events --log-group-name /ecs/my-app

# Common: Out of memory
# Increase task memory in task definition
```

### Issue: ALB Not Routing Traffic
```json
{
  "healthCheck": {
    "path": "/health",
    "interval": 30,
    "timeout": 5,
    "healthyThreshold": 2,
    "unhealthyThreshold": 3
  }
}
```

## AWS Lambda

### Issue: Cold Start Timeout
```python
# Increase timeout in serverless.yml
functions:
  api:
    timeout: 30
    memorySize: 1024
```

### Issue: API Gateway 502 Error
- Check Lambda function logs in CloudWatch
- Ensure response format matches API Gateway expectations
- Verify IAM permissions