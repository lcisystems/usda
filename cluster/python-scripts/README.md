# Container Signing Using AWS Signer and Notation CLI 

# Background
Signing container images before deployment in a Kubernetes cluster is essential for ensuring security, trust, and integrity in your application delivery.

- **Security Assurance:** Verify the authenticity of images, preventing unauthorized or malicious code execution.

- **Malware Prevention:** Protect against malware and unauthorized modifications during image transit.

- **Compliance:**  Meet regulatory requirements, simplify audits, and ensure secure deployments.

- **Proactive Risk Mitigation:** Reduce vulnerabilities and deployment risks, ensuring consistent, trusted images.

- **Image Provenance:** Maintain a reliable record of image source, origin, and modifications.

By signing container images, you enhance the security and reliability of your Kubernetes deployments, safeguarding your applications and data.

# Container Image Signing with AWS Signer
AWS Signer is a fully managed code signing service that ensures the trust and integrity of your container images. It allows organizations to validate images through digital signatures, confirming that the image is unaltered and comes from a trusted source. AWS Signer simplifies the management of your code signing environment by enabling you to define signing roles and regions in one central location. It takes care of code signing certificates and private keys, streamlining the code signing lifecycle. Integration with AWS CloudTrail provides visibility into signature generation, aiding compliance efforts.

# Key features of AWS Signer include:

- **Cross Account Signing:** Security administrators can create and manage signing profiles in restricted accounts and grant explicit permissions to other accounts for artifact signing. This setup enhances governance and auditability, with AWS CloudTrail logs automating tracking across accounts.

- **Signature Validity Period:** Signers can specify a signature validity period, allowing control over signature validation. Signatures can either be warned or failed if verified after their validity period has expired.

- **Profile Lifecycle Management:** Signers can cancel a signing profile to prevent further signature generation, and they can revoke a profile to invalidate existing signatures generated after the revocation date and time. This provides control over verification operations and enables quick response to changes in governance or security incidents.

- **Individual Signature Revocation:** AWS Signer offers flexibility by allowing the revocation of individual signatures, providing a means to invalidate specific signatures on individual images.

AWS Signer is a powerful tool for ensuring the trustworthiness of your container images, enhancing security, compliance, and control in your container deployment pipeline.

# Solution overview
This solution is a Python script for automating the process of downloading, installing, and signing Docker images from various sources, typically used in the context of Amazon Web Services (AWS). Here's a brief description of its key components:

- **File Downloading:**

The script supports both Windows and Linux platforms.
It can download a file from a given URL using the appropriate method for the platform.
    
- **Installer:** 

The installer class is used to install downloaded files. It has separate implementations for Windows and Linux.
On Windows, it installs MSI packages quietly and records installation logs.
On Linux, it installs RPM packages.
    
- **Image Processing:**

This part of the script focuses on working with Docker images and AWS services.
It reads configuration from a YAML file, which includes AWS accounts, regions, base images, and ECR repository details.
It can pull Docker images, create or get Amazon Elastic Container Registry (ECR) repositories, tag and push Docker images to these repositories.
It can fetch image digests from ECR repositories, a crucial step for AWS Signer.
    
- **AWS Signer:**

The script uses AWS Signer to sign Docker images.
It manages the signing process and can create or retrieve a signing profile.
The script then uses AWS Signer to sign Docker images using specified profiles.
    
- **Main Function:**

The script has a main function that prompts the user for a URL for file download, initiates the download, and installs the downloaded file.
After successful installation, the user is notified.
The script also has an image_siging_process function to orchestrate the image signing process, leveraging AWS Signer.


# Use case – Signing Amazon ECR container images with Notation and AWS Signer

## Prerequisites
1. Docker 
2. AWS Cli 
3. python 3 
4. pyyaml 


## How to use the script for image signing 

1. Under the python-scripts folder, there is a config.yaml file. This is the file where you can specify the list of images, their tags, and respective ECR repository names.

**Note:** The base images listed in the file are default images that are required for the pipeline solution. However, you can add more images to the list according to the specified format and feed them to the script to sign them. 




```
version: v1 
accounts:
- name: <your aws account>
  region: <region>
  baseimages:
    - name: sonarqube:lts-community
      tag: 1.0.0
      ecrrepo: sonarqube
    - name: jenkins/jenkins:lts
      tag: 1.0.0
      ecrrepo: jenkins
    - name: sonatype/nexus3:latest
      tag: 1.0.0
      ecrrepo: nexus
    - name: ranaziauddin/signing:latest
      tag: 1.0.0
      ecrrepo: notationcli
    - name: maven:3-openjdk-17
      tag: 1.0.0
      ecrrepo: maven
    - name: alpine/k8s:1.25.14
      tag: 1.0.0
      ecrrepo: kubectl
    - name: docker:dind 
      tag: 1.0.0
      ecrrepo: dockerdind 
    - name: phpmyadmin/phpmyadmin
      tag: 1.0.0
      ecrrepo: phpadmin 
    - name: tomcat:latest
      tag: 1.0.0
      ecrrepo: tomcat 
    - name: mysql:5.7 
      tag: 1.0.0
      ecrrepo: mysql
    - name: postgres:14
      tag: 1.0.0
      ecrrepo: postgres
    - name: jenkins/inbound-agent:latest
      tag: 1.0.0
      ecrrepo: jnlp


```

2. Run the requirements.txt file. Follow the command below 

    **Note:** Make sure you change the directory and get into the python-scripts directory before executing the command
    ```
    pip3 install -r requirements.txt 
    ```
   
3. Execute the script. follow the command below.
    
    ```
    python3 aws-image-signer.py
    ```

4. Provide the URL for Notation CLI with AWS Signer plugin. 

    If your are on windowns plaform. Provide the following url 

    ```
    https://d2hvyiie56hcat.cloudfront.net/windows/amd64/installer/latest/aws-signer-notation-cli.msi 
    ```
    
    if your are on linux platform. Provide the following url 

    **Note:** follow the URL https://docs.aws.amazon.com/signer/latest/developerguide/image-signing-prerequisites.html to get the link for the specific flavour of your linux platform. 

    ```
    https://d2hvyiie56hcat.cloudfront.net/linux/amd64/installer/rpm/latest/aws-signer-notation-cli_amd64.rpm
    ```

## Conclusion 

Once the script finishes execution, it will sign all the images provided in the config.yaml file. It will create individual AWS Signer profiles and ECR private repositories. 
