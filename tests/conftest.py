from typing import Tuple, Dict
import pytest
from pathlib import Path
import os

import corrosiffpy

# for playing around on my computer and not dealing with dropbox stuff

# get the path to the current conftest.py file
# and then get the path to the `data` directory

def local_files():
    """
    Fixture to provide a list of all files in the `data` directory.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    files = []
    for root, _, filenames in os.walk(data_dir):
        for filename in filenames:
            if Path(filename).suffix == ".siff":
                files.append(os.path.join(root, filename))
    
    return files

LOCAL_TEST_FILES = local_files()

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

    dbx = Dropbox(
        app_key= DROPBOX_APP_KEY,
        app_secret=DROPBOX_SECRET_TOKEN,
        oauth2_refresh_token=REFRESH_TOKEN,
    )

    dbx.check_and_refresh_access_token()
    link = dropbox.files.SharedLink(url=SHARED_LINK)

    # link = dbx.sharing_get_shared_link_metadata(SHARED_LINK)

    for x in dbx.files_list_folder('', shared_link=link).entries:
        meta, response = dbx.sharing_get_shared_link_file(link.url, path = f'/{x.name}')
        with open(local_path / meta.name, 'wb') as f:
            f.write(response.content)


@pytest.fixture(scope='session')
def siffreaders(tmp_path_factory) -> Tuple['corrosiffpy.SiffIO']:
    
    # Create a temporary directory, install
    # files from the server to it.
    
    tmp_dir = tmp_path_factory.mktemp("test_siff_files")

    if 'DROPBOX_SECRET' not in os.environ:
        # Copy local test files to the temporary directory
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        import json
        print(os.path.join(data_dir, 'local_keys.json'))
        with open(os.path.join(data_dir, 'local_keys.json')) as f:
            keys : Dict = json.load(f)
            for k,v in keys.items():
                os.environ[k] = v

    download_files_from_dropbox(tmp_dir)
    return tuple(
        [
            corrosiffpy.open_file(str(filename))
            for filename in tmp_dir.glob('*.siff')
        ]
    )
