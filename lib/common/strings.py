from typing import Dict, Optional

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


