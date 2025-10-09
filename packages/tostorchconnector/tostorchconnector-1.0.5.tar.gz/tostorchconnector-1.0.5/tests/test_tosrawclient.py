import os
import unittest
import uuid

import tos
from tos.exceptions import TosServerError


class TestTosRawClient(unittest.TestCase):
    def test_put_get(self):
        from tosnativeclient import TosRawClient, HeadObjectInput, TosException, DeleteObjectInput, \
            PutObjectFromBufferInput, \
            GetObjectInput, GetObjectOutput

        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        key = str(uuid.uuid4())
        tos_raw_client = TosRawClient(region, endpoint, ak, sk)

        doutput = tos_raw_client.delete_object(DeleteObjectInput(bucket, key))
        assert doutput.status_code == 204

        try:
            tos_raw_client.head_object(HeadObjectInput(bucket, key))
            assert False
        except TosException as e:
            assert e.args[0].status_code == 404
            assert len(e.args[0].request_id) > 0

        data = str(uuid.uuid4()).encode('utf-8')
        input = PutObjectFromBufferInput(bucket, key, data)
        poutput = tos_raw_client.put_object_from_buffer(input)
        assert poutput.status_code == 200
        assert len(poutput.etag) > 0

        houtput = tos_raw_client.head_object(HeadObjectInput(bucket, key))
        assert houtput.status_code == 200
        assert houtput.etag == poutput.etag
        assert houtput.content_length == len(data)

        goutput: GetObjectOutput = tos_raw_client.get_object(GetObjectInput(bucket, key))
        assert goutput.status_code == 200
        assert goutput.etag == poutput.etag
        rdata = goutput.read_all()
        assert rdata == data

        doutput = tos_raw_client.delete_object(DeleteObjectInput(bucket, key))
        assert doutput.status_code == 204

        try:
            tos_raw_client.get_object(GetObjectInput(bucket, key))
            assert False
        except TosException as e:
            assert e.args[0].status_code == 404
            assert len(e.args[0].request_id) > 0

    def test_put_get_old(self):
        region = os.getenv('TOS_REGION')
        endpoint = os.getenv('TOS_ENDPOINT')
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        bucket = 'tos-pytorch-connector'
        key = str(uuid.uuid4())
        tos_client = tos.TosClientV2(ak, sk, endpoint=endpoint, region=region)
        doutput = tos_client.delete_object(bucket, key)
        assert doutput.status_code == 204

        try:
            tos_client.head_object(bucket, key)
            assert False
        except TosServerError as e:
            assert e.status_code == 404
            assert len(e.request_id) > 0

        data = str(uuid.uuid4()).encode('utf-8')
        poutput = tos_client.put_object(bucket, key, content=data)
        assert poutput.status_code == 200
        assert len(poutput.etag) > 0

        houtput = tos_client.head_object(bucket, key)
        assert houtput.status_code == 200
        assert houtput.etag == poutput.etag
        assert houtput.content_length == len(data)

        goutput = tos_client.get_object(bucket, key)
        assert goutput.status_code == 200
        assert goutput.etag == poutput.etag
        rdata = goutput.read()
        assert rdata == data

        doutput = tos_client.delete_object(bucket, key)
        assert doutput.status_code == 204

        try:
            tos_client.get_object(bucket, key)
            assert False
        except TosServerError as e:
            assert e.status_code == 404
            assert len(e.request_id) > 0
