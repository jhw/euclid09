from euclid09.model import Project
from euclid09.git import Git, CommitId

from unittest.mock import patch, mock_open

import itertools
import json
import os
import shutil
import unittest

class GitTest(unittest.TestCase):

    def setUp(self):
        self.root_dir = "tmp/mock_root"
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)
        self.git = Git(root=self.root_dir)
        self.sample_content = Project()

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_git_initialization(self, mock_exists, mock_makedirs):
        git = Git(root=self.root_dir)
        mock_exists.assert_called_with(self.root_dir)
        mock_makedirs.assert_called_once_with(self.root_dir)
        self.assertEqual(git.root, self.root_dir)
        self.assertEqual(git.commits, [])
        self.assertTrue(git.is_empty())

    @patch("euclid09.git.random_name", return_value="random-slug")
    @patch("euclid09.model.Project.to_json", return_value={})
    @patch("builtins.open", new_callable=mock_open)
    def test_commit(self, mock_open, mock_to_json, mock_random_name):
        commit_id = self.git.commit(content=self.sample_content)
        self.assertEqual(len(self.git.commits), 1)
        self.assertEqual(self.git.head.commit_id, commit_id)
        self.assertIn("random-slug", str(commit_id))
        
        # Ensure file was written
        filename = f"{self.root_dir}/{commit_id}.json"
        mock_open.assert_called_once_with(filename, "w")
        handle = mock_open()
        handle.write.assert_called_once_with(json.dumps({}, indent=2))

    def unique_slug_generator():
        for i in itertools.count(1):
            yield f"slug-{i}"

    @patch("euclid09.git.random_name", side_effect=unique_slug_generator())
    @patch("euclid09.model.Project.clone", return_value=Project())
    def test_checkout(self, mock_clone, mock_random_name):
        first_commit_id = self.git.commit(content=self.sample_content)
        second_commit_id = self.git.commit(content=self.sample_content)
        with self.assertLogs(level="INFO") as log:
            new_commit_id = self.git.checkout(str(first_commit_id))
            self.assertIsNotNone(new_commit_id)
            self.assertEqual(len(self.git.commits), 3)
            self.assertEqual(self.git.head.commit_id, new_commit_id)
            self.assertIn("Checked out to new commit at HEAD", log.output[0])
        with self.assertLogs(level="WARNING") as log:
            self.git.checkout("non-existent-id")
            self.assertIn("Commit non-existent-id not found", log.output[0])
        
    def test_undo(self):
        self.git.commit(content=self.sample_content)
        self.git.commit(content=self.sample_content)
        self.git.undo()
        self.assertEqual(self.git.head_index, 0)
        self.assertEqual(len(self.git.redo_stack), 1)

    def test_redo(self):
        self.git.commit(content=self.sample_content)
        self.git.commit(content=self.sample_content)
        self.git.undo()
        self.git.redo()
        self.assertEqual(self.git.head_index, 1)
        self.assertEqual(len(self.git.redo_stack), 0)

    def test_undo_with_no_commits(self):
        self.git.undo()
        self.assertTrue(self.git.is_empty())
        self.assertEqual(len(self.git.redo_stack), 0)

    def test_redo_with_no_redo_stack(self):
        self.git.commit(content=self.sample_content)
        self.git.redo()
        self.assertEqual(self.git.head_index, 0)

    @patch("os.listdir", return_value=["2024-11-10-12-30-00-random-slug.json"])
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"tracks": []}))
    def test_fetch(self, mock_open, mock_listdir):
        with patch.object(Project, "from_json", return_value=self.sample_content) as mock_from_json:
            self.git.fetch()
            self.assertEqual(len(self.git.commits), 1)
            self.assertEqual(self.git.head_index, 0)
            mock_from_json.assert_called_once()
            mock_open.assert_called_once_with(f"{self.root_dir}/2024-11-10-12-30-00-random-slug.json", "r")

if __name__ == "__main__":
    unittest.main()
