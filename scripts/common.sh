
# Function to switch to a new shell environment
function toShell() {
    /usr/bin/env bash
}

function createUserSshPublicKey() {
    local username="$1"
    
    # Check if username is provided
    if [[ -z "$username" ]]; then
        echo "Usage: createUserSshPublicKey <username>"
        return 1
    fi

    # Check if user already exists
    if id "$username" &>/dev/null; then
        echo "User $username already exists."
        return 1
    fi

    # Generate RSA key pair
    ssh-keygen -t rsa -b 4096 -C "$username@localhost" -f "/home/$username/.ssh/id_rsa" -N ""

    # Generate DSA key pair
    ssh-keygen -t dsa -b 1024 -C "$username@localhost" -f "/home/$username/.ssh/id_dsa" -N ""

    # Generate ECDSA key pair
    ssh-keygen -t ecdsa -b 521 -C "$username@localhost" -f "/home/$username/.ssh/id_ecdsa" -N ""

    # Generate Ed25519 key pair
    ssh-keygen -t ed25519 -C "$username@localhost" -f "/home/$username/.ssh/id_ed25519" -N ""

    # Display public keys
    echo "Public keys for user $username:"
    cat "/home/$username/.ssh/id_rsa.pub"
    cat "/home/$username/.ssh/id_dsa.pub"
    cat "/home/$username/.ssh/id_ecdsa.pub"
    cat "/home/$username/.ssh/id_ed25519.pub"
}


