from pydantic_fhir import r4


def test_meta_information():
    empty_profiles = [r4.FHIRAbstractBase, r4.FHIRAbstractResource]

    nodes = [r4.FHIRAbstractBase]
    while len(nodes) > 0:
        node = nodes.pop()
        nodes += node.__subclasses__()
        if node in empty_profiles:
            assert len(node.Meta.profile) == 0
        else:
            assert len(node.Meta.profile) > 0
