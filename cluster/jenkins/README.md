# Jenkins

Jenkins is an open-source automation server that simplifies the process of building, testing, and deploying software projects. It provides a platform for continuous integration and continuous delivery (CI/CD), allowing developers to automate various stages of the software development lifecycle. Jenkins offers a wide range of plugins and integrations, making it highly customizable and adaptable to various development and deployment workflows. With Jenkins, teams can achieve faster development cycles, increased code quality, and improved collaboration, ultimately streamlining the software development process.

# Introduction

This README provides step-by-step instructions for deploying Jenkins in a Kubernetes cluster as a Kubernetes deployment. Jenkins is a widely used open-source automation server, and running it in Kubernetes allows for scalability and flexibility in managing your CI/CD pipelines.

# Prerequisites
Before you begin, ensure that you have the following prerequisites:

- A running Kubernetes cluster.
- `kubectl` configured to access the cluster.
- AWS EFS file system with a valid access point.
- Docker installed and active.
- AWS CLI configured.

# Deploy Jenkins

1. Deploy the storage class for the Jenkins persistent volume. This deployment provides steps for static provisioning of the volumes.

    **Note:** Make sure you are in the project directory for the deployment.

    - Change the access point and filesystem ID to map your Persistent Volume to the EFS File system in the `jenkins-pv.yaml` file under the Jenkins folder.

    ```
    apiVersion: v1
    kind: PersistentVolume
    metadata:
    name: efs-pv1
    spec:
    capacity:
        storage: 5Gi
    volumeMode: Filesystem
    accessModes:
        - ReadWriteMany
    persistentVolumeReclaimPolicy: Retain
    storageClassName: efs-sc
    csi:
        driver: efs.csi.aws.com
        volumeHandle: <FileSystemId>::<FileSystemIdAccessPoint>
    ```
    - After adding AWS EFS "File System ID" and "File System Access Point ID":
       - RUN the following command

         ```
         kubectl apply -f jenkins/jenkins-sc.yaml,jenkins/jenkins-pv.yaml,jenkins/jenkins-pvc.yaml
         ```

2. Deploy Jenkins as a deployment in the cluster with a replicaset of 1. You can scale the deployment by increasing the number of replicas in the deployment YAML file, **jenkin-deployment.yaml**.
    To make the deployment run the following command:

    ```
    kubectl apply -f jenkins/jenkins-deployment.yaml
    ```

3. Verify the deployment.
    To verify the deployment, run the following command:

    ```
    kubectl get pods -n team-cicd-controlplane
    ```

    Output:

    ```
    NAME                                   READY   STATUS    RESTARTS   AGE
    jenkins-7b56ff5cf8-mk76z               1/1     Running   0          3d20h
    ```

4. Access Jenkins Pods.
    To access the Jenkins deployment, run the following command:

    ```
    kubectl get services -n team-cicd-controlplane
    ```

    Output:

    ```
    NAME                TYPE           CLUSTER-IP      EXTERNAL-IP                                                              PORT(S)
    AGE
    jenkins-service     LoadBalancer   172.20.177.51   a73571a87cc9842768c5f196403854c9-761694311.us-east-1.elb.amazonaws.com   80:30905/TCP,50000:31061/TCP   3d20h
    ```

    Copy the DNS Name of the Load balancer and paste it in the browser with **http://a73571a87cc9842768c5f196403854c9-761694311.us-east-1.elb.amazonaws.com**. Please note that the DNS will be different in your case. Obtain the correct DNS name to access the Jenkins server.

# Jenkins Agent Configuration

# Introduction
Jenkins Kubernetes Agents provide a seamless way to enhance your Jenkins CI/CD pipelines by leveraging the power of Kubernetes. With Kubernetes-based agents, you can dynamically provision build nodes within your Kubernetes cluster, improving scalability, resource isolation, and flexibility for your Jenkins jobs.

# Key Benefits

- **Scalability:** Jenkins Kubernetes Agents enable automatic scaling of build nodes based on workload demands, ensuring that your CI/CD pipeline can handle high loads without manual intervention.

- **Resource Isolation:** Each Jenkins job runs within a dedicated agent pod, guaranteeing resource isolation and minimizing interference between different build processes.

