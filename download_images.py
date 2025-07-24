#!/usr/bin/env python3

# will extract urls from the custom.ipxe file
# and then download the files to the images directory
# into a subdirectory names after the host and os version

import os
import re
import requests
import argparse
from urllib.parse import urlparse

def extract_ubuntu_release(url):
    """
    Extracts and normalizes the Ubuntu release from a URL.
    Returns 'version-codename' (e.g., '18.04-bionic'), or just version/codename if only one is found, or 'unknown'.
    """
    version_codename_map = {
        "24.04": "noble",
        "23.10": "mantic",
        "22.04": "jammy",
        "21.10": "impish",
        "21.04": "hirsute",
        "20.04": "focal",
        "19.10": "eoan",
        "19.04": "disco",
        "18.04": "bionic",
        "16.04": "xenial",
        "14.04": "trusty",
        "12.04": "precise",
        "10.04": "lucid"
    }
    codename_version_map = {v: k for k, v in version_codename_map.items()}

    codenames = list(codename_version_map.keys())
    codename_pattern = r'(' + '|'.join(codenames) + r')'
    version_pattern = r'(\d{2}\.\d{2})'

    codename = None
    version = None

    # 1. Try to match codename and version as before
    codename_match = re.search(codename_pattern, url)
    if codename_match:
        codename = codename_match.group(1)

    version_match = re.search(version_pattern, url)
    if version_match:
        version = version_match.group(1)

    # 2. Try to match u18, u2004, etc.
    u_short_match = re.search(r'u(\d{2})(?!\d)', url)  # u18
    u_long_match = re.search(r'u(\d{2})(\d{2})', url)  # u2004

    if not version:
        if u_long_match:
            version = f"{u_long_match.group(1)}.{u_long_match.group(2)}"
        elif u_short_match:
            # Map u18 to 18.04, u20 to 20.04, etc.
            version = f"{u_short_match.group(1)}.04"

    # Try to fill in the missing component
    if version and not codename:
        codename = version_codename_map.get(version)
    if codename and not version:
        version = codename_version_map.get(codename)

    if version and codename:
        return f"{version}-{codename}"
    elif version:
        return version
    elif codename:
        return codename
    else:
        return "unknown"

def download_images(ipxe_file, images_dir, dry_run=False):
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    urls = []
    with open(ipxe_file, 'r') as file:
        for line in file:
            stripped = line.lstrip()
            if stripped.startswith('#'):
                continue  # Skip commented lines
            urls.extend(re.findall(r'(https?://[^\s]+)', line))

    for url in urls:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        release = extract_ubuntu_release(url)
        if release:
            subdir = os.path.join(images_dir, parsed_url.netloc, release)
        else:
            subdir = os.path.join(images_dir, parsed_url.netloc)

        if not os.path.exists(subdir):
            os.makedirs(subdir)

        file_path = os.path.join(subdir, filename)

        if dry_run:
            print(f'DRY RUN: Would download {url} to {file_path}')
            continue

        # Download the file
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f'Downloaded {url} to {file_path}')
        else:
            print(f'Failed to download {url}: {response.status_code}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from custom.ipxe URLs.")
    parser.add_argument('--dry-run', '-d', action='store_true', help='Print URLs and destinations without downloading')
    parser.add_argument('--ipxe-file', default='custom.ipxe', help='Path to your custom.ipxe file')
    parser.add_argument('--images-dir', default='images', help='Directory where images will be saved')
    args = parser.parse_args()

    download_images(args.ipxe_file, args.images_dir, dry_run=args.dry_run)
    print("Download completed." if not args.dry_run else "Dry run completed.")