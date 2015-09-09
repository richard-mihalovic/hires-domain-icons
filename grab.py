from __future__ import print_function
import requests
import lxml.html
import shutil
import os


def __load_domains_from_file():
    domains = []
    with open('domains.txt') as f:
        domains = f.readlines()

    return domains


def __grab_url(url):
    r = requests.get(url)
    return r.text


def __extract_images(html):
    tree = lxml.html.fromstring(html)
    images = []

    elements = tree.xpath('//meta[@property="og:image"]')
    for element in elements:
        images.append(element.get('content'))

    elements = tree.xpath('//link[@rel="apple-touch-icon"]')
    for element in elements:
        images.append(element.get('href'))

    if len(elements) == 0:
        elements = tree.xpath('//link[@rel="shortcut icon"]')
        for element in elements:
            images.append(element.get('href'))

    return images


def __save_image(content, file_name):
    with open(file_name, 'wb') as f:
        f.write(content)


def __extract_file_name(file_name):
    lpos = file_name.rfind('/')
    return file_name[lpos + 1:]


def __extract_extension(file_name):
    lpos = file_name.rfind('.')
    lpos += 1
    return file_name[lpos:lpos + 3]


def __setup_images_directory():
    # delete images directory
    if os.path.exists('images'):
        shutil.rmtree('images')

    # create images directory
    if not os.path.exists('images'):
        os.makedirs('images')

def grab_domain_icons():

    __setup_images_directory()
    for domain in __load_domains_from_file():

        domain = domain.replace('\n', '').replace('\r', '')
        try:
            domain_url = domain
            if 'http://' not in domain:
                domain_url = 'http://' + domain

            print('Search for icons: ' + domain)

            html = __grab_url(domain_url)
            images = __extract_images(html)
            image_counter = 1
            for image in images:
                if '.ico' in image:
                    continue

                file_name = __extract_file_name(image)
                extension = __extract_extension(file_name)

                if len(images) == 1:
                    file_name = domain + '.' + extension
                else:
                    file_name = domain + str(image_counter) + '.' + extension

                image_counter += 1

                print('    > ' + file_name)
                if image.startswith('//'):
                    image = 'http:' + image

                if not image.startswith('http://') and not image.startswith('https://'):
                    image = domain_url + '/' + image

                print(image)
                r = requests.get(image)
                __save_image(r.content, './images/' + file_name)
        except:
            print('Failed to process: ' + domain)

if __name__ == "__main__":
    grab_domain_icons()
