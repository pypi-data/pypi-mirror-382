from brynq_sdk_brynq import BrynQ
import os
from typing import List, Union, Literal, Optional
import requests
import json
from io import BytesIO
import typing


class Sharepoint(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, site: str = None, site_id: str = None, json_subset: int = None, site_name: str = None, debug: bool = False, deviating_data_interface_id: int = None):
        """
        :param label: label of the sharepoint system in BrynQ
        :param site: base url of the sharepoint site
        :param site_id: site id of the sharepoint site
        :param json_subset: fill in the part of the json that needs to be accessed to get the wanted drive id, accompanying the drive you are looking for
        :param debug: set to True to enable debug logging
        :param deviating_data_interface_id: Sometimes you need to get credentials from another data interface. This is the data interface id of the data interface you want to get the credentials from.
        """
        super().__init__()
        self.system_type = system_type
        self.data_interface_id = deviating_data_interface_id if deviating_data_interface_id is not None else self.data_interface_id
        credentials = self.interfaces.credentials.get(system="sharepoint", system_type=system_type)
        credentials = credentials.get('data')
        self.debug = debug
        self.timeout = 3600
        if self.debug:
            print(f"credentials: {credentials}")
        self.access_token = credentials['access_token']
        if site_name is not None:
            self.json_subset = 0 if json_subset is None else json_subset
            self.site_id = self.get_site_id(site_name=site_name)
        elif site_id is not None:
            self.site_id = f"{site},{site_id}"
            self.json_subset = json_subset
        else:
            raise KeyError('Either site_name or site_id, site and json_subset must be provided')
        if self.debug:
            print(f"site_id: {self.site_id}, json_subset: {self.json_subset}, credentials: {credentials}")

    def _refresh_credentials(self):
        credentials = self.interfaces.credentials.get(system="sharepoint", system_type=self.system_type)
        credentials = credentials.get('data')
        self.access_token = credentials['access_token']

    def _get_sharepoint_headers(self):
        self._refresh_credentials()
        headers = {'Authorization': f'Bearer {self.access_token}'}
        if self.debug:
            print(headers)

        return headers

    def get_site_id(self, site_name: str) -> str:
        """
        Get the site id of a site
        :param site_name: name of the site
        :return: site id
        """
        url = f'https://graph.microsoft.com/v1.0/sites?search={site_name}'
        if self.debug:
            print(f"url: {url}")
        response = requests.get(url=url, headers=self._get_sharepoint_headers(), timeout=self.timeout)
        response.raise_for_status()
        site_id = response.json()['value'][0]['id']
        if self.debug:
            print(f"site_id: {site_id}")

        return site_id

    def get_driveid(self):
        """
        This method is used to derive the driveid to which the files have to be uploaded. Needed in the upload url for file upload.
        :return: returns the needed driveid
        """
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives'
        if self.debug:
            print(f"url: {url}")
        response = requests.get(url, headers=self._get_sharepoint_headers(), timeout=self.timeout)
        response.raise_for_status()
        drive_id = response.json()['value'][self.json_subset]['id']
        if self.debug:
            print(f"drive_id: {drive_id}")

        return drive_id

    def upload_file(self, local_file_path: str, remote_file_path: str):
        """
        This method performs the actual file upload to the formerly derived site + drive.
        local_file_path: local path of the file you want to upload
        remote_file_path: remote path of the folder and filename where you want to place the file
        """
        drive_id = self.get_driveid()
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{drive_id}/root:/{remote_file_path}:/createUploadSession'
        if self.debug:
            print(f"url: {url}")
        headers = self._get_sharepoint_headers()
        response = requests.post(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        upload_url = response.json()['uploadUrl']
        if self.debug:
            print(f"upload_url: {upload_url}")
        with open(f'{local_file_path}', 'rb') as file_input:
            file_bytes = os.path.getsize(f'{local_file_path}')
            headers_upload = {'Content-Type': 'application/json',
                              'Content-Length': f'{file_bytes}',
                              'Content-Range': f'bytes 0-{file_bytes - 1}/{file_bytes}'}
            response_upload = requests.put(url=upload_url, headers=headers_upload, data=file_input, timeout=self.timeout)
            response_upload.raise_for_status()

        return response_upload

    def open_file(self, remote_file_path: str) -> bytes:
        """
        Get a file from sharepoint as a bytesstream
        remote_file_path: filepath on sharepoint
        :return: bytes of file object
        """
        drive_id = self.get_driveid()
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{drive_id}/root:/{remote_file_path}'
        if self.debug:
            print(f"url: {url}")
        headers = self._get_sharepoint_headers()
        response = requests.get(url=url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        download_url = response.json()['@microsoft.graph.downloadUrl']
        if self.debug:
            print(f"download_url: {download_url}")
        response_download = requests.get(url=download_url, headers=headers, timeout=self.timeout)
        response_download.raise_for_status()

        return response_download.content

    def download_file(self, local_file_path: str, remote_file_path: str):
        """
        This method downloads a file from sharepoint to the local machine.
        local_file_path: local folder where the file will be downloaded to
        remote_file_path: remote path of the file on sharepoint
        """
        driveid = self.get_driveid()
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{driveid}/root:/{remote_file_path}'
        headers = self._get_sharepoint_headers()
        response = requests.get(url=url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        download_url = response.json()['@microsoft.graph.downloadUrl']
        response_download = requests.get(url=download_url, headers=headers, timeout=self.timeout)
        response_download.raise_for_status()
        with open(file=f'{local_file_path}', mode='wb') as f:
            f.write(BytesIO(response_download.content).read())

        return response_download

    def download_files(self, local_folder_path: str, remote_folder_path: str):
        """
        This method downloads a file from sharepoint to the local machine.
        local_folder_path: local folder where the files will be downloaded to
        remote_folder_path: remote path of the folder you want to get on sharepoint
        """
        driveid = self.get_driveid()
        folder_content = self.list_dir(remote_folder_path=remote_folder_path)
        # remove subdirectories, can not be downloaded
        folder_content = [item for item in folder_content if 'file' in item]
        if self.debug:
            print(f"folder_content: {folder_content}")
        filecount = 0

        responses = []
        for file in folder_content:
            url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{driveid}/root:/{remote_folder_path}{file["name"]}'
            if self.debug:
                print(f"url: {url}")
            headers = self._get_sharepoint_headers()
            response = requests.get(url=url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            download_url = response.json()['@microsoft.graph.downloadUrl']
            response_download = requests.get(url=download_url, headers=headers, timeout=self.timeout)
            with open(file=f'{local_folder_path}{file["name"]}', mode='wb') as f:
                f.write(BytesIO(response_download.content).read())
            filecount += 1
            responses.append(response_download)
        print(f'{filecount} files downloaded')

        return responses

    def list_dir(self, remote_folder_path: str, get_files_from_nested_folders: bool = False) -> [json, typing.Generator]:
        """
        Fetch the contents of the API and return the "children"
        which has the information of all the items under that folder
        remote_folder_path: folder path you want to list
        :return: all the contents of the folder items
        """
        if get_files_from_nested_folders:
            return list(self._get_all_files_in_folder(folder_path=remote_folder_path))

        drive_id = self.get_driveid()
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{drive_id}/root:/{remote_folder_path}?expand=children'
        if self.debug:
            print(f"url: {url}")
        response = requests.get(url, headers=self._get_sharepoint_headers(), timeout=120)
        response.raise_for_status()

        return response.json()['children']

    # helpers function to get all files in a nested directory
    def _get_all_files_in_folder(self, folder_path) -> typing.Generator:
        children = self.list_dir(remote_folder_path=folder_path)
        for child in children:
            if 'file' in child:
                yield {"folder": folder_path, "file": child['name'], "id": child['id']}
            else:
                yield from self._get_all_files_in_folder(folder_path=f"{folder_path}/{child['name']}")

    def remove_file(self, remote_file_path: str):
        """
        Remove a file from Sharepoint
        remote_file_path: complete path including filename
        :return: response from Sharepoint
        """
        drive_id = self.get_driveid()
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{drive_id}/root:/{remote_file_path}'
        if self.debug:
            print(f"url: {url}")
        response = requests.delete(url=url, headers=self._get_sharepoint_headers(), timeout=self.timeout)
        response.raise_for_status()

        return response

    def remove_files(self, remote_folder_path: str):
        """
        Remove a file from Sharepoint
        remote_folder_path: folder path that you want to empty
        """
        drive_id = self.get_driveid()
        folder_content = self.list_dir(remote_folder_path=remote_folder_path)
        responses = []
        for file in folder_content:
            url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{drive_id}/root:/{remote_folder_path}{file["name"]}'
            if self.debug:
                print(f"url: {url}")
            response = requests.delete(url=url, headers=self._get_sharepoint_headers(), timeout=self.timeout)
            response.raise_for_status()
            responses.append(response)

        return responses

    def remove_folder(self, folder_id: str):
        """
        Remove a folder from Sharepoint
        folder: folder id that you want to delete
        """
        drive_id = self.get_driveid()
        url = f'https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{drive_id}/items/{folder_id}'
        if self.debug:
            print(f"url: {url}")
        response = requests.delete(url=url, headers=self._get_sharepoint_headers(), timeout=self.timeout)
        response.raise_for_status()

        return response
