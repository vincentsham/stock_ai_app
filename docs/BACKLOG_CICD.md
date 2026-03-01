# CI/CD Backlog

## Features
examples:
- Set up GitHub Actions for automated testing
- Create a deployment pipeline for production
- Implement semantic versioning automation
- Add linting and formatting capability to the pipeline

## Bugs
examples:
- Fix failed build on main branch
- Resolve Docker container caching issues
- Address permission issues in deployment scripts

## Technical
examples:
- Optimize build time for Docker images
- Refactor workflow files for reusability
- Secure secrets management in CI/CD

## Research
examples:
- Evaluate different CI/CD providers or runners
- Research best practices for security scanning in pipelines

## Miscellaneous
examples:
- Document the release process
- Update README with build badges

## Backlog Table

### Open Backlog Items
<div style="font-size:smaller">

| ID | Category | Description | Priority | Status | Branch | Open Date | Close Date |
|---|---|---|---|---|---|---|---|
| 10 | Technical | GitHub Actions CI/CD Pipeline | Medium | Open | - | 2026-02-20 | - |
| 11 | Technical | 10-Hour AI Agent Production Run | Critical | In-Progress | d_tech_2 | 2026-02-20 | - |
| 12 | Technical | Implement Sync Utility (Delta-Sync logic) | Critical | Open | - | 2026-02-20 | - |
</div>

### Closed Backlog Items
<div style="font-size:smaller">

| ID  | Category | Description | Priority | Status | Branch | Open Date | Close Date |
|------|----------|-------------|----------|--------|--------|------------|------------|
| 1 | Technical | Test AWS connection | High | Closed | d_tech_1 | 2026-02-19 | 2026-02-19 |
| 2 | Technical | Create S3 and Dynamo Table | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 3 | Technical | Set up VPC, Subnets, and NAT Gateway | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 4 | Technical | Provision RDS PostgreSQL Instance | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 5 | Technical | Create ECR Repositories (ETL & Web) | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 6 | Technical | Dockerize ETL Agent (Python 3.13.5) | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 7 | Technical | Sync Local Data to RDS (Migration) | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 8 | Technical | ECS Fargate Cluster & Task Definition | High | Closed | d_tech_2 | 2026-02-20 | 2026-02-21 |
| 9 | Technical | Dockerize Next.js Web App | Medium | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
| 9.1 | Technical | Deploy Web App to ECS Fargate (SG, Task Def, Secrets) | Medium | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
| 13 | Technical | Refactor Secrets to AWS Secrets Manager (Code side) | High | Closed | d_tech_3 | 2026-02-21 | 2026-02-28 |
| 13.1 | Technical | Refactor duplicated env logic into config.py | High | Closed | d_tech_3 | 2026-02-21 | 2026-02-28 |
| 15 | Technical | Provision ALB + Target Group + Listener for Web App | High | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
| 16 | Technical | Create ECS Service for Web App (Fargate, ALB-attached) | High | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
| 14 | Security | Restrict RDS SG from 0.0.0.0/0 to Task IP only | Medium | Closed | d_tech_3 | 2026-02-21 | 2026-02-28 |
| 17 | Technical | ETL dual-write to RDS + Supabase (updated 12 publish files) | High | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
| 18 | Technical | Add Supabase secret to Secrets Manager + ETL task definition | High | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
| 19 | Technical | Fix web app DB connection (SUPABASE_TRANSACTION local, PGCONNECTION_TRANSACTION AWS) | High | Closed | d_tech_3 | 2026-02-28 | 2026-02-28 |
</div>
