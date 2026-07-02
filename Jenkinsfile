def runCommand(String unixCommand, String windowsCommand = null) {
    if (isUnix()) {
        sh unixCommand
    } else {
        bat(windowsCommand ?: unixCommand)
    }
}

def venvPython() {
    return isUnix() ? '.venv/bin/python' : '.venv\\Scripts\\python.exe'
}

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_PORT = '5000'
        APP_URL = 'http://127.0.0.1:5000'
        SONARQUBE_ENV = 'SonarQube'
        SONAR_SCANNER_TOOL = 'SonarScanner'
        DEPENDENCY_CHECK_TOOL = 'OWASP-Dependency-Check'
        ZAP_DOCKER_IMAGE = 'ghcr.io/zaproxy/zaproxy:stable'
    }

    stages {
        stage('Build') {
            steps {
                script {
                    def requirementsFile = fileExists('requirements.txt') ? 'requirements.txt' : '.ci-requirements.txt'

                    if (!fileExists('requirements.txt')) {
                        writeFile file: requirementsFile, text: 'flask\npytest\nrequests\n'
                    }

                    runCommand(
                        """
                        python3 -m venv .venv
                        ${venvPython()} -m pip install --upgrade pip
                        ${venvPython()} -m pip install -r ${requirementsFile}
                        """,
                        """
                        py -3 -m venv .venv
                        ${venvPython()} -m pip install --upgrade pip
                        ${venvPython()} -m pip install -r ${requirementsFile}
                        """
                    )
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    def hasTests = fileExists('tests') || fileExists('test_vulnerable.py')
                    def smokeTestCommand = "${venvPython()} -c \"from vulnerable import app; client = app.test_client(); response = client.get('/hello?name=CI'); assert response.status_code == 200; assert b'Hello, CI!' in response.data\""
                    def testCommand = hasTests ? "${venvPython()} -m pytest -q" : smokeTestCommand

                    runCommand(testCommand, testCommand)
                }
            }
        }

        stage('Analyze') {
            steps {
                script {
                    def scannerHome = tool env.SONAR_SCANNER_TOOL

                    withSonarQubeEnv(env.SONARQUBE_ENV) {
                        runCommand(
                            """
                            "${scannerHome}/bin/sonar-scanner" \
                              -Dsonar.projectKey=ev3 \
                              -Dsonar.projectName=ev3 \
                              -Dsonar.sources=. \
                              -Dsonar.exclusions=.venv/**,dependency-check-report/**,zap-report/** \
                              -Dsonar.python.version=3
                            """,
                            """
                            "${scannerHome}\\bin\\sonar-scanner.bat" ^
                              -Dsonar.projectKey=ev3 ^
                              -Dsonar.projectName=ev3 ^
                              -Dsonar.sources=. ^
                              -Dsonar.exclusions=.venv/**,dependency-check-report/**,zap-report/** ^
                              -Dsonar.python.version=3
                            """
                        )
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    runCommand(
                        """
                        mkdir -p logs
                        nohup ${venvPython()} -m flask --app vulnerable run --host=0.0.0.0 --port=${env.APP_PORT} > logs/app.log 2>&1 &
                        echo \$! > app.pid
                        for i in \$(seq 1 30); do
                          curl -fsS "${env.APP_URL}/hello?name=zap" && exit 0
                          sleep 1
                        done
                        echo "La aplicacion no respondio en ${env.APP_URL}" >&2
                        exit 1
                        """,
                        """
                        if not exist logs mkdir logs
                        powershell -NoProfile -Command "\$p = Start-Process -FilePath '${venvPython()}' -ArgumentList '-m flask --app vulnerable run --host=0.0.0.0 --port=${env.APP_PORT}' -PassThru -RedirectStandardOutput 'logs\\app.log' -RedirectStandardError 'logs\\app.err.log' -WindowStyle Hidden; Set-Content -Path app.pid -Value \$p.Id"
                        powershell -NoProfile -Command "\$deadline = (Get-Date).AddSeconds(30); do { try { \$r = Invoke-WebRequest -UseBasicParsing '${env.APP_URL}/hello?name=zap'; if (\$r.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Seconds 1 } while ((Get-Date) -lt \$deadline); Write-Error 'La aplicacion no respondio en ${env.APP_URL}'; exit 1"
                        """
                    )
                }
            }
        }

        stage('Security Test') {
            parallel {
                stage('OWASP Dependency-Check') {
                    steps {
                        script {
                            def dependencyCheckHome = tool env.DEPENDENCY_CHECK_TOOL

                            runCommand(
                                """
                                mkdir -p dependency-check-report
                                "${dependencyCheckHome}/bin/dependency-check.sh" \
                                  --project ev3 \
                                  --scan . \
                                  --format ALL \
                                  --out dependency-check-report \
                                  --exclude .venv
                                """,
                                """
                                if not exist dependency-check-report mkdir dependency-check-report
                                "${dependencyCheckHome}\\bin\\dependency-check.bat" ^
                                  --project ev3 ^
                                  --scan . ^
                                  --format ALL ^
                                  --out dependency-check-report ^
                                  --exclude .venv
                                """
                            )
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'dependency-check-report/**', allowEmptyArchive: true
                            dependencyCheckPublisher pattern: 'dependency-check-report/dependency-check-report.xml'
                        }
                    }
                }

                stage('OWASP ZAP') {
                    steps {
                        script {
                            def zapTarget = isUnix() ? env.APP_URL : "http://host.docker.internal:${env.APP_PORT}"

                            runCommand(
                                """
                                mkdir -p zap-report
                                docker run --rm --network host \
                                  -v "\$PWD:/zap/wrk/:rw" \
                                  ${env.ZAP_DOCKER_IMAGE} zap-baseline.py \
                                  -t "${zapTarget}" \
                                  -r zap-report/zap-report.html \
                                  -J zap-report/zap-report.json \
                                  -w zap-report/zap-report.md
                                """,
                                """
                                if not exist zap-report mkdir zap-report
                                docker run --rm ^
                                  -v "%CD%:/zap/wrk/:rw" ^
                                  ${env.ZAP_DOCKER_IMAGE} zap-baseline.py ^
                                  -t "${zapTarget}" ^
                                  -r zap-report/zap-report.html ^
                                  -J zap-report/zap-report.json ^
                                  -w zap-report/zap-report.md
                                """
                            )
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'zap-report/**', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                runCommand(
                    """
                    if [ -f app.pid ]; then
                      kill "\$(cat app.pid)" || true
                    fi
                    """,
                    """
                    if exist app.pid powershell -NoProfile -Command "Stop-Process -Id (Get-Content app.pid) -Force -ErrorAction SilentlyContinue"
                    """
                )
            }
            archiveArtifacts artifacts: 'logs/**', allowEmptyArchive: true
        }
    }
}
