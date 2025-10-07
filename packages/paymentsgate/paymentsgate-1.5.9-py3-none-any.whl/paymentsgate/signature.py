import enum
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


class SignatureCheckMode(enum.StrEnum):
    none = enum.auto()
    decrypt_only = enum.auto()
    full = enum.auto()


def flatten_stringify(d: dict, count: int = 1) -> dict:
    def inner(d, count):
        res = {}
        for k, v in d.items():
            if type(v) is list:
                count += 1
            elif type(v) is dict:
                new_d, count = inner(v, count)
                res = res | new_d
            else:
                res[(k.lower(), count)] = str(v).lower() if type(v) is bool else str(v)
                count += 1
        return res, count

    (d, _) = inner(d, count)
    return d


class SignatureHelper:
    def __init__(
        self,
        private_key_data: str,
        password: str = None,
        mode: SignatureCheckMode = SignatureCheckMode.full,
    ) -> None:
        decoded_key = base64.decodebytes(private_key_data.encode("utf-8"))
        self.private_key = serialization.load_pem_private_key(
            decoded_key, password=password
        )
        self.mode = mode

    def check(self, api_signature: str, json_value: dict) -> bool:
        try:
            self._check_impl(api_signature, json_value)
        except ValueError:
            return False
        except:
            raise
        return True

    def sign(self, json_value: dict) -> str:
        digest = self.encode(json_value)
        return base64.encodebytes(
            self.private_key.sign(
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        ).decode("utf-8")

    def encode(self, json_value: dict) -> bytes:
        d = flatten_stringify(json_value)
        val = "".join(d[k] for k in sorted(d.keys()))
        return hashlib.sha256(val.encode("utf-8")).hexdigest().encode("utf-8")

    def check_raise(self, api_signatre: str, json_value: dict) -> None:
        self._check_impl(api_signatre, json_value)

    def _check_impl(self, api_signature: str, json_value: dict) -> None:
        if self.mode == SignatureCheckMode.none:
            return
        if len(api_signature) < 256:
            raise ValueError(
                "wrong api_signature length, check Webhook version.in project settings, should be 3!"
            )
        decoded_signature = base64.decodebytes(api_signature.encode("utf-8"))
        alg = hashes.SHA256()
        digest = self.private_key.decrypt(
            decoded_signature,
            padding.OAEP(mgf=padding.MGF1(algorithm=alg), algorithm=alg, label=None),
        )
        if self.mode == SignatureCheckMode.decrypt_only:
            return
        if self.encode(json_value) != digest:
            raise ValueError("Error while checking signature")
