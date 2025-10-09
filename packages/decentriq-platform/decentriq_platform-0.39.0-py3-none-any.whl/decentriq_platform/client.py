import hashlib
import json
import os
from base64 import b64decode, b64encode, urlsafe_b64decode, urlsafe_b64encode
from concurrent import futures
from threading import BoundedSemaphore
from typing import BinaryIO, Dict, List, Optional, Tuple, cast, Generator
import io
import requests

from decentriq_dcr_compiler import compiler
from decentriq_dcr_compiler import ab_media as ab_media_compiler
from decentriq_dcr_compiler.schemas import DataScienceDataRoom
from decentriq_dcr_compiler.schemas import AbMediaDcr as AbMediaDcrSchema
from decentriq_dcr_compiler.schemas.secret_store_entry_state import SecretStoreEntryState as SecretStoreEntryStateSchema, v0 as v0_schema
from decentriq_dcr_compiler.types.secret_store_entry_state import v0

from .analytics import AnalyticsDcr, AnalyticsDcrDefinition
from .api import Api, Endpoints, NotFoundError, retry
from .attestation import enclave_specifications
from .authentication import Auth, generate_key, generate_self_signed_certificate
from .config import (
    _DECENTRIQ_UNSAFE_DISABLE_KNOWN_ROOT_CA_CHECK,
    DECENTRIQ_CLIENT_ID,
    DECENTRIQ_HOST,
    DECENTRIQ_PORT,
    DECENTRIQ_USE_TLS,
    DECENTRIQ_MRSIGNER_DRIVER_ATTESTATION_SPECIFICATION,
    DECENTRIQ_DISABLE_DATASET_ACL_ORGANIZATION_CHECK,
)
from .connection import Connection
from .endorsement import Endorser
from .graphql import GqlClient
from .ab_media import AbMediaDcr, AbMediaDcrDefinition
from .proto import AttestationSpecification, AuthenticationMethod, CreateDcrKind
from .proto import DataRoom as ProtoDataRoom
from .proto import PkiPolicy, parse_length_delimited, serialize_length_delimited
from .session import LATEST_WORKER_PROTOCOL_VERSION, Session
from .archv2 import Secret, SessionV2, ClientV2
from .storage import Chunker, Key, StorageCipher, create_encrypted_chunk, decrypt_chunk
from .types import (
    JSONType,
    CreateMediaComputeJobInput,
    DataLabDefinition,
    DataLabListFilter,
    DataRoom,
    DataRoomDescription,
    DataRoomKind,
    DatasetDescription,
    DatasetUsage,
    EnclaveSpecification,
    MediaComputeJob,
    MediaComputeJobFilterInput,
    OrganizationUser,
)
from .logger import logger

class SecretStoreOptions:
    def __init__(
        self,
        *,
        store_encryption_key: bool = True,
        encryption_key_acl: Optional[JSONType] = None,
        encryption_key_acl_version: int = 0,
    ):
        self.store_encryption_key = store_encryption_key
        if not store_encryption_key and encryption_key_acl is not None:
            raise ValueError("Encryption key ACL can only be set when storing the encryption key")
        self.encryption_key_acl = encryption_key_acl
        self.encryption_key_acl_version = encryption_key_acl_version

    def validate_users(self, client_user: str, organization_user: List[OrganizationUser]):
        # Validate the encryption key ACL
        if self.encryption_key_acl is not None:
            if self.encryption_key_acl_version == 0:
                # Check it's in valid format
                v0_schema.SecretStoreEntryAcl.model_validate(self.encryption_key_acl)
                validated_encryption_key_acl = cast(v0.SecretStoreEntryAcl, self.encryption_key_acl)
                if validated_encryption_key_acl["type"] == "UsersList":
                    # Check it contains at least one owner
                    if not any(user["role"] == "Owner" for user in validated_encryption_key_acl["users"]):
                        raise ValueError("Encryption key ACL must contain at least one owner")
                    # Check:
                    # - it contains only users from the organization

                    # Allow users to share datasets with other orgs (used for service users in the DMP)
                    if DECENTRIQ_DISABLE_DATASET_ACL_ORGANIZATION_CHECK:
                        return

                    organization_user_emails = set(user["email"] for user in organization_user)
                    for user in validated_encryption_key_acl["users"]:
                        if user["id"] == client_user:
                            continue
                        if user["id"] not in organization_user_emails:
                            raise ValueError("Encryption key ACL must contain only users from your organization")
                else:
                    raise ValueError(f"Unsupported encryption key ACL type {validated_encryption_key_acl['type']}")
            else:
                raise ValueError(f"Unsupported encryption key ACL version {self.encryption_key_acl_version}")

