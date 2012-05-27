import sys
sys.path = ["src"] + sys.path

import unittest

import rawapi


class TestSaneInit(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        version = rawapi.sane_init()
        self.assertTrue(version.is_current())
        rawapi.sane_exit()

    def tearDown(self):
        pass

class TestSaneGetDevices(unittest.TestCase):
    def setUp(self):
        rawapi.sane_init()

    def test_get_devices(self):
        devices = rawapi.sane_get_devices()
        self.assertTrue(len(devices) > 0)

    def tearDown(self):
        rawapi.sane_exit()


class TestSaneOpen(unittest.TestCase):
    def setUp(self):
        rawapi.sane_init()
        devices = rawapi.sane_get_devices()
        self.assertTrue(len(devices) > 0)
        self.dev_name = devices[0].name

    def test_open_invalid(self):
        self.assertRaises(rawapi.SaneException, rawapi.sane_open, "whatever")

    def test_open_valid(self):
        dev_handle = rawapi.sane_open(self.dev_name)
        rawapi.sane_close(dev_handle)

    def tearDown(self):
        rawapi.sane_exit()


class TestSaneGetOptionDescriptor(unittest.TestCase):
    def setUp(self):
        rawapi.sane_init()
        devices = rawapi.sane_get_devices()
        self.assertTrue(len(devices) > 0)
        dev_name = devices[0].name
        self.dev_handle = rawapi.sane_open(dev_name)

    def test_get_option_descriptor_0(self):
        opt_desc = rawapi.sane_get_option_descriptor(self.dev_handle, 0)
        self.assertEqual(opt_desc.name, "")
        self.assertEqual(opt_desc.title, "Number of options")
        self.assertEqual(opt_desc.type, rawapi.SaneValueType.INT)
        self.assertEqual(opt_desc.unit, rawapi.SaneUnit.NONE)
        self.assertEqual(opt_desc.size, 4)
        self.assertEqual(opt_desc.cap, rawapi.SaneCapabilities.SOFT_DETECT)
        self.assertEqual(opt_desc.constraint_type,
                         rawapi.SaneConstraintType.NONE)

    def test_get_option_descriptor_out_of_bounds(self):
        # XXX(Jflesch): Sane's documentation says get_option_descriptor()
        # should return NULL if the index value is invalid. It seems the actual
        # implementation prefers to segfault.

        #self.assertRaises(rawapi.SaneException,
        #                  rawapi.sane_get_option_descriptor, self.dev_handle,
        #                  999999)
        pass

    def tearDown(self):
        rawapi.sane_close(self.dev_handle)
        rawapi.sane_exit()


class TestSaneControlOption(unittest.TestCase):
    def setUp(self):
        rawapi.sane_init()
        devices = rawapi.sane_get_devices()
        self.assertTrue(len(devices) > 0)
        dev_name = devices[0].name
        self.dev_handle = rawapi.sane_open(dev_name)
        self.nb_options = rawapi.sane_get_option_value(self.dev_handle, 0)

    def test_get_option_value(self):
        for opt_idx in range(0, self.nb_options):
            desc = rawapi.sane_get_option_descriptor(self.dev_handle, opt_idx)
            if not rawapi.SaneValueType(desc.type).can_getset_opt():
                continue
            val = rawapi.sane_get_option_value(self.dev_handle, opt_idx)
            print "OPT: %d, %s -> %s" % (opt_idx, desc.name, str(val))

    def test_set_option_value(self):
        pass

    def test_set_option_auto(self):
        pass

    def tearDown(self):
        rawapi.sane_close(self.dev_handle)
        rawapi.sane_exit()


def get_all_tests():
    all_tests = unittest.TestSuite()

    tests = unittest.TestSuite([TestSaneInit("test_init")])
    all_tests.addTest(tests)

    tests = unittest.TestSuite([TestSaneGetDevices("test_get_devices")])
    all_tests.addTest(tests)

    tests = unittest.TestSuite([
        TestSaneOpen("test_open_invalid"),
        TestSaneOpen("test_open_valid"),
    ])
    all_tests.addTest(tests)

    tests = unittest.TestSuite([
        TestSaneGetOptionDescriptor("test_get_option_descriptor_0"),
        TestSaneGetOptionDescriptor(
            "test_get_option_descriptor_out_of_bounds"),
    ])
    all_tests.addTest(tests)

    tests = unittest.TestSuite([
        TestSaneControlOption("test_get_option_value"),
        TestSaneControlOption("test_set_option_value"),
        TestSaneControlOption("test_set_option_auto"),
    ])
    all_tests.addTest(tests)

    return all_tests
