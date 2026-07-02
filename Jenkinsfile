pipeline {
    agent any

    stages {

        stage('Build') {
            steps {
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install flask
                '''
            }
        }

        stage('Test') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    python -m py_compile vulnerable.py
                '''
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    start /B python vulnerable.py
                '''
            }
        }

    }

    post {
        success {
            echo 'Pipeline finalizado correctamente.'
        }

        failure {
            echo 'Pipeline con errores.'
        }
    }
}