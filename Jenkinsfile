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
            steps {
                script {
                    // Use SSH Agent to run Docker commands on the remote server
                    sshagent(['f355d542-7358-4d58-93a6-cc2e50f192fd']) {
                        // Set the DOCKER_HOST environment variable to specify the remote Docker server
                        env.DOCKER_HOST = "ssh://${DOCKER_SERVER_USER}@${DOCKER_SERVER}"

                        /* //Show PWD
                        sh "pwd"

                        // Show HostName                        
                        sh "hostname"

                        //Clear frontEnd Temp
                        sh "sudo rm -r /tmp/frontend"

                        // Clone the GitHub repository on the remote server
                        sh "git clone ${GITHUB_REPO} /tmp/frontend" */

                       sh "git --version"

                        /* // Build Docker image on the remote server
                        sh """
                            cd /tmp/yourrepo
                            docker build -t ${DOCKER_IMAGE_NAME} -f ${DOCKERFILE_PATH} .
                        """

                        // Save and load Docker image on the remote server
                        sh "docker save ${DOCKER_IMAGE_NAME} | docker load" */
                    }
                }
            }
        }
    }
}

