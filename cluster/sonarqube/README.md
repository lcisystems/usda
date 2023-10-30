# SonarQube

SonarQube is an open-source platform for automated code quality inspection. It offers static code analysis, customizable rules, and seamless CI/CD integration. SonarQube helps improve code quality, reduce technical debt, enforce coding standards, identify security vulnerabilities, and enhance developer productivity. It's a valuable tool for ensuring software quality and compliance with coding standards.

# Introduction
This guide provides instructions for deploying SonarQube on Amazon Elastic Kubernetes Service (EKS). SonarQube is a popular code quality analysis tool, and running it in an EKS cluster offers scalability, reliability, and easy management. This deployment will help ensure that your codebase maintains high standards of quality, security, and reliability.

# Benefits of Using SonarQube
SonarQube is a powerful code quality and security analysis platform that offers a wide range of benefits for your development process. Here are some of the key advantages of using SonarQube:

- **Code Quality Improvement:** SonarQube helps identify and rectify code quality issues, making your codebase cleaner, more maintainable, and less error-prone.

- **Code Security:** It detects vulnerabilities and security issues in your code, allowing you to address them proactively and reduce security risks.

- **Automated Code Reviews:** SonarQube automates the code review process, reducing the manual effort required for code inspections and enforcing coding standards consistently.

- **Early Issue Detection:** By analyzing code as you write it, SonarQube catches issues early in the development process, reducing the cost of fixing problems later.

- **Support for Multiple Languages:** It supports a wide range of programming languages, making it a versatile tool for diverse software development projects.

- **Integration with CI/CD:** SonarQube can be seamlessly integrated into your CI/CD pipeline, providing continuous code quality and security checks.

- **Customizable Rules and Profiles:** You can define custom coding rules and quality profiles to tailor SonarQube to your specific project requirements.

- **Historical Data and Trends:** It provides historical code analysis data and trends, allowing you to track improvements or regressions in your codebase over time.

- **Open Source and Commercial Versions:** SonarQube offers both open-source and commercial editions, making it accessible for projects of all sizes.

- **Plugin Ecosystem:** You can extend SonarQube's functionality through a vast ecosystem of plugins and integrations, further enhancing its capabilities.

By incorporating SonarQube into your development workflow, you can significantly enhance your code quality, security, and overall software reliability.

# Deploy SonarQube in EKS Cluster

To deploy SonarQube in an EKS Cluster, you need to follow these steps:

1. **Create a Secret to Store PostgreSQL Password**

    Kubernetes has a built-in capability to store secrets. To create a secret, you need to base64 encode a secret value. Add the base64 encoded value in `postgresql_db_password.yaml`:

    ```
    apiVersion: v1
    kind: Secret
    metadata:
      name: postgres
      namespace: team-cicd-controlplane
    type: Opaque
    data:
      password: U29mdHdhcmU3ODYjNzg2Iw==
    ```

    Run the following command after adding the base64 encoded password:

    ```
    kubectl apply -f sonarqube/postgresql/postgresql_db_password.yaml
    ```

2. **Create the Persistent Volume and Persistent Volume Claim for PostgreSQL Deployment**

    Run the following command:

    ```
    kubectl apply -f sonarqube/postgresql/postgres_pv.yml,sonarqube/postgresql/postgres_pvc.yml
    ```

3. **Deploy PostgreSQL**

    Run the following command:

    ```
    kubectl apply -f sonarqube/postgresql/postgres_deployment.yml
    ```

4. **Verify the Deployment**

    Run the following command:

    ```
    kubectl get pods -n team-cicd-controlplane
    ```

    Output:

    ```
    NAME                                   READY   STATUS    RESTARTS   AGE
    postgres-deployment-665c4b5b59-d5v2d   1/1     Running   0          4d3h
    ```

5. **Deploy SonarQube**

    To deploy SonarQube, edit the Persistent Volume and add the 'filesystemID' and 'FileSystemAccessPointId' in `sonarqube_pv.yml` under the SonarQube folder.

    ```
    apiVersion: v1
    kind: PersistentVolume
    metadata:
      name: sonar-data-pv
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

6. **After adding the required file system ID and file system access point ID, create the Persistent Volume and Persistent Volume Claim**

    Run the following command:

    ```
    kubectl apply -f sonarqube/sonarqube_pv.yml,sonarqube/sonarqube_sonar_data_pvc.yml
    ```

    Verify the PV and PVC:

    Run the following command:

    ```
    kubectl get pv sonar-data-pv
    ```

    Output:

    ```
    NAME            CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                   STORAGECLASS   REASON   AGE
    sonar-data-pv   5Gi        RWX            Retain           Bound    team-cicd-controlplane/sonar-data-pvc   efs-sc                  4d3h
    ```

7. **Deploy SonarQube**

    Run the following command:

    ```
    kubectl apply -f sonarqube/sonarqube_deployment.yml
    ```

8. **Verify the Deployment**

    Run the following command:

    ```
    kubectl get pods -n team-cicd-controlplane
    ```

    Output:

    ```
    NAME                                   READY   STATUS    RESTARTS   AGE
    sonarqube-deployment-9c7559965-rmj6j   1/1     Running   0          4d4h
    ```

## Access SonarQube

To access SonarQube, you need the Load Balancer DNS name. To find it, run the following command:

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
