# AWS CMD TOOL

## Setup  ##
- aws cli install version 2.0+

https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

- kubectl install

https://kubernetes.io/docs/tasks/tools/


- terraform install

https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

- helm install
  - brew install kubernetes-helm

- copy or create symbol link of awstool to /usr/local/bin/awstool
- add this line to `~/.bashrc`
    
  eval "$(register-python-argcomplete awsso)"
    
Then you use awsso to login aws, switch aws account, login ec2 instance, search or update secrets manager
