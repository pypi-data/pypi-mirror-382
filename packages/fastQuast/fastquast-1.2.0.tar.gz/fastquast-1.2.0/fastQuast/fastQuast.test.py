import unittest
import os
import shutil
from fastQuast import main

class TestFastQuast(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "test_output"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_main(self):
        # Test with a single file
        input_file = "test_data/test.fasta"
        output_file = os.path.join(self.test_dir, "test_output.quast")
        args = [input_file, "-o", self.test_dir]
        main(args)
        self.assertTrue(os.path.exists(output_file))

        # Test with multiple files
        input_files = ["test_data/test.fasta", "test_data/test2.fasta"]
        output_files = [os.path.join(self.test_dir, "test_output.quast"), os.path.join(self.test_dir, "test2_output.quast")]
        args = input_files + ["-o", self.test_dir]
        main(args)
        for output_file in output_files:
            self.assertTrue(os.path.exists(output_file))

if __name__ == '__main__':
    unittest.main()