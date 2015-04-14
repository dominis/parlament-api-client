# parlament-api-client
A very simple python client for the Hungarian Parliament's api

You can obtain an access token at: http://www.parlament.hu/w-api-tajekoztato

## Getting started
pip -r install requirements.txt

## Usage
### Simple example
```python
from papi import PAPI

c = PAPI(token='YOUR-TOKEN')

kepviselo = c.kepviselo(p_azon='z004')
print kepviselo['nev']

for item in kepviselo['kepvcsop-tagsagok']['tagsag']:
     print '%s -> %s' % (item['@ciklus'], item['@kepvcsop'])
```

### Debug mode
```python
from papi import PAPI

c = PAPI(token='YOUR-TOKEN', debug=True)

kepviselo = c.kepviselo(p_azon='z004')
```

### Redis cache
```bash
sudo pip install redis
```

```python
import papi

c = papi.PAPI(token='YOUR-TOKEN', debug=True, cache=papi.RedisCache())

for i in range(0,100):
    c.kepviselo(p_azon='z004')
```


