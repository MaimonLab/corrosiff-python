from typing import Tuple
import pytest
from pathlib import Path
import os

import corrosiffpy

LOCAL_TEST_FILES = [
    '/Users/stephen/Desktop/Data/imaging/2024-04/2024-04-17/21Dhh_GCaFLITS/Fly1/Flashes_1.siff',
    '/Users/stephen/Desktop/Data/imaging/2024-05/2024-05-27/R60D05_TqCaFLITS/Fly1/EBAgain_1.siff',
    '/Users/stephen/Desktop/Data/imaging/2024-05/2024-05-27/SS02255_greenCamui_alpha/Fly1/PB_1.siff',
]

def download_files_from_dropbox(local_path : Path):
    """
    Accesses the .siff files from the shared link
    on Dropbox. Short-to-medium term filesharing
    solution
    """
    from dropbox import Dropbox
    import dropbox

    DROPBOX_SECRET_TOKEN = os.environ['DROPBOX_SECRET']
    DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
    REFRESH_TOKEN = os.environ['DROPBOX_REFRESH_TOKEN']
    SHARED_LINK = os.environ['DROPBOX_SHARED_LINK']

    dbx = Dropbox(app_key= DROPBOX_APP_KEY, app_secret=DROPBOX_SECRET_TOKEN, oauth2_refresh_token=REFRESH_TOKEN)

    dbx.check_and_refresh_access_token()
    link = dropbox.files.SharedLink(url=SHARED_LINK)

    for x in dbx.files_list_folder('', shared_link=link).entries:
        meta, response = dbx.sharing_get_shared_link_file(link.url, path = f'/{x.name}')
        with open(local_path / meta.name, 'wb') as f:
            f.write(response.content)


@pytest.fixture(scope='session')
def siffreaders(tmp_path_factory) -> Tuple['corrosiffpy.SiffIO']:
    
    # Create a temporary directory, install
    # files from the server to it.
    
    tmp_dir = tmp_path_factory.mktemp("test_siff_files")

    if 'DROPBOX_SECRET_TOKEN' in os.environ:
        download_files_from_dropbox(tmp_dir)
    else:
        # Copy local test files to the temporary directory
        for file in LOCAL_TEST_FILES:
            file_path = Path(file)
            file_name = file_path.name
            os.system(f'cp {file} {tmp_dir}/{file_name}')

    return tuple(
        [
            corrosiffpy.open_file(str(filename))
            for filename in tmp_dir.glob('*.siff')
        ]
    )
