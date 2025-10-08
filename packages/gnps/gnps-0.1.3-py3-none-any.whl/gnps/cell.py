from .parser.ast.variable import Variable


class Cell:
    """
      The class representing a cell.

      :param id: The id of the cell.
      :type id: int

      :param contents: The contents of the cell. It is a dictionary of variables.
      :type contents: dict[str, Variable]
    """
    id: int
    contents: dict[str, Variable]

    def __init__(self, cell_id: int, contents: dict[str, Variable]):
        """
        Initialize a cell.
        :param cell_id: the cell id
        :type cell_id: int
        :param contents: the contents of the cell (a dictionary of variables)
        :type contents: dict[str, Variable]
        """
        self.id = cell_id
        self.contents = contents
