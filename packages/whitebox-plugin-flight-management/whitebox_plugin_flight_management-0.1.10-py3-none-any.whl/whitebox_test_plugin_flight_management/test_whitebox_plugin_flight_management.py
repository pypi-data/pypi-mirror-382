from django.test import TestCase

from plugin.manager import plugin_manager


class TestWhiteboxPluginFlightManagement(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginFlightManagement"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "Flight Management")

    def test_plugin_capabilities(self):
        self.assertIn("flight-management", self.plugin.provides_capabilities)
