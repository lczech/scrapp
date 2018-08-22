from os import path

class TEA:
  """Class holding Tree Edge Anntations. Ensures adherence to the related file format specifications"""

  _version = "0.0.1"
  _meta = {"invocation":""}

  _tree = "" #TODO internally as an actual tree? convert on write?
  _samples = []

  # def __init__(self):
  #   self.arg = arg

  def invocation(self, invocation_string):
    self._meta["invocation"] = invocation_string

  def invocation(self):
    return self._meta["invocation"]

  def version(self, version_string):
    self._version = version_string

  def version(self):
    return self._version

  def tree(self, tree_string):
    self._tree = tree_string

  def tree(self):
    return self._tree

  def sample(self, name):
    # find sample with specified name

    # return it

  def add_annotation(self, sample_name, edge_id, annotations):
    """ adds an arbitrary number of key-value pairs ("annotations")
        belonging to an edge in the tree ("edge_id")
        to a given named sample ("sample_name").
    """

    # look up sample, make one if it's not there
    sample_found = False

    for s in self._samples:
      if s["name"] == sample_name:
        sample_found = True
        edge_found = False
        for a in s["annotation"]:
          if a["edge"] == edge_id:
            edge_found = True
            a.append( annotations )
        if not edge_found:
          annotations["edge"] = edge_id
          s["annotation"].append( annotations )

    if not sample_found:
      annotations["edge"] = edge_id
      self._samples.append( { "name": sample_name,
                              "annotation": [ annotations ]})