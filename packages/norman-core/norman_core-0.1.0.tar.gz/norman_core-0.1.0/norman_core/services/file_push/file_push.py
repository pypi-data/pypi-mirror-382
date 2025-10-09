from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_asset_pairing_request import SocketAssetPairingRequest
from norman_objects.services.file_push.pairing.socket_input_pairing_request import SocketInputPairingRequest
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.clients.http_client import HttpClient


class FilePush:
    @staticmethod
    async def allocate_socket_for_asset(http_client: HttpClient, token: Sensitive[str], pairing_request: SocketAssetPairingRequest):
        response = await http_client.post("file-push/socket/pair/asset", token, json=pairing_request.model_dump(mode="json"))
        return SocketPairingResponse.model_validate(response)

    @staticmethod
    async def allocate_socket_for_input(http_client: HttpClient, token: Sensitive[str], pairing_request: SocketInputPairingRequest):
        response = await http_client.post("file-push/socket/pair/input", token, json=pairing_request.model_dump(mode="json"))
        return SocketPairingResponse.model_validate(response)

    @staticmethod
    async def complete_file_transfer(http_client: HttpClient, token: Sensitive[str], checksum_request: ChecksumRequest):
        await http_client.post("file-push/socket/complete", token, json=checksum_request.model_dump(mode="json"))
