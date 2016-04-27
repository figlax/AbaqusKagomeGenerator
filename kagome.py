from math import sqrt
from pprint import pprint
# import pyplot
import matplotlib.pyplot as plt

class Kagome:
    def __init__(self, x_count, y_count, strut_length):
        stars = list()
        # for now, (0, 0) is the center of the first star
        # the height of a star is 2 * sqrt(3) * strut_length
        star_height = 2 * sqrt(3) * strut_length
        star_width = 2 * strut_length

        for row in range(y_count):
            for col in range(x_count):
                star_center = [col * star_width, row * star_height]
                stars.append(
                    Star(star_center, strut_length)
                )
        # now we have a set of stars that define the kagome

        # Fill self.nodes and self.elements with the stuff from the stars
        self.nodes = list()
        self.elements = list()
        self.cracked_nodes = list()

        for star in stars:
            for node in star.nodes:
                # if there are no nodes already in this location
                # add the node
                if not find_node_in_same_location(self.nodes, node):
                    self.nodes.append(node)
            # always add elements - they are handled in fix_element_nodes()
            self.elements += star.elements

        self.fix_element_nodes()

        self.recenter(x_count, y_count, star_width, star_height)

    def fix_element_nodes(self):
        # for each element
        for element in self.elements:
            # check if the element points to a node that doesn't "exist"
            if element.start_node not in self.nodes:
                # if so, replace the duplicate node with the correct node
                duplicate_node = find_node_in_same_location(
                    self.nodes,
                    element.start_node
                )

                #element.start_node = duplicate_node

                #element.start_node.member_elements.append(duplicate_node.member_elements)
                if element.start_node is None:
                    raise Exception("Couldn't find duplicate node for element " + str(element))

            if element.end_node not in self.nodes:
                # if so, replace the duplicate node with the correct node
                element.end_node = find_node_in_same_location(
                    self.nodes,
                    element.end_node
                )
                if element.end_node is None:
                    raise Exception("Couldn't find duplicate node for element " + str(element))

        # now remove duplicate elements
        # magic: self.elements = list(set(self.elements))

        # boring nonmagic:
        unique_elements = list()
        for element in self.elements:
            if not element in unique_elements:
                unique_elements.append(element)
        self.elements = unique_elements

    def recenter(self, x_count, y_count, star_width, star_height):
        """Move the center of this shape to (0, 0)"""
        center = [
            ((x_count - 1) * star_width) / 2.0,
            ((y_count - 1) * star_height) / 2.0,
        ]
        for node in self.nodes:
            node.x -= center[0]
            node.y -= center[1]

    def fancy_format(self):
        node_text = ""
        for i, node in enumerate(self.nodes):
            node_text += "{0}, {1}, {2}, {3}\n".format(
                i+1,
                node.x,
                node.y,
                0
            )

        element_text = ""
        for i, element in enumerate(self.elements):
            element_text += "{0}, {1}, {2}\n".format(
                i+1,
                self.nodes.index(element.start_node) + 1,
                self.nodes.index(element.end_node) + 1
            )

        fancy_text = "\n".join([
            "*HEADING",
            "**CHRISTINE GREGG",
            "**KAGOME ANALYSIS",
            "*NODE, NSET=BEAMS",
            node_text,
            "",
            "*ELEMENT, ELSET=BEAM_ELEMENTS, TYPE=B23",
            element_text,
            "*MATERIAL, NAME=K_MAT",
            "*ELASTIC",
            "2E9, 0.3",
            "*BEAM SECTION, SECTION = RECT, ELSET= BEAM_ELEMENTS, MATERIAL=K_MAT, poisson = 0.3 ",
            "0.313, 0.313",
            "*Step, name=Step=1, nlgeom=NO, perturbation",
            "*Static"
        ])
        return fancy_text

    def create_crack(self, crack_length):
        """Create a crack in a Kagome

        Args:
            cracked_nodes (list of Node objects)
            crack_orientation (string)
        """

        # for now, assume we can only crack in the middle of our shape
        # because it's what we want
        nodes_on_zero_plane = list()
        for node in self.nodes:
            if node.y == 0:
                nodes_on_zero_plane.append(node)
        nodes_on_zero_plane.sort(key = lambda node: node.x)

        self.cracked_nodes = nodes_on_zero_plane[:crack_length]

        for cracking_node in nodes_on_zero_plane[:crack_length]:
            # create a list of affected elements
            affected_elements = list()
            for element in self.elements:
                if element.has_node(cracking_node):
                    affected_elements.append(element)

            above_elements = list()
            for element in affected_elements:
                element_is_above = element.start_node.y > 0 or element.end_node.y > 0
                if element_is_above:
                    above_elements.append(element)

            # now we know which elements are above and below the crack
            # so split the cracking_node and reconfigure the elements
            # let's break the elements above

            new_node = Node(cracking_node.x, cracking_node.y)
            # add the new node to our list of nodes
            self.nodes.append(new_node)
            # make the above elements point to the new node
            for element in above_elements:
                if element.start_node.same_location(new_node):
                    element.start_node = new_node
                elif element.end_node.same_location(new_node):
                    element.end_node = new_node
                else:
                    raise Exception("this should not be possible :(")