class Client:
    """
    A `Client` object allows you to upload datasets and to create `Session` objects that
    can communicate with enclaves and perform essential operations such as publishing
    data rooms and execute computations and retrieve results.

    Objects of this class can be used to create and run data rooms, as well as to securely
    upload data and retrieve computation results.

    Objects of this class should be created using the `create_client` function.
    """

    _api: Api
    _graphql: GqlClient
    _connections: Dict[str, Connection]
    _mrsigner_driver_spec: AttestationSpecification
    _cached_session_v2: Optional[SessionV2] = None
    client_v2: ClientV2

    def __init__(
        self,
        user_email: str,
        enclave_api_token: str,
        api: Api,
        graphql: GqlClient,
        request_timeout: Optional[int] = None,
        unsafe_disable_known_root_ca_check: bool = False,
        custom_mrsigner_driver_spec: Optional[AttestationSpecification] = None,
    ):
        """
        Create a client instance.

        Rather than creating `Client` instances directly using this constructor,
        use the function `create_client`.
        """
        self.user_email = user_email
        self.enclave_api_token = enclave_api_token
        self._api = api
        self._graphql = graphql
        self.request_timeout = request_timeout
        self.unsafe_disable_known_root_ca_check = unsafe_disable_known_root_ca_check
        self._connections = dict()
        if custom_mrsigner_driver_spec is not None:
            self._mrsigner_driver_spec = custom_mrsigner_driver_spec
        else:
            if DECENTRIQ_MRSIGNER_DRIVER_ATTESTATION_SPECIFICATION is not None:
                mrsigner_decoded_spec = AttestationSpecification()
                parse_length_delimited(
                    b64decode(DECENTRIQ_MRSIGNER_DRIVER_ATTESTATION_SPECIFICATION),
                    mrsigner_decoded_spec,
                )
                self._mrsigner_driver_spec = mrsigner_decoded_spec
            else:
                self._mrsigner_driver_spec = enclave_specifications.specifications["decentriq.driver:mrsigner"]["proto"]
        self.client_v2 = ClientV2(self._api)

    def check_enclave_availability(self, specs: Dict[str, EnclaveSpecification]):
        """
        Check whether the selected enclaves are deployed at this moment.
        If one of the enclaves is not deployed, an exception will be raised.
        """
        available_specs = [
            spec["proto"].SerializeToString()
            for spec in self._get_enclave_specifications()
        ]
        for spec in specs.values():
            if spec["proto"].SerializeToString() not in available_specs:
                raise Exception(
                    "No available enclave deployed for attestation spec '{name}' (version {version})".format(
                        name=spec["name"], version=spec["version"]
                    )
                )

    def _get_enclave_specifications(self) -> List[EnclaveSpecification]:
        data = self._graphql.post(
            """
            {
                attestationSpecsV2 {
                    name
                    version
                    spec
                }
            }
            """
        )
        enclave_specs = []
        for spec_json in data["attestationSpecsV2"]:
            attestation_specification = AttestationSpecification()
            spec_length_delimited = b64decode(spec_json["spec"])
            parse_length_delimited(spec_length_delimited, attestation_specification)
            enclave_spec = EnclaveSpecification(
                name=spec_json["name"],
                version=spec_json["version"],
                proto=attestation_specification,
                decoder=None,
                workerProtocols=[LATEST_WORKER_PROTOCOL_VERSION],
                clientProtocols=None,
            )
            enclave_specs.append(enclave_spec)
        return enclave_specs

    def create_session_from_data_room_description(
        self,
        data_room_description: DataRoomDescription,
        specs: Optional[List[EnclaveSpecification]] = None,
    ) -> Session:
        """
        Create a session for interacting with a DCR of the given data room description.
        """
        driver_attestation_hash = data_room_description["driverAttestationHash"]
        driver_enclave_spec = dict()
        specs = specs if specs else enclave_specifications.all()
        for spec in specs:
            attestation_hash = hashlib.sha256(
                serialize_length_delimited(spec["proto"])
            ).hexdigest()
            if attestation_hash == driver_attestation_hash:
                driver_enclave_spec = {"decentriq.driver": spec}
                break
        if not driver_enclave_spec:
            raise Exception(
                f"Driver enclave specification with attestation hash {driver_attestation_hash} not found"
            )
        auth, _ = self.create_auth_using_decentriq_pki(driver_enclave_spec)
        return self.create_session(auth, driver_enclave_spec)

    def create_session_v2(
        self,
    ) -> SessionV2:
        """
        Creates a new `decentriq_platform.session.SessionV2` instance to communicate
        with a driver enclave.
        """
        if self._cached_session_v2 is None:
            attestation_proto = self._mrsigner_driver_spec
            attestation_specification_hash = hashlib.sha256(
                serialize_length_delimited(attestation_proto)
            ).hexdigest()
            connection = self._connections.get(attestation_specification_hash)
            if connection is None:
                connection = Connection(
                    attestation_proto,
                    self._api,
                    self._graphql,
                    self.unsafe_disable_known_root_ca_check,
                )
                self._connections[attestation_specification_hash] = connection
            session = SessionV2(
                self,
                connection,
            )
            self._cached_session_v2 = session
        return self._cached_session_v2

    def create_session(
        self,
        auth: Auth,
        enclaves: Dict[str, EnclaveSpecification],
    ) -> Session:
        """
        Creates a new `decentriq_platform.session.Session` instance to communicate
        with a driver enclave.
        The passed set of enclave specifications must include a specification for
        a driver enclave.

        Messages sent through this session will be authenticated
        with the given authentication object.
        """
        if "decentriq.driver" not in enclaves:
            raise Exception(
                "Unable to find a specification for the driver enclave"
                + f" named 'decentriq.driver', you can get these specifications"
                + " from the main package."
            )
        driver_spec = enclaves["decentriq.driver"]
        if (
            "clientProtocols" not in driver_spec
            or driver_spec["clientProtocols"] is None
        ):
            raise Exception("Missing client supported protocol versions")
        attestation_proto = driver_spec["proto"]
        client_protocols = driver_spec["clientProtocols"]
        attestation_specification_hash = hashlib.sha256(
            serialize_length_delimited(attestation_proto)
        ).hexdigest()
        connection = self._connections.get(attestation_specification_hash)
        if connection is None:
            connection = Connection(
                attestation_proto,
                self._api,
                self._graphql,
                self.unsafe_disable_known_root_ca_check,
            )
            self._connections[attestation_specification_hash] = connection
        session = Session(
            self,
            connection,
            client_protocols,
            auth=auth,
        )

        return session

    def _ensure_dataset_scope(
        self,
        manifest_hash: Optional[str] = None,
    ) -> str:
        payload = {
            "manifestHash": manifest_hash,
        }
        data = self._graphql.post(
            """
            mutation GetOrCreateDatasetScope($input: CreateDatasetScopeInput!) {
                scope {
                    getOrCreateDatasetScope(input: $input) {
                        record {
                            id
                        }
                    }

                }
            }
            """,
            {"input": payload},
        )
        scope = data["scope"]["getOrCreateDatasetScope"]["record"]
        return scope["id"]

    def _ensure_dcr_data_scope(
        self,
        data_room_hash: str,
    ) -> str:
        data = self._graphql.post(
            """
            mutation GetOrCreateDcrDataScope($input: CreateDcrDataScopeInput!) {
                scope {
                    getOrCreateDcrDataScope(input: $input) {
                        record {
                            id
                        }
                    }

                }
            }
            """,
            {
                "input": {
                    "dataRoomHash": data_room_hash,
                }
            },
        )
        scope = data["scope"]["getOrCreateDcrDataScope"]["record"]
        return scope["id"]

    def _set_datalab_matching_dataset(
        self,
        data_lab_id: str,
        manifest_hash: Optional[str],
    ) -> str:
        """
        Store the matching dataset manifest hash in the database.
        """
        data = self._graphql.post(
            """
            mutation SetDataLabUsersDataset($input: SetDataLabDatasetInput!) {
                dataLab {
                    setUsersDataset(input: $input) {
                        record {
                            id
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                        }
                    }

                }
            }
            """,
            {"input": {"id": data_lab_id, "manifestHash": manifest_hash}},
        )
        return data["dataLab"]["setUsersDataset"]["record"]["id"]

    def _set_datalab_segments_dataset(
        self,
        data_lab_id: str,
        manifest_hash: Optional[str],
    ) -> str:
        """
        Store the segments dataset manifest hash in the database.
        """
        data = self._graphql.post(
            """
            mutation SetDataLabSegmentsDataset($input: SetDataLabDatasetInput!) {
                dataLab {
                    setSegmentsDataset(input: $input) {
                        record {
                            id
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                        }
                    }

                }
            }
            """,
            {"input": {"id": data_lab_id, "manifestHash": manifest_hash}},
        )
        return data["dataLab"]["setSegmentsDataset"]["record"]["id"]

    def _set_datalab_demographics_dataset(
        self,
        data_lab_id: str,
        manifest_hash: Optional[str],
    ) -> str:
        """
        Store the demographics dataset manifest hash in the database.
        """
        data = self._graphql.post(
            """
            mutation SetDataLabDemographicsDataset($input: SetDataLabDatasetInput!) {
                dataLab {
                    setDemographicsDataset(input: $input) {
                        record {
                            id
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                        }
                    }

                }
            }
            """,
            {"input": {"id": data_lab_id, "manifestHash": manifest_hash}},
        )
        return data["dataLab"]["setDemographicsDataset"]["record"]["id"]

    def _set_datalab_embeddings_dataset(
        self,
        data_lab_id: str,
        manifest_hash: Optional[str],
    ) -> str:
        """
        Store the embeddings dataset manifest hash in the database.
        """
        data = self._graphql.post(
            """
            mutation SetDataLabEmbeddingsDataset($input: SetDataLabDatasetInput!) {
                dataLab {
                    setEmbeddingsDataset(input: $input) {
                        record {
                            id
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                        }
                    }

                }
            }
            """,
            {"input": {"id": data_lab_id, "manifestHash": manifest_hash}},
        )
        return data["dataLab"]["setEmbeddingsDataset"]["record"]["id"]

    def _set_datalab_job_ids(
        self,
        data_lab_id: str,
        validation_compute_job_id: str,
        statistics_compute_job_id: str,
        jobs_driver_attestation_hash: str,
    ) -> str:
        """
        Store the job IDs associated with the DataLab.
        """
        data = self._graphql.post(
            """
            mutation SetDataLabJobIds($input: SetDataLabJobIdsInput!) {
                dataLab {
                    setJobIds(input: $input) {
                        record {
                            id
                        }
                    }

                }
            }
            """,
            {
                "input": {
                    "id": data_lab_id,
                    "validationComputeJobId": validation_compute_job_id,
                    "statisticsComputeJobId": statistics_compute_job_id,
                    "jobsDriverAttestationHash": jobs_driver_attestation_hash,
                }
            },
        )
        return data["dataLab"]["setJobIds"]["record"]["id"]

    def _set_datalab_statistics(
        self,
        data_lab_id: str,
        statistics: str,
    ) -> str:
        """
        Store the DataLab statistics in the database.
        """
        data = self._graphql.post(
            """
            mutation SetDataLabStatistics($input: SetDataLabStatisticsInput!) {
                dataLab {
                    setStatistics(input: $input) {
                        record {
                            id
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "id": data_lab_id,
                    "statistics": json.loads(statistics),
                }
            },
        )
        return data["dataLab"]["setStatistics"]["record"]["id"]

    def _iter_response_encrypted_chunks(self, response):
        expecting_header = True
        buffer = bytearray()
        chunk_size = None
        for chunk in response.iter_content(chunk_size=8 * 1024 * 1024 + 4096):
            buffer += chunk
            while True:
                if expecting_header:
                    splits = buffer.split(b'\n', 1)
                    if len(splits) == 1:
                        break
                    if len(splits) != 2:
                        raise Exception(f"Error during stream decoding: Expected header and data to be separated by a newline")
                    json_header = json.loads(splits[0])
                    if "V0" not in json_header:
                        raise Exception(f"Error during stream decoding: Expected V0 header")
                    if "Failure" in json_header["V0"]:
                        raise Exception(f"Error during stream decoding: {json_header['V0']['Failure']['error']}")
                    if "Next" not in json_header["V0"]:
                        raise Exception(f"Error during stream decoding: Expected Next header")
                    chunk_size = json_header["V0"]["Next"]['size']
                    if chunk_size > 8 * 1024 * 1024 + 4096:
                        raise Exception(f"Chunk size {chunk_size} is too large")
                    expecting_header = False
                    buffer = splits[1]

                if len(buffer) < chunk_size:
                    break
                else:
                    yield memoryview(buffer)[:chunk_size]
                    buffer = buffer[chunk_size:]
                    chunk_size = None
                    expecting_header = True

        if len(buffer) > 0:
            raise Exception(f"Error during stream decoding: unexpected trailing data")

    def _iter_response_decrypted(self, response: requests.Response, key: Key, chunk_hashes: List[str]) -> Generator[bytes, None, None]:
        for chunk_hash, encrypted_chunk in zip(chunk_hashes, self._iter_response_encrypted_chunks(response)):
            yield decrypt_chunk(key, chunk_hash, encrypted_chunk)

    def _stream_response_decrypted(self, response: requests.Response, key: Key, chunk_hashes: List[str]) -> io.RawIOBase:
        return GeneratorStream(self._iter_response_decrypted(response, key, chunk_hashes))

    def download_dataset(self, manifest_hash: str, key: Key) -> io.RawIOBase:
        # First get the manifest
        response = self._api.post(
            Endpoints.DATASET_CHUNKS_STREAM.replace(":manifest_hash", manifest_hash),
            headers={"Content-type": "application/octet-stream"},
            req_body=manifest_hash,
        )
        chunk_hashes = json.loads(self._stream_response_decrypted(response, key, [manifest_hash]).read())

        # Now download the chunks
        response = self._api.post(
            Endpoints.DATASET_CHUNKS_STREAM.replace(":manifest_hash", manifest_hash),
            headers={"Content-type": "application/octet-stream"},
            req_body="\n".join(chunk_hashes),
        )

        return self._stream_response_decrypted(response, key, chunk_hashes)

    def download_job_result(self, job_id: str, manifest_hash: str, task_result_hash: str, key: Key) -> io.RawIOBase:
        endpoint = Endpoints.JOB_RESULT_CHUNKS_STREAM.replace(":job_id", job_id).replace(
            ":task_result_hash", task_result_hash
        )

        # First get the manifest
        response = self._api.post(
            endpoint,
            headers={"Content-type": "application/octet-stream"},
            req_body=manifest_hash,
        )
        chunk_hashes = json.loads(
            self._stream_response_decrypted(response, key, [manifest_hash]).read()
        )

        # Now download the chunks
        response = self._api.post(
            endpoint,
            headers={"Content-type": "application/octet-stream"},
            req_body="\n".join(chunk_hashes),
        )

        return self._stream_response_decrypted(response, key, chunk_hashes)

    def upload_dataset(
        self,
        data: BinaryIO,
        key: Key,
        file_name: str,
        /,
        *,
        description: str = "",
        chunk_size: int = 8 * 1024**2,
        parallel_uploads: int = 8,
        usage: DatasetUsage = DatasetUsage.PUBLISHED,
        secret_store_options: Optional[SecretStoreOptions] = None,
        is_accessory: bool = False
    ) -> str:
        """
        Uploads `data` as a file usable by enclaves and returns the
        corresponding manifest hash.

        **Parameters**:
        - `data`: The data to upload as a buffered stream.
            Such an object can be obtained by wrapping a binary string in a `io.BytesIO()`
            object or, if reading from a file, by using `with open(path, "rb") as file`.
        - `key`: Encryption key used to encrypt the file.
        - `file_name`: Name of the file.
        - `description`: An optional file description.
        - `chunk_size`: Size of the chunks into which the stream is split in bytes.
        - `parallel_uploads`: Whether to upload chunks in parallel.
        - `usage`: The usage of the dataset.
        - `secret_store_options`: Options for the secret store.
            It can be used to specify if the encryption key should be stored in the secret store
            and can also be used to provide a custom ACL for the encryption key.
        - `is_accessory`: Whether this dataset should be hidden from the datasets page.
        """
        if secret_store_options is None:
            secret_store_options = SecretStoreOptions()
        else:
            secret_store_options.validate_users(self.user_email, self._get_my_organization_users())
        uploader = BoundedExecutor(
            bound=parallel_uploads * 2, max_workers=parallel_uploads
        )
        # create and upload chunks
        chunker = Chunker(data, chunk_size=chunk_size)
        chunk_hashes: List[str] = []
        chunk_content_sizes: List[int] = []
        chunk_uploads_futures = []
        upload_id = self._create_upload()

        for chunk_hash, chunk_data, chunk_content_size in chunker:
            chunk_uploads_futures.append(
                uploader.submit(
                    self._encrypt_and_upload_chunk,
                    chunk_hash,
                    chunk_data,
                    key.material,
                    upload_id,
                )
            )
            chunk_hashes.append(chunk_hash.hex())
            chunk_content_sizes.append(chunk_content_size)

        # check chunks uploads were successful
        completed, pending = futures.wait(
            chunk_uploads_futures, None, futures.FIRST_EXCEPTION
        )
        # re-raise exception
        for future in completed:
            future.result()
        uploader.shutdown(wait=False)

        # create manifest and upload
        manifest_hash_bytes, manifest_encrypted = create_encrypted_chunk(
            key.material,
            os.urandom(16),
            json.dumps(chunk_hashes).encode("utf-8"),
            content_size=chunker.content_size,
            chunk_content_sizes=chunk_content_sizes,
        )
        scope_id = self._ensure_dataset_scope(
            manifest_hash_bytes.hex(),
        )
        manifest_hash = self._finalize_upload(
            scope_id=scope_id,
            upload_id=upload_id,
            name=file_name,
            manifest_hash_bytes=manifest_hash_bytes,
            manifest_encrypted=manifest_encrypted,
            chunks=chunk_hashes,
            description=description,
            usage=usage,
            size=sum(chunk_content_sizes),
            is_accessory=is_accessory,
        )

        if secret_store_options.store_encryption_key:
            session_v2 = self.create_session_v2()

            if secret_store_options.encryption_key_acl_version == 0:
                acl = secret_store_options.encryption_key_acl if secret_store_options.encryption_key_acl is not None else {
                    "type": "UsersList",
                    "users": [
                        {
                            "id": self.user_email,
                            "role": "Owner",
                        },
                    ],
                }
                encryption_key_secret = Secret(secret=key.material, state=SecretStoreEntryStateSchema.model_validate(
                    {
                        "version": "V0",
                        "acl": acl,
                        "type": "DatasetKey",
                        "manifest_hash": manifest_hash,
                    }
                ))
            else:
                raise ValueError(f"Unsupported encryption key ACL version {secret_store_options.encryption_key_acl_version}")
            session_v2.create_secret(encryption_key_secret)

        return manifest_hash

    def get_dataset_key(self, manifest_hash: str) -> Key:
        dataset_encryption_key_secret_id = self.get_dataset_encryption_key_secret_id(manifest_hash)
        if dataset_encryption_key_secret_id is None:
            raise Exception(f"Dataset with manifest hash {manifest_hash} has no associated secret")
        session_v2 = self.create_session_v2()
        dataset_encryption_key_secret, _ = session_v2.get_secret(dataset_encryption_key_secret_id)
        dataset_key = dataset_encryption_key_secret.secret
        return Key(dataset_key)

    def get_dataset_encryption_key_secret_id(self, manifest_hash: str) -> Optional[str]:
        dataset = self.get_dataset(manifest_hash)
        if dataset is None:
            raise Exception(f"Dataset with manifest hash {manifest_hash} not found")
        return dataset["encryptionKeySecretId"]

    def _encrypt_and_upload_chunk(
        self, chunk_hash: bytes, chunk_data: bytes, key: bytes, upload_id: str
    ):
        cipher = StorageCipher(key)
        chunk_data_encrypted = cipher.encrypt(chunk_data)
        self._upload_chunk(chunk_hash, chunk_data_encrypted, upload_id)

    def _create_upload(self) -> str:
        """
        Create an upload record for the user identified by the used
        API token and return its id.
        """
        data = self._graphql.post(
            """
            mutation CreateUpload() {
                upload {
                    create {
                        record {
                            id
                        }
                    }
                }
            }
            """,
        )
        upload_id = data["upload"]["create"]["record"]["id"]
        return upload_id

    def _upload_chunk(
        self, chunk_hash: bytes, chunk_data_encrypted: bytes, upload_id: str
    ):
        url = Endpoints.USER_UPLOAD_CHUNKS.replace(":uploadId", upload_id).replace(
            ":chunkHash", chunk_hash.hex()
        )
        try:
            self._api.put(
                url,
                chunk_data_encrypted,
                {"Content-type": "application/octet-stream"},
                retry=retry,
            )
        except Exception as e:
            logger.error(e)
            raise e

    def _delete_user_upload(self, upload_id: str):
        self._graphql.post(
            """
            mutation DeleteUpload($id: Id!) {
                upload {
                    delete(id: $id)
                }
            }
            """,
            {"id": upload_id},
        )

    def _finalize_upload(
        self,
        scope_id: str,
        upload_id: str,
        name: str,
        manifest_hash_bytes: bytes,
        manifest_encrypted: bytes,
        chunks: List[str],
        size: int,
        description: Optional[str] = None,
        usage: Optional[DatasetUsage] = None,
        is_accessory: bool = False,
    ) -> str:
        data = self._graphql.post(
            """
            mutation FinalizeUpload($input: CreateDatasetForUploadInput!) {
                upload {
                    finalizeUploadAndCreateDataset(input: $input) {
                        record {
                            id
                            manifestHash
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "uploadId": upload_id,
                    "manifest": b64encode(manifest_encrypted).decode("ascii"),
                    "manifestHash": manifest_hash_bytes.hex(),
                    "name": name,
                    "description": description,
                    "usage": usage,
                    "chunkHashes": chunks,
                    "scopeId": scope_id,
                    "size": size,
                    "isAccessory": is_accessory,
                }
            },
            retry=retry,
        )

        dataset = data["upload"]["finalizeUploadAndCreateDataset"]["record"]
        manifest_hash = dataset["manifestHash"]

        return manifest_hash

    def get_dataset(self, manifest_hash: str) -> Optional[DatasetDescription]:
        """
        Returns information about a user dataset given a dataset id.
        """
        try:
            data = self._graphql.post(
                """
                query GetDataset($manifestHash: HexString!)
                {
                    datasetByManifestHash(manifestHash: $manifestHash) {
                        id
                        name
                        manifestHash
                        description
                        createdAt
                        encryptionKeySecretId
                        metadataSecretId
                    }
                }
                """,
                {"manifestHash": manifest_hash},
            )
            return data["datasetByManifestHash"]
        except NotFoundError:
            return None

    def get_available_datasets(self) -> List[DatasetDescription]:
        """
        Returns the a list of datasets that the current user uploaded,
        regardless of whether they have already been connected to a
        data room or not.
        """
        data = self._graphql.post(
            """
            {
                myself {
                    datasets {
                        nodes {
                            id
                            name
                            manifestHash
                            statistics
                            size
                            description
                            createdAt
                            usage
                        }
                    }
                }
            }
            """
        )
        return data["myself"]["datasets"]["nodes"]

    def delete_dataset(self, manifest_hash: str, force: bool = False):
        """
        Deletes the dataset with the given id from the Decentriq platform.

        In case the dataset is still published to one or more data rooms,
        an exception will be thrown and the dataset will need to be
        unpublished manually from the respective data rooms using
        `Session.remove_published_dataset`.
        This behavior can be overridden by using the `force` flag.
        Note, however, that this might put some data rooms in a broken
        state as they might try to read data that does not exist anymore.
        """
        data_rooms_ids_with_dataset = self._get_data_room_ids_with_published_dataset(
            manifest_hash
        )
        if data_rooms_ids_with_dataset:
            id_list = "\n".join(
                [f"- {dcr_id}" for dcr_id in data_rooms_ids_with_dataset]
            )
            if force:
                logger.warning(
                    "This dataset is published to the following data rooms."
                    " These data rooms might be in a broken state now:"
                    f"\n{id_list}"
                )
            else:
                raise Exception(
                    "This dataset is published to the following data rooms"
                    " and needs to be unpublished before it can be deleted!"
                    f"\n{id_list}"
                )
        self._graphql.post(
            """
            mutation DeleteDataset($manifestHash: HexString!) {
                dataset {
                    deleteByManifestHash(manifestHash: $manifestHash)
                }
            }
            """,
            {
                "manifestHash": manifest_hash,
            },
        )

    @property
    def decentriq_ca_root_certificate(self) -> bytes:
        """
        Returns the root certificate used by the Decentriq identity provider.
        Note that when using this certificate in any authentication scheme,
        you trust Decentriq as an identity provider!
        """
        data = self._graphql.post(
            """
            {
                certificateAuthority {
                    rootCertificate
                }
            }
        """
        )
        certificate = data["certificateAuthority"]["rootCertificate"].encode("utf-8")
        return certificate

    @property
    def decentriq_pki_authentication(self) -> AuthenticationMethod:
        """
        The authentication method that uses the Decentriq root certificate to authenticate
        users.

        This method should be specified when building a data room in case you want to interact
        with the that data room either via the web interface or with sessions created using
        `create_auth_using_decentriq_pki`.
        Note that when using this authentication method you trust Decentriq as an identity provider!

        You can also create an `AuthenticationMethod` object directly and supply your own root certificate,
        with which to authenticate users connecting to your data room.
        In this case you will also need to issue corresponding user certificates and create your
        own custom `decentriq_platform.authentication.Auth` objects.
        """
        root_pki = self.decentriq_ca_root_certificate
        return AuthenticationMethod(dqPki=PkiPolicy(rootCertificatePem=root_pki))

    def create_auth_using_decentriq_pki(
        self, enclaves: Dict[str, EnclaveSpecification]
    ) -> Tuple[Auth, Endorser]:
        auth = self.create_auth()
        endorser = Endorser(auth, self, enclaves)
        dq_pki = endorser.decentriq_pki_endorsement()
        auth.attach_endorsement(decentriq_pki=dq_pki)
        return auth, endorser

    def create_auth(self) -> Auth:
        """
        Creates a `decentriq_platform.authentication.Auth` object which can be attached
        to `decentriq_platform.session.Session`.
        """
        keypair = generate_key()
        cert_chain_pem = generate_self_signed_certificate(self.user_email, keypair)
        auth = Auth(cert_chain_pem, keypair, self.user_email)
        return auth

    def get_data_room_descriptions(self, *, exclude_stopped_dcrs: bool = False) -> List[DataRoomDescription]:
        """
        Returns a list of data room descriptions that a user has created or
        participates in.

        Setting `exclude_stopped_dcrs` to `True` omits stopped data room descriptions
        from the returned list.
        """
        data = self._graphql.post(
            """
            {
                publishedDataRooms {
                    nodes {
                        id
                        title
                        driverAttestationHash
                        isStopped
                        createdAt
                        updatedAt
                        owner {
                            email
                        }
                        kind
                    }
                }
            }
            """
        )
        all_dcr_descriptions = [
            DataRoomDescription(**item) for item in data["publishedDataRooms"]["nodes"]
        ]
        if exclude_stopped_dcrs:
            active_dcr_descriptions = [
                d for d in all_dcr_descriptions if d["isStopped"] == False
            ]
            return active_dcr_descriptions
        else:
            return all_dcr_descriptions

    def get_data_room_description(
            self, data_room_hash, enclave_specs=None
    ) -> Optional[DataRoomDescription]:
        """
        Get a single data room description.
        """
        if enclave_specs is not None:
            driver_spec = enclave_specs["decentriq.driver"]
            attestation_proto = driver_spec["proto"]
            driver_attestation_hash = hashlib.sha256(
                serialize_length_delimited(attestation_proto)
            ).hexdigest()
        else:
            driver_attestation_hash = None
        return self._get_data_room_by_hash(data_room_hash, driver_attestation_hash)

    def _get_data_room_kind(
        self,
        data_room_id: str,
    ) -> DataRoomKind:
        """
        Get the kind of data room.
        """
        data = self._graphql.post(
            """
            query GetPublishedDataRoomType($dataRoomId: String!) {
                publishedDataRoom(id: $dataRoomId) {
                    kind
                }
            }
            """,
            {
                "dataRoomId": data_room_id,
            },
        )
        return data["publishedDataRoom"]["kind"]

    def _get_data_room_by_hash(
        self, data_room_hash: str, driver_attestation_hash: Optional[str] = None
    ) -> Optional[DataRoomDescription]:
        data = self._graphql.post(
            """
            query GetPublishedDataRoom($dataRoomHash: String!) {
                publishedDataRoom(id: $dataRoomHash) {
                    id
                    title
                    driverAttestationHash
                    isStopped
                    createdAt
                    updatedAt
                    owner {
                        email
                    }
                    kind
                }
            }
            """,
            {
                "dataRoomHash": data_room_hash,
            },
        )
        result = data.get("publishedDataRoom")
        if result is not None:
            dcr: DataRoomDescription = result
            if driver_attestation_hash is not None and dcr["driverAttestationHash"] != driver_attestation_hash:
                raise Exception(
                    f"Driver attestation hash for request dataroom doesn't match '{dcr['driverAttestationHash']}' != {driver_attestation_hash})"
                )
            return dcr
        else:
            return None

    def _get_user_certificate(self, email: str, csr_pem: str) -> str:
        data = self._graphql.post(
            """
            query getUserCertificate($input: UserCsrInput!) {
                certificateAuthority {
                    userCertificate(input: $input)
                }
            }
            """,
            {
                "input": {
                    "csrPem": csr_pem,
                    "email": email,
                }
            },
        )
        cert_chain_pem = data["certificateAuthority"]["userCertificate"]
        return cert_chain_pem

    def _get_data_room_ids_with_published_dataset(
        self, manifest_hash
    ) -> List[str]:
        data = self._graphql.post(
            """
                query GetDatasetPublications($manifestHash: HexString!) {
                    datasetByManifestHash(manifestHash: $manifestHash) {
                        publications {
                            nodes {
                                dataRoom {
                                    id
                                }
                            }
                        }
                    }
                }
                """,
            {
                "manifestHash": manifest_hash,
            },
        )
        publications = data["datasetByManifestHash"]["publications"]["nodes"]

        if publications:
            dcr_ids = list(set([publication["dataRoom"]["id"] for publication in publications]))
            return dcr_ids
        else:
            return []

    def _get_scope(self, scope_id: str):
        data = self._graphql.post(
            """
            query GetScope($scopeId: String!) {
                scope(id: $scopeId) {
                    id
                    organization {
                        id
                        name
                    }
                    owner {
                        id
                        email
                    }
                    scopeType
                    manifestHash
                    dataRoomHash
                    driverAttestationHash
                    createdAt
                }
            }
            """,
            {"scopeId": scope_id},
        )
        return data["scope"]

    def list_data_labs(
        self, filter: Optional[DataLabListFilter] = None
    ) -> List[DataLabDefinition]:
        """
        Return a list of DataLabs based on the `filter` criteria.

        **Parameters**:
        - `filter`: Criteria used to filter the list. Can be one of the following values:
            - NONE: Display all DataLabs.
            - VALIDATED: Display DataLabs that have been validated.
            - UNVALIDATED: Display DataLabs that have not been validated.
        """
        data = self._graphql.post(
            """
            query ListDataLabIds() {
                dataLabs {
                    nodes {
                        id
                        name
                        datasets {
                            name
                            dataset {
                                id
                                manifestHash
                                name
                            }
                        }
                        usersDataset {
                            id
                            manifestHash
                            name
                        }
                        segmentsDataset {
                            id
                            manifestHash
                            name
                        }
                        demographicsDataset {
                            id
                            manifestHash
                            name
                        }
                        embeddingsDataset  {
                            id
                            manifestHash
                            name
                        }
                        requireDemographicsDataset
                        requireEmbeddingsDataset
                        isValidated
                        numEmbeddings
                        matchingIdFormat
                        matchingIdHashingAlgorithm
                        validationComputeJobId
                        statisticsComputeJobId
                        jobsDriverAttestationHash
                        highLevelRepresentationAsString
                        createdAt
                        updatedAt
                    }
                }
            }
            """,
        )
        data_labs = data["dataLabs"]["nodes"]
        if filter is None:
            return [lab for lab in data_labs]
        elif filter == DataLabListFilter.VALIDATED:
            return [lab for lab in data_labs if lab["isValidated"] == True]
        elif filter == DataLabListFilter.UNVALIDATED:
            return [lab for lab in data_labs if lab["isValidated"] == False]
        else:
            raise Exception(f"Unknown DataLab filter {filter}")

    def get_data_lab(
        self,
        id: str,
    ) -> DataLabDefinition:
        """
        Return the DataLab with the given ID.

        **Parameters**:
        - `id`: ID of the DataLab to get.
        """
        data = self._graphql.post(
            """
            query GetDataLab($id: String!) {
                dataLab(id: $id) {
                    id
                    name
                    datasets {
                        name
                        dataset {
                            id
                            manifestHash
                            name
                        }
                    }
                    usersDataset {
                        id
                        manifestHash
                        name
                    }
                    segmentsDataset {
                        id
                        manifestHash
                        name
                    }
                    demographicsDataset {
                        id
                        manifestHash
                        name
                    }
                    embeddingsDataset {
                        id
                        manifestHash
                        name
                    }
                    statistics
                    requireSegmentsDataset
                    requireDemographicsDataset
                    requireEmbeddingsDataset
                    isValidated
                    numEmbeddings
                    matchingIdFormat
                    matchingIdHashingAlgorithm
                    validationComputeJobId
                    statisticsComputeJobId
                    jobsDriverAttestationHash
                    highLevelRepresentationAsString
                    forceSparkValidation
                    dropInvalidRows
                }
            }
            """,
            {"id": id},
        )
        return data["dataLab"]

    def _publish_data_lab_from_existing(
        self,
        data_lab: Dict[str, str],
    ) -> str:
        """
        Publish a DataLab from an existing high level representation.

        **Parameters**:
        - `data_lab`: DataLab high level representation
        """
        data = self._graphql.post(
            """
            mutation PublishDataLab($input: CreateDataLabFromExistingInput!) {
                dataLab {
                    createFromExisting(input: $input) {
                        record {
                            id
                        }
                    }
                }
            }
            """,
            {"input": {"dataLab": data_lab}},
        )
        return data["dataLab"]["createFromExisting"]["record"]["id"]

    def _get_enclave_spec_from_hash(self, hash: str) -> Optional[EnclaveSpecification]:
        available_specs = self._get_enclave_specifications()
        for spec in available_specs:
            hashed_attestation_spec = hashlib.sha256(
                serialize_length_delimited(spec["proto"])
            ).hexdigest()
            if hashed_attestation_spec == hash:
                return spec
        return None

    def _create_media_compute_job(
        self,
        input: CreateMediaComputeJobInput,
    ) -> MediaComputeJob:
        """
        Create a compute job for the Media DCR.
        """
        data = self._graphql.post(
            """
            mutation CreateMediaComputeJob($input: CreateMediaComputeJobInput!) {
                mediaComputeJob {
                    create(input: $input) {
                        record {
                            jobIdHex
                            publishedDataRoomId
                            computeNodeName
                            jobType
                            cacheKey
                            createdAt
                        }
                    }
                }
            }
            """,
            {"input": input},
        )
        return data["mediaComputeJob"]["create"]["record"]

    def _get_media_compute_job(
        self,
        input: MediaComputeJobFilterInput,
    ) -> MediaComputeJob:
        """
        Get a compute job for the Media DCR.
        """
        data = self._graphql.post(
            """
            query GetMediaComputeJob($input: MediaComputeJobFilterInput!) {
                mediaComputeJob (input: $input) {
                    jobIdHex
                    publishedDataRoomId
                    computeNodeName
                    jobType
                    cacheKey
                    createdAt
                }
            }
            """,
            {"input": input},
        )
        return data["mediaComputeJob"]

    def _provision_data_lab(
        self,
        data_room_id: str,
        data_lab_id: str,
    ) -> DataLabDefinition:
        """
        Provision a DataLab to a DCR.

        **Parameters**:
        - `data_room_id`: ID of the DCR to provision to.
        - `data_lab_id`: ID of the DataLab to be provisioned.
        """
        data = self._graphql.post(
            """
            mutation ProvisionDataLab($input: ProvisionDataLabInput!) {
                dataLab {
                    provisionDataLab(input: $input) {
                        publishedDataLab {
                            id
                            name
                            datasets {
                                name
                                dataset {
                                    id
                                    manifestHash
                                    name
                                }
                            }
                            usersDataset {
                                id
                                manifestHash
                                name
                            }
                            segmentsDataset {
                                id
                                manifestHash
                                name
                            }
                            demographicsDataset {
                                id
                                manifestHash
                                name
                            }
                            embeddingsDataset {
                                id
                                manifestHash
                                name
                            }
                            statistics
                            requireDemographicsDataset
                            requireEmbeddingsDataset
                            isValidated
                            numEmbeddings
                            matchingIdFormat
                            matchingIdHashingAlgorithm
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                            highLevelRepresentationAsString
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "dataRoomId": data_room_id,
                    "dataLabId": data_lab_id,
                }
            },
        )
        return data["dataLab"]["provisionDataLab"]["publishedDataLab"]

    def _deprovision_data_lab(self, data_room_id: str) -> DataLabDefinition:
        """
        Deprovision a DataLab from a DCR.

        **Parameters**:
        - `data_room_id`: ID of the DCR to deprovision from.
        """
        data = self._graphql.post(
            """
            mutation DeprovisionDataLab($input: String!) {
                dataLab {
                    deprovisionDataLab(lookalikeMediaDcrId: $input) {
                        publishedDataLab {
                            id
                            name
                            datasets {
                                name
                                dataset {
                                    id
                                    manifestHash
                                    name
                                }
                            }
                            usersDataset {
                                id
                                manifestHash
                                name
                            }
                            segmentsDataset {
                                id
                                manifestHash
                                name
                            }
                            demographicsDataset {
                                id
                                manifestHash
                                name
                            }
                            embeddingsDataset {
                                id
                                manifestHash
                                name
                            }
                            statistics
                            requireDemographicsDataset
                            requireEmbeddingsDataset
                            isValidated
                            numEmbeddings
                            matchingIdFormat
                            matchingIdHashingAlgorithm
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                            highLevelRepresentationAsString
                        }
                    }
                }
            }
            """,
            {
                "input": data_room_id,
            },
        )
        return data["dataLab"]["deprovisionDataLab"]["publishedDataLab"]

    def retrieve_analytics_dcr(
        self,
        dcr_id,
        enclave_specs: Optional[List[EnclaveSpecification]] = None,
    ) -> AnalyticsDcr:
        """
        Retrieve an existing Analytics DCR.

        **Parameters**:
        - `dcr_id`: Data Clean Room ID.
        - `enclave_specs`: The enclave specifications that are considered
          to be trusted. If not specified, all enclave specifications known
          to this version of the SDK will be used.
        """
        return AnalyticsDcr._from_existing(
            dcr_id, client=self, enclave_specs=enclave_specs
        )

    def publish_analytics_dcr(
        self,
        dcr_definition: AnalyticsDcrDefinition,
        *,
        enclave_specs: Optional[Dict[str, EnclaveSpecification]] = None,
    ) -> AnalyticsDcr:
        """
        Publish an Analytics DCR.

        **Parameters**:
        - `dcr_definition`: Definition of the Analytics DCR.
        - `enclave_specs`: The enclave specifications that are considered
          to be trusted. If not specified, all enclave specifications known
          to this version of the SDK will be used.
        """
        hl = dcr_definition._get_high_level_representation()

        data_room = DataScienceDataRoom.model_validate(hl)
        compiled_data_room = compiler.compile_data_science_data_room(data_room)
        self.compile_context = compiled_data_room.compile_context

        low_level_data_room = ProtoDataRoom()
        parse_length_delimited(compiled_data_room.data_room, low_level_data_room)

        # Get a new session.
        # Determine which driver enclave spec (as given by the enclave_specs value)
        # to use. If this is not explicitly specified, try to check whether it was
        # already set on the builder that constructed the DCR definition.
        # If this is also not specified, simply use the latest specifications known to this SDK.
        specs = (
            enclave_specs
            or dcr_definition.enclave_specs
            or enclave_specifications.latest()
        )
        auth, _ = self.create_auth_using_decentriq_pki(specs)
        session = self.create_session(auth, specs)

        dcr_id = session.publish_data_room(
            low_level_data_room,
            kind=CreateDcrKind.DATASCIENCE,
            high_level_representation=compiled_data_room.datascience_data_room_encoded,
        )

        # Now that we've published the DCR the simplest way to construct
        # the DCR is using the `from_existing` method. This takes care
        # of correctly constructing all the node definitions.
        published_ds_dcr = AnalyticsDcr._from_existing(
            dcr_id=dcr_id, client=self, enclave_specs=list(specs.values())
        )

        data_room_description = self.get_data_room_description(dcr_id, specs)
        if not data_room_description:
            raise Exception(f"Failed to get data room description for DCR ID {dcr_id}")

        # Notify participants of DCR creation.
        data = self._graphql.post(
            """
            mutation NotifyParticipants($input: InviteParticipantsInput!) {
                publishedDataRoom {
                    inviteParticipants(input: $input) {
                        id
                    }
                }
            }
            """,
            {
                "input": {
                    "publishedDataRoomEnclaveId": dcr_id,
                    "publishedDataRoomDriverAttestationHash": data_room_description[
                        "driverAttestationHash"
                    ],
                    "dataRoomDescription": dcr_definition._get_description(),
                },
            },
        )

        return published_ds_dcr

    def retrieve_ab_media_dcr(
        self,
        dcr_id,
        enclave_specs: Optional[List[EnclaveSpecification]] = None,
    ) -> AbMediaDcr:
        """
        Retrieve an existing Audience Builder DCR.

        **Parameters**:
        - `dcr_id`: Data Clean Room ID.
        - `enclave_specs`: The enclave specifications that are considered
          to be trusted. If not specified, all enclave specifications known
          to this version of the SDK will be used.
        """
        return AbMediaDcr._from_existing(
            dcr_id, client=self, enclave_specs=enclave_specs
        )

    def publish_ab_media_dcr(
        self,
        dcr_definition: AbMediaDcrDefinition,
        *,
        enclave_specs: Optional[Dict[str, EnclaveSpecification]] = None,
    ) -> AbMediaDcr:
        """
        Publish an Audience Builder DCR.

        **Parameters**:
        - `dcr_definition`: Definition of the Audience Builder DCR.
        - `enclave_specs`: The enclave specifications that are considered
          to be trusted. If not specified, all enclave specifications known
          to this version of the SDK will be used.
        """
        dcr = AbMediaDcrSchema.model_validate_json(
            json.dumps(dcr_definition._high_level)
        )
        # Ensure we create the latest known version of the DCR.
        dcr_latest = ab_media_compiler.upgrade_ab_media_dcr_to_latest(dcr)

        compiled_serialized = ab_media_compiler.compile_ab_media_dcr(dcr_latest)
        low_level_dcr = ProtoDataRoom()
        parse_length_delimited(compiled_serialized, low_level_dcr)

        # Get a new session.
        # Determine which driver enclave spec (as given by the enclave_specs value)
        # to use. If this is not explicitly specified, try to check whether it was
        # already set on the builder that constructed the DCR definition.
        # If this is also not specified, simply use the latest specifications known to this SDK.
        specs = (
            enclave_specs
            or dcr_definition._enclave_specs
            or enclave_specifications.latest()
        )
        auth, _ = self.create_auth_using_decentriq_pki(specs)
        session = self.create_session(auth, specs)

        dcr_id = session.publish_data_room(
            low_level_dcr,
            kind=CreateDcrKind.AB_MEDIA,
            high_level_representation=dcr_latest.model_dump_json(
                by_alias=True
            ).encode(),
        )
        existing_dcr = AbMediaDcr._from_existing(
            dcr_id=dcr_id,
            client=self,
            enclave_specs=list(specs.values()),
        )
        return existing_dcr

    def _provision_data_lab_to_midcr(
        self,
        data_room_id: str,
        data_lab_id: str,
    ) -> DataLabDefinition:
        """
        Provision a DataLab to a Media DCR.

        **Parameters**:
        - `data_room_id`: ID of the DCR to provision to.
        - `data_lab_id`: ID of the DataLab to be provisioned.
        """
        data = self._graphql.post(
            """
            mutation ProvisionDataLabToMediaInsightsDcr($input: ProvisionDataLabInput!) {
                dataLab {
                    provisionDataLabToMediaInsightsDcr(input: $input) {
                        publishedDataLab {
                            id
                            name
                            datasets {
                                name
                                dataset {
                                    id
                                    manifestHash
                                    name
                                }
                            }
                            usersDataset {
                                id
                                manifestHash
                                name
                            }
                            segmentsDataset {
                                id
                                manifestHash
                                name
                            }
                            demographicsDataset {
                                id
                                manifestHash
                                name
                            }
                            embeddingsDataset {
                                id
                                manifestHash
                                name
                            }
                            statistics
                            requireDemographicsDataset
                            requireEmbeddingsDataset
                            isValidated
                            numEmbeddings
                            matchingIdFormat
                            matchingIdHashingAlgorithm
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                            highLevelRepresentationAsString
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "dataRoomId": data_room_id,
                    "dataLabId": data_lab_id,
                }
            },
        )
        return data["dataLab"]["provisionDataLabToMediaInsightsDcr"]["publishedDataLab"]

    def _deprovision_data_lab_from_midcr(self, data_room_id: str) -> DataLabDefinition:
        """
        Deprovision a DataLab from a Media DCR.

        **Parameters**:
        - `data_room_id`: ID of the DCR to deprovision from.
        """
        data = self._graphql.post(
            """
            mutation DeprovisionDataLabFromMediaInsightsDcr($input: String!) {
                dataLab {
                    deprovisionDataLabFromMediaInsightsDcr(mediaInsightsDcrId: $input) {
                        publishedDataLab {
                            id
                            name
                            datasets {
                                name
                                dataset {
                                    id
                                    manifestHash
                                    name
                                }
                            }
                            usersDataset {
                                id
                                manifestHash
                                name
                            }
                            segmentsDataset {
                                id
                                manifestHash
                                name
                            }
                            demographicsDataset {
                                id
                                manifestHash
                                name
                            }
                            embeddingsDataset {
                                id
                                manifestHash
                                name
                            }
                            statistics
                            requireDemographicsDataset
                            requireEmbeddingsDataset
                            isValidated
                            numEmbeddings
                            matchingIdFormat
                            matchingIdHashingAlgorithm
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                            highLevelRepresentationAsString
                        }
                    }
                }
            }
            """,
            {
                "input": data_room_id,
            },
        )
        return data["dataLab"]["deprovisionDataLabFromMediaInsightsDcr"][
            "publishedDataLab"
        ]

    def _provision_data_lab_to_ab_dcr(
        self,
        data_room_id: str,
        data_lab_id: str,
    ) -> DataLabDefinition:
        """
        Provision a DataLab to an Audience Builder DCR.

        **Parameters**:
        - `data_room_id`: ID of the DCR to provision to.
        - `data_lab_id`: ID of the DataLab to be provisioned.
        """
        data = self._graphql.post(
            """
            mutation ProvisionDataLabToMediaInsightsDcr($input: ProvisionDataLabInput!) {
                dataLab {
                    provisionDataLabToMediaInsightsDcr(input: $input) {
                        publishedDataLab {
                            id
                            name
                            datasets {
                                name
                                dataset {
                                    id
                                    manifestHash
                                    name
                                }
                            }
                            usersDataset {
                                id
                                manifestHash
                                name
                            }
                            segmentsDataset {
                                id
                                manifestHash
                                name
                            }
                            demographicsDataset {
                                id
                                manifestHash
                                name
                            }
                            embeddingsDataset {
                                id
                                manifestHash
                                name
                            }
                            statistics
                            requireDemographicsDataset
                            requireEmbeddingsDataset
                            isValidated
                            numEmbeddings
                            matchingIdFormat
                            matchingIdHashingAlgorithm
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                            highLevelRepresentationAsString
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "dataRoomId": data_room_id,
                    "dataLabId": data_lab_id,
                }
            },
        )
        return data["dataLab"]["provisionDataLabToMediaInsightsDcr"]["publishedDataLab"]

    def _deprovision_data_lab_from_ab_dcr(self, data_room_id: str) -> DataLabDefinition:
        """
        Deprovision a DataLab from an Audience Builder DCR.

        **Parameters**:
        - `data_room_id`: ID of the DCR to deprovision from.
        """
        data = self._graphql.post(
            """
            mutation DeprovisionDataLabFromMediaInsightsDcr($input: String!) {
                dataLab {
                    deprovisionDataLabFromMediaInsightsDcr(mediaInsightsDcrId: $input) {
                        publishedDataLab {
                            id
                            name
                            datasets {
                                name
                                dataset {
                                    id
                                    manifestHash
                                    name
                                }
                            }
                            usersDataset {
                                id
                                manifestHash
                                name
                            }
                            segmentsDataset {
                                id
                                manifestHash
                                name
                            }
                            demographicsDataset {
                                id
                                manifestHash
                                name
                            }
                            embeddingsDataset {
                                id
                                manifestHash
                                name
                            }
                            statistics
                            requireDemographicsDataset
                            requireEmbeddingsDataset
                            isValidated
                            numEmbeddings
                            matchingIdFormat
                            matchingIdHashingAlgorithm
                            validationComputeJobId
                            statisticsComputeJobId
                            jobsDriverAttestationHash
                            highLevelRepresentationAsString
                        }
                    }
                }
            }
            """,
            {
                "input": data_room_id,
            },
        )
        return data["dataLab"]["deprovisionDataLabFromMediaInsightsDcr"][
            "publishedDataLab"
        ]

    def _get_my_organization_users(self) -> List[OrganizationUser]:
        data = self._graphql.post(
            """
            query MyOrganizationUsers() {
                myself {
                    organization {
                        users {
                            nodes {
                                id
                                email
                            }
                        }
                    }
                }
            }
            """
        )
        return data["myself"]["organization"]["users"]["nodes"]



def create_client(
    user_email: str,
    api_token: str,
    *,
    client_id: str = DECENTRIQ_CLIENT_ID,
    api_host: str = DECENTRIQ_HOST,
    api_port: int = DECENTRIQ_PORT,
    api_use_tls: bool = DECENTRIQ_USE_TLS,
    request_timeout: Optional[int] = None,
    unsafe_disable_known_root_ca_check: bool = _DECENTRIQ_UNSAFE_DISABLE_KNOWN_ROOT_CA_CHECK,
) -> Client:
    """
    The primary way to create a `Client` object.

    **Parameters**:
    - `api_token`: An API token with which to authenticate oneself.
        The API token can be obtained in the user
        account settings in the Decentriq UI.
    - `user_email`: The email address of the user that generated the given API token.
    """

    enclave_api_token = api_token
    enclave_api_token_raw = urlsafe_b64decode(enclave_api_token)
    platform_api_token_raw = hashlib.sha256(enclave_api_token_raw).digest()
    platform_api_token = urlsafe_b64encode(platform_api_token_raw).decode("ascii")

    api = Api(
        platform_api_token,
        client_id,
        api_host,
        api_port,
        api_prefix="",
        use_tls=api_use_tls,
        timeout=request_timeout,
    )

    graphql = GqlClient(api, path=Endpoints.GRAPHQL)

    return Client(
        user_email,
        enclave_api_token,
        api,
        graphql,
        request_timeout=request_timeout,
        unsafe_disable_known_root_ca_check=unsafe_disable_known_root_ca_check,
    )


class BoundedExecutor:
    def __init__(self, bound, max_workers):
        self.executor = futures.ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = BoundedSemaphore(bound + max_workers)

    def submit(self, fn, *args, **kwargs):
        def done_callback(f):
            error = f.exception()
            if error:
                logger.error(f"Error in future: {error}")
            self.semaphore.release()

        self.semaphore.acquire()
        try:
            future = self.executor.submit(fn, *args, **kwargs)
        except:
            self.semaphore.release()
            raise
        else:
            future.add_done_callback(done_callback)
            return future

    def shutdown(self, wait=True):
        self.executor.shutdown(wait)

"""
Converts a generator of bytes into a read-only input stream. This takes ownership of the generator and will close it when the stream is closed.
"""
class GeneratorStream(io.RawIOBase):
    def __init__(self, generator, buffer_size=io.DEFAULT_BUFFER_SIZE):
        self.leftover = None
        self.has_next = True
        self.generator = generator
        self.buffer_size = buffer_size

    def readable(self):
        return True

    def readinto(self, output_buffer):
        if not self.has_next:
            return 0
        try:
            chunk = self.leftover or next(self.generator)
            read_size = min(len(output_buffer), len(chunk))
            output_buffer[:read_size] = chunk[:read_size]
            self.leftover = chunk[read_size:] if read_size < len(chunk) else None
            return read_size
        except StopIteration:
            self.has_next = False
            return 0

    def read(self, size=-1):
        if size == 0:
            return b""
        elif size < 0:
            buffers = []
            while self.has_next:
                buffer = bytearray(self.buffer_size)
                read_size = self.readinto(buffer)
                buffer = buffer[:read_size]
                buffers.append(buffer)
            return b"".join(buffers)
        else:
            buffer = bytearray(size)
            num_read = self.readinto(buffer)
            return bytes(buffer[:num_read])

    def close(self):
        self.generator.close()
