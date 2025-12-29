"""
Schema 模块
"""
from app.schemas.common import (
    SuccessResponse,
    ErrorResponse,
    PaginatedData,
    PaginationParams,
)
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    PasswordChangeRequest,
    UserBase,
    UserResponse,
    TokenData,
    LoginResponse,
)
from app.schemas.teacher import (
    TeacherCreateRequest,
    TeacherUpdateRequest,
    TeacherResponse,
    TeacherListResponse,
)
from app.schemas.student import (
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse,
    StudentListResponse,
    StudentWithEnrollment,
)
from app.schemas.course import (
    CourseCreateRequest,
    CourseUpdateRequest,
    AddStudentRequest,
    BatchAddStudentsRequest,
    CourseResponse,
    CourseListResponse,
    CourseWithTeacher,
    StudentCoursesResponse,
    TeacherCoursesResponse,
    BatchAddResult,
)
from app.schemas.homework import (
    FileAttachment,
    GradingCriteria,
    HomeworkCreateRequest,
    HomeworkUpdateRequest,
    HomeworkResponse,
    HomeworkListResponse,
    StudentHomework,
    StudentHomeworksResponse,
)
from app.schemas.submission import (
    SubmissionCreateRequest,
    SubmissionUpdateRequest,
    GradeRequest,
    SubmissionResponse,
    SubmissionWithStudent,
    SubmissionListResponse,
    GradeResponse,
    StudentSubmission,
    StudentSubmissionsResponse,
)
from app.schemas.resource import (
    FolderCreateRequest,
    FolderUpdateRequest,
    FileUploadRequest,
    FileUpdateRequest,
    FileResponse,
    FileWithoutContent,
    FolderResponse,
    FolderWithFiles,
    FolderListResponse,
    FileListResponse,
    CourseResourcesResponse,
)
from app.schemas.ai import (
    PPTGenerateRequest,
    PPTGenerateResponse,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentEditRequest,
    ContentEditResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
)

__all__ = [
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedData",
    "PaginationParams",
    # Auth
    "SignupRequest",
    "LoginRequest",
    "PasswordChangeRequest",
    "UserBase",
    "UserResponse",
    "TokenData",
    "LoginResponse",
    # Teacher
    "TeacherCreateRequest",
    "TeacherUpdateRequest",
    "TeacherResponse",
    "TeacherListResponse",
    # Student
    "StudentCreateRequest",
    "StudentUpdateRequest",
    "StudentResponse",
    "StudentListResponse",
    "StudentWithEnrollment",
    # Course
    "CourseCreateRequest",
    "CourseUpdateRequest",
    "AddStudentRequest",
    "BatchAddStudentsRequest",
    "CourseResponse",
    "CourseListResponse",
    "CourseWithTeacher",
    "StudentCoursesResponse",
    "TeacherCoursesResponse",
    "BatchAddResult",
    # Homework
    "FileAttachment",
    "GradingCriteria",
    "HomeworkCreateRequest",
    "HomeworkUpdateRequest",
    "HomeworkResponse",
    "HomeworkListResponse",
    "StudentHomework",
    "StudentHomeworksResponse",
    # Submission
    "SubmissionCreateRequest",
    "SubmissionUpdateRequest",
    "GradeRequest",
    "SubmissionResponse",
    "SubmissionWithStudent",
    "SubmissionListResponse",
    "GradeResponse",
    "StudentSubmission",
    "StudentSubmissionsResponse",
    # Resource
    "FolderCreateRequest",
    "FolderUpdateRequest",
    "FileUploadRequest",
    "FileUpdateRequest",
    "FileResponse",
    "FileWithoutContent",
    "FolderResponse",
    "FolderWithFiles",
    "FolderListResponse",
    "FileListResponse",
    "CourseResourcesResponse",
    # AI
    "PPTGenerateRequest",
    "PPTGenerateResponse",
    "ContentGenerateRequest",
    "ContentGenerateResponse",
    "ContentEditRequest",
    "ContentEditResponse",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
]
