'''
This code is a Python script for automating the process of downloading, installing, and signing Docker images from various sources, typically used in the context of Amazon Web Services (AWS). Here's a brief description of its key components:

File Downloading:

    The script supports both Windows and Linux platforms.
    It can download a file from a given URL using the appropriate method for the platform.
    
Installer:

    The installer class is used to install downloaded files. It has separate implementations for Windows and Linux.
    On Windows, it installs MSI packages quietly and records installation logs.
    On Linux, it installs RPM packages.
    
Image Processing:

    This part of the script focuses on working with Docker images and AWS services.
    It reads configuration from a YAML file, which includes AWS accounts, regions, base images, and ECR repository details.
    It can pull Docker images, create or get Amazon Elastic Container Registry (ECR) repositories, tag and push Docker images to these repositories.
    It can fetch image digests from ECR repositories, a crucial step for AWS Signer.
    
AWS Signer:

    The script uses AWS Signer to sign Docker images.
    It manages the signing process and can create or retrieve a signing profile.
    The script then uses AWS Signer to sign Docker images using specified profiles.
    
Main Function:

    The script has a main function that prompts the user for a URL for file download, initiates the download, and installs the downloaded file.
    After successful installation, the user is notified.
    The script also has an image_siging_process function to orchestrate the image signing process, leveraging AWS Signer.


'''

import os
import subprocess
import ssl
import urllib.request
import yaml
import boto3
import subprocess
import boto3
import json
import botocore

class FileDownloader:
    def __init__(self, url):
        self.url = url

    def download(self, src_path):
        raise NotImplementedError("Subclasses must implement the 'download' method.")
# Define a Windows-specific file downloader
class WindowsFileDownloader(FileDownloader):
    def download(self, src_path):
        try:
            filepath = os.path.join(src_path, os.path.basename(self.url))
            request = urllib.request.Request(self.url, headers={'User-Agent': "Magic Browser"})
            try:
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLS)
                parsed = urllib.request.urlopen(request, context=gcontext)
            except:
                parsed = urllib.request.urlopen(request)
            if not os.path.exists(src_path):
                os.makedirs(src_path)
            with open(filepath, 'wb') as f:
                while True:
                    chunk = parsed.read(100 * 1000 * 1000)
                    if chunk:
                        f.write(chunk)
                    else:
                        break
            return filepath
        except:
            return ''
        
# Define a Linux-specific file downloader
class LinuxFileDownloader(FileDownloader):
    def download(self, src_path):
        try:
            filepath = os.path.join(src_path, os.path.basename(self.url))
            request = urllib.request.Request(self.url, headers={'User-Agent': "Magic Browser"})
            try:
                gcontext = ssl.SSLContext(ssl.PROTOCOL_TLS)

                parsed = urllib.request.urlopen(request, context=gcontext)
            except:
                parsed = urllib.request.urlopen(request)
            if not os.path.exists(src_path):
                os.makedirs(src_path)
            with open(filepath, 'wb') as f:
                while True:
                    chunk = parsed.read(100 * 1000 * 1000)
                    if chunk:
                        f.write(chunk)
                    else:
                        break
            return filepath
        except:
            return ''
        
# Define a base class for installers
class Installer:
    def install(self, file_path):
        raise NotImplementedError("Subclasses must implement the 'install' method.")
 
# Define a Windows-specific installer
class WindowsInstaller(Installer):
    
    def install(self, file_path):
        log_file_destination = os.path.join(os.path.expanduser("~"))
        command = f'msiexec /i {file_path} /quiet /l*vx {log_file_destination}/aws_signer.log'
        # obj = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        obj = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return obj.returncode
    
# Define a Linux-specific installer
class LinuxInstaller(Installer):
    
    def install(self, file_path):
     
        command = f'sudo rpm -U {file_path}'
        obj = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return obj.returncode
    
