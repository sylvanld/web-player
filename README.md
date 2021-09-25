# Video Player

*This is a minimalist service that provide a **web interface** to **play MKV videos** from an **FTP server***

## Configuration

When starting the container, you must provide the following environment variables
* **USERNAME**: Name used to authenticate
* **PASSWORD_HASH**: Hash of the password used to authenticate ([how do I get my password's hash ?](#hash-password))
* **VIDEO_SERVER_URL**: Path to the folder where [videos manifest](#videos-manifest) is stored

### Hash password

Here is an example of how you can hash your password using python:

```python
import hashlib

my_password = "toto"
password_hash = hashlib.sha256(my_password.encode("utf-8")).hexdigest()
print(password_hash)
```

### Videos manifest

It is a simple JSON file that map a name to a file.

This file must be included along with the videos at the root of your FTP server.

```json
{
    "videos": [
        {
            "title": "My video",
            "filename": "my_video.mkv"
        }
    ]
}
```
