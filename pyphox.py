from __future__ import print_function
import os
import io
import zipfile
import datetime
import requests
import argparse
import lxml.html as lh
from multiprocessing import Pool


def get_links(data_type='daily', version='current'):
    """
    Function to pull the links from the Phoenix data website.

    Parameters
    ----------

    data_type: String.
                Which data source to download: daily or historical.

    version: String.
                Data version. Defaults to current.

    Returns
    -------

    dl_links: List.
                Links to data files.

    """

    if data_type == 'daily':
        if version == 'current':
            page = requests.get('http://phoenixdata.org/data/current')
        elif version == 'v010':
            page = requests.get('http://phoenixdata.org/data/v010')

        print('Obtaining daily links...')
        text = page.content
        doc = lh.fromstring(text)

        table = doc.xpath('//table[@name="data"]')
        dl_links = []
        for link in table[0].iterlinks():
            dl_links.append(link[2])

        return dl_links
    elif data_type == 'historical':
        pass
    elif data_type == 'update':
        if version == 'current':
            link_root = 'https://s3.amazonaws.com/oeda/data/current/events.full.'
            d = datetime.datetime.now() - datetime.timedelta(days=1)
            d_string = '{}{:02d}{:02d}'.format(d.year, d.month, d.day)
            link = '{}{}.txt.zip'.format(link_root, d_string)

            dl_links = [link]

            return dl_links
    else:
        print('Please enter a valid data type: daily, historical, or update.')


def download_data(link, directory, unzip=False):
    """

    Parameters
    ----------

    link: String.
            Link to a data file.

    directory: String.
               Directory to write the downloaded file.

    unzip: Boolean.
            Whether to unzip the downloaded file.
    """
    print('Downloading data from {}...'.format(link))
    link_file = link.split('/')[-1]
    zip_file = os.path.join(directory, link_file)
    txt_file = zip_file.replace('.zip', '')
    if not os.path.isfile(zip_file) and not os.path.isfile(txt_file):
        written_file = _download_chunks(directory, link)
        if unzip:
            print('Unzipping {}...'.format(written_file))
            _unzip_file(directory, written_file)
    else:
        print('File for {} already exists. Passing.'.format(link_file))


def _unzip_file(directory, zipped_file):
    """
    Private function to unzip a zipped file that was downloaded.

    Parameters
    ----------
    directory: String.
               Directory to write the unzipped file.

    zipped_file: String.
                 Filepath of the zipped file to unzip.
    """
    print('Unzipping {}'.format(zipped_file))
    try:
        z = zipfile.ZipFile(zipped_file)
        for name in z.namelist():
            f = z.open(name)
            out_path = os.path.join(directory, name)
            with io.open(out_path, 'w', encoding='utf-8') as out_file:
                content = f.read().decode('utf-8')
                out_file.write(content)
        print('Done unzipping {}'.format(zipped_file))
        return out_path
    except zipfile.BadZipfile:
        print('Bad zip file for {}, passing.'.format(zipped_file))


def _download_chunks(directory, url):
    """
    Private function to download a zipped file in chunks.

    Parameters
    ----------
    directory: String.
               Directory to write the downloaded file.

    url: String.
         URL of the file to download.
    """

    base_file = os.path.basename(url)

    temp_path = directory
    try:
        local_file = os.path.join(temp_path, base_file)

        req = requests.get(url, stream=True)
        with io.open(local_file, 'wb') as fp:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)
    except Exception as e:
        print("There was an error: {}; {}".format(e, url))

    return local_file


def parse_cli_args():
    """Function to parse the command-line arguments."""

    aparse = argparse.ArgumentParser(prog='phox_download',
                                     description="""Program to download the
                                     Phoenix datasets.""")

    aparse.add_argument('-t', '--type', help="""Which dataset to download:
                        daily, historical, or update.""", required=True)
    aparse.add_argument('-v', '--version', help="""Which version of the daily
                        data to download. Defaults to current.""",
                        default='current', required=False)
    aparse.add_argument('-d', '--directory', help="""Directory in which to
                        store data.""", required=True)
    aparse.add_argument('-U', '--unzip', action='store_true', default=True,
                        help="""Boolean flag indicating whether or not to unzip
                        the downloaded files. Default to True.""")
    aparse.add_argument('-P', '--parallel', action='store_true', default=False,
                        help="""Boolean flag indicating whether or not to
                        download files in parallel. Default to False.""")

    args = aparse.parse_args()
    return args


if __name__ == '__main__':
    args = parse_cli_args()
    data_type = args.type
    dl_directory = args.directory
    unzip = args.unzip
    version = args.version
    parallel = args.parallel

    links = get_links(data_type=data_type, version=version)
    if parallel:
        pool = Pool(4)
        print('Downloading data asynchronously...')
        results = [pool.apply_async(download_data, (link, dl_directory, unzip))
                   for link in links]
        timeout = [r.get(9999999) for r in results]
        pool.terminate()
    else:
        for link in links:
            download_data(link, dl_directory)
