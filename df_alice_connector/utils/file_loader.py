import os
import requests
from typing import Optional, Dict

from pydantic import BaseModel, Field

from .common import partialmethod


class StoredImage(BaseModel):
    id: str = ...
    size: int = ...
    createdAt: str = ...
    origUrl: Optional[str] = None


class StoredSound(BaseModel):
    id: str = ...
    skill_id: str = ...
    size: Optional[int] = None
    originalName: str = ...
    createdAt: str = ...
    isProcessed: bool = False
    error: Optional[str] = None


class FileLoader(object):
    """
    Class FileLoader should facilitate loading files to Yandex Dialogs http API.

    Parameters
    -----------

    oauth_token: str
        Yandex HTTP API token
    skill_id: str
        Alice skill identificator (issued on creation)
    fallback_img_id: Optional[str]
        ID of the image to show on upload failure.
    fallback_sound_id: Optional[str]
        ID of the sound to show on upload failure.

    """

    def __init__(
        self,
        oauth_token: str,
        skill_id: str,
        fallback_img_id: Optional[str] = None,
        fallback_sound_id: Optional[str] = None,
    ) -> None:

        self.oauth_token = oauth_token
        self.skill_id = skill_id
        self.fallback_img_id = fallback_img_id
        self.fallback_sound_id = fallback_sound_id
        self.sound_file_2_id = dict()
        self.image_file_2_id = dict()
        self.image_url_2_id = dict()

    def get_media_by_url(self, *, url: str, key: str, registry: str) -> Optional[str]:
        """
        Uploads the {key} file accessible by the URL to Yandex via the http API.
        Returns the ID of the file or `None` on upload failure.
        The result is cached in the {registry} attribute.
        Uploading the audio by link is not supported by Yandex yet.

        Parameters
        -----------

        url: str
            The target url (keyword-only argument).

        """
        if key == "sound":
            raise NotImplementedError("Getting sound by URL is not implemented in the original Yandex protocol.")

        reg: dict = getattr(self, registry)
        file_id: str = reg.get(url)
        if file_id:
            return file_id

        result: dict = requests.post(
            url=f"https://dialogs.yandex.net/api/v1/skills/{self.skill_id}/{key}s",
            headers={"Authorization": f"OAuth {self.oauth_token}"},
            json={"url": url},
        ).json()
        file_id = result.get(key, {}).get("id")

        reg[url] = file_id
        setattr(self, registry, reg)

        return file_id

    get_sound_by_url = partialmethod(get_media_by_url, key="sound", registry="sound_url_2_id")

    get_image_by_url = partialmethod(get_media_by_url, key="image", registry="image_url_2_id")

    def get_media_by_filename(self, *, filename: str, key: str, registry: str) -> Optional[str]:
        """
        Uploads the {key} file accessible by the provided path to Yandex via the http API.
        Returns the ID of the file or `None` on upload failure.
        The result is cached in the {registry} attribute.
        Uploading the audio by link is not supported by Yandex yet.

        Parameters
        -----------

        filename: str
            The target file (keyword-only argument).

        """
        if not os.path.isfile(filename):
            raise OSError(f"Missing file: {filename}")

        reg: dict = getattr(self, registry)
        file_id: str = reg.get(filename)
        if file_id:
            return file_id

        with open(filename, "rb") as file:
            result: dict = requests.post(
                url=f"https://dialogs.yandex.net/api/v1/skills/{self.skill_id}/{key}s",
                headers={"Authorization": f"OAuth {self.oauth_token}"},
                data=file,
            ).json()
            file_id = result.get(key, {}).get("id")

        reg[filename] = file_id
        setattr(self, registry, reg)

        return file_id

    get_sound_by_filename = partialmethod(get_media_by_filename, key="sound", registry="sound_file_2_id")

    get_image_by_filename = partialmethod(get_media_by_filename, key="image", registry="image_file_2_id")

    def del_media_by_id(self, file_id: str, key: str, registry: str) -> None:
        """
        Deletes the {key} file from Yandex servers and from the local cache.

        Parameters
        -----------

        file_id: str
            Target ID (keyword-only argument).

        """
        r = requests.delete(
            url=f"https://dialogs.yandex.net/api/v1/skills/{self.skill_id}/{key}s/{file_id}",
            headers={"Authorization": f"OAuth {self.oauth_token}"},
        )

        if not r.ok:
            return

        self.del_id_from_registry(file_id, registry)
        if key == "image":
            self.del_id_from_registry(file_id, "image_url_2_id")

    del_sound_by_id = partialmethod(del_media_by_id, key="sound", registry="sound_file_2_id")

    del_image_by_id = partialmethod(del_media_by_id, key="image", registry="image_file_2_id")

    def get_quota(self):
        """
        Get the cyrrent occupied amount of storage for images and sounds in bytes

        """
        r = requests.get(
            url="https://dialogs.yandex.net/api/v1/status", headers={"Authorization": f"OAuth {self.oauth_token}"}
        )
        return r.json()

    def del_id_from_registry(self, file_id: str, registry: str) -> None:
        reg = getattr(self, registry)
        for key in reg:
            if reg[key] == file_id:
                target_key = key
        del reg[target_key]
        setattr(self, registry, reg)


file_loader = FileLoader(os.getenv("OAUTH_TOKEN"), os.getenv("SKILL_ID"))
