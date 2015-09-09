from __future__ import print_function
import requests
import lxml.html
import shutil
import os


def load_domains_from_file():
    domains = []
    with open('domains.txt') as f:
        domains = f.readlines()

    return domains


def grab_url(url):
    r = requests.get(url)
    return r.text


def extract_images(html):
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


def save_image(content, file_name):
    with open(file_name, 'wb') as f:
        f.write(content)


def extract_file_name(file_name):
    lpos = file_name.rfind('/')
    return file_name[lpos + 1:]


def extract_extension(file_name):
    lpos = file_name.rfind('.')
    lpos += 1
    return file_name[lpos:lpos + 3]

# delete images directory
if os.path.exists('images'):
    shutil.rmtree('images')

# create images directory
if not os.path.exists('images'):
    os.makedirs('images')

for domain in load_domains_from_file():
    domain = domain.replace('\n', '').replace('\r', '')
    try:
        domain_url = domain
        if 'http://' not in domain:
            domain_url = 'http://' + domain

        print('Search for icons: ' + domain)

        html = grab_url(domain_url)
        images = extract_images(html)
        image_counter = 1
        for image in images:
            if '.ico' in image:
                continue

            file_name = extract_file_name(image)
            extension = extract_extension(file_name)

            if len(images) == 1:
                file_name = domain + '.' + extension
            else:
                file_name = domain + str(image_counter) + '.' + extension

            image_counter += 1

            print('    > ' + file_name)
            if image.startswith('//'):
                image = 'http:' + image
            r = requests.get(image)
            save_image(r.content, './images/' + file_name)
    except:
        print('Failed to process: ' + domain)
