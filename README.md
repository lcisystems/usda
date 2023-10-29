# Cluster Deployment RunBook

## Prerequisites

### Windows Platform

If you are on a Windows platform, follow these steps:

1. **Install AWS CLI**: [Install AWS CLI for Windows using MSI Installer](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

2. **Install CDK**:
   - AWS CDK is a software development framework to define AWS application resources using familiar programming languages. For EKS Blueprints, we will use TypeScript to write our code.
   - Ensure you have the right version of CDK installed. Remove the current version of CDK:
     ```
     npm uninstall -g aws-cdk
     ```
   - Install CDK version 2.99.1:
     ```
     npm install -g aws-cdk@2.99.1
     ```
   - Verify the CDK version:
     ```
     cdk --version
     ```

3. **Install kubectl Binary with Curl on Windows**:
- Download the latest 1.28 patch release, for example, kubectl 1.28.3.
- Alternatively, if you have Curl installed, you can use this command:
  ```
  curl.exe -LO "https://dl.k8s.io/release/v1.28.3/bin/windows/amd64/kubectl.exe"
  ```
- Validate the binary (optional):
  - Download the kubectl checksum file:
    ```
    curl.exe -LO "https://dl.k8s.io/v1.28.3/bin/windows/amd64/kubectl.exe.sha256
    ```
  - Run the following command to verify the installation:
    ```
    kubectl version --client
    ```

### Linux Platform

If you are on a Linux platform, follow these steps:

1. **Install CDK**:
- AWS CDK is a software development framework to define AWS application resources using familiar programming languages. For EKS Blueprints, we will use TypeScript to write our code.
- Ensure you have the right version of CDK installed. Remove the current version of CDK:
  ```
  rm $(which cdk)
  ```
- Install CDK version 2.99.1:
  ```
  npm install -g aws-cdk@2.99.1
  ```
- Verify the CDK version:
  ```
  cdk --version
  ```
  You should see something like this:
  ```
  2.99.1 (build b2a895e)

2. **Install kubectl Binary with Curl on Linux**:
- Download the latest 1.28 patch release: kubectl 1.28.3.
- Alternatively, you can use Curl with the following command:
  ```
  sudo curl --silent --location -o /usr/local/bin/kubectl \
    https://s3.us-west-2.amazonaws.com/amazon-eks/1.23.7/2022-06-29/bin/linux/amd64/kubectl

  sudo chmod +x /usr/local/bin/kubectl
  ```
- Validate the binary (optional):
  - Run the following command to verify the installation:
    ```
    kubectl version --client
    ```

# Installation Guide for AWS CLI and Additional Utilities

This guide will help you install the AWS CLI, along with some essential utilities on a Linux system. Follow the steps below:

## Install AWS CLI

1. Download the AWS CLI installation package:
   
   ```
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```
2. Install jq, envsubst (from GNU gettext utilities), bash-completion, and moreutils:

   ```
   sudo yum -y install jq gettext bash-completion moreutils
   ```
   Verify that the binaries are in the system's path and executable:

   ```
   for command in kubectl jq envsubst aws
   do
      which $command &>/dev/null && echo "$command in path" || echo "$command NOT FOUND"
   done
   ```

3. Enable kubectl bash completion:
   
   ```
     kubectl completion bash >>  ~/.bash_completion
     . /etc/profile.d/bash_completion.sh
     . ~/.bash_completion
   ```
   
# Cluster Deployment and Access Guide

This guide provides instructions for deploying a cluster, configuring the AWS CLI, and gaining access to an Amazon Elastic Kubernetes Service (EKS) cluster.

## Deployment

1. **Configure AWS CLI**: First, add your AWS access keys and secret access keys using the following command:

   ```
     aws configure
   ```

2. We are interested in, and will be working mostly with, the following:

    lib/: This is where your CDK project's stacks or constructs are defined. This is where most of our code revisions will happen.
    bin/eks-democluster: This is the entrypoint of the CDK project. It will load the constructs defined under lib/.
    
3. Navigate to the bin/eks-democluster directory.

    Run the following command:
   ```
     cdk synth
   ```
   Description: cdk synth will synthesize the project and create a CloudFormation template for deployment.

   ```
     cdk deploy
   ```
   Description: cdk deploy will deploy the cluster using the CloudFormation template prepared earlier

# Accessing the Cluster

After the stack deployment is complete, you will have a working EKS cluster deployed in the `us-west-2` region. You can access the cluster both via the CLI and the AWS Management Console.

## Setting up kubectl Access

To gain access to the cluster using the CLI, you need to update your `kubeconfig` file using `kubectl`. You will find a command in one of the stack outputs that resulted from the deployment, which should look similar to the following:

```
cluster-stack.clusterstackConfigCommand3CE2A6DC = aws eks update-kubeconfig --name cluster-stack --region us-west-2 --role-arn arn:aws:iam::123456789012:role/
```

You can run this command (replace the role ARN with the one that matches your account):

```
  aws eks update-kubeconfig --name cluster-stack --region us-west-2 --role-arn arn:aws:iam::123456789012:role/
```
In case you cleared your terminal or exited and re-entered your browser, you can find and apply the config command with the following:

```
  export KUBE_CONFIG=$(aws cloudformation describe-stacks --stack-name cluster-stack | jq -r '.Stacks[0].Outputs[] | select(.OutputKey|match("ConfigCommand"))| .OutputValue')
  $KUBE_CONFIG
```

Once the kubeconfig has been updated, you should be able to access the EKS cluster. Try listing the Kubernetes services:
```
  kubectl get svc
```
This command will display information about the services in the EKS cluster, including their names, types, cluster IPs, external IPs, ports, and age.



