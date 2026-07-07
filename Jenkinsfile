pipeline {
    agent {
        kubernetes {
            cloud 'ibm-cloud-k8s'
            namespace 'jenkins-agents'
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: pseudo-entropy-ci
spec:
  serviceAccountName: jenkins-agent
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: python
    image: python:3.11-slim
    command: ["sleep", "infinity"]
    imagePullPolicy: IfNotPresent
    resources:
      requests: { cpu: "2", memory: "4Gi" }
      limits:   { cpu: "4", memory: "8Gi" }
    envFrom:
    - secretRef:
        name: ibm-quantum-credentials
    env:
    - name: QPU_BUDGET_SECONDS
      value: "1.0"
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
'''
            idleMinutes: 5
        }
    }

    environment {
        HOME                     = '/tmp'
        USAGE_FILE               = 'quantum_usage.json'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PIP_NO_CACHE_DIR         = '1'
        PYTHONDONTWRITEBYTECODE  = '1'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 120, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install Dependencies') {
            steps {
                container('python') {
                    sh 'python -m pip install --upgrade pip && python -m pip install -r requirements.txt'
                }
            }
        }

        stage('Lint') {
            steps {
                container('python') {
                    sh '''
                        flake8 src tests --max-line-length=100 --extend-ignore=E203,W503
                        black --check src tests
                    '''
                }
            }
        }

        stage('Test (Simulator)') {
            steps {
                container('python') {
                    sh '''
                        pytest tests/ \
                            --ignore=tests/test_hardware_data.py \
                            -m "not requires_ibm" \
                            --cov=src --cov-report=xml:coverage.xml \
                            --html=pytest_simulator_report.html \
                            --self-contained-html -v
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pytest_simulator_report.html, coverage.xml',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Validate IBM Secrets') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                    expression { env.RUN_HARDWARE_TESTS == 'true' }
                }
            }
            steps {
                container('python') {
                    sh '''
                        if [ -z "${QISKIT_IBM_TOKEN:-}" ]; then
                            echo "QISKIT_IBM_TOKEN is not set. Hardware tests cannot run." >&2
                            exit 1
                        fi
                        if [ -n "${ORG_ID:-}" ]; then
                            echo "ORG_ID provided: ${ORG_ID}"
                        else
                            echo "ORG_ID is empty; continuing with default instance resolution."
                        fi
                    '''
                }
            }
        }

        stage('Resolve Configured Backends') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                    expression { env.RUN_HARDWARE_TESTS == 'true' }
                }
            }
            steps {
                container('python') {
                    sh '''
                        python - <<'PY'
import sys
try:
    from src.config import resolve_cfg_backends
    active = resolve_cfg_backends()
    print('Resolved active backends:', active)
except Exception as e:
    print('ERROR: failed to resolve configured backends:', e, file=sys.stderr)
    sys.exit(2)
PY
                    '''
                }
            }
        }

        stage('Test (IBM Quantum Hardware)') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                    expression { env.RUN_HARDWARE_TESTS == 'true' }
                }
            }
            steps {
                container('python') {
                    sh '''
                        pytest tests/ -m "requires_ibm" \
                            --html=pytest_hardware_report.html \
                            --self-contained-html -v
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pytest_hardware_report.html, hardware/*.csv',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Quantum Gate Time Budget') {
            steps {
                container('python') {
                    sh '''
                        python scripts/quantum_usage.py --output ${USAGE_FILE}
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${USAGE_FILE}", allowEmptyArchive: true
                }
                failure {
                    echo "❌ Gate time budget exceeded."
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists("${USAGE_FILE}")) {
                    def data = readJSON file: "${USAGE_FILE}"
                    echo "══════════════════════════════════════"
                    echo "  QUANTUM GATE TIME  — Build #${env.BUILD_NUMBER}"
                    echo "══════════════════════════════════════"
                    echo "  Jobs:        ${data.job_count}"
                    echo "  Gate time:   ${data.total_gate_time_seconds} s"
                    echo "  Budget:      ${data.budget_seconds} s"
                    echo "  Status:      ${data.budget_exceeded ? '❌ EXCEEDED' : '✅ OK'}"
                    if (data.first_violation) {
                        echo "  Violation:   job ${data.first_violation.job_id} " +
                             "on ${data.first_violation.backend} " +
                             "(${data.first_violation.gate_time_seconds}s)"
                    }
                    echo "══════════════════════════════════════"
                }
            }
        }
        failure {
            emailext(
                subject: 'Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}',
                body: 'Console: ${env.BUILD_URL}',
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'dev-team@yourorg.com'}"
            )
        }
    }
}
