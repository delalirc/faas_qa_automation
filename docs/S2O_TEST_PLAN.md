# Statement-to-Offer (S2O) Test Plan

**Version:** 1.0  
**Last Updated:** 2025-03-18  
**Scope:** faas_s2o_orchestrator, faas_doc2data, faas_truid, faas_spike  
**Target Environment:** UAT

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture & Flow](#2-architecture--flow)
3. [Test Scope](#3-test-scope)
4. [Prerequisites & Assumptions](#4-prerequisites--assumptions)
5. [Test Data Requirements](#5-test-data-requirements)
6. [Test Cases](#6-test-cases)
7. [Execution Strategy](#7-execution-strategy)
8. [Environment Configuration](#8-environment-configuration)

---

## 1. Overview

### 1.1 Purpose

This test plan defines comprehensive QA testing for the Statement-to-Offer (S2O) journey—a multi-service flow that processes bank statements and other documents to generate financial offers. Testing covers both **positive flows** (happy path) and **negative flows** (error handling, edge cases).

### 1.2 Services Under Test

| Service | Role | UAT Base URL | Key Responsibilities |
|---------|------|--------------|----------------------|
| **faas_s2o_orchestrator** | Orchestration | `https://uat.api.rcdevops.co.za/orchestrator` | Session lifecycle, presigned URLs, document registration, status tracking, webhook handling |
| **faas_doc2data** | Document Routing | `https://uat.api.rcdevops.co.za/doc2data` | Document ingestion, OCR orchestration, S3 events, callback invocation |
| **faas_truid** | OCR (Identity/Docs) | Lambda (invoked by doc2data) | TruID Connect OCR—document verification, extraction for ID/company docs |
| **faas_spike** | OCR (Statements) | Lambda (invoked by doc2data) | Spike Statements API—bank statement extraction |

### 1.3 S2O Journey Flow Summary

```
Client → POST /sessions (Orchestrator)
       → POST /documents/{session_id}/presigned-url (Orchestrator)
       → PUT [presigned URL] (S3 upload via boto3/requests)
       → POST /documents/{session_id} (Orchestrator - register documents)
       → [Async] S3 event → Doc2Data → TruID/Spike Lambda (provider_name)
       → [Async] Doc2Data webhook → Orchestrator
       → [Async] Databricks webhook → Orchestrator
       → [Async] Offer webhook → Orchestrator
       → Client GET /sessions/{session_id}/status (poll)
       → Client GET /sessions/{session_id}/offer (retrieve offer)
```

---

## 2. Architecture & Flow

### 2.1 Service Dependencies

```
                    ┌─────────────────┐
                    │     Client      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────────────────────┐
                    │   faas_s2o_orchestrator          │
                    │   - Sessions                     │
                    │   - Presigned URLs               │
                    │   - Document Registration       │
                    │   - Webhooks (Doc2Data, Databricks, Offer) │
                    └────────┬─────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────────┐   ┌──────────────┐
        │   S3     │   │ faas_doc2data│   │  Databricks   │
        └────┬─────┘   └──────┬───────┘   │  (External)   │
             │                │           └───────────────┘
             │                │
             │                ├─────────────────┬─────────────────┐
             │                ▼                 ▼                 │
             │         ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
             └────────►│ faas_truid   │   │ faas_spike  │   │  Databricks  │
                       │ (provider:   │   │ (provider:  │   │ Offer Engine │
                       │  truid)      │   │  spike)     │   |  (External)  |
                       └─────────────┘    └─────────────┘   └──────────────┘ 
```

### 2.2 Session State Lifecycle

| State | Description |
|-------|-------------|
| `CREATED` | Session created, no documents |
| `IN_PROGRESS` | Documents uploaded, OCR in progress |
| `EVALUATING` | All OCR succeeded, Databricks evaluating |
| `EVALUATING_PARTIAL` | Some OCR failed, evaluating with partial data |
| `FAILED` | All OCR failed or invalid Databricks outcome |
| `APPROVED` | Databricks approved |
| `REJECTED` | Databricks rejected |
| `OFFER_GENERATED` | Offer received and available |

---

## 3. Test Scope

### 3.1 In Scope

- End-to-end S2O journey (orchestrator → doc2data → truid/spike → offer)
- Individual service health checks
- Presigned URL generation and S3 upload (via boto3)
- Document registration and provider selection (truid vs spike)
- Positive flows: valid bank statements, password-protected PDFs
- Negative flows: invalid session, missing documents, wrong password, malformed requests
- Session status polling and offer retrieval
- Error handling and validation

### 3.2 Out of Scope

- Databricks decisioning logic (external system)
- Offer system internal logic (external system)
- Performance/load testing (separate plan)
- Security penetration testing (separate plan)

---

## 4. Prerequisites & Assumptions

### 4.1 Prerequisites

- **UAT access**: Valid API credentials for UAT (Bearer token from Cognito)
- **Test PDFs**: Valid bank statements and test documents (see [5. Test Data Requirements](#5-test-data-requirements))
- **boto3**: For generating test presigned URLs when needed (e.g., bypassing orchestrator for isolated tests) or for S3 uploads
- **Environment variables**: `BASE_URL` (e.g. `https://uat.api.rcdevops.co.za`), `AUTH_TOKEN`, `TEST_PARTNER_ID`, `TEST_MERCHANT_ID`

### 4.2 Assumptions

- Valid bank statements for all positive test flows
- Password-protected PDFs available for password-encrypted tests (password known)
- UAT endpoints for all four services are deployed and accessible
- Partner configuration in UAT allows TruID and/or Spike as OCR providers
- S3 bucket(s) configured for UAT with correct IAM for doc2data → truid/spike

---

## 5. Test Data Requirements

### 5.1 PDF Assets (User to Provide)

| Asset ID | Description | Format | Notes |
|----------|-------------|--------|-------|
| `BANK_STATEMENT_VALID` | Valid bank statement PDF | PDF | Single bank statement, clear text |
| `BANK_STATEMENT_PW_PROTECTED` | Password-protected statement | PDF | Password known (e.g. `test123`) |
| `BANK_STATEMENT_CORRUPT` | Corrupt/invalid PDF | PDF | For negative flow |
| `ID_DOCUMENT_VALID` | Valid ID document | PDF | For TruID flow if applicable |
| `EMPTY_OR_BLANK` | Blank or minimal content | PDF | For OCR failure scenario |

**Location:** Place PDFs in `faas_qa_automation/tests/s2o/assets/` (create if not exists). Paths referenced in test config.

### 5.2 Test Identifiers

- **Partner ID**: From `TEST_PARTNER_ID` or fixture (e.g. FNB, Netcash)
- **Merchant ID**: From `TEST_MERCHANT_ID` or generated
- **Application ID**: Unique per session (e.g. `s2o-test-{uuid}`)

---

## 6. Test Cases

### 6.1 Health & Connectivity

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-HC-001 | Orchestrator health check | Positive | GET `/orchestrator/health` | 200, status ACTIVE |
| S2O-HC-002 | Doc2Data health check | Positive | GET `/doc2data/health` | 200, status ACTIVE |
| S2O-HC-003 | Orchestrator info/version | Positive | GET `/orchestrator/info`, `/orchestrator/version` | 200, valid response |
| S2O-HC-004 | Doc2Data info/version | Positive | GET `/doc2data/info`, `/doc2data/version` | 200, valid response |

### 6.2 Session Management

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-SM-001 | Create session with valid payload | Positive | POST `/orchestrator/api/v1/sessions` with partner_id, merchant_id, application_id | 201, session_id returned |
| S2O-SM-002 | Create session missing partner_id | Negative | POST with missing partner_id | 400 validation error |
| S2O-SM-003 | Get session by ID | Positive | GET `/sessions/{session_id}` | 200, session details |
| S2O-SM-004 | Get non-existent session | Negative | GET `/sessions/{invalid-uuid}` | 404 SESSION_NOT_FOUND |
| S2O-SM-005 | Get session status | Positive | GET `/sessions/{session_id}/status` | 200, status summary |

### 6.3 Document Upload (Presigned URL & S3)

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-DU-001 | Get presigned URL for bank statement | Positive | POST `/documents/{session_id}/presigned-url` with filename, provider_name | 200, presigned_url returned |
| S2O-DU-002 | Upload PDF to S3 via presigned URL | Positive | PUT presigned_url with PDF body | 200/204 |
| S2O-DU-003 | Register documents after upload | Positive | POST `/documents/{session_id}` with presigned_url, filename, provider_name | 201, documents registered |
| S2O-DU-004 | Presigned URL with password metadata | Positive | Include password in request for PW-protected PDF | 200, URL returned |
| S2O-DU-005 | Presigned URL invalid session | Negative | POST with non-existent session_id | 404 |
| S2O-DU-006 | Register with wrong presigned URL | Negative | POST with invalid/malformed presigned_url | 400/207 partial failure |
| S2O-DU-007 | Multiple documents (2+ statements) | Positive | Request 2 presigned URLs, upload both, register both | 201, all registered |

### 6.4 Full S2O Positive Journey

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-PJ-001 | Complete S2O with valid bank statement (Spike) | Positive | 1. Create session 2. Get presigned URL 3. Upload PDF to S3 4. Register documents (provider: spike) 5. Poll status until processed 6. (Mock/simulate Databricks & Offer webhooks if needed) 7. Get offer | Session progresses CREATED→IN_PROGRESS→EVALUATING→APPROVED→OFFER_GENERATED; offer retrievable |
| S2O-PJ-002 | Complete S2O with password-protected PDF | Positive | Same as PJ-001, use PW-protected PDF and pass password in register | OCR succeeds after decryption; session completes |
| S2O-PJ-003 | Complete S2O with TruID provider | Positive | Same flow with provider_name: truid, valid ID/statement for TruID | Session completes with TruID OCR |
| S2O-PJ-004 | Poll status and document details | Positive | GET `/sessions/{id}/status`, GET `/sessions/{id}/documents` during flow | Correct counts, status transitions |

### 6.5 Negative Flows

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-NF-001 | Wrong password for PW-protected PDF | Negative | Register with wrong password | OCR fails; session may reach EVALUATING_PARTIAL or FAILED |
| S2O-NF-002 | Corrupt or invalid PDF upload | Negative | Upload corrupt file, register | OCR fails; appropriate error in Doc2Data callback |
| S2O-NF-003 | Missing authentication | Negative | All requests without Bearer token | 401 Unauthorized |
| S2O-NF-004 | Invalid presigned URL (expired) | Negative | Use expired presigned URL for upload | 403 Forbidden from S3 |
| S2O-NF-005 | Register documents before S3 upload | Negative | POST register before PUT to presigned URL | 207 partial failure or Doc2Data processes nothing |
| S2O-NF-006 | Unsupported document type/provider | Negative | provider_name not configured | 400 or OCR routing failure |
| S2O-NF-007 | Get offer before ready | Negative | GET `/sessions/{id}/offer` before OFFER_GENERATED | 404 |
| S2O-NF-008 | Duplicate document registration | Negative | Register same document twice | Idempotent or appropriate handling |

### 6.6 Doc2Data Direct (Isolated)

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-DD-001 | Doc2Data create document with pre-signed | Positive | POST `/doc2data/api/v1/documents/pre-signed` | 200/201, document_id, presigned URL |
| S2O-DD-002 | Doc2Data get document status | Positive | GET `/doc2data/api/v1/documents/{id}` | 200, status |
| S2O-DD-003 | Doc2Data list results | Positive | GET `/doc2data/api/v1/documents/{id}/results` | 200, result files list |

### 6.7 TruID & Spike (Lambda Invocation)

*Note: Direct Lambda invocation tests typically run in service repos or with localstack. For E2E, we rely on Doc2Data→TruID/Spike integration.*

| ID | Test Case | Type | Steps | Expected Result |
|----|-----------|------|-------|-----------------|
| S2O-OC-001 | Spike OCR with valid statement | Positive | Full S2O flow with provider spike | OCR result in S3, Doc2Data callback success |
| S2O-OC-002 | TruID OCR with valid document | Positive | Full S2O flow with provider truid | OCR result in S3, Doc2Data callback success |
| S2O-OC-003 | Spike OCR wrong password | Negative | provider spike, wrong password | INVALID_PASSWORD or OCR_FAILED_INCORRECT_PASSWORD |

---

## 7. Execution Strategy

### 7.1 Test Execution Order

1. **Phase 1 – Health & Smoke**: S2O-HC-* (all services reachable)
2. **Phase 2 – Session Management**: S2O-SM-*
3. **Phase 3 – Document Upload**: S2O-DU-*
4. **Phase 4 – Doc2Data Isolated**: S2O-DD-* (optional, for isolated Doc2Data validation)
5. **Phase 5 – Full Positive Journey**: S2O-PJ-*
6. **Phase 6 – Negative Flows**: S2O-NF-*
7. **Phase 7 – OCR Integration**: S2O-OC-*

### 7.2 pytest Markers

```python
@pytest.mark.s2o
@pytest.mark.s2o_health
@pytest.mark.s2o_positive
@pytest.mark.s2o_negative
@pytest.mark.s2o_e2e
```

### 7.3 Execution Commands

```bash
# All S2O tests
pytest tests/s2o/ -v -m s2o

# Health only
pytest tests/s2o/ -v -m s2o_health

# Positive flows only
pytest tests/s2o/ -v -m s2o_positive

# Negative flows only
pytest tests/s2o/ -v -m s2o_negative

# E2E (full journey - longer)
pytest tests/s2o/ -v -m s2o_e2e

# Generate report after run
pytest tests/s2o/ -v --tb=short -q && python -m framework.utils.s2o_report_generator
```

---

## 8. Environment Configuration

### 8.1 Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | UAT API base | `https://uat.api.rcdevops.co.za` |
| `AUTH_TOKEN` | Cognito Bearer token | `eyJ...` |
| `TEST_PARTNER_ID` | Test partner UUID | `30f50c8b-7b88-49c1-8b61-ca93b8f6ea7e` |
| `TEST_MERCHANT_ID` | Test merchant | `merchant-s2o-test-001` |
| `S2O_TEST_PDF_PATH` | Path to valid bank statement | `tests/s2o/assets/valid_statement.pdf` |
| `S2O_TEST_PW_PDF_PATH` | Path to PW-protected PDF | `tests/s2o/assets/pw_statement.pdf` |
| `S2O_TEST_PDF_PASSWORD` | Password for PW-protected PDF | `test123` |
| `AWS_REGION` | For boto3 presigned URL tests | `af-south-1` |
| `S3_BUCKET_ORCHESTRATOR` | Orchestrator S3 bucket (if generating presigned URLs via boto3) | From UAT config |

### 8.2 Optional: boto3 Presigned URL Generation

For tests that need to generate presigned URLs directly (e.g., bypassing orchestrator for isolation):

```python
import boto3
from botocore.config import Config

def generate_presigned_upload_url(bucket: str, key: str, expiry: int = 3600) -> str:
    s3 = boto3.client("s3", config=Config(signature_version="s3v4"))
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expiry,
    )
```

Use UAT bucket and key pattern that Doc2Data expects (e.g. `doc/{provider}/{document_id}/{filename}`).

---

## Appendix A: API Quick Reference

### Orchestrator (UAT)

- Base: `https://uat.api.rcdevops.co.za/orchestrator`
- Create session: `POST /api/v1/sessions`
- Presigned URL: `POST /api/v1/documents/{session_id}/presigned-url`
- Register docs: `POST /api/v1/documents/{session_id}`
- Status: `GET /api/v1/sessions/{session_id}/status`
- Offer: `GET /api/v1/sessions/{session_id}/offer`

### Doc2Data (UAT)

- Base: `https://uat.api.rcdevops.co.za/doc2data`
- Create (pre-signed): `POST /api/v1/documents/pre-signed`
- Document status: `GET /api/v1/documents/{document_id}`
- Results: `GET /api/v1/documents/{document_id}/results`

---

## Appendix B: Test Report Template Reference

See `S2O_TEST_REPORT_TEMPLATE.md` and `framework/utils/s2o_report_generator.py` for the test report structure and generation.

---

**Document Version:** 1.0  
**Maintained By:** FAAS QA / faas_qa_automation
