import unittest

import obanalyser.analyse_obf_geometry as analyse_obf_geometry
import obanalyser.data_classes as data_classes

class TestMain(unittest.TestCase):
    def test_main(self):
        path1 = r"tests\input\cubes_test\buildInfo.json"
        path2 = r"tests\output\geometryInfo.json"
        geometry_info = analyse_obf_geometry.analyse_obf_geometry(path1)
        geometry_info.to_json_file(path2)
        print(f"Geometry analysation saved to {path2}")

        geometry_info2 = data_classes.GeometryInfo.from_json_file(path2)
        


if __name__ == "__main__":
    unittest.main()



