import subprocess
import re
import os
import pwd
import grp

def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def set_file_ownership(file_path, user, group):
    """Set the ownership of the file to the specified user and group."""
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    os.chown(file_path, uid, gid)

def cancel_transactions(password):
    # Step 1: Get the transactions
    command = f"echo '{password}' | grin-wallet txs"
    output = run_command(command)

    # Step 2: Write the output to a file
    file_path = 'transactions.txt'
    with open(file_path, 'w') as file:
        file.write(output)

    # Step 3: Set the ownership of the file to user 'grin' and group 'grin'
    set_file_ownership(file_path, 'grin', 'grin')

    # Step 4: Read the file and process transactions
    with open(file_path, 'r') as file:
        lines = file.readlines()

    canceled_count = 0
    skipped_count = 0

    # Step 5: Find unconfirmed transactions that are not canceled
    for line in lines:
        # Match the transaction line with regex, accounting for varying spaces
        match = re.match(r'^\s*(\d+)\s+\w+\s+\w+\s+(\S+)\s+.*?\s+(false)\s+.*?\s+(\S+)\s*$', line)
        if match:
            transaction_id = match.group(2)
            confirmed = match.group(3)
            canceled = '-Cancelled' in line

            if confirmed == 'false' and not canceled:
                # Step 6: Cancel the transaction
                cancel_command = f"echo '{password}' | grin-wallet cancel -t {transaction_id}"
                print(f"Cancelling transaction {transaction_id}...")
                cancel_output = run_command(cancel_command)
                print(cancel_output)
                canceled_count += 1
            else:
                skipped_count += 1

    # Step 7: Output the summary
    print(f"\nSummary:")
    print(f"Total transactions canceled: {canceled_count}")
    print(f"Total transactions skipped: {skipped_count}")

if __name__ == "__main__":
    # Replace '<password>' with your actual password
    password = '<password>'
    cancel_transactions(password)

