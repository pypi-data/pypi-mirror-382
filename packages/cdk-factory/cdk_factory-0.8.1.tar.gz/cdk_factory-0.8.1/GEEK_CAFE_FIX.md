# Fix for geek-cafe Cognito Error

## The Problem

```
ValueError: User pool ID is required for API Gateway authorizer.
```

Your API Gateway stack can't find the Cognito User Pool because the new separated pattern requires **SSM imports** instead of environment variables.

## Quick Fix

In your `/Users/eric.wilson/Projects/geek-cafe/geek-cafe-web/geek-cafe-lambdas/cdk` config:

### Option 1: Add SSM Import (Recommended)

**api-gateway-stack.json:**
```json
{
  "name": "geek-cafe-prod-api-gateway",
  "module": "api_gateway_stack",
  "api_gateway": {
    "name": "geek-cafe-prod-api",
    "api_type": "REST",
    "stage_name": "prod",
    "ssm": {
      "enabled": true,
      "auto_export": true,
      "workload": "geek-cafe",
      "environment": "prod",
      "imports": {
        "workload": "geek-cafe",
        "environment": "prod",
        "user_pool_arn": "auto"  // ✅ ADD THIS - imports from Cognito stack
      }
    },
    "cognito_authorizer": {
      "authorizer_name": "geek-cafe-cognito-authorizer"
    },
    "routes": [...]
  }
}
```

This assumes your Cognito stack is configured to export:
```json
{
  "name": "geek-cafe-prod-cognito",
  "module": "cognito_stack",
  "ssm": {
    "enabled": true,
    "auto_export": true,  // ✅ Must be enabled
    "workload": "geek-cafe",
    "environment": "prod"
  }
}
```

### Option 2: Use Explicit SSM Path

If auto-discovery doesn't work, find the exact SSM parameter:

```bash
# Find the parameter
aws ssm get-parameters-by-path --path "/geek-cafe/prod/cognito" --recursive
```

Then use the explicit path:
```json
{
  "api_gateway": {
    "ssm": {
      "imports": {
        "user_pool_arn": "/geek-cafe/prod/cognito/user-pool/user-pool-arn"
      }
    }
  }
}
```

### Option 3: Direct ARN (Quick Temporary Fix)

If you just need to deploy NOW and fix properly later:

```json
{
  "api_gateway": {
    "cognito_authorizer": {
      "authorizer_name": "geek-cafe-authorizer",
      "user_pool_arn": "arn:aws:cognito-idp:us-east-1:ACCOUNT_ID:userpool/us-east-1_XXXXX"
    }
  }
}
```

Get the ARN from AWS Console → Cognito → User Pools → geek-cafe-prod → ARN

## Deployment Order

With the new pattern, deploy in this order:

```bash
# 1. Deploy Cognito (if separate stack)
cdk deploy geek-cafe-prod-cognito

# 2. Deploy Lambdas
cdk deploy geek-cafe-prod-lambdas

# 3. Deploy API Gateway (imports from both above)
cdk deploy geek-cafe-prod-api-gateway
```

Or set up a pipeline with stages:
```json
{
  "pipeline": {
    "stages": [
      {"name": "infrastructure", "stacks": ["cognito-stack"]},
      {"name": "lambdas", "stacks": ["lambda-stack"]},
      {"name": "api-gateway", "stacks": ["api-gateway-stack"]}
    ]
  }
}
```

## Verify SSM Parameters Exist

```bash
# Check what Cognito exported
aws ssm get-parameter --name "/geek-cafe/prod/cognito/user-pool/user-pool-arn"

# Check what Lambda exported
aws ssm get-parameters-by-path --path "/geek-cafe/prod/lambda" --recursive

# Check what API Gateway exported
aws ssm get-parameters-by-path --path "/geek-cafe/prod/api-gateway" --recursive
```

## Complete Example Config

**cognito-stack.json:**
```json
{
  "name": "geek-cafe-prod-cognito",
  "module": "cognito_stack",
  "ssm": {
    "enabled": true,
    "auto_export": true,
    "workload": "geek-cafe",
    "environment": "prod"
  },
  "cognito": {
    "user_pool_name": "geek-cafe-prod",
    "exists": false
  }
}
```

**lambda-stack.json:**
```json
{
  "name": "geek-cafe-prod-lambdas",
  "module": "lambda_stack",
  "ssm": {
    "enabled": true,
    "workload": "geek-cafe",
    "environment": "prod"
  },
  "resources": [
    {
      "name": "geek-cafe-prod-get-cafes",
      "src": "./src/handlers/cafes",
      "handler": "get_cafes.lambda_handler"
    }
  ]
}
```

**api-gateway-stack.json:**
```json
{
  "name": "geek-cafe-prod-api-gateway",
  "module": "api_gateway_stack",
  "api_gateway": {
    "name": "geek-cafe-prod-api",
    "api_type": "REST",
    "stage_name": "prod",
    "ssm": {
      "enabled": true,
      "auto_export": true,
      "workload": "geek-cafe",
      "environment": "prod",
      "imports": {
        "workload": "geek-cafe",
        "environment": "prod",
        "user_pool_arn": "auto"  // ✅ This is the key fix
      }
    },
    "cognito_authorizer": {
      "authorizer_name": "geek-cafe-cognito-authorizer"
    },
    "routes": [
      {
        "path": "/cafes",
        "method": "GET",
        "lambda_name": "geek-cafe-prod-get-cafes",
        "authorization_type": "COGNITO_USER_POOLS"
      }
    ]
  }
}
```

## Summary of Changes

| Old Pattern (Combined) | New Pattern (Separated) |
|------------------------|-------------------------|
| `COGNITO_USER_POOL_ID` env var | SSM import with `user_pool_arn: "auto"` |
| Single stack with Lambda + API | Three stacks: Cognito → Lambda → API Gateway |
| Environment vars in CI/CD | Config-driven SSM parameters |
| `"exports": {"enabled": true}` ❌ | `"auto_export": true` ✅ |

## If Still Having Issues

1. **Check CDK Factory version:**
   ```bash
   pip show cdk-factory
   # Should be v0.8.0 or higher
   ```

2. **Enable debug logging:**
   ```bash
   export LOG_LEVEL=DEBUG
   cdk deploy
   ```

3. **Verify workload/environment match** in all three stacks

4. **Check SSM permissions** in your deployment role

5. **Use explicit path** as fallback if auto-discovery fails
