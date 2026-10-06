import unittest
from unittest.mock import Mock
from research_harness import v022_macros as macros

class MacroTests(unittest.TestCase):
    def test_macros_are_controller_only_and_release_keys(self):
        for macro in (macros.boot_continue,macros.normal_report,macros.open_shop_buy_list):
            client=Mock(); macro(client)
            calls=[c.args for c in client.command.call_args_list]
            self.assertTrue(all(c[0] in ('frames','set_keys') for c in calls))
            for i,c in enumerate(calls):
                if c[0]=='set_keys' and c[1]:
                    self.assertEqual(calls[i+2],('set_keys',0))
            self.assertTrue(all(1<=c[1]<=120 for c in calls if c[0]=='frames'))
