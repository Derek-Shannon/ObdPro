import requests
import os
import threading
import tkinter as tk
from tkinter import messagebox

class GitHubUpdater:
    """
    A class to handle fetching and downloading the latest release from a GitHub repository.
    """
    def __init__(self, repo_owner, repo_name):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def get_latest_release_url(self):
        """
        Fetches the download URL for the latest release asset from the repository.
        Returns the URL or None if an error occurs.
        """
        api_url = f"{self.api_base_url}/releases/latest"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            release_data = response.json()
            
            # Assuming the asset is a single file in the release,
            # we grab the URL of the first asset.
            if release_data['assets']:
                return release_data['assets'][0]['browser_download_url']
            else:
                print("Error: No assets found in the latest release.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching release info: {e}")
            return None

    def download_file(self, url, save_path):
        """
        Downloads a file from a given URL and saves it to a specified path.
        Returns the path to the downloaded file or None on error.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            filename = os.path.basename(url)
            file_path = os.path.join(save_path, filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded to: {file_path}")
            return file_path
        
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            return None

### Example Usage: Tkinter Application
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Updater")
        
        # Replace with your repository details
        self.repo_owner = "your-username"
        self.repo_name = "your-repository"
        self.save_directory = os.path.expanduser("~/Downloads") # Example save path
        
        # Create an instance of the GitHubUpdater class
        self.updater = GitHubUpdater(self.repo_owner, self.repo_name)
        
        # Create the button
        self.download_button = tk.Button(self, text="Download Latest Version", command=self.on_download_click)
        self.download_button.pack(pady=20, padx=20)
        
    def on_download_click(self):
        """
        Handles the button click event. Starts a new thread for the download.
        """
        self.download_button.config(state=tk.DISABLED)
        messagebox.showinfo("Download", "Checking for latest version...")
        
        # Start the download process in a separate thread
        threading.Thread(target=self._perform_download_thread).start()

    def _perform_download_thread(self):
        """
        The download logic to be run in the background thread.
        This must not directly call GUI functions.
        """
        download_url = self.updater.get_latest_release_url()
        
        if download_url:
            downloaded_file_path = self.updater.download_file(download_url, self.save_directory)
            
            # Use self.after() to schedule the GUI update back on the main thread
            if downloaded_file_path:
                self.after(0, self._show_success_message, downloaded_file_path)
            else:
                self.after(0, self._show_error_message, "Download failed.")
        else:
            self.after(0, self._show_error_message, "Could not find latest release.")

    def _show_success_message(self, file_path):
        """
        Shows a success message and re-enables the button.
        This is called from the main thread.
        """
        messagebox.showinfo("Success", f"Download complete!\nFile saved at: {file_path}")
        self.download_button.config(state=tk.NORMAL)

    def _show_error_message(self, message):
        """
        Shows an error message and re-enables the button.
        This is called from the main thread.
        """
        messagebox.showerror("Error", message)
        self.download_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = App()
    app.mainloop()