from pathlib import Path


class MooseBlock():
    TAB = '    '

    def __init__(self, name, collection, root=False):
        self.name = name
        self.root = root
        self.attributes = {}
        self.blocks = []

        for key, val in collection.items():
            # if isinstance(val, CommentedMap):
            if isinstance(val, dict):
                self.blocks.append(MooseBlock(key, val))
                continue
            self.attributes[key] = val

    def __str__(self) -> str:
        if self.root:
            tab = ''
            txt = ''
        else:
            tab = self.TAB
            txt = f'[{self.name}]\n'
        
        for key, val in self.attributes.items():
            txt += f'{tab}{key} = {val}\n'
        for block in self.blocks:
            txt += tab
            txt += str(block).replace('\n', f'\n{tab}')
            txt = txt[:len(txt)-len(tab)]
        if not self.root:
            txt += '[]\n'
        return txt
    
    def to_file(self, path: Path):
        with path.open('w') as f:
            f.write(self.__str__())


def write_input(path, input_deck):
    input_deck = MooseBlock('root', input_deck, root=True)
    input_deck.to_file(path)
