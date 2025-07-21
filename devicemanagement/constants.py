from enum import Enum
from pymobiledevice3.lockdown import LockdownClient

class Version:
	def __init__(self, major_or_ver, minor: int = 0, patch: int = 0):
		# Accept either a single "X.Y.Z" string or three ints
		if isinstance(major_or_ver, str):
			parts = major_or_ver.split(".")
			self.major = int(parts[0])
			self.minor = int(parts[1]) if len(parts) > 1 else 0
			self.patch = int(parts[2]) if len(parts) > 2 else 0
		else:
			self.major = major_or_ver
			self.minor = minor
			self.patch = patch

	def compare_to(self, other: "Version") -> int:
		if self.major != other.major:
			return 1 if self.major > other.major else -1
		if self.minor != other.minor:
			return 1 if self.minor > other.minor else -1
		if self.patch != other.patch:
			return 1 if self.patch > other.patch else -1
		return 0

	def __gt__(self, other):  return self.compare_to(other) == 1
	def __ge__(self, other):  return self.compare_to(other) >= 0
	def __lt__(self, other):  return self.compare_to(other) == -1
	def __le__(self, other):  return self.compare_to(other) <= 0
	def __eq__(self, other):  return self.compare_to(other) == 0

class Device:
	# bump this to the first major version you want unsupported
	_MAX_SUPPORTED_VERSION = Version("26.1")
	# you still want to block that weird 17.7.1–17.9.x range?
	_UNSUPPORTED_RANGE_START = Version("17.7.1")
	_UNSUPPORTED_RANGE_END   = Version("18.0")
	# legacy builds that remain supported regardless of version
	_LEGACY_BUILD_EXCEPTIONS = {
		"22B5007p", "22B5023e", "22B5034e", "22B5045g"
	}

	def __init__(
		self,
		uuid: int,
		name: str,
		version: str,
		build: str,
		model: str,
		locale: str,
		ld: LockdownClient
	):
		self.uuid    = uuid
		self.name    = name
		self.version = version
		self.build   = build
		self.model   = model
		self.locale  = locale
		self.ld      = ld

	def has_exploit(self) -> bool:
		parsed = Version(self.version)

		# block that one oddball range still
		if parsed >= self._UNSUPPORTED_RANGE_START and parsed < self._UNSUPPORTED_RANGE_END:
			return False

		# if it's below the max supported OR a legacy build exception, we support it
		if parsed < self._MAX_SUPPORTED_VERSION or self.build in self._LEGACY_BUILD_EXCEPTIONS:
			return True

		# otherwise, no exploit support
		return False

	def supported(self) -> bool:
		return self.has_exploit()

class Tweak(Enum):
	SkipSetup = 'Setup Options'
	cloud_config = "SkipSetup/ConfigProfileDomain/Library/ConfigurationProfiles/CloudConfigurationDetails.plist"
