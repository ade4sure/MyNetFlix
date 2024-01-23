steps {
    sshagent(credentials: ['ssh-credentials-id']) {
      sh '''
          [ -d ~/.ssh ] || mkdir ~/.ssh && chmod 0700 ~/.ssh
          ssh-keyscan -t rsa,dsa example.com >> ~/.ssh/known_hosts
          ssh user@example.com ...
      '''
    }
}
