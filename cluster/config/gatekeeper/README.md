# Gatekeeper and Ratify for Kubernetes Clusters

# Background

## Image Signing and Security

Image signing is a critical security practice in container orchestration. It involves digitally signing container images to ensure their integrity and authenticity. Signed images are essential for verifying that the image hasn't been tampered with and originates from a trusted source. Ensuring only signed container images are deployed in your Kubernetes cluster is a fundamental aspect of maintaining a secure and trusted environment.

## Gatekeeper and Ratify for Image Signing

**Gatekeeper** and **Ratify** are valuable tools that enhance security and governance in your Kubernetes clusters, ensuring that only signed container images are deployed:

- **Gatekeeper**: Gatekeeper enforces policies and constraints within your cluster, allowing you to define policies that require signed container images. It prevents the deployment of unsigned or unverified images, reducing the risk of security vulnerabilities.

- **Ratify**: Ratify automates the approval process for changes to Kubernetes resources, including the deployment of container images. This includes verifying image signatures as part of the approval workflow, enhancing your image security practices.

## AWS Signer Plugin

The **AWS Signer Plugin** is an essential component that integrates with the AWS ecosystem for secure image signing. AWS Signer allows you to digitally sign container images using AWS Key Management Service (KMS) keys. By using this plugin in your image signing workflow, you can ensure that your container images are securely signed, making them eligible for deployment within a secure Kubernetes cluster.

## Introduction

Gatekeeper and Ratify are two essential tools for Kubernetes clusters designed to enhance security, policy enforcement, and governance. They help ensure that your Kubernetes environment adheres to security standards, compliances, and best practices.

Gatekeeper for cluster is deployed in the eks cluster using eks blueprint as an eks addOn. 

Verify the deployment for the gatekeeper by running the following command:

```
    kubectl get ns gatekeeper-system
```

if its installed and active the follwoing will be the output:

```
    NAME                STATUS   AGE
    gatekeeper-system   Active   3d18h

```

## Gatekeeper

**Gatekeeper** is an open-source policy controller for Kubernetes. It enforces policies and constraints on the resources and configurations within your cluster to ensure they meet specific security and compliance requirements. Key features of Gatekeeper include:

- **Custom Resource Definitions (CRDs)**: Gatekeeper leverages CRDs to allow administrators to define and enforce policies in a declarative manner.

- **Open Policy Agent (OPA)**: It integrates with OPA, a powerful policy framework, to enforce policies effectively.

- **Security and Best Practices**: Gatekeeper helps prevent misconfigurations, enforces best practices, and enhances the overall security of your Kubernetes workloads.

- **Policy Enforcement**: It acts as a gatekeeper, ensuring that only compliant resources are admitted to the cluster. This makes it a powerful tool for policy enforcement and governance.

## Ratify

**Ratify** is a tool tailored for Kubernetes that focuses on approval workflows and policy enforcement. It provides a structured and auditable process for managing changes to Kubernetes resources. Key features of Ratify include:

- **Approval Workflows**: It automates the approval process for changes to Kubernetes resources, allowing organizations to implement structured workflows.

- **Compliance and Audit Trails**: Ratify is particularly useful in environments where compliance, audit trails, and controlled access to resources are critical.

- **Integration**: It seamlessly integrates with existing Kubernetes environments, allowing administrators to define and enforce workflows requiring approval for resource changes.

- **Reduced Risk**: Ratify helps ensure that only authorized changes are made to the cluster, reducing the risk of misconfigurations and security breaches.

## Summary

In summary, Gatekeeper and Ratify are invaluable tools for Kubernetes clusters:

- **Gatekeeper** focuses on policy enforcement and configuration validation, enhancing the security and compliance of your Kubernetes environment.

- **Ratify** specializes in approval workflows and policy enforcement, ensuring a structured, auditable process for managing changes to Kubernetes resources.

Both of these tools contribute to a more secure, well-governed Kubernetes environment, helping organizations maintain the highest standards of security and compliance.

