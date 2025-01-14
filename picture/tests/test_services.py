import os
from mock import ANY, call, Mock, patch
import uuid

from flask import current_app
import pytest 

import picture.services as ps
import conftest
from thermal.exceptions import DocumentConfigurationError, NotFoundError


class TestPictureIntegration(object):
    def test_find_picture_finds_the_correct_picture_document(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        current_app.db[the_pic_id] = picture_doc
        new_picture_doc = ps.find_picture(the_pic_id)
        assert new_picture_doc['_id'] == the_pic_id
        assert new_picture_doc['type'] == 'picture'
        assert '_rev' in new_picture_doc

    def test_find_picture_fails_if_the_picture_doesnt_exist(self):
        the_id = str(uuid.uuid4())
        with pytest.raises(NotFoundError):
            the_returned_doc = ps.find_picture(the_id)

    def test_save_picture_document_works(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        ps.save_picture_document(picture_doc)
        new_picture_doc = ps.find_picture(the_pic_id)
        assert new_picture_doc['_id'] == the_pic_id

    def test_save_picture_document_fails_if_picture_already_in_db(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'picture'
        }
        ps.save_picture_document(picture_doc)
        with pytest.raises(DocumentConfigurationError):
            ps.save_picture_document(picture_doc)

    def test_save_picture_document_fails_if_no_type_defined(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id
        }
        with pytest.raises(DocumentConfigurationError):
            ps.save_picture_document(picture_doc)

    def test_save_picture_document_fails_if_type_is_not_picture(self):
        the_pic_id = str(uuid.uuid4())
        picture_doc = {
            '_id': the_pic_id,
            'type': 'not_picture'
        }
        with pytest.raises(DocumentConfigurationError):
            ps.save_picture_document(picture_doc)

    def test_find_pictures_works_with_snap_id(self):
        snap_id_1 = uuid.uuid4()
        snap_id_2 = uuid.uuid4()
        pic_id_1 = uuid.uuid4()
        pic_id_2 = uuid.uuid4()
        pic_id_3 = uuid.uuid4()
        pic_doc_1 = {
            '_id': str(pic_id_1),
            'snap_id': str(snap_id_1),
            'type': 'picture'
        }
        ps.save_picture_document(pic_doc_1)
        pic_doc_2 = {
            '_id': str(pic_id_2),
            'snap_id': str(snap_id_2),
            'type': 'picture'
        }
        ps.save_picture_document(pic_doc_2)
        pic_doc_3 = {
            '_id': str(pic_id_3),
            'snap_id': str(snap_id_1),
            'type': 'picture'
        }
        ps.save_picture_document(pic_doc_3)
        pictures_dict = ps.find_pictures({'snap_id': str(snap_id_1)})
        expected_dict = {str(pic_id_1): {'_id': str(pic_id_1),
                                         '_rev': ANY,
                                         'snap_id': str(snap_id_1),
                                         'type': 'picture'},
                         str(pic_id_3): {'_id': str(pic_id_3),
                                         '_rev': ANY,
                                         'snap_id': str(snap_id_1),
                                         'type': 'picture'}
                         }
        assert pictures_dict == expected_dict

    def test_find_pictures_only_fetches_pictures(self):
        snap_id_1 = uuid.uuid4()
        id_1 = uuid.uuid4()
        id_2 = uuid.uuid4()
        doc_1 = {
            '_id': str(id_1),
            'snap_id': str(snap_id_1),
            'type': 'picture'
        }
        ps.save_picture_document(doc_1)
        doc_2 = {
            '_id': str(id_2),
            'snap_id': str(snap_id_1),
            'type': 'not_picture'
        }
        current_app.db[str(id_2)] = doc_2
        pictures_dict = ps.find_pictures({'snap_id': str(snap_id_1)})
        expected_dict = {str(id_1): {'_id': str(id_1),
                                     '_rev': ANY,
                                     'snap_id': str(snap_id_1),
                                     'type': 'picture'}
                        }
        assert pictures_dict == expected_dict

    def test_build_picture_name_builds_picture_name_with_jpg(self):
        picture_id = uuid.uuid4()
        picture_name = ps.build_picture_name(picture_id)
        expected_name = str(picture_id) + '.jpg'
        assert expected_name == picture_name

    def test_build_picture_path_creates_directory_if_not_present(self):
        picture_name = 'whatever'
        snap_id = uuid.uuid4()
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        picture_path = ps.build_picture_path(picture_name=picture_name, snap_id=snap_id)
        assert os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))

    def test_build_picture_path_does_not_create_directory_if_requested(self):
        picture_name = 'whatever'
        snap_id = uuid.uuid4()
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))
        picture_path = ps.build_picture_path(picture_name=picture_name, snap_id=snap_id, create_directory=False)
        assert not os.path.isdir(os.path.join(current_app.config['PICTURE_SAVE_DIRECTORY'], str(snap_id)))

    def test_picture_exists_returns_true_when_picture_exists(self):
        pic_id = uuid.uuid4()
        doc_1 = {
            '_id': str(pic_id),
            'type': 'picture'
        }
        ps.save_picture_document(doc_1)

        assert True == ps.picture_exists(pic_id)

    def test_picture_exists_returns_false_when_picture_does_not_exist(self):
        pic_id = uuid.uuid4()

        assert False == ps.picture_exists(pic_id)
