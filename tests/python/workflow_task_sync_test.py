from __future__ import annotations

import unittest

from scripts.validate_workflow_task_sync import validate_sync


class WorkflowTaskSyncTests(unittest.TestCase):
    def test_workflows_tasks_and_catalogs_are_synced(self) -> None:
        self.assertEqual(validate_sync(), [])


if __name__ == "__main__":
    unittest.main()