# Configure Gatekeeper and Ratify in the Cluster

Log in to your AWS account where the cluster has been deployed.

1. Navigate to the IAM. Click on "Create Policy" and add the following JSON policy:

   ```
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "signer:GetRevocationStatus"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

2. Create a role. Select "Web Identity" as the trusted entity. Name the role as signer_role (make sure you name the role as is because the serviceaccount.yaml file inside the config folder has the name hardcoded. If you change the name of the role as per your naming convention, make sure to replace it with the required name).

    - Choose an identity provider from the list.

    - Choose policies to add to the role:

    - Choose the policy you created earlier in step 1.
    - Choose one AWS Managed policy (AmazonEC2ContainerRegistryReadOnly).
        Finally, click on "Create Role."

3. Create a service account inside the cluster with an annotation to the role ARN you created above.

    - To create the service account, make sure you are inside your project folder.
       Run the following command:

    ```
        kubectl apply -f config/gatekeeper/serviceaccount.yaml  
    ```
4. Next, we need to deploy a Gatekeeper policy and constraint. For this guide, we will use a sample policy and constraint that requires images to have at least one trusted signature.
    - RUN the Following commad 
    ```
        kubectl apply -f config/gatekeeper/constraint.yaml  
        kubectl apply -f config/gatekeeper/notation-validation-template.yaml 
    ```

    Description: 
        If you want to add specific namespace to your policy constraint you can add the namespaces to the the constraint.yaml file. 
        Contents of the file 

    ```
    apiVersion: constraints.gatekeeper.sh/v1beta1
    kind: notationvalidation
    metadata:
    name: ratify-constraint
    spec:
    enforcementAction: deny
    match:
        kinds:
        - apiGroups: [""]
            kinds: ["Pod"]
        namespaces: ["team-dev", "team-signed-cicd-controlplane", "team-cicd-controlplane"]
        
    ```

5. Deploy Ratify

    Now we can deploy Ratify to our cluster with the AWS Signer root as the notation verification certificate:
    ```
        curl -sSLO https://d2hvyiie56hcat.cloudfront.net/aws-signer-notation-root.cert

        helm install ratify ratify/ratify --atomic true --namespace gatekeeper-system --set-file notationCert=aws-signer-notation-root.cert --set featureFlags.RATIFY_EXPERIMENTAL_DYNAMIC_PLUGINS=true --set serviceAccount.create=false --set oras.authProviders.awsEcrBasicEnabled=true --set featureFlags.RATIFY_CERT_ROTATION=true
    ```

6. After deploying Ratify, we will download the AWS Signer notation plugin to the Ratify pod using the Dynamic Plugins feature:
    - RUN the following command 
        ```
        kubectl apply -f config/gatekeeper/aws-signer-plugin.yaml
        ```
6. Finally, we will create a verifier that specifies the trust policy to use when verifying signatures. In this guide, we will  use a trust policy that only trusts images signed by the SigningProfile we created earlier
    
    To apply this policy provide the list of aws signer profile arn under **trustedIdentities**

    ```
    apiVersion: config.ratify.deislabs.io/v1beta1
    kind: Verifier
    metadata:
    name: verifier-notation
    spec:
    name: notation
    artifactTypes: application/vnd.cncf.notary.signature
    parameters:
        verificationCertStores:
        certs:
            - ratify-notation-inline-cert
        trustPolicyDoc:
        version: "1.0"
        trustPolicies:
            - name: default
            registryScopes:
                - "*"
            signatureVerification:
                level: strict
            trustStores:
                - signingAuthority:certs
            trustedIdentities:
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/mysqlprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/jenkinsprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/nexusprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/postgresprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/sonarqubeprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/notationcliprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/mavenprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/kubectlprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/dockerdindprofile
                - arn:aws:signer:us-east-1:<accountId>:/signing-profiles/jnlpprofile
    ```

    - Apply the policy to to cluster:
        Run the following command:
        ```
        kubectl apply -f config/gatekeeper/notation-verifier.yaml
        ```
