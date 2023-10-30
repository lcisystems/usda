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

## 1. Deployment

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

# 2. Accessing the Cluster

After the stack deployment is complete, you will have a working EKS cluster deployed in the `required` region. You can access the cluster both via the CLI and the AWS Management Console.

## Setting up kubectl Access

To gain access to the cluster using the CLI, you need to update your `kubeconfig` file using `kubectl`. You will find a command in one of the stack outputs that resulted from the deployment, which should look similar to the following:

```
cluster-stack.clusterstackConfigCommand3CE2A6DC = aws eks update-kubeconfig --name cluster-stack --region <region> --role-arn arn:aws:iam::123456789012:role/
```

You can run this command (replace the role ARN with the one that matches your account) and (region in which the deployment was carried out):

```
  aws eks update-kubeconfig --name cluster-stack --region <region> --role-arn arn:aws:iam::123456789012:role/
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


## Update the Role for efs mount target creation

1. Go to the console and find the role created by the cluster for csi driver

2. Click on Edit role

3. Replace the existing policy with the following json policy:

   ```
      {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "elasticfilesystem:DescribeAccessPoints",
           "elasticfilesystem:DescribeFileSystems",
           "elasticfilesystem:DescribeMountTargets",
           "ec2:DescribeAvailabilityZones"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "elasticfilesystem:CreateAccessPoint"
         ],
         "Resource": "*",
         "Condition": {
           "StringLike": {
             "aws:RequestTag/efs.csi.aws.com/cluster": "true"
           }
         }
       },
       {
         "Effect": "Allow",
         "Action": [
           "elasticfilesystem:TagResource"
         ],
         "Resource": "*",
         "Condition": {
           "StringLike": {
             "aws:ResourceTag/efs.csi.aws.com/cluster": "true"
           }
         }
       },
       {
         "Effect": "Allow",
         "Action": "elasticfilesystem:DeleteAccessPoint",
         "Resource": "*",
         "Condition": {
           "StringEquals": {
             "aws:ResourceTag/efs.csi.aws.com/cluster": "true"
           }
         }
       }
     ]
   }
   ```
4. Click Save


## Create EFS File Access Point 

AWS EFS Access Points simplify client access to EFS file systems, providing user and group-level permissions, root directory permissions, and integration with IAM. They are particularly useful for isolating users, applications, and directories on shared file systems, enhancing security, and ensuring fine-grained control without relying on NFSv4.1 ACLs.

Create the access points for the following application 
   1. Nexus
   2. SonarQube
   3. Jenkins

**Note:** Single Access pint can be created to give access to all three applications. But is recommended and is counted as a best practice to separate the access points. 

To create the access point Run the following commands:

You can run this command (replace the file-system-id with what you have for your EFS file sytem):

```
aws efs create-access-point --file-system-id <your file system ID> --posix-user Uid=1000,Gid=1000 --root-directory "Path=/jenkins,CreationInfo={OwnerUid=1000,OwnerGid=1000,Permissions=777}"
```
```
aws efs create-access-point --file-system-id <your file system ID> --posix-user Uid=1000,Gid=1000 --root-directory "Path=/nexus,CreationInfo={OwnerUid=1000,OwnerGid=1000,Permissions=777}"
```
```
aws efs create-access-point --file-system-id <your file system ID> --posix-user Uid=1000,Gid=1000 --root-directory "Path=/sonarqube,CreationInfo={OwnerUid=1000,OwnerGid=1000,Permissions=777}"
```


# 3. Sign Container Images for deployment in AWS EKS CLUSTER 

To sign images find the solution under python-scripts folder. The readme provided in the folder will help you do signing of the images that are needed to be deployed inside the cluster. 

# 4. Configure Cluster with Gatekeeper and Ratify to reject deployments of unverified images

To configure the cluster find the solution under the config folder. The readme provided in the folder provides step-by-step guidance for deployment. 

# 5. Deploy Jenkins 

To deploy Jenkins as deployment in the AWS EKS cluster find the YAML files and scripts under the Jenkins folder. The readme provided in the folder provides step-by-step guidance for the deployment

# 6. Configure Jenkins to Retrieve secrets From AWS Secret Manager 

# Prerequisites
  AWS CLI 
1. **Create IAM Policy**
   - Login to aws console
   - Create an IAM Policy
     ```
        {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "AllowJenkinsToGetSecretValues",
               "Effect": "Allow",
               "Action": "secretsmanager:GetSecretValue",
               "Resource": "*"
           },
           {
               "Sid": "AllowJenkinsToListSecrets",
               "Effect": "Allow",
               "Action": "secretsmanager:ListSecrets"
           },
           {
               "Sid": "AllowJenkinsToAccessKMSKEY",
               "Effect": "Allow",
               "Action": "kms:*"
               "Resource": "*"
           }
       ]
   }
     ```
2. Attach this Policy to an IAM User
3. Login to Jenkins Server
4. Install Plugin (AWS Secrets Manager Credentials Provider)
5. Configure the plugin under System Configuration
6. Provide the access key and secret Access key for the IAM user who has permission to access the AWS Secret Manager

Now when you create a secret in AWS Secret Manager Jenkins will capture that secret and it will appear inside Jenkins credentials 

# 7. Deploy SonarQube 

To deploy SonarQube as Kubernetes deployment find the YAML file and scripts under sonarqube folder. The readme provided in the folder provides step-by-step guidance for the deployment

# 8. Deploy Nexus 

To deploy Nexus as Kubernetes deployment find the YAML file and scripts under nexus folder. The readme provided in the folder provides step-by-step guidance for the deployment




