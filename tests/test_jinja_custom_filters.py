from fhirzeug.fhirrenderer import cut_first_letter


def test_camelcase_lower_cut_first_letter():
  result = cut_first_letter("AccountUse")
  assert result == "use"