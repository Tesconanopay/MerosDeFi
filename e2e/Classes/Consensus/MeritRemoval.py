from typing import Dict, Union, Any

from e2e.Libs.BLS import Signature

from e2e.Classes.Consensus.Element import Element, SignedElement
from e2e.Classes.Consensus.Verification import Verification, SignedVerification
from e2e.Classes.Consensus.VerificationPacket import MeritRemovalVerificationPacket, SignedMeritRemovalVerificationPacket
from e2e.Classes.Consensus.SendDifficulty import SendDifficulty, SignedSendDifficulty
from e2e.Classes.Consensus.DataDifficulty import DataDifficulty, SignedDataDifficulty

MeritRemovalElement: Any = Union[
  SignedVerification,
  SignedMeritRemovalVerificationPacket,
  SignedSendDifficulty,
  SignedDataDifficulty
]

MERIT_REMOVAL_PREFIX: bytes = b'\5'

class MeritRemoval(
  Element
):
  def __init__(
    self,
    e1: Element,
    e2: Element,
    partial: bool,
    holder: int = -1
  ) -> None:
    self.prefix: bytes = MERIT_REMOVAL_PREFIX
    self.e1: Element = e1
    self.e2: Element = e2
    self.partial: bool = partial
    self.holder: int = holder
    if self.holder == -1:
      self.holder = self.e1.holder

  def signatureSerialize(
    self
  ) -> bytes:
    raise Exception("MeritRemoval's signatureSerialize was called.")

  def serialize(
    self
  ) -> bytes:
    return (
      self.holder.to_bytes(2, "little") +
      (b'\1' if self.partial else b'\0') +
      self.e1.signatureSerialize() +
      self.e2.signatureSerialize()
    )

  def toJSON(
    self
  ) -> Dict[str, Any]:
    result: Dict[str, Any] = {
      "descendant": "MeritRemoval",
      "holder": self.holder,
      "partial": self.partial,
      "elements": [self.e1.toJSON(), self.e2.toJSON()]
    }
    if "holder" in result["elements"][0]:
      del result["elements"][0]["holder"]
    if "holder" in result["elements"][1]:
      del result["elements"][1]["holder"]

    return result

  @staticmethod
  def fromJSON(
    jsonArg: Dict[str, Any]
  ) -> Any:
    json: Dict[str, Any] = dict(jsonArg)
    json["elements"] = list(json["elements"])
    json["elements"][0] = dict(json["elements"][0])
    json["elements"][1] = dict(json["elements"][1])

    json["elements"][0]["holder"] = json["holder"]
    json["elements"][1]["holder"] = json["holder"]

    e1: Element = Verification(bytes(32), 0)
    if json["elements"][0]["descendant"] == "Verification":
      e1 = Verification.fromJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "VerificationPacket":
      e1 = MeritRemovalVerificationPacket.fromJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "SendDifficulty":
      e1 = SendDifficulty.fromJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "DataDifficulty":
      e1 = DataDifficulty.fromJSON(json["elements"][0])
    else:
      raise Exception("Unknown Element used to construct a MeritRemoval.")

    e2: Element = Verification(bytes(32), 0)
    if json["elements"][1]["descendant"] == "Verification":
      e2 = Verification.fromJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "VerificationPacket":
      e2 = MeritRemovalVerificationPacket.fromJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "SendDifficulty":
      e2 = SendDifficulty.fromJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "DataDifficulty":
      e2 = DataDifficulty.fromJSON(json["elements"][1])
    else:
      raise Exception("Unknown Element used to construct a MeritRemoval.")

    return MeritRemoval(e1, e2, json["partial"], json["holder"])

class PartialMeritRemoval(
  SignedElement,
  MeritRemoval
):
  def __init__(
    self,
    e1: Element,
    e2: MeritRemovalElement,
    holder: int = -1
  ) -> None:
    MeritRemoval.__init__(self, e1, e2, True, holder)
    self.se2: SignedElement = e2
    self.signature: Signature = e2.signature

  def signedSerialize(
    self
  ) -> bytes:
    return MeritRemoval.serialize(self) + self.signature.serialize()

  def toSignedJSON(
    self
  ) -> Dict[str, Any]:
    result: Dict[str, Any] = MeritRemoval.toJSON(self)
    result["elements"][1]["signature"] = self.se2.signature.serialize().hex().upper()
    result["signed"] = True
    result["signature"] = self.signature.serialize().hex().upper()
    return result

  @staticmethod
  def fromSignedJSON(
    jsonArg: Dict[str, Any]
  ) -> Any:
    json: Dict[str, Any] = dict(jsonArg)
    json["elements"] = list(json["elements"])
    json["elements"][0] = dict(json["elements"][0])
    json["elements"][1] = dict(json["elements"][1])

    json["elements"][0]["holder"] = json["holder"]
    json["elements"][1]["holder"] = json["holder"]

    e1: MeritRemovalElement = SignedVerification(bytes(32), 0)
    if json["elements"][0]["descendant"] == "Verification":
      e1 = Verification.fromJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "VerificationPacket":
      e1 = SignedMeritRemovalVerificationPacket.fromJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "SendDifficulty":
      e1 = SendDifficulty.fromJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "DataDifficulty":
      e1 = DataDifficulty.fromJSON(json["elements"][0])

    e2: MeritRemovalElement = SignedVerification(bytes(32), 0)
    if json["elements"][1]["descendant"] == "Verification":
      e2 = SignedVerification.fromSignedJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "VerificationPacket":
      e2 = SignedMeritRemovalVerificationPacket.fromSignedJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "SendDifficulty":
      e2 = SignedSendDifficulty.fromSignedJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "DataDifficulty":
      e2 = SignedDataDifficulty.fromSignedJSON(json["elements"][1])

    return PartialMeritRemoval(e1, e2, json["holder"])

class SignedMeritRemoval(
  PartialMeritRemoval
):
  def __init__(
    self,
    e1: MeritRemovalElement,
    e2: MeritRemovalElement,
    holder: int = -1
  ) -> None:
    PartialMeritRemoval.__init__(self, e1, e2, holder)
    self.partial = False
    self.se1: SignedElement = e1
    self.signature = Signature.aggregate([e1.signature, e2.signature])

  def signedSerialize(
    self
  ) -> bytes:
    return MeritRemoval.serialize(self) + self.signature.serialize()

  def toSignedJSON(
    self
  ) -> Dict[str, Any]:
    result: Dict[str, Any] = MeritRemoval.toJSON(self)
    result["elements"][0]["signature"] = self.se1.signature.serialize().hex().upper()
    result["elements"][1]["signature"] = self.se2.signature.serialize().hex().upper()
    result["signed"] = True
    result["signature"] = self.signature.serialize().hex().upper()
    return result

  @staticmethod
  def fromSignedJSON(
    jsonArg: Dict[str, Any]
  ) -> Any:
    json: Dict[str, Any] = dict(jsonArg)
    json["elements"] = list(json["elements"])
    json["elements"][0] = dict(json["elements"][0])
    json["elements"][1] = dict(json["elements"][1])
    json["elements"][0]["holder"] = json["holder"]
    json["elements"][1]["holder"] = json["holder"]

    e1: MeritRemovalElement = SignedVerification(bytes(32), 0)
    if json["elements"][0]["descendant"] == "Verification":
      e1 = SignedVerification.fromSignedJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "VerificationPacket":
      e1 = SignedMeritRemovalVerificationPacket.fromSignedJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "SendDifficulty":
      e1 = SignedSendDifficulty.fromSignedJSON(json["elements"][0])
    elif json["elements"][0]["descendant"] == "DataDifficulty":
      e1 = SignedDataDifficulty.fromSignedJSON(json["elements"][0])

    e2: MeritRemovalElement = SignedVerification(bytes(32), 0)
    if json["elements"][1]["descendant"] == "Verification":
      e2 = SignedVerification.fromSignedJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "VerificationPacket":
      e2 = SignedMeritRemovalVerificationPacket.fromSignedJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "SendDifficulty":
      e2 = SignedSendDifficulty.fromSignedJSON(json["elements"][1])
    elif json["elements"][1]["descendant"] == "DataDifficulty":
      e2 = SignedDataDifficulty.fromSignedJSON(json["elements"][1])

    return SignedMeritRemoval(e1, e2, json["holder"])
