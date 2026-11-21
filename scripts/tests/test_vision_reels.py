"""The nightly sync must retain each published reel once and preserve the article body."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vision_reels import EPISODES, insert

ARTICLE = '<header class="masthead"><h1>제목</h1></header>\n<dl class="spec"></dl>\n<section>본문</section>'


class VisionReelsTest(unittest.TestCase):
    def test_sync_is_idempotent_and_keeps_existing_content(self):
        for slug in EPISODES:
            with self.subTest(slug=slug):
                result = insert(ARTICLE, slug)
                self.assertEqual(insert(result, slug), result)
                self.assertEqual(result.count('id="video-explainer"'), 1)
                self.assertEqual(
                    result.count('class="vision-reel"'), len(EPISODES[slug])
                )
                self.assertEqual(result.count('src="../vision-reels.js'), 1)
                for entry in EPISODES[slug]:
                    self.assertEqual(
                        result.count(f'src="../media/vision/{entry[0]}/video.mp4"'), 1
                    )
                self.assertTrue(result.startswith(ARTICLE.split("\n")[0]))
                self.assertTrue(result.endswith(ARTICLE.split("\n", 1)[1]))

    def test_unpublished_article(self):
        self.assertEqual(insert(ARTICLE, "embeddings"), ARTICLE)