class Star:
    def __init__(self, center, strut_length):
        self.center = center
        self.strut_length = strut_length

        self.nodes = self.init_nodes()
        self.elements = self.init_elements()

    def init_nodes(self):
        nodes = list()
        # first row
        nodes.append(Node( 0.0, sqrt(3) * self.strut_length))

        # second row
        y = (sqrt(3) / 2) * self.strut_length
        nodes.append(Node(-1.5 * self.strut_length, y))
        nodes.append(Node( -0.5 * self.strut_length, y))
        nodes.append(Node( 0.5 * self.strut_length, y))
        nodes.append(Node( 1.5 * self.strut_length, y))

        # third row
        y = 0.0
        nodes.append(Node( -self.strut_length, y))
        nodes.append(Node( self.strut_length, y))

        # fourth row
        y = -(sqrt(3) / 2) * self.strut_length
        nodes.append(Node( -1.5 * self.strut_length, y))
        nodes.append(Node( -0.5 * self.strut_length, y))
        nodes.append(Node( 0.5 * self.strut_length, y))
        nodes.append(Node( 1.5 * self.strut_length, y))

        # fifth row
        nodes.append(Node( 0.0, -sqrt(3) * self.strut_length))

        # shift it by the center
        for node in nodes:
            node[0] = node[0] + self.center[0]
            node[1] = node[1] + self.center[1]

        return nodes

    def init_elements(self):
        elements = list()

        def create_triangle(node_index_1, node_index_2, node_index_3):
            first_node = self.nodes[node_index_1]
            second_node = self.nodes[node_index_2]
            third_node = self.nodes[node_index_3]
            first_element = Element(
                first_node,
                second_node
            )
            node_index_1.member_elements.append(first_element)
            node_index_2.member_elements.append(first_element)
            second_element = Element(
                first_node,
                third_node
            )
            node_index_1.member_elements.append(second_element)
            node_index_3.member_elements.append(second_element)
            third_element = Element(
                second_node,
                third_node
            )
            node_index_2.member_elements.append(third_element)
            node_index_3.member_elements.append(third_element)

            return [
                first_element,
                second_element,
                third_element
            ]

        # go around clockwise
        elements += create_triangle(0, 2, 3)
        elements += create_triangle(3, 4, 6)
        elements += create_triangle(6, 9, 10)
        elements += create_triangle(8, 9, 11)
        elements += create_triangle(5, 7, 8)
        elements += create_triangle(1, 2, 5)

        return elements

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.member_elements = list()

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise Exception("You have done something horribly wrong")

    def __setitem__(self, i, value):
        if i == 0:
            self.x = value
        elif i == 1:
            self.y = value
        else:
            raise Exception("You have done something else horribly wrong")

    def __str__(self):
        return "Node({0}, {1})".format(self.x, self.y)

    def same_location(self, node):
        return self.x == node.x and self.y == node.y


class Element:
    def __init__(self, start_node, end_node):
        self.start_node = start_node
        self.end_node = end_node

    def has_node(self, node):
        return node == self.start_node or node == self.end_node

    def __repr__(self):
        return "Element({0}, {1})".format(repr(self.start_node), repr(self.end_node))

    def __eq__(self, element):
        return self.start_node == element.start_node and self.end_node == element.end_node

def debug_output(test_kagome):
    #pprint(test_kagome.nodes)
    #pprint(test_kagome.elements)
    for node in test_kagome.nodes:
        plt.scatter(node[0], node[1])
    for node in test_kagome.cracked_nodes:
        plt.scatter(node[0], node[1], c='r', marker='o')
    plt.show()
    print "node count:", len(test_kagome.nodes)
    print "element count:", len(test_kagome.elements)

def write_abaqus_file(file_name, kagome):

    f = open(file_name, "w")
    f.write(kagome.fancy_format())
    f.close()



def substitute_node_instance_in_elements(elements, node):
    """Use the given node instance to replace other instances in the same location

    Args:
        elements (list of Elements)
        node (Node)
    """

def find_node_in_same_location(node_list, node):
    """Find a node in node_list in the same location as node

    Args:
        node_list (list of Nodes)
        node (Node)

    Yields:
        Node if a node in the same location exists
        None otherwise
    """

    for other_node in node_list:
        if other_node.same_location(node):
            return other_node
    return None

def main():
    test_kagome = Kagome(
        x_count=10,
        y_count=10,
        strut_length=2,
    )
    test_kagome.create_crack(3)
    debug_output(test_kagome)
    #print test_kagome.fancy_format()
    # print test_kagome.nodes[:, 1]
    write_abaqus_file(
        "test_kagome_10x10_3.txt",
        test_kagome
    )
    write_abaqus_file(
        "test_kagome_10x10_3.inp",
        test_kagome
    )

main()