- **Dockerized Environments:** Kubernetes agents can execute build jobs within Docker containers, ensuring consistent and reproducible build environments that closely match your production setup.

- **Dynamic Provisioning:** Build nodes are created on-the-fly, optimizing resource utilization and reducing infrastructure costs. No more overprovisioning.

- **Versatility:** Jenkins Kubernetes Agents support a wide range of build tools and programming languages, making them suitable for a variety of development projects.

- **Container Orchestration:** Leveraging Kubernetes as the platform, Jenkins can take advantage of Kubernetes' built-in features for container orchestration, such as scheduling, load balancing, and service discovery.

## Cluster Side Configuration

1. Create a namespace inside the cluster.
    Run the following command.

    ```
    kubectl create namespace build-server
    ```

    Verify the creation of the namespace.

    Run the following command:

    ```
    kubectl get ns
    ```

    Output:

    ```
    NAME                            STATUS   AGE
    default                         Active   3d21h
    gatekeeper-system               Active   3d21h
    build-server                    Active   3d20h
    karpenter                       Active   3d21h
    kube-node-lease                 Active   3d21h
    kube-public                     Active   3d21h
    kube-system                     Active   3d21h
    team-cicd-controlplane          Active   3d21h
    team-dev                        Active   3d21h
    team-signed-cicd-controlplane   Active   3d21h
    ```

2. Create the service account.
    To create the service account, run the following command:

    Run the following command:

    ```
    kubectl create sa build-server -n build-server
    ```

3. Create a Role bind for the service account with cluster admin role.
    To create the role binding:

    ```
    kubectl create rolebinding jenkins-admin-binding --clusterrole=admin --serviceaccount=build-server:build-server --namespace=build-server
    ```

4. Create the Cluster Role bind to allow the build-server account to give access to the other namespaces in the cluster.
    To create a cluster role binding, run the following command:

    ```
    kubectl create clusterrolebinding default-pod --clusterrole cluster-admin --serviceaccount=build-server:build-server --namespace=build-server
    ```

5. Add a secret to pull build server container images from a private AWS ECR registry.

    Run the following cluster.

    **Note:** Make sure to add the cluster AWS account and region before running the following command.

    ## If you are on a Windows platform

    ```
    $registryServer = "<yourawsaccountid>.dkr.ecr.<yourregion>.amazonaws.com"
    $dockerUsername = "AWS"
    $dockerPassword = aws ecr get-login-password --region <youregion>

    # Namespace
    $namespace = "build-server"

    # Create the Docker registry secret
    kubectl create secret docker-registry regcred `
    --docker-server=$registryServer `
    --docker-username=$dockerUsername `
    --docker-password=$dockerPassword `
    --namespace=$namespace
    ```

    ## If you are on a Linux platform

    Run the following command:

    ```
    kubectl create secret docker-registry regcred \
    --docker-server=<youraccountid>.dkr.ecr.<region>.amazonaws.com \
    --docker-username=AWS \
    --docker-password=$(aws ecr get-login-password) \
    --namespace=build-server
    ```

# Jenkins side Configuration 

1. install plugin and active called **Kubernetes** 

2. After plugin installation Cloud option will appear under the Manage Jenkins Plugin. 

    ![alt text](http://url/to/img.png)

3. Create the Cloud. Name it whatever is the required naming convention. 

4. Configure the cloud **Cloud Kubernetes Configuration** 
    - Add kubernetes URL 
      To get the URL for the kubernetes cluster 
      Run the following command 

      ```
      aws eks describe-cluster --name cluster-stack
      ```
      
5. Create credentials 
    AWS secrete manager is used to store secrets for the jenkins pipeline 
    To integrate aws secret manager with jenkins please refer to the eks cluster runbook readme file 

    1. create a cluster access token 

        Run the following command:

        ```
        kubectl create token jenkins --duration=8760h -n build-server 
        ```

    2. Create aws secret using the token created earlier 
        Run the following command:

        **Note:** Make sure to add the secret and secret string value 

        ```
        aws secretsmanager create-secret --name 'your secret name' --secret-string 'your secret token here' --tags 'Key=jenkins:credentials:type,Value=string' --description 'eks secret'
        ```

    3. Disable HTTPS certificate status check.

    4. Select the Credentials.

    5. Test the connection by clicking on the test connection button.

    6. Apply & Save.


