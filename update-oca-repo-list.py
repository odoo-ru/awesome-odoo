import os
import logging

from dotenv import load_dotenv
from github import Github, GithubException, UnknownObjectException


logging.basicConfig(level=logging.INFO, format='%(message)s')


def get_oca_repos_list():
    load_dotenv()
    access_token = os.getenv('GITHUB_ACCESS_TOKEN')

    g = Github(access_token)
    oca = g.get_organization('OCA')
    repos = get_module_repos(oca)
    return format_markdown(repos)


def format_markdown(repos):
    list_items = []
    for repo in sorted(repos, key=lambda r: r.name):
        list_item = f'* [{repo.name}]({repo.svn_url})'
        if repo.description:
            list_item += f' - {repo.description}'

        list_items.append(list_item)

    return '\n'.join(list_items)


def get_module_repos(organization):
    repos = []

    for repo in organization.get_repos():
        try:
            contents = repo.get_contents('', ref='12.0')
        except GithubException:
            logging.info(f'{repo.full_name} has no actual version branch')
            continue

        for module in contents:
            if module.type == 'dir' and module.name != 'setup':
                try:
                    if repo.get_contents(os.path.join(module.path, '__manifest__.py')):
                        repos.append(repo)
                        logging.info(f'{repo.full_name} has dir with manifest file')
                except UnknownObjectException:
                    logging.info(f'{repo.full_name} has dir without manifest file')

                break
        else:
            logging.info(f'{repo.full_name} has no dirs')

    return repos


if __name__ == '__main__':
    print(get_oca_repos_list())
