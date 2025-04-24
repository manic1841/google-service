import win32com.client


class ShortCut:
    def __init__(self):
        # Initialize the Windows Shell object
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def create_shortcut(self, target, shortcut_path, working_dir=None, description="", icon=None):
        # Create the shortcut
        shortcut = self.shell.CreateShortCut(shortcut_path)

        # Set the target of the shortcut
        shortcut.TargetPath = target

        # Set the working directory (optional)
        if working_dir:
            shortcut.WorkingDirectory = working_dir

        # Set a description for the shortcut (optional)
        shortcut.Description = description

        # Set the icon for the shortcut (optional)
        if icon:
            shortcut.IconLocation = icon

        # Save the shortcut
        shortcut.save()

    def get_target_path(self, shortcut_path):
        # Load the shortcut
        shortcut = self.shell.CreateShortCut(shortcut_path)

        # Return the target path (real path) of the shortcut
        return shortcut.TargetPath