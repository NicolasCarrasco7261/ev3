pipeline {
    agent any

    environment {
        PYTHON = "py"
        VENV = "venv"
        SONAR_SCANNER_HOME = tool "SonarScanner"
    }

    stages {

        stage('Build') {
            steps {
                bat """
                    %PYTHON% -m venv %VENV%
                    call %VENV%\\Scripts\\activate

                    python -m pip install --upgrade pip

                    if exist requirements.txt (
                        pip install -r requirements.txt
                    ) else (
                        pip install flask pytest
                    )
                """
            }
        }

        stage('Test') {
            steps {
                bat """
                    call %VENV%\\Scripts\\activate

                    python -m py_compile vulnerable.py

                    if exist tests (
                        pytest
                    ) else (
                        echo No existen pruebas unitarias.
                    )
                """
            }
        }

        stage('Analyze - SonarQube') {
            steps {
                withSonarQubeEnv('SonarQube') {

                    bat """
                        %SONAR_SCANNER_HOME%\\bin\\sonar-scanner.bat ^
                        -Dsonar.projectKey=PipelineAppVulnerable ^
                        -Dsonar.projectName=PipelineAppVulnerable ^
                        -Dsonar.sources=. ^
                        -Dsonar.python.version=3.11
                    """
                }
            }
        }

        stage('Security Test - Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '--scan .',
                                 odcInstallation: 'DependencyCheck'
            }
        }

        stage('Security Test - OWASP ZAP') {
            steps {
                bat """
                docker run --rm ^
                    -t owasp/zap2docker-stable ^
                    zap-baseline.py ^
                    -t http://host.docker.internal:5000 ^
                    -r zap-report.html
                """
            }
        }

        stage('Deploy') {
            steps {
                bat """
                    call %VENV%\\Scripts\\activate

                    start /B python vulnerable.py

                    timeout /t 10
                """
            }
        }
    }

    post {

        always {

            dependencyCheckPublisher pattern: '**/dependency-check-report.xml'

            archiveArtifacts artifacts: 'zap-report.html', fingerprint: true

        }

        success {
            echo 'Pipeline ejecutado correctamente.'
        }

        failure {
            echo 'Pipeline falló.'
        }
    }
}