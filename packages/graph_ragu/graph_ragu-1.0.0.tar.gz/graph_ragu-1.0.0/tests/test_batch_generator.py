import unittest
from ragu.common.batch_generator import BatchGenerator


class TestBatchGenerator(unittest.TestCase):
    def test_batch_correctness(self):
        data = list(range(10))
        batch_size = 3
        generator = BatchGenerator(data, batch_size)
        batches = list(generator.get_batches())

        expected_batches = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        self.assertEqual(batches, expected_batches)

    def test_return_type(self):
        data = ["Hello"]
        generator = BatchGenerator(data, 3)
        batch = next(generator.get_batches())
        self.assertIsInstance(batch, list)

    def test_empty_data(self):
        generator = BatchGenerator([], 3)
        self.assertEqual(len(list(generator.get_batches())), 0)

    def test_single_batch(self):
        data = [1, 2]
        generator = BatchGenerator(data, 5)
        self.assertEqual(list(generator.get_batches()), [data])

    def test_len_method(self):
        data = list(range(10))
        batch_size = 3
        generator = BatchGenerator(data, batch_size)
        self.assertEqual(len(generator), 4)

if __name__ == "__main__":
    unittest.main()