pipeline {
    agent any
    stages {
        stage('SSH') {
            steps {
                        sshagent(credentials: ['f355d542-7358-4d58-93a6-cc2e50f192fd']) {
                        sh "pwd"
                    }
                }
        }
    }
}

