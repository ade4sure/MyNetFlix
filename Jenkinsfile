pipeline {
    agent any
    environment {
        // Define your environment variables
        GITHUB_REPO = 'https://github.com/ade4sure/MyNetFlix.git'
        DOCKERFILE_PATH = 'path/to/Dockerfile'
        DOCKER_SERVER = '10.128.0.3'
        DOCKER_SERVER_USER = 'jenkinsMaster'
        DOCKER_IMAGE_NAME = 'frontEndImage'
    }
    stages {
        stage('SSH') {
            steps {
                        sshagent(credentials: ['f355d542-7358-4d58-93a6-cc2e50f192fd']) {
                        sh "pwd"

                        // Clone the GitHub repository on the remote server
                        sh "mkdir ~/tmp/frontend"
                        sh "git clone ${GITHUB_REPO} ~/tmp/frontend"

                    }
                }
        }
    }
}