# Define a class for processing images      
class ImageProcessor:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        
        # Initialize a Boto3 Signer client
        self.ecr_client = boto3.client('ecr', region_name='us-east-1')
        self.signer_client = boto3.client('signer', region_name='us-east-1')
        
    # Read YAML configuration file
    def read_yaml(self):
        with open(self.yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            accounts = data.get('accounts', [])

            account_info = []  # List to store account info, including region and base images

            for account_data in accounts:
                account_info.append(account_data)

            return account_info
        
    # Pull Docker images
    def pull_images(self, baseimages):
        for image_info in baseimages:
            name = image_info['name']
            subprocess.run(['docker', 'pull', f'{name}'])
            
    # Create or get an ECR repository
    def create_ecr_repository(self, ecrrepo):
        try:
            response = self.ecr_client.create_repository(repositoryName=ecrrepo)
            return response['repository']['repositoryUri']
        except self.ecr_client.exceptions.RepositoryAlreadyExistsException:
            # Repository already exists, return the URI
            return f'{self.ecr_client.describe_repositories(repositoryNames=[ecrrepo])["repositories"][0]["repositoryUri"]}'

    # Tag and push Docker images to ECR
    def tag_and_push_images(self, baseimages, ecr_repositories, region, account):
        login_command = f'aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account}.dkr.ecr.{region}.amazonaws.com'
        
        subprocess.run(login_command, shell=True)
        for image_info, ecrrepo in zip(baseimages, ecr_repositories):
            name = image_info['name']
            tag = image_info['tag']
            version = image_info['ecrrepo']
            image_uri = f'{name}'
            
            subprocess.run(['docker', 'tag', image_uri, f'{ecrrepo}:{tag}'])

            # Push the tagged image to the ECR repository
            subprocess.run(['docker', 'push', f'{ecrrepo}:{tag}'])

    # Get image digests and sign images        
    def get_images_digest(self, baseimages, ecr_repositories, region, account):
            for image_info, ecrrepo in zip(baseimages, ecr_repositories):
                name = image_info['name']
                tag = image_info['tag']
                ecr_repo = image_info['ecrrepo']

                # Get the image descriptor
                image_uri = f'{name}:{tag}'
                image_descriptor = self.get_image_descriptor(ecr_repo, region, account)

                if image_descriptor:
                    # Extract the image digest from the image descriptor
                    # Now you have the image digest for the ECR repository
                    print(f'ECR Repository: {ecr_repo}')
                    print(f'Image Digest: {image_descriptor}')
                else:
                    print(f'Failed to get image descriptor for repository: {ecr_repo}')

    # Get image descriptor for a specific ECR repository
    def get_image_descriptor(self, ecr_repo, region, account):
        try:
            response = self.ecr_client.list_images(
                repositoryName=ecr_repo,
            )

            image_digest = response['imageIds'][0]['imageDigest']
            
            if image_digest: 
                self.sign_images(image_digest, ecr_repo, region, account)
                return image_digest
            else:
                print('Failed to find the image digest for the specified image')
        
        except Exception as e:
            print(f'Error: {str(e)}')
            return None
        
    # Sign images using AWS Signer
    def sign_images(self, image_data, ecr_rep, region, account):
        # Here you need to parse image digest
        signer_arn = self.create_or_get_signer_profile(ecr_rep)

        try:
            command = f'notation sign {account}.dkr.ecr.{region}.amazonaws.com/{ecr_rep}:1.0.0 --plugin com.amazonaws.signer.notation.plugin --id {signer_arn}'
            # Run the describe-images command
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                output = result.stdout.split()
                print(output)
            else:
              print(result.stderr)
        except Exception as e:
            print(f'Error parsing image data: {e}')
            return None
    
    # create aws signer if it doesn't exists and return the Arns
    def create_or_get_signer_profile(self, signer_profile_name):
        try:
        # Try to get the existing signer profile
            response = self.signer_client.get_signing_profile(profileName=f'{signer_profile_name}profile')

            # If it exists, return its ARN
            signer_arn = response['profileVersionArn']
            components = signer_arn.split('/')
            # Remove the last component (in this case, 'gfzCxvAGSl')
            stripped_arn = '/'.join(components[:-1])
            return stripped_arn

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # If the profile doesn't exist, create it
                response = self.signer_client.put_signing_profile(
                    profileName=f'{signer_profile_name}profile',
                    platformId='Notation-OCI-SHA384-ECDSA',
                )

                # Return the ARN of the created profile
                signer_arn = response['profileVersionArn']
                components = signer_arn.split('/')
                # Remove the last component (in this case, 'gfzCxvAGSl')
                stripped_arn = '/'.join(components[:-1])
                return stripped_arn
            else:
                # Handle other errors as needed
                print(f"An error occurred: {e}")       

def main():
    print('File Downloading')
    destination = os.path.join(os.path.expanduser("~"))
    downloader = None
    
    Url = input("Enter the URL for the file download: ")

    if os.name == 'nt':
        downloader = WindowsFileDownloader(Url)
    else:
        downloader = LinuxFileDownloader(Url)

    file_path = downloader.download(destination)

    if os.path.exists(file_path):
        print('File downloaded')
        installer = None

        if os.name == 'nt':
            installer = WindowsInstaller()
        else:
            installer = LinuxInstaller()

        result = installer.install(file_path)
        
        if result == 0:
            print(os.path.basename(file_path).replace('.msi', '') + "[Successfully Installed]")
        else:
            print("Installation failed")
    else:
        print("Unable to download the file. Please provide a valid link.")
        
def image_siging_process():
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_directory, 'config.yaml')
    image_processor = ImageProcessor(config_path)
   
    account_info = image_processor.read_yaml()
    
    ecr_repositories = []
    for account_data in account_info:
        account = account_data['name']
        region = account_data['region']
        baseimages = account_data.get('baseimages', [])
        if baseimages:
            ecr_repositories = []
            for image_info in baseimages:
                ecrrepo = image_info.get('ecrrepo', '')
                if ecrrepo:
                    ecr_uri = image_processor.create_ecr_repository(ecrrepo)
                    ecr_repositories.append(ecr_uri)
    
            image_processor.pull_images(baseimages)
            image_processor.tag_and_push_images(baseimages, ecr_repositories, region, account)
            image_processor.get_images_digest(baseimages, ecr_repositories, region, account)

if __name__ == '__main__':
    # Url = "https://d2hvyiie56hcat.cloudfront.net/windows/amd64/installer/latest/aws-signer-notation-cli.msi"
    main()
    image_siging_process()
