#!/usr/bin/env python3

import requests
import os
import shutil

from client import create_google_client

API_NAME = 'photoslibrary'
API_VERSION = 'v1'
SCOPE = [
    'https://www.googleapis.com/auth/photoslibrary'
]

def list_all_albums(service):
    response = service.albums().list().execute()
    albums_list = response['albums']
    next_page_token = response.get('nextPageToken')
    while next_page_token:
        response = service.albums(
            pageToken=next_page_token
        ).list().execute()
        albums_list.append(response['albums'])
        next_page_token = response.get('next_page_token')

    # list all albums title
    print(len(albums_list))
    for album in albums_list:
        print(album['title'])

    return albums_list

def create_new_album(service, title):
    body = {
        'album': {
            'title': title
        }
    }
    response = service.albums().create(body=body).execute()
    new_album = response
    return new_album

def get_ascii_string(s: str):
    if s.isascii():
        return s

    s = filter(lambda i: i.isascii(), s)
    return ''.join(['IMG'] + list(s))

def upload_file_to_google(filename, folder, creds):
    """
    Return:
        str: Upload Token
    """
    upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
        'Authorization': 'Bearer ' + creds.token,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Protocol': 'raw'
    }


    headers['X-Goog-Upload-File-Name'] = get_ascii_string(filename)
    with open(os.path.join(folder, filename), 'rb') as img:
        response = requests.post(upload_url, data=img.read(), headers=headers)

    return response.content.decode('utf-8')

def add_batch_photo_to_album(service, album_id, upload_token_list):
    n = len(upload_token_list)

    first = 0
    while n > 0:
        count = n if n < 50 else 50
        n = n - count
        token_list = upload_token_list[first:first + count]
        first = first + count

        new_media_items = []
        for token in token_list:
            new_media_items.append({
                'simpleMediaItem': {
                    'uploadToken': token
                }
            })

        body = {
            'albumId': album_id,
            'newMediaItems': new_media_items
        }
        response = service.mediaItems().batchCreate(body=body).execute()

        # show upload result
        results = response['newMediaItemResults']
        for res in results:
            status = res['status']
            mediaItem = res.get('mediaItem')
            if mediaItem:
                filename = mediaItem['filename']
                print(f'File: {filename}, status: {status["message"]}')
            elif mediaItem is None:
                print(f'Miss mediaItem: {res}')
            elif (status['message'] != 'Success' and
                status['message'] != 'OK' and
                status['code'] != 6):
                print(f'status is not Success: {res}')

    return True

def upload_photos_to_new_album(service, album_title, folder, creds):
    is_running = True
    # create new album
    new_album = create_new_album(service, album_title)
    print(f'Create Album: {new_album["title"]}')

    upload_token_list = []
    # step 1: upload byte data to Google
    for file in os.listdir(folder):
        if file.endswith('.json') or file.endswith('.AAE'):
            continue
        print(f'Upload file: {file}')
        token = upload_file_to_google(file, folder, creds)
        # print(f'Upload token: {token}')
        upload_token_list.append(token)

    # No photo in folder
    if len(upload_token_list) == 0:
        return is_running

    # step 2: Add file to photolibrary and album
    is_running = add_batch_photo_to_album(service, new_album['id'], upload_token_list)

    return is_running


def main():
    # create album
    service, creds = create_google_client(API_NAME, API_VERSION, SCOPE)

    # # get all albums
    # list_all_albums(service)

    is_running = True

    target_folder_list = []
    skip_folder_list = []
    image_dir = 'D:\Pictures\大大'
    for folder_name in os.listdir(image_dir):
        if not is_running:
            break

        folder = os.path.join(image_dir, folder_name)
        if not os.path.isdir(folder):
            continue

        if len(folder_name) < 6 or not folder_name[:6].isnumeric():
            album_title = folder_name
            target_folder_list.append({
                'folder': folder_name,
                'album_title': album_title
            })
            # print(f'Get folder: {folder_name}, Create album: {album_title}')
        else:
            date = int(folder_name[:6])
            if date <= 160905:
                skip_folder_list.append({
                    'folder': folder_name
                })
                # print(f'Skip folder: {folder_name}')
            else:
                album_title = '20' + folder_name
                target_folder_list.append({
                    'folder': folder_name,
                    'album_title': album_title
                })
                # print(f'Get folder: {folder_name}, Create album: {album_title}')

    # print(f"Skip folder count: {len(skip_folder_list)}")
    # for f in skip_folder_list:
    #     print(f'Skip folder: {f["folder"]}')

    def sort_cb(item):
        album_title = item['album_title']
        if album_title.startswith('20'):
            return int(album_title[:8])
        else:
            return 99999999
    target_folder_list.sort(key=sort_cb)
    # print(f"Target folder count: {len(target_folder_list)}")
    # for f in target_folder_list:
    #     print(f'Target folder: {f["folder"]}, album title: {f["album_title"]}')

    n = len(target_folder_list)
    i = 0
    for f in target_folder_list:
        i = i + 1
        folder_name = f['folder']
        album_title = f['album_title']
        folder = os.path.join(image_dir, folder_name)
        print(f'=== Get folder: {folder_name} ======')
        if not upload_photos_to_new_album(service, album_title, folder, creds):
            print('Error!!!')
            break
        new_folder = os.path.join('D:\\Pictures\\完成', folder_name)
        shutil.move(folder, new_folder)
        print(f'=== Finish ({i}/{n})===')


if __name__ == '__main__':
    main()
