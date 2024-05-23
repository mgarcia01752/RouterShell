import hashlib
import re
from typing import Dict, List, Optional

from lib.common.constants import STATUS_OK, STATUS_NOK

class StringFormats:
    
    @staticmethod
    def modify_dict_value(dictionary: Dict[str, Optional[str]], key: str, search: str, replace: str) -> bool:
        """
        Modify the value associated with the given key in the dictionary.
        Strip leading and trailing whitespaces and replace a specified substring.

        Parameters:
            dictionary (Dict[str, Optional[str]]): The dictionary to modify.
            key (str): The key whose value needs to be modified.
            search (str): The substring to search for in the value.
            replace (str): The substring to replace 'search' with in the value.

        Returns:
            bool: STATUS_OK if the modification was successful, STATUS_NOK otherwise.
        """
        if key in dictionary:
            value = dictionary[key]
            if isinstance(value, str):
                # Strip leading and trailing whitespaces
                value_stripped = value.strip()

                # Replace the specified substring
                value_modified = value_stripped.replace(search, replace)

                # Update the dictionary with the modified value
                dictionary[key] = value_modified
                
                return STATUS_OK  # Return True to indicate success
        
        return STATUS_NOK  # Return False to indicate failure

    @staticmethod
    def generate_hash_from_list(data: List[str]) -> str:
        """
        Generate a hash value from a list of strings.

        Args:
            data (List[str]): The list of strings to be hashed.

        Returns:
            str: The hexadecimal representation of the generated hash value.
        """
        # Concatenate all strings in the list
        combined_data = ''.join(data)

        # Generate a hash using SHA-256 algorithm
        hash_object = hashlib.sha256(combined_data.encode())

        # Get the hexadecimal representation of the hash
        hashed_result = hash_object.hexdigest()

        return hashed_result

    @staticmethod
    def reduce_ws(text: str) -> str:
        """
        Reduces excessive whitespace in a string to a single space.

        Args:
            text (str): The input string with potentially excessive whitespace.

        Returns:
            str: The modified string with reduced whitespace.
        """
        return re.sub(r'\s+', ' ', text)