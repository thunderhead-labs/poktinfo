# Introduction
[PoktInfo](https://beta.pokt.info) is a comprehensive data analytics tool designed specifically for users and node operators within the Pocket Network ecosystem. We leverage on-chain data and data exposed to us from the PNI gateway to leverage insights into network health, node performance and more to help users make more informed decisions and optimize their infrastructure. With [PoktInfo](https://beta.pokt.info), users can access a wide range of information, including rewards, errors, latency, and location data. PoktInfo uses highly efficent caching mechanisms to reduce load times. 

# Installation
1) Clone this repo as well as:
* Common - `https://github.com/thunderhead-labs/common-os.git`
* Chain Service - `https://github.com/thunderhead-labs/chain_service.git`
* Errors Service - `https://github.com/thunderhead-labs/errors_service.git`
2) Follow the instructions in the README.md files for each repo.

## Setup (Linux/Mac)

1) Setup postgres db with image 13.0-alpine or above
   1) Install Docker on your system if you haven't already done so.
   2) Create a new directory for your PostgreSQL data, for example, `~/pgdata`.
   3) Open a terminal or command prompt and run the following command to start a new PostgreSQL container:
      ```bash
      docker run --name my-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 -v ~/pgdata:/var/lib/postgresql/data postgres:13.0-alpine
      ```
2) Create the poktinfo schema with it's tables and indexes:
```python
import json
from common.db_utils import ConnFactory
from common.orm.schema.poktinfo import *

engine = ConnFactory.get_engine(json.load(open(f'{ConnFactory.creds_directory}poktinfo_creds.json')))
PoktInfoBase.metadata.create_all(engine)
```
3) Sync up data of `rewards info` and `nodes info` using historical mode, with script or from chain_service:
   1) Script (update base path in script): `./run_service_history.sh $service_name $start_height $end_height`
   2) Chain Service - `https://github.com/thunderhead-labs/chain_service/#readme`
4) Sync up data of `errors info` and `latency info` using historical mode, with script or from errors_service:
   1) Script (update base path in script): `./run_service_history.sh $service_name $start_height $end_height`
   2) Errors Service - `https://github.com/thunderhead-labs/errors_service/#readme`
   - Note: Errors Service creates a lot of data, that's why it's recommended to only sync last few thousand blocks.
5) After historical mode is done, run above services in live mode:
   1) Script (update base path in script): `./run_service_live.sh $service_name`
   2) From repos
6) From chain service run location_info service (can't be run from script) to sync up location info data:
   1) Run `python3 location_info.py $ran_from` `ran_from` can be `na`, `eu` or `sg`
7) Create node sets using scripts in scripts folder (eg. cache_service_cli.py, create_cache_set.py, create_cache_sets_by_domain.py)
8) Run poktinfo for intervals (such as 4, 24, 96)

#### Run with - python3 run_cache_service.py $interval $mode
* interval is required and is the interval in blocks to cache by
* mode is optional and is the mode to run the service in if you want to only cache specific data (rewards, errors, latency)
* `run_cache_service.py` is the main file which invokes the logic in `cache_service.py`.

## Logic
1. Wait for `height % BLOCKS_INTERVAL == 0` then cache data of all node sets up until current height.
   1. Calls `update_cache_set()` for each node set in using a process pool
   2. Inside `update_cache_set()` each cache set is updated by calling it's matching function in parallel using a process pool:
      1. `update_rewards_cache()` - updates rewards cache from last cached height to current height in `BLOCKS_INTERVAL` skips
      2. `update_errors_cache()` - updates errors cache from last cached height to current height in `BLOCKS_INTERVAL` skips
      3. `update_latency_cache()` - updates latency cache from last cached height to current height in `BLOCKS_INTERVAL` skips
      4. `update_location_cache()` - updates location cache from last cached height to current height in `BLOCKS_INTERVAL` skips
      5. `update_nodes_cache()` - updates nodes cache from last cached height to current height in `BLOCKS_INTERVAL` skips
      * Each of the functions above has a stuck logic where if it gets stuck for more than x attempts it will be skipped to next interval.
   3. The data grouped and transformed and then saved in it's corresponding cache set table

### Schema

Please see [here](https://github.com/thunderhead-labs/common-os/blob/master/common/orm/schema/poktinfo.py) for the poktinfo schema definition.


## Services Used
#### Common - https://github.com/thunderhead-labs/common-os/blob/master/README.md
#### Reward/Nodes/Location info - https://github.com/thunderhead-labs/chain_service/blob/master/README.md
#### Errors/Latency cache - https://github.com/thunderhead-labs/errors_service/blob/master/README.md


## Contributing

Please read [CONTRIBUTING.md] for details on our code of conduct, and the process for submitting pull requests to us.
