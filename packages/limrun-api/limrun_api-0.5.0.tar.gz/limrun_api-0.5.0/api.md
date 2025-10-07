# AndroidInstances

Types:

```python
from limrun_api.types import AndroidInstance, AndroidInstanceListResponse
```

Methods:

- <code title="post /v1/android_instances">client.android_instances.<a href="./src/limrun_api/resources/android_instances.py">create</a>(\*\*<a href="src/limrun_api/types/android_instance_create_params.py">params</a>) -> <a href="./src/limrun_api/types/android_instance.py">AndroidInstance</a></code>
- <code title="get /v1/android_instances">client.android_instances.<a href="./src/limrun_api/resources/android_instances.py">list</a>(\*\*<a href="src/limrun_api/types/android_instance_list_params.py">params</a>) -> <a href="./src/limrun_api/types/android_instance_list_response.py">AndroidInstanceListResponse</a></code>
- <code title="delete /v1/android_instances/{id}">client.android_instances.<a href="./src/limrun_api/resources/android_instances.py">delete</a>(id) -> None</code>
- <code title="get /v1/android_instances/{id}">client.android_instances.<a href="./src/limrun_api/resources/android_instances.py">get</a>(id) -> <a href="./src/limrun_api/types/android_instance.py">AndroidInstance</a></code>

# Assets

Types:

```python
from limrun_api.types import Asset, AssetListResponse, AssetGetOrCreateResponse
```

Methods:

- <code title="get /v1/assets">client.assets.<a href="./src/limrun_api/resources/assets.py">list</a>(\*\*<a href="src/limrun_api/types/asset_list_params.py">params</a>) -> <a href="./src/limrun_api/types/asset_list_response.py">AssetListResponse</a></code>
- <code title="get /v1/assets/{assetId}">client.assets.<a href="./src/limrun_api/resources/assets.py">get</a>(asset_id, \*\*<a href="src/limrun_api/types/asset_get_params.py">params</a>) -> <a href="./src/limrun_api/types/asset.py">Asset</a></code>
- <code title="put /v1/assets">client.assets.<a href="./src/limrun_api/resources/assets.py">get_or_create</a>(\*\*<a href="src/limrun_api/types/asset_get_or_create_params.py">params</a>) -> <a href="./src/limrun_api/types/asset_get_or_create_response.py">AssetGetOrCreateResponse</a></code>

# IosInstances

Types:

```python
from limrun_api.types import IosInstance, IosInstanceListResponse
```

Methods:

- <code title="post /v1/ios_instances">client.ios_instances.<a href="./src/limrun_api/resources/ios_instances.py">create</a>(\*\*<a href="src/limrun_api/types/ios_instance_create_params.py">params</a>) -> <a href="./src/limrun_api/types/ios_instance.py">IosInstance</a></code>
- <code title="get /v1/ios_instances">client.ios_instances.<a href="./src/limrun_api/resources/ios_instances.py">list</a>(\*\*<a href="src/limrun_api/types/ios_instance_list_params.py">params</a>) -> <a href="./src/limrun_api/types/ios_instance_list_response.py">IosInstanceListResponse</a></code>
- <code title="delete /v1/ios_instances/{id}">client.ios_instances.<a href="./src/limrun_api/resources/ios_instances.py">delete</a>(id) -> None</code>
- <code title="get /v1/ios_instances/{id}">client.ios_instances.<a href="./src/limrun_api/resources/ios_instances.py">get</a>(id) -> <a href="./src/limrun_api/types/ios_instance.py">IosInstance</a></code>
