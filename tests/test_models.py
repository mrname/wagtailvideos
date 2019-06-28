from __future__ import unicode_literals

from unittest.mock import Mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from wagtail.tests.utils import WagtailTestUtils

from tests.utils import create_test_video_file
from wagtailvideos.models import Video, video_saved

class TestVideoModel(WagtailTestUtils, TestCase):

    def test_post_save_signal_raw(self):
        '''
        When called with the 'raw' kwarg, the post_save signal handler should
        do nothing. We will test this by asserting that it never calls save
        on the instance.
        '''
        mocked_instance = Mock()
        del mocked_instance._from_signal
        video_saved(Video, mocked_instance, raw=True)
        assert not mocked_instance.save.called

    @override_settings(WAGTAILVIDEOS_CREATE_FILE_HASH=True)
    def test_create_file_hash(self):
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert video.file_hash
        assert video.file_size
        current_hash = video.file_hash
        new_video_file = create_test_video_file(file_name='big_buck_bunny.mp4')
        video.file = new_video_file
        video.save()
        assert video.file_hash != current_hash

    def test_create_file_hash_disabled(self):
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert not video.file_hash
        assert video.file_size

    def test_thumbnail(self):
        # Creating a video with no provided thumbnail should auto-create one
        video_file = create_test_video_file()
        video = Video(
            file=video_file
        )
        video.save()
        assert video.thumbnail
        # Change the thumbnail to a manually provided one
        video.thumbnail = SimpleUploadedFile('test.jpg', b'')
        video.save()
        # Change the video file, and ensure that our manually provided
        # thumbnail is still there
        video_file = create_test_video_file()
        video.file = video_file
        video.save()
        assert video.thumbnail.name == 'original_videos/test.jpg'
