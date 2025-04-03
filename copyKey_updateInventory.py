import subprocess
import os

# Path to your SSH private and public key
private_key_path = os.path.expanduser("~/.ssh/id_rsa")
public_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")

# Path to your Ansible inventory file
inventory_file_path = "/path/to/your/Ansible_repo/inventory.ini"

# Terraform command to fetch the output
terraform_command = "terraform output -json instance_ips"

# Run the Terraform command to get instance IPs
def get_instance_ips():
    try:
        result = subprocess.run(terraform_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        # Parse the JSON output from Terraform to get the list of IPs
        return subprocess.check_output("echo '{}' | jq -r '.instance_ips.value[]'".format(output), shell=True).decode().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching instance IPs: {e.stderr.decode()}")
        return []

# Use ssh-copy-id to copy the SSH public key to the instance
def copy_ssh_key_to_instance(instance_ip):
    try:
        # Use subprocess to call the ssh-copy-id command
        print(f"Copying SSH key to {instance_ip}...")
        subprocess.run(["ssh-copy-id", "-i", public_key_path, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", f"ubuntu@{instance_ip}"], check=True)
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
