from storages.backends.gcloud import GoogleCloudStorage

class SolaceMediaStorage(GoogleCloudStorage):
    location = "media"


class SolaceStaticStorage(GoogleCloudStorage):
    location = "static"
