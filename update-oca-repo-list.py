import ast
import json
import os
import logging
import pickle
from collections import defaultdict
import time

from github import Github, GithubException, UnknownObjectException


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Result schema:
# {'user':
#     {'repo':
#         {'version':
#             {'module': str,
#              'name': str,
#              'summary': str,
#             }
#         }
#     }
# }

def collect_modules(access_token):
    result = {}
    timestamp = int(time.time())

    github = Github(access_token)
    for user_login in GITHUB_USERS:
        logger.info('Get %s user repos', user_login)
        user = github.get_user(user_login)

        for repo in user.get_repos():
            if repo.fork:
                # TODO Use user.get_repos(type='sources')
                continue

            if repo.name[0] != 'a':
                continue

            for odoo_version in ODOO_VERSIONS:
                try:
                    contents = repo.get_contents('', ref=odoo_version)
                except GithubException:
                    # logging.info(f'{repo.full_name} has no actual version branch')
                    continue

                for module in contents:
                    if module.type == 'dir' and module.name != 'setup':
                        manifest_path = os.path.join(module.path, '__manifest__.py')
                        try:
                            manifest_file = repo.get_contents(manifest_path, ref=odoo_version)
                            manifest = ast.literal_eval(manifest_file.decoded_content.decode('utf8'))
                            result[user.login, module.name, odoo_version] = {
                                'user': user.login,
                                'module': module.name,
                                'odoo_version': odoo_version,
                                'timestamp': timestamp,

                                'repo': repo.name,
                                'stars': repo.stargazers_count,

                                'last_modified': module.last_modified,
                                'html_url': module.html_url,
                                'name': manifest['name'],
                                'summary': manifest.get('summary', '').strip(),
                            }
                        except UnknownObjectException:
                            logging.info(f'{repo.full_name} has dir without manifest file')

    return result


def format_markdown(repos):
    list_items = []
    for repo in sorted(repos, key=lambda r: r.name):
        list_item = f'* [{repo.name}]({repo.svn_url})'
        if repo.description:
            list_item += f' - {repo.description}'

        list_items.append(list_item)

    return '\n'.join(list_items)


ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
GITHUB_USERS = (
    'OCA',
)
ODOO_VERSIONS = ['11.0', '12.0', '13.0', '14.0']
# ODOO_VERSIONS = ['11.0', '12.0']
# ODOO_ACTUAL_VERSION = ['12.0']

def update_module_info(module_pickle_file_path, users=GITHUB_USERS, repos=None, versions=None):
    module_info = {}
    try:
        with open(module_pickle_file_path, 'rb') as module_pickle_file:
            module_info = pickle.load(module_pickle_file)
    except FileNotFoundError:
        pass
    except pickle.UnpicklingError:
        os.remove(module_pickle_file_path)

    result = collect_modules(ACCESS_TOKEN)
    module_info.update(result)

    with open('modules.pickle', 'wb') as modules_file:
        pickle.dump(module_info, modules_file)


if __name__ == '__main__':
    update_module_info('modules.pickle', )
