# ---------------------------------------------------------
# Copyright (c) vuepy.org. All rights reserved.
# ---------------------------------------------------------
import panel as pn


class NotificationsManager:
    """
    Manager class for Panel notifications that provides methods to create and manage notifications.
    This class is designed to be used as a singleton accessed through the notifications global.
    """
    
    def __init__(self):
        self._notifications = pn.state.notifications
    
    def info(self, message: str, duration: int = 3000, title: str = None):
        """
        Display an informational notification.
        
        Args:
            message: The message to display
            duration: Duration in milliseconds to display the notification
            title: Optional title for the notification
        """
        return self._notifications.info(message, duration=duration, title=title)
    
    def success(self, message: str, duration: int = 3000, title: str = None):
        """
        Display a success notification.
        
        Args:
            message: The message to display
            duration: Duration in milliseconds to display the notification
            title: Optional title for the notification
        """
        return self._notifications.success(message, duration=duration, title=title)
    
    def warning(self, message: str, duration: int = 3000, title: str = None):
        """
        Display a warning notification.
        
        Args:
            message: The message to display
            duration: Duration in milliseconds to display the notification
            title: Optional title for the notification
        """
        return self._notifications.warning(message, duration=duration, title=title)
    
    def error(self, message: str, duration: int = 3000, title: str = None):
        """
        Display an error notification.
        
        Args:
            message: The message to display
            duration: Duration in milliseconds to display the notification
            title: Optional title for the notification
        """
        return self._notifications.error(message, duration=duration, title=title)
    
    def clear(self):
        """
        Clear all current notifications.
        """
        return self._notifications.clear()


# Create a global singleton instance
notifications = NotificationsManager()
