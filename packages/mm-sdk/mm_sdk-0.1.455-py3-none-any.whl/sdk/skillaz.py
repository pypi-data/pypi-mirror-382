import json
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict, Any

from pydantic import BaseModel
from .client import SDKClient, SDKResponse, Empty


class FileType(str, Enum):
    TEST_RESULT = "testResultDataFile"
    DOCUMENTS = "documents"


class StatusType(str, Enum):
    ProfExtraordinary = "SentToExtraordinaryMO"
    LmkProfPeriodic = "SentForPeriodicMO"
    Passed = "MedicalExaminationPassedUnscheduled"

    LmkProfPreliminary = "SentForMedicalExaminationMassMobileMed"
    LmkProfPassed = "MedicalExaminationPassedMass"


class Paging(BaseModel):
    CurrentPage: int
    PageSize: int


class SkillazAPIError(BaseModel):
    Type: Optional[str] = None
    Title: Optional[str] = None
    Status: Optional[int] = None
    Detail: Optional[str] = None
    Instance: Optional[str] = None
    Extensions: Optional[Dict[str, Any]] = None


class CandidateRequest(BaseModel):
    Statuses: List[str]
    UpdatedSince: datetime
    UpdatedTo: datetime
    Paging: Optional["Paging"] = None


class CandidateStatus(BaseModel):
    Id: str
    FunnelId: Optional[str] = None
    Name: Optional[str] = None


class CandidateShort(BaseModel):
    Id: str
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    ContactPhoneNumber: Optional[str] = None
    ContactEmail: Optional[str] = None
    CurrentStatus: CandidateStatus


class CandidateResponse(BaseModel):
    Items: Optional[List[CandidateShort]] = None
    NextPage: Optional[int]
    TotalPages: int = 0
    TotalItems: int = 0


class StatusChangeRequest(BaseModel):
    NewStatus: str
    Comment: Optional[str] = None


class UploadFileRequest(BaseModel):
    file_type: FileType
    filename: str
    file_bytes: bytes


class UploadFileResult(BaseModel):
    IsOk: bool
    FileId: Optional[str] = None
    FileName: Optional[str] = None
    ErrorMessage: Optional[str] = None


class UploadFileResponse(BaseModel):
    CandidateId: str
    Result: UploadFileResult


class SkillazClient:
    def __init__(self, client: SDKClient, token: str) -> None:
        self._client = client
        self._url = "https://api.skillaz.ru"
        self._token = token

    def get_candidates(
        self, query: CandidateRequest, timeout=3
    ) -> SDKResponse[Union[CandidateResponse, SkillazAPIError]]:
        return self._client.post(
            self._url + "/open-api/objects/candidates/filtered",
            CandidateResponse,
            data=json.dumps(query.dict()),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def change_candidate_status(
        self, candidate_id: str, query: StatusChangeRequest, timeout=3
    ) -> SDKResponse[Union[Empty, SkillazAPIError]]:
        return self._client.post(
            f"{self._url}/open-api/objects/candidates/{candidate_id}/forced/workflow",
            Empty,
            data=json.dumps(query.dict()),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def upload_candidate_file(
        self, candidate_id: str, query: UploadFileRequest, timeout=3
    ) -> SDKResponse[UploadFileResponse]:
        return self._client.post(
            f"{self._url}/open-api/objects/candidates/{candidate_id}/file",
            UploadFileResponse,
            files={
                "file": (query.filename, query.file_bytes, "application/pdf")
            },
            params={"fileType": query.file_type.value},
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def upload_multiple_files(
        self, candidate_id: str, query: List[UploadFileRequest], timeout=3
    ) -> SDKResponse[UploadFileResponse]:
        return self._client.post(
            f"{self._url}/open-api/objects/candidates/{candidate_id}/files",
            UploadFileResponse,
            files=[
                ("files", (q.filename, q.file_bytes, "application/pdf"))
                for q in query
            ],
            params={"fileType": query[0].file_type.value},  # предполагаем одинаковый тип
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )
