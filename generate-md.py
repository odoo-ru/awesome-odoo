import pickle
from itertools import groupby

class MarkdownGenerator:
    def __init__(self):
        self.content = ''

    def _add_line(self, line):
        self.content += line + '\n'

    def add_header(self, text):
        self._add_line(text)
        self._add_line('=' * len(text))

    def add_table_row(self, row):
        self._add_line('| ' + ' | '.join(row) + ' |')

    def add_table_header(self, header):
        self.add_table_row(header)
        self._add_line('|---' * len(header) + '|')

    def add_table_body(self, rows):
        for row in rows:
            self.add_table_row(row)

    def write(self, file):
        file.write(self.content)


ODOO_VERSIONS = ['11.0', '12.0', '13.0', '14.0']
MODULE_ROW_VERSION_POSITIONS = {version: row_position for row_position, version in enumerate(ODOO_VERSIONS, start=1)}


def generate_markdown(modules_file_path, markdown_file_path):
    with open(modules_file_path, 'rb') as modules_file:
        modules = pickle.load(modules_file)
        print(len(modules))

    markdown_generator = MarkdownGenerator()
    modules = sorted(modules.values(), key=lambda x: (x['user'], x['module'], x['odoo_version']))
    for user, modules_info in groupby(modules, key=lambda x: x['user']):
        markdown_generator.add_header(user)
        markdown_generator.add_table_header(['', '11', '12', '13', '14'])
        for module, module_infos in groupby(modules_info, key=lambda x: x['module']):
            # module_row = [f'__{module}__<br/>{name}'] + [''] * len(ODOO_VERSIONS)
            module_row = [''] + [''] * len(ODOO_VERSIONS)
            name = None
            summary = None
            for module_info in module_infos:
                name = name or module_info['name']
                summary = summary or module_info['summary']
                module_row[MODULE_ROW_VERSION_POSITIONS[module_info['odoo_version']]] = (
                    f'[{module_info["odoo_version"][:-2]}]({module_info["html_url"]})'
                )
            # module_row[0] = f'__{module}__<br/>{name}'
            # module_row[0] = f'{module}<br/>{name}'
            module_row[0] = f'{module}<br/>{summary}'
            markdown_generator.add_table_row(module_row)

    with open(markdown_file_path, 'w') as markdown_file:
        markdown_generator.write(markdown_file)


if __name__ == '__main__':
    generate_markdown('modules.pickle', 'modules.md')
