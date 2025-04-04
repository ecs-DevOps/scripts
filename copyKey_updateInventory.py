import subprocess
import os
import json

# Path to your SSH private and public key
private_key_path = os.path.expanduser("~/.ssh/id_rsa")
public_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")

# Path to your Ansible inventory file
inventory_file_path = "/home/ubuntu/Ansible_repo/inventory.ini"

# Terraform directory (set this to the correct relative path)
terraform_dir = "/home/ubuntu/terraform-ec2"  # Adjust the path as needed

# Run the Terraform command to get instance IPs
def get_instance_ips():
    try:
        # Change the working directory to the Terraform configuration folder
        result = subprocess.run(
            ["terraform", "output", "-json", "instance_ips"],
            cwd=terraform_dir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Decode the output and parse the JSON to get the IPs
        output = result.stdout.decode('utf-8')
        instance_ips = json.loads(output)

        # Return the list of IPs (flattening if it's nested)
        return instance_ips
    except subprocess.CalledProcessError as e:
        print(f"Error fetching instance IPs: {e.stderr.decode()}")
        return []

# Use ssh-copy-id to copy the SSH public key to the instance
def copy_ssh_key_to_instance(instance_ip):
    try:
        # Use subprocess to call the ssh-copy-id command
        print(f"Copying SSH key to {instance_ip}...")
        subprocess.run(
            ["ssh-copy-id", "-i", public_key_path, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", f"ubuntu@{instance_ip}"],
            check=True
        )
        print(f"Successfully copied the SSH public key to {instance_ip}")
    except subprocess.CalledProcessError as e:
        print(f"Error copying SSH key to {instance_ip}: {str(e)}")

# Update the Ansible inventory file
def update_inventory_file(instance_ip, instance_name):
    try:
        # Open the inventory file in append mode
        with open(inventory_file_path, 'a') as inventory_file:
            inventory_file.write(f"\n{instance_name} ansible_host={instance_ip} ansible_user=ubuntu ansible_ssh_private_key_file={private_key_path}")
        print(f"Successfully updated inventory file with {instance_name} ({instance_ip})")
    except Exception as e:
        print(f"Error updating inventory file: {str(e)}")

# Main function to run the process
def main():
    # Get instance IPs from Terraform output
    instance_ips = get_instance_ips()

    if not instance_ips:
        print("No instances found.")
        return

    # Process each instance
    for idx, ip in enumerate(instance_ips):
        # Generate a name for the instance, e.g., instance-<idx>
        instance_name = f"instance-{idx + 1}"
        
        # Step 1: Copy SSH public key to the instance
        copy_ssh_key_to_instance(ip)
        
        # Step 2: Update the Ansible inventory file
        update_inventory_file(ip, instance_name)

if __name__ == "__main__":
    main()
