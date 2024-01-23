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
        stage('Deploy to Remote Docker Server') {
            agent {
                // Use SSH Agent to run the entire pipeline on the remote server
                sshagent(['f355d542-7358-4d58-93a6-cc2e50f192fd'])
            }
            steps {
                // Clone the GitHub repository on the remote server
                sh "git clone ${GITHUB_REPO} /tmp/frontend"

                // Build Docker image on the remote server
                sh """
                    cd /tmp/frontend
                //  docker build -t ${DOCKER_IMAGE_NAME} -f ${DOCKERFILE_PATH} .
                    docker build -t ${DOCKER_IMAGE_NAME} .
                """

                // Save and load Docker image on the remote server
                sh """
                    docker save ${DOCKER_IMAGE_NAME} | docker -H ssh://${DOCKER_SERVER} load
                """
            }
        }
    }
}
