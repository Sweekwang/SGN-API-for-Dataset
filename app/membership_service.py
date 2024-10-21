import re
from cryptography.fernet import Fernet
from phonenumbers import parse as parse_phone, is_valid_number, NumberParseException

class MembershipService:
    """Handles membership data validation, encryption, and retrieval."""
    
    email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    def __init__(self, fernet_key=None):
        """
        Initializes MembershipService with a specified Fernet key.
        Generates a new key if not provided.
        """
        if fernet_key:
            self.fernet_key = fernet_key
        else:
            self.fernet_key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.fernet_key)

    def validate_full_name(self, full_name):
        """
        Validates the full name, ensuring it is a non-empty string.
        """
        if not full_name or not isinstance(full_name, str) or not full_name.strip():
            raise ValueError("Full name must be a non-empty string.")
        return True

    def validate_email(self, email):
        """
        Validates the email format using a regex pattern.
        """
        if not email or not self.email_regex.match(email):
            raise ValueError("Invalid email format.")
        return True

    def validate_phone(self, phone, region='SG'):
        """
        Validates the phone number format.
        """
        try:
            phone_obj = parse_phone(phone, region)
            if not is_valid_number(phone_obj):
                raise ValueError("Invalid phone number.")
            return True
        except NumberParseException:
            raise ValueError("Invalid phone number.")

    def encrypt_data(self, data):
        """
        Encrypts the given data using Fernet encryption.
        """
        if not isinstance(data, str) or not data.strip():
            raise ValueError("Data must be a non-empty string.")
        
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """
        Decrypts the given encrypted data using Fernet decryption.
        """
        if not isinstance(encrypted_data, str) or not encrypted_data.strip():
            raise ValueError("Encrypted data must be a non-empty string.")
        
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def get_fernet_key(self):
        """
        Returns the current Fernet encryption key.
        """
        return self.fernet_key.decode()

# Example usage
if __name__ == "__main__":
    service = MembershipService()

    # Sample data for validation and encryption
    full_name = "John Doe"
    email = "john.doe@example.com"
    phone = "+14155552671"

    try:
        # Validate data
        service.validate_full_name(full_name)
        service.validate_email(email)
        service.validate_phone(phone)

        # Encrypt and decrypt data
        encrypted_name = service.encrypt_data(full_name)
        decrypted_name = service.decrypt_data(encrypted_name)

        print(f"Encrypted Name: {encrypted_name}")
        print(f"Decrypted Name: {decrypted_name}")

    except ValueError as e:
        print(f"Validation Error: {str(e)}")
