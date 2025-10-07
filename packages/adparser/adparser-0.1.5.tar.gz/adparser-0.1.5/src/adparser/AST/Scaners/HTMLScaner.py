# Implementation of a scaner that builds an asciidoc tree of a document based on its html version

from lxml import html

from adparser.AST.Scaners.Scaner import Scaner
from adparser.AST.Blocks.Blocks import *
from adparser.AST.ASTree import ASTree
from queue import Queue


class HTMLScaner(Scaner):

    def __init__(self):

        # stacks for creating lists of styles and headings in tree blocks

        self.__heading_stack = []  # [['h1', 'h1name'], ['h2', 'h2curname'], ['h3', 'h2curname'], ...]

        # The counter is how many items are currently planned to be added to the tree with the current style
        self.__style_stack = []  # [['style1name',style1curcounter], ['style2name':style2curcounter], ['style3name':style3curcounter], ...]
        self.__htmltree_stack = []  # [[htmlnode1, adparentnode1], [htmlnode2, adparentnode2], [htmlnode3, adparentnode3] ]

        self._go_down_flag = False
        self.adtree = RootBlock()

    @property
    def heading_list(self):
        return [heading[1] for heading in self.__heading_stack]

    @property
    def style_list(self):
        return [style[0] for style in self.__style_stack]

    # -------  functions for working with stacks of styles and headers -------

    def __push_heading(self, htag, hname):  # hname - name of header tag, hkey, hvalue as above
        
        if self.__heading_stack:
            new_level = int(htag[1])
            last_level = int(self.__heading_stack[-1][0][1])

        if not self.__heading_stack:
            self.__heading_stack.append([htag, hname])
        # subheading
        elif new_level > last_level:
            self.__heading_stack.append([htag, hname])
        # out of the subheadings
        elif new_level < last_level:
            # loop of cleaning heading stack
            while new_level <= last_level:
                self.__heading_stack.pop()
                if self.__heading_stack:
                    last_level = int(self.__heading_stack[-1][0][1])
                else: 
                    break
            self.__heading_stack.append([htag, hname])
        # equal levels
        else:
            self.__heading_stack[-1] = [htag, hname]

    def __push_style(self, stylename, stylecounter):

        self.__style_stack.append([stylename, stylecounter])

    def __pop_style(self):
        if self.__style_stack and self.__style_stack[-1][1] == 0:
            self.__style_stack.pop()
            # double pop for nested situations
            if self.__style_stack and self.__style_stack[-1][1] == 0:
                self.__style_stack.pop()

    def __increase_style(self):
        if self.__style_stack:
            self.__style_stack[-1][1] += 1

    def __decrease_style(self, html_node):
        if self.__style_stack:
            self.__style_stack[-1][1] -= 1

    # -------  functions for creating tree blocks -------

    # html_node - a node from the html tree from which we take information to create a block
    # old_ad_parent - the node of the tree being formed, to which we bind the new block

    # go_down_flag - if False, then we will no longer process the child elements of the html node
    # (i.e. this node will not further give the elements to the depth search)
    def __create_heading(self, html_node, old_ad_parent):

        self.__push_heading(html_node.tag,
                            html_node.text_content())
        new_ad_parent = Section(self.heading_list, old_ad_parent)
        ASTree.add_sub_element(new_ad_parent,
                               Heading(html_node.text_content(),
                                       new_ad_parent.section,
                                       new_ad_parent
                                       )
                               )
        # for the last elements in the stack, we change the references to the parent ad_tree
        change_len = 0
        if html_node.tag == 'h1':  # h1 can be in the header tag, so we apply all the elements should be
            # inherited from the sector with it, and not just what is in the header tag

            change_len = len(self.__htmltree_stack)
        else:
            change_len = len(html_node.getparent())
        for node in self.__htmltree_stack[-(change_len - 1):]:
            node[1] = new_ad_parent

        self._go_down_flag = False

        return new_ad_parent

    def __create_admonition(self, html_node, old_ad_parent):
        self.__push_style(html_node.get("class").split()[1], 0)  # we set the counter to 0,
        # because we need to add only the number
        # of internal elements to the counter,
        # and not + external ones,
        # as in the case of headers

        self._go_down_flag = True

        return Admonition(old_ad_parent.section,
                          old_ad_parent,
                          self.style_list)

    def _get_title_from_html_node(self, html_node) -> str | None:
        title = html_node.xpath(".//*[@class='title']")
        if title:
            title_text = title[0].text_content()
        else:
            title_text = None
        return title_text
    
    def __create_delimeter(self, html_node, old_ad_parent):
        self.__push_style(html_node.get("class"), 0)

        new_ad_parent = DelimeterBlock(old_ad_parent.section,
                                       old_ad_parent,
                                       self.style_list)

        self._go_down_flag = True

        if html_node.get("class") == 'listingblock' and html_node.find('.//code') is not None:
            title = self._get_title_from_html_node(html_node)
            source_block = self.__create_source(html_node.find('.//code'), new_ad_parent)
            source_block.title = title
            ASTree.add_sub_element(new_ad_parent, source_block)
            self._go_down_flag = False

        # in the style of a quote, we add the author to the styles attribute
        elif new_ad_parent.styles[-1] == "quoteblock":
            ASTree.add_sub_element(new_ad_parent,
                                   self.__create_paragraph(html_node.xpath(".//*[@class='paragraph'] | .//blockquote")[-1],
                                                           new_ad_parent)
                                   )
            new_ad_parent.styles.append(html_node.xpath(".//*[@class='attribution']")[0].text_content())
            self._go_down_flag = False

        return new_ad_parent
     
    def __create_table(self, html_node, old_ad_parent):
        """
            This implementation currently supports storing tables 
            with colspan and rowspan only if the header is clearly defined in it:
                1) It should list all the columns
                2) If the header is not explicitly specified, the first row will be used instead.
                3) header columns should not have colspan or rowspan attributes
        """
        title = self._get_title_from_html_node(html_node)

        if html_node.find("tbody") is None: # admonition fix
            return self.__create_paragraph(html_node, old_ad_parent)
        
        cur_span_dict = {} # { column_name: [remain_rows, cell_text], ... }
                           # column_name - in the current row iteration, it contains a joined cell
                           # remain_rows -> deincrements each row
                           # if remain_rows == 0 -> column_name key deleting
        def cur_span_update(tcol, column_name: str, header_columns: list[str]):
            """if tcol has colspan or rowspan attributes:
                    add columns to cur_span_dict"""
            def get_span(name: str):
                span = tcol.get(name)
                if span is None:
                    span = 1
                else:
                    span = int(span)
                return span
            
            rowspan = get_span("rowspan")
            colspan = get_span("colspan")

            if colspan > 1 or rowspan > 1:
                colspan = int(colspan)

                # search column in header_columns
                for idx, column in enumerate(header_columns):
                    if column == column_name:
                        start_idx = idx
                        break
                # add colspan columns in cur_span_dict
                joined_columns = header_columns[start_idx:start_idx+colspan]
                for column in joined_columns:
                    cur_span_dict[column] = [rowspan, tcol.text_content()]

        def cur_span_decrement():
            """decrement remain_rows in cur_span_dict:
                if remain_rows == 0 -> column_name key deleting"""
            del_columns = []
            for column in cur_span_dict:
                cur_span_dict[column][0] -= 1
                if cur_span_dict[column][0] == 0:
                    del_columns.append(column)
            for column in del_columns:
                del cur_span_dict[column]

        def table_span_row_processing(tr, table_dict: dict[str, list[str]], header_columns: list[str]):
            """add to table_dict row data"""       
            # not joined cells 
            usual_cells = Queue()
            for cell in tr.findall(".//td"):
                usual_cells.put(cell)

            for column in header_columns:
                if column not in cur_span_dict:
                    tcol = usual_cells.get()
                    cur_span_update(tcol, column, header_columns)
                    table_dict[column].append(tcol.text_content())
                else:
                    table_dict[column].append(cur_span_dict[column][1])
            cur_span_decrement()

        # if table has explicitly set header
        if html_node.find("thead") is not None: 
            head = html_node.find("thead")
            header_columns = [x.text_content() for x in head.findall(".//th")]
            table_dict = {x: [] for x in header_columns}
            body = html_node.find("tbody")

            for tr in body.findall(".//tr"):
                table_span_row_processing(tr, table_dict, header_columns)

        # if table hasn`t explicitly set header              
        else: 
            body = html_node.find("tbody")

            # table without header and without span attrs
            #  -> table_dict = {col1:[...], col2: [...], ...}
            if not body.xpath(".//*[@rowspan] | .//*[@colspan]"): 
                table_dict = {'col' + str(i): [] for i in range(1, len(body.find(".//tr").findall(".//td")) + 1)}
                for tr in body.findall(".//tr"):
                    for dcolkey, td in zip(table_dict.keys(), tr.findall(".//td")):
                        table_dict[dcolkey].append(td.text_content())

            # table without header but with span attrs
            else:
                header_columns = []
                table_dict = {}

                body = html_node.find("tbody")

                for tr in body.findall(".//tr"):
                    if not header_columns: # header = first row
                        header_columns = [x.text_content() for x in tr.findall(".//td")]
                        table_dict = {x: [] for x in header_columns}
                        continue

                    table_span_row_processing(tr, table_dict, header_columns)

        self._go_down_flag = False

        return Table(table_dict, old_ad_parent.section,
                     old_ad_parent,
                     old_ad_parent.styles, title)

    def __create_list(self, html_node, old_ad_parent):

        title = self._get_title_from_html_node(html_node)

        self._go_down_flag = False
        html_text = html_node.text_content()
        html_text = html_text.lstrip('\n')
        html_text = html_text.rstrip('\n')

        if title is not None: # remove title
            html_text = html_text.replace(title, "", 1)

        return List(html_text,
                    old_ad_parent.section,
                    old_ad_parent,
                    old_ad_parent.styles, title)

    def __create_source(self, html_node, old_ad_parent):
        
        self._go_down_flag = False
        code_style = old_ad_parent.styles.copy()
        code_style.append(html_node.get('data-lang'))

        return SourceBlock(html_node.text_content(),
                           old_ad_parent.section,
                           old_ad_parent,
                           code_style)

    def __create_image(self, html_node, old_ad_parent):
        title = self._get_title_from_html_node(html_node)
        self._go_down_flag = False
        srcnode = html_node.xpath("..//*[@src]")[0]
        return Image(srcnode.get("src"),
                     old_ad_parent.section,
                     old_ad_parent,
                     old_ad_parent.styles, title)

    def __create_audio(self, html_node, old_ad_parent):
        title = self._get_title_from_html_node(html_node)
        self._go_down_flag = False
        srcnode = html_node.xpath(".//*[@src]")[0]
        return Audio(srcnode.get("src"),
                     old_ad_parent.section,
                     old_ad_parent,
                     old_ad_parent.styles, title)

    def __create_video(self, html_node, old_ad_parent):
        title = self._get_title_from_html_node(html_node)
        self._go_down_flag = False
        srcnode = html_node.xpath(".//*[@src]")[0]
        return Video(srcnode.get("src"),
                     old_ad_parent.section,
                     old_ad_parent,
                     old_ad_parent.styles, title)

    def __create_link(self, html_node, old_ad_parent):
        self._go_down_flag = False

        return Link(html_node.get("href"),
                    old_ad_parent.section,
                    old_ad_parent,
                    old_ad_parent.styles,
                    html_node.text_content())

    def __create_textline(self, html_node, old_ad_parent):

        self._go_down_flag = False

        old_styles = old_ad_parent.styles.copy()

        if isinstance(html_node, str):
            html_node = html_node.lstrip('\n')
            html_node = html_node.rstrip('\n')
            return TextLine(html_node,
                        old_ad_parent.section,
                        old_ad_parent,
                        old_ad_parent.styles,
                        )
        if html_node.text is None: # <br>
            return TextLine('\n',
                            old_ad_parent.section,
                            old_ad_parent,
                            old_ad_parent.styles,
                            )
        html_text = html_node.text
        html_text = html_text.lstrip('\n')
        html_text = html_text.rstrip('\n')

        # styled text
        if html_node.tag == 'b' or html_node.tag == 'strong':
            old_styles.append('bold')
            return TextLine(html_text,
                            old_ad_parent.section,
                            old_ad_parent,
                            old_styles,
                            )
        elif html_node.tag == 'em' or html_node.tag == 'i':
            old_styles.append('italic')
            return TextLine(html_text,
                            old_ad_parent.section,
                            old_ad_parent,
                            old_styles,
                            )
        elif html_node.tag == 'code':
            old_styles.append('monospace')
            return TextLine(html_text,
                            old_ad_parent.section,
                            old_ad_parent,
                            old_styles,
                            )

        return TextLine(html_text,
                        old_ad_parent.section,
                        old_ad_parent,
                        old_ad_parent.styles,
                        )

    def __create_paragraph(self, html_node, old_ad_parent):

        new_ad_parent = Paragraph(None,
                                  old_ad_parent.section,
                                  old_ad_parent,
                                  old_ad_parent.styles
                                  )
        # we go through all the elements of the tag
        # (including plain text without a tag, links, images, video, audio and stylized text)
        for pelem in [x for x in html_node.xpath('./node()') if x != '\n']:
            if not hasattr(pelem, 'tag'):
                ASTree.add_sub_element(new_ad_parent,
                                       self.__create_textline(pelem, new_ad_parent)
                                       )
            elif pelem.tag == 'a':
                ASTree.add_sub_element(new_ad_parent,
                                       self.__create_link(pelem, new_ad_parent)
                                       )
            elif pelem.get("class") in ['image']:
                ASTree.add_sub_element(new_ad_parent,
                                       self.__create_image(pelem.find("./*"), new_ad_parent)
                                       )

            else:
                ASTree.add_sub_element(new_ad_parent,
                                       self.__create_textline(pelem, new_ad_parent)
                                       )

            self._go_down_flag = False

        return new_ad_parent

    # ------- a function that forms a new block -------
    # sequentially checking the html element of the document for belonging to certain conditions
    def __checknode_createblock(self, html_node, old_ad_parent) -> Block:  # -> parent (old or new)

        new_ad_parent = old_ad_parent

        # ---- 1 - the header element? -------
        # we work with the header tag in a special way, because it does not recursively include other html tags
        if html_node.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            new_ad_parent = self.__create_heading(html_node, old_ad_parent)

        # ---- 2 - the admonition element? -------
        elif html_node.get("class") in ['admonitionblock caution', 'admonitionblock note', 'admonitionblock tip',
                                        'admonitionblock important',
                                        'admonitionblock warning']:

            new_ad_parent = self.__create_admonition(html_node, old_ad_parent)

        # ---- 3 - the delimeter element? Also create source-------
        elif html_node.get("class") in ['sidebarblock', 'exampleblock', 'quoteblock', 'listingblock',

                                        'literalblock', 'literalblock output']:
            new_ad_parent = self.__create_delimeter(html_node, old_ad_parent)

        # ---- 4 - the table element? -------
        elif html_node.get("class") and html_node.tag == 'table' and html_node.get("class").startswith('tableblock '):
            new_ad_parent = self.__create_table(html_node, old_ad_parent)

        # ---- 5 - the list element? -------
        elif html_node.get("class") and (html_node.get("class").startswith('dlist')
                                         or html_node.get("class").startswith('ulist')
                                         or html_node.get("class").startswith('olist')):
            new_ad_parent = self.__create_list(html_node, old_ad_parent)

        # ---- 6 - the image element? -------
        elif html_node.get("class") in ['imageblock']:
            new_ad_parent = self.__create_image(html_node, old_ad_parent)

        # ---- 7 - the video element? -------
        elif html_node.get("class") in ['videoblock']:
            new_ad_parent = self.__create_video(html_node, old_ad_parent)

        # ---- 8 - the audio element? -------
        elif html_node.get("class") in ['audioblock']:
            new_ad_parent = self.__create_audio(html_node, old_ad_parent)

        # ---- 9 - the paragraph element? -------
        elif html_node.tag in ['p', 'pre']:
            new_ad_parent = self.__create_paragraph(html_node, old_ad_parent)

        # ---- 10 - the link element? -------
        elif html_node.tag in ['a']:
            new_ad_parent = self.__create_link(html_node, old_ad_parent)

        # a special case when a block contains text without a <p> tag
        elif html_node.get("class") in ['content'] and not hasattr(
                                                            [x for x in html_node.xpath('.//node()') if x != '\n'][0],
                                                            "tag"):
            new_ad_parent = self.__create_paragraph(html_node, old_ad_parent)

        # other with text (also not title - like in admonition)
        elif not len(html_node) and html_node.text and html_node.get("class") not in ['title'] and \
                                                            html_node.get("id") != "header": 
                                                            # skip \n text_line -> case if file doesnt have 0 header level
            new_ad_parent = self.__create_paragraph(html_node, old_ad_parent)

        return new_ad_parent

    # ------- the main function, which, through a search in the depth of the html document, forms a tree -------
    def build_AST(self, htmltext: str) -> ASTree:
        cur_ad_parent = self.adtree
        cur_html_node = html.fromstring(htmltext)
        cur_html_node = cur_html_node.find(".//body") # we consider only the body

        # DFS through the entire html tree
        self.__htmltree_stack.append([cur_html_node, cur_ad_parent])

        while self.__htmltree_stack:
            cur_html_node, cur_ad_parent = self.__htmltree_stack.pop()  # cur_html_node - html node from stack
                                                # cur_ad_parent - the parent to which we will link the new block

            self.__decrease_style(cur_html_node)

            # a flag indicating that the current block has been not fully processed
            self._go_down_flag = True

            new_ad_parent = self.__checknode_createblock(cur_html_node, cur_ad_parent)

            # creating a new tree node
            if not (new_ad_parent is cur_ad_parent):
                ASTree.add_sub_element(cur_ad_parent, new_ad_parent)

            child_counter = 0
            if self._go_down_flag:
                for child in reversed(cur_html_node.getchildren()):
                    child_counter += 1
                    self.__htmltree_stack.append([child, new_ad_parent])
                    self.__increase_style()
            # if the current block has not given any children and the last counter in the stack = 0,
            # then there are no more elements with the current style, we remove the element from the stack
            if not child_counter:
                self.__pop_style()

        # remove paragraph with metadata of html
        if len(self.adtree._children) > 1:
            self.adtree._children = self.adtree._children[:-1]

        return ASTree(self.adtree)
