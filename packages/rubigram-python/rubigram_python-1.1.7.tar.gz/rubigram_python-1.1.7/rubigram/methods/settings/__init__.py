
from .setup_two_step_verification import SetupTwoStepVerification
from .get_two_passcode_status import GetTwoPasscodeStatus
from .get_privacy_setting import GetPrivacySetting
from .get_blocked_users import GetBlockedUsers
from .terminate_session import TerminateSession
from .get_my_sessions import GetMySessions
from .get_suggested_folders import GetSuggestedFolders
from .set_setting import SetSetting
from .update_profile import UpdateProfile
from .update_username import UpdateUsername
from .set_birthday import SetBirthday
from .terminate_other_session import TerminateOtherSession
from .request_delete_account import RequestDeleteAccount


class Settings(
    TerminateOtherSession,
    SetupTwoStepVerification,
    GetTwoPasscodeStatus,
    GetPrivacySetting,
    GetBlockedUsers,
    TerminateSession,
    GetMySessions,
    GetSuggestedFolders,
    SetSetting,
    UpdateProfile,
    UpdateUsername,
    SetBirthday,
    RequestDeleteAccount
):
    pass
