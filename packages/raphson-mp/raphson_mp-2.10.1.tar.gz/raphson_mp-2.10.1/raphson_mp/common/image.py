from enum import Enum


class ImageFormat(Enum):
    WEBP = "webp"
    JPEG = "jpeg"

    @property
    def content_type(self):
        if self is ImageFormat.WEBP:
            return "image/webp"
        elif self is ImageFormat.JPEG:
            return "image/jpeg"
        else:
            raise ValueError(self)


class ImageQuality(Enum):
    HIGH = "high"
    LOW = "low"

    @property
    def resolution(self) -> int:
        if self is ImageQuality.HIGH:
            return 1200  # 1200x1200 matches highest quality MusicBrainz cover
        elif self is ImageQuality.LOW:
            return 512
        else:
            raise ValueError()
