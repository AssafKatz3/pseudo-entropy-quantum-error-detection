# IBM Cloud Preparation Guide

This guide walks through the prerequisite setup on IBM Cloud so the
CI/CD pipeline can authenticate to IBM Quantum and run hardware tests.

---

## 1. Create an IBM Cloud Account

1. Go to https://cloud.ibm.com and sign up (free Lite tier is enough to start).
2. Verify your email and complete account setup.

---

## 2. Get an IBM Quantum Platform Account

1. Go to https://quantum.ibm.com and sign in with the same IBMid.
2. Navigate to **Dashboard → Account → API key** (or **Manage → API tokens**).
3. Click **Generate new token** and copy the value — this is your
   `QISKIT_IBM_TOKEN`.

> ⚠️ Store this token securely. It grants access to your quantum
> compute credits and QPU queue.

---

## 3. Provision a Quantum Service Instance (Optional but recommended)

If your organization uses a paid plan via IBM Cloud:

1. In IBM Cloud, search the catalog for **Quantum Services**.
2. Create an instance in your preferred region.
3. From the instance page, open **Manage** and copy the **CRN**
   (Cloud Resource Name) — this is your `ORG_ID`.

For personal accounts using the open-access plan, `ORG_ID` can be
left empty or set to the instance CRN from the Quantum Platform
dashboard.

---

## 4. Create an IBM Cloud API Key (for Secrets Manager)

The pipeline uses External Secrets Operator, which needs an IBM Cloud
API key to read secrets from Secrets Manager.

1. In IBM Cloud, go to **Manage → Access (IAM) → API keys**.
2. Click **Create** → name it `eso-ibm-secrets-reader`.
3. Assign it a service policy granting **Reader** on **Secrets Manager**.
4. Copy the generated key value.

---

## 5. Store Credentials in IBM Cloud Secrets Manager

1. Provision or open a **Secrets Manager** instance in IBM Cloud.
2. Create two secrets of type **Arbitrary**:

   | Secret name          | Value                  |
   |----------------------|------------------------|
   | `ibm-quantum/token`  | your QISKIT_IBM_TOKEN  |
   | `ibm-quantum/org-id` | your ORG_ID (CRN)      |

3. Note the Secrets Manager **instance CRN** and **region** — these go
   into `k8s/secretstore-ibm-cloud.yaml`.

---

## 6. Provision an IBM Cloud Kubernetes Cluster

1. In IBM Cloud, create a **VPC or Classic Kubernetes Service** cluster.
2. Wait for the cluster to reach **Normal** state.
3. Configure `kubectl` access:
   ```bash
   ibmcloud ks cluster config --cluster <cluster-name>
   ```

---

## 7. Install Required Cluster Operators

On the cluster:

```bash
# External Secrets Operator
kubectl apply -f https://github.com/external-secrets/external-secrets/releases/download/v0.9.0/external-secrets.yaml

# Jenkins (via Helm)
helm repo add jenkins https://charts.jenkins.io
helm repo update
helm install jenkins jenkins/jenkins -n jenkins --create-namespace
```

---

## 8. Configure Kubernetes Agent Namespace

```bash
kubectl create namespace jenkins-agents
kubectl create serviceaccount jenkins-agent -n jenkins-agents
kubectl create rolebinding jenkins-agent-default \
  --clusterrole=edit \
  --serviceaccount=jenkins-agents:jenkins-agent \
  --namespace=jenkins-agents
```

---

## 9. Apply the SecretStore and ExternalSecret

Edit `k8s/secretstore-ibm-cloud.yaml` and fill in:

- `region` — your Secrets Manager region (e.g. `us-south`)
- `secret_ref` — name of the K8s Secret holding your IBM Cloud API key
  (from step 4)

Then apply:

```bash
kubectl apply -f k8s/secretstore-ibm-cloud.yaml
kubectl apply -f k8s/externalsecret-quantum.yaml
```

Verify the synced secret:

```bash
kubectl get secret ibm-quantum-credentials -n jenkins-agents -o yaml
```

You should see `QISKIT_IBM_TOKEN` and `ORG_ID` populated.

---

## 10. Set Jenkins to Use the Kubernetes Cloud

1. In Jenkins → **Manage Jenkins → Clouds → New cloud → Kubernetes**.
2. Set **Kubernetes URL** to your cluster API endpoint.
3. Set **Jenkins URL** and **Jenkins tunnel**.
4. Namespace: `jenkins-agents`.
5. Save and test connectivity.

---

## 11. Create the Jenkins Pipeline

1. Create a new **Multibranch Pipeline** or **Pipeline** job.
2. Point it at your Git repository.
3. The `Jenkinsfile` at the repo root defines all stages.
4. For hardware tests on non-main branches, set the build parameter
   `RUN_HARDWARE_TESTS=true`.

---

## Environment Variables Summary

| Variable           | Source                | Used for                      |
|--------------------|-----------------------|-------------------------------|
| `QISKIT_IBM_TOKEN` | Secrets Manager       | Qiskit Runtime authentication |
| `ORG_ID`           | Secrets Manager       | Service instance CRN          |
| `QPU_BUDGET_SECONDS` | Jenkinsfile (env)   | Per-job gate-time limit       |

---

## Quick Smoke Test

Once everything is wired up, verify locally before relying on the
pipeline:

```bash
export QISKIT_IBM_TOKEN=<token>
export ORG_ID=<crn>
pip install -r requirements.txt
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; \
           svc = QiskitRuntimeService(); \
           print(svc.backends())"
```

A list of available backends confirms your credentials are valid.
