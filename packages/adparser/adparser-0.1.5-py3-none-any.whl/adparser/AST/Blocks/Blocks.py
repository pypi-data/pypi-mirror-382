# base block class for AST
import abc

class Block(abc.ABC):

    def __init__(self, data, section, parent, style):
        if not section:
            self.section = []
        else:
            self.section = section

        if not style:
            self.styles = []
        else:
            self.styles = style

        self.data = data
        self._parent = parent

        self._children: list = []  # list of children blocks

    def add_style(self, style):
        if style:
            self.styles.append(style)

    @abc.abstractmethod
    def accept(self, visitor):
        pass

    def __type_check(self, elstr, elem, searchstyle):
        str_type_dict = {'text_line':TextLine, 'link': Link, 'paragraph': Paragraph, 'heading': Heading, 'list': List,
                         'source_block':SourceBlock, 'table': Table,  'audio': Audio, 'video': Video, 'image': Image}
        if elstr in str_type_dict:
            if isinstance(elem, str_type_dict[elstr]) and set(searchstyle).issubset(set(elem.styles)):
                return True
        return False


    def get_near(self, element: str, style=None, direction='up'):

        if style is None:
            style = []

        curparent = self._parent
        if direction == 'up':
            rev_cildren = list(reversed(curparent._children))
        elif direction =='down':
            rev_cildren = curparent._children
        else:
            print('Incorrect direction')
            return

        for i in range(len(rev_cildren)):
            if rev_cildren[i] is self:
                rev_cildren = rev_cildren[i + 1:]
                break

        stop = False
        while not stop:
            if isinstance(curparent, RootBlock):
                stop = True
            for elem in rev_cildren:
                stack = [elem]
                while stack:
                    inelem = stack.pop()

                    if self.__type_check(element, inelem, style):
                        return inelem
                    if direction == 'down':
                        for inel in reversed(inelem._children):
                            stack.append(inel)
                    else:
                        for inel in inelem._children:
                            stack.append(inel)

            if not stop:
                oldparent = curparent
                curparent = curparent._parent

                if direction == 'up':
                    rev_cildren = list(reversed(curparent._children))
                elif direction == 'down':
                    rev_cildren = curparent._children

                for i in range(len(rev_cildren)):
                    if rev_cildren[i] is oldparent:
                        rev_cildren = rev_cildren[i + 1:]
                        break

        return None



"""blocks classes description"""


class RootBlock(Block):

    def __init__(self, section=None):
        super().__init__(None, section, None, None)

    def accept(self, visitor):
        pass


class DelimeterBlock(Block):

    def __init__(self, section, parent, style):
        super().__init__(None, section, parent, style)

    def accept(self, visitor):
        pass


class TextLine(Block):

    def __init__(self, data, section, parent, style=None):
        super().__init__(data, section, parent, style)

    def accept(self, visitor):
        visitor.visit_text_line(self)


class Link(Block):

    def __init__(self, data, section, parent, style, attribute):
        super().__init__(data, section, parent, style)
        self.attribute = attribute

    def accept(self, visitor):
        visitor.visit_link(self)


class Paragraph(Block):

    def __init__(self, data, section, parent, style=None):
        super().__init__(data, section, parent, style)

    def accept(self, visitor):
        visitor.visit_paragraph(self)

    def get_text(self, url_opt="hide_urls"):
        full_str = ''
        for i in range(len(self._children)):
            if url_opt == 'hide_urls':
                if isinstance(self._children[i], Link):
                    full_str += f"{self._children[i].attribute}"
                elif isinstance(self._children[i], Image):
                    full_str += self._children[i].data
                else:
                    full_str += str(self._children[i].data)
            elif url_opt == 'show_urls':
                if isinstance(self._children[i], Link):
                    full_str += f"{self._children[i].data}[{self._children[i].attribute}]"
                elif isinstance(self._children[i], Image):
                    full_str += f"image[{self._children[i].data}]"
                else:
                    full_str += str(self._children[i].data)
            else:
                print("Incorrect url_opt!")
                break

        return full_str


class Section(Block):

    def __init__(self, section, parent):
        super().__init__(None, section, parent, None)

    def accept(self, visitor):
        pass


class Heading(Block):

    def __init__(self, data, section, parent, style=None):
        super().__init__(data, section, parent, style)

    def accept(self, visitor):
        visitor.visit_heading(self)


class List(Block):

    def __init__(self, data, section, parent, style, title=None):
        super().__init__(data, section, parent, style)
        self.title = title

    def accept(self, visitor):
        visitor.visit_list(self)


class SourceBlock(Block):

    def __init__(self, data, section, parent, style, title=None):
        super().__init__(data, section, parent, style)
        self.title = title

    def accept(self, visitor):
        visitor.visit_source(self)


class Table(Block):

    def __init__(self, diction, section, parent, style=None, title=None):
        super().__init__(diction, section, parent, style)
        self.title = title

    def to_matrix(self):
        if not isinstance(self.data, list):
            self.data = [[key] + [value for value in self.data[key]] for key in self.data.keys()]

    def to_dict(self):
        if not isinstance(self.data, dict):
            self.data = {col[0]: col[1:] for col in self.data}

    def accept(self, visitor):
        visitor.visit_table(self)


class Admonition(Block):

    def __init__(self, section, parent, style):
        super().__init__(None, section, parent, style)

    def accept(self, visitor):
        pass


class Audio(Block):

    def __init__(self, data, section, parent, style, title=None):
        super().__init__(data, section, parent, style)
        self.title = title

    def accept(self, visitor):
        visitor.visit_audio(self)


class Image(Block):

    def __init__(self, data, section, parent, style, title=None):
        super().__init__(data, section, parent, style)
        self.title = title

    def accept(self, visitor):
        visitor.visit_image(self)


class Video(Block):

    def __init__(self, data, section, parent, style, title=None):
        super().__init__(data, section, parent, style)
        self.title = title

    def accept(self, visitor):
        visitor.visit_video(self)
