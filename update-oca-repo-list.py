import os

from github import Github


def get_oca_repos_list():
    g = Github()
    oca = g.get_organization('OCA')
    for repo in oca.get_repos():
        for module in repo.get_contents(ref='12.0'):
            if module.type == 'dir' and module.name != 'setup':
                if repo.get_contents(os.path.join(module.path, '__manifest__.py')):
                    break
        else:
            print('Not modules: ', repo)
            continue

        print('Modules: ', repo)
