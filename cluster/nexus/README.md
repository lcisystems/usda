# Nexus

Nexus Repository is a versatile and powerful artifact repository manager that simplifies the storage, retrieval, and management of software components and dependencies. It plays a crucial role in streamlining your software development and deployment processes by providing a secure and organized central repository.

# Key Features of Nexus

Nexus offers several key features, including:

- **Universal Format Support:** Nexus is compatible with a wide range of repository formats, including Maven, Docker, npm, NuGet, and more, making it suitable for various development technologies.

- **Dependency Management:** It ensures that your projects have access to the necessary components, enhancing the reliability of your builds and deployments.

- **Proxying and Caching:** Nexus can act as a proxy for remote repositories, reducing build times and enhancing reliability by caching artifacts locally.

- **Access Control:** Robust access control and security features enable you to define who can access and publish artifacts, ensuring data integrity.

- **Integration with CI/CD:** Nexus easily integrates into your CI/CD pipelines, facilitating artifact publication, retrieval, and management during the software development lifecycle.

- **User-Friendly Web Interface:** Its user-friendly web interface simplifies artifact discovery and repository content exploration.

Nexus Repository is an indispensable tool for software development, ensuring that your artifacts are stored, organized, and retrieved efficiently, ultimately improving your software delivery process.

# Introduction
This guide outlines the process of deploying Nexus Repository in Amazon Elastic Kubernetes Service (EKS) as a Kubernetes deployment. Nexus Repository is a powerful artifact repository manager used to store and manage your software artifacts and dependencies.

# Deploy Nexus

To deploy Nexus, follow these steps:

1. **To deploy Nexus, edit the persistent volume and add the 'filesystemID' and 'FileSystemAccessPointId' in `nexus_pv.yml` under the Nexus folder:**

    ```
    apiVersion: v1
    kind: PersistentVolume
    metadata:
      name: efs-pv2
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
          volumeHandle: <your file system ID>::<your file system access point ID>
    ```

2. **After adding the required file system ID and file system access point ID, create the persistent volume and persistent volume claim:**

    Run the following command:

    ```
    kubectl apply -f nexus/nexus-pv.yml,nexus/nexus-pvc.yml
    ```

    Verify the PV and PVC:

    Run the following command:

    ```
    kubectl get pv efs-pv2
    ```

    Output:

    ```
    NAME      CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                    STORAGECLASS   REASON   AGE
    efs-pv2   5Gi        RWX            Retain           Bound    team-cicd-controlplane/efs-nexus-claim   efs-sc                  4d4h
    ```

3. **Deploy Nexus:**

    Run the following command:

    ```
    kubectl apply -f nexus/nexus-deployment.yaml
    ```

4. **Verify the deployment:**

    Run the following command:

    ```
    kubectl get pods -n team-cicd-controlplane
    ```

    Output:

    ```
    NAME                                   READY   STATUS    RESTARTS   AGE
    nexus-848bfd9664-5p2gv                 1/1     Running   0          4d4h
    ```

## Access Nexus

To access Nexus, you need the Load Balancer DNS name. To find it, run the following command:

```
kubectl get services -n team-cicd-controlplane
```

output:

```
NAME                TYPE           CLUSTER-IP      EXTERNAL-IP                                                              PORT(S)                        AGE
jenkins-service     LoadBalancer   172.20.177.51   a73571a87cc9842768c5f196403854c9-761694311.us-east-1.elb.amazonaws.com   80:30905/TCP,50000:31061/TCP   4d16h
nexus-service       LoadBalancer   172.20.74.219   a9e10564de20542479ec77dc20e4b01d-596046380.us-east-1.elb.amazonaws.com   8081:31515/TCP                 4d4h
postgres-service    ClusterIP      172.20.84.110   <none>                                                                   5432/TCP                       4d4h
sonarqube-service   LoadBalancer   172.20.50.176   a995db548071c45e6ac2efe27f41d1f9-664316547.us-east-1.elb.amazonaws.com   9000:31312/TCP                 4d4h

```
