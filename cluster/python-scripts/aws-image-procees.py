import yaml
import subprocess
import boto3
import os
import json
import botocore

class ImageProcessor:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        
        # Initialize a Boto3 Signer client
        self.ecr_client = boto3.client('ecr')
        self.signer_client = boto3.client('signer')

    def read_yaml(self):
        with open(self.yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            accounts = data.get('accounts', [])

            account_info = []  # List to store account info, including region and base images

            for account_data in accounts:
                account_info.append(account_data)

            return account_info

    def pull_images(self, baseimages):
        for image_info in baseimages:
            name = image_info['name']
            subprocess.run(['docker', 'pull', f'{name}'])

    def create_ecr_repository(self, ecrrepo):
        try:
            response = self.ecr_client.create_repository(repositoryName=ecrrepo)
            return response['repository']['repositoryUri']
        except self.ecr_client.exceptions.RepositoryAlreadyExistsException:
            # Repository already exists, return the URI
            return f'{self.ecr_client.describe_repositories(repositoryNames=[ecrrepo])["repositories"][0]["repositoryUri"]}'

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
    
    def sign_images(self, image_data, ecr_rep, region, account):
        # Here you need to parse image digest
        signer_arn = self.create_or_get_signer_profile(ecr_rep)

        try:
            command = f'notation sign {account}.dkr.ecr.{region}.amazonaws.com/{ecr_rep}@{image_data} --plugin com.amazonaws.signer.notation.plugin --id {signer_arn}'
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

if __name__ == '__main__':
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
