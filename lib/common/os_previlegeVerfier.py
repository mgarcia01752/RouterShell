import os
import grp

class OsPrivilegeVerifier:
    """Static class to check for root user and root group membership."""
    
    @staticmethod
    def is_root_user() -> bool:
        """
        Check if the current user is the root user.
        
        Returns:
            bool: True if the current user is root, False otherwise.
        """
        return os.geteuid() == 0

    @staticmethod
    def is_in_root_group() -> bool:
        """
        Check if the current user belongs to the root group.
        
        Returns:
            bool: True if the current user is in the root group, False otherwise.
        """
        try:
            root_gid = grp.getgrnam('root').gr_gid
            user_groups = os.getgroups()
            return root_gid in user_groups
        except KeyError:
            # This might happen if the 'root' group does not exist
            return False

    @staticmethod
    def has_root_privileges() -> bool:
        """
        Check if the user is root or in the root group.
        
        Returns:
            bool: True if the user is root or in the root group, False otherwise.
        """
        return OsPrivilegeVerifier.is_root_user() or OsPrivilegeVerifier.is_in_root_group()
