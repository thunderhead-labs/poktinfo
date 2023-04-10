--- cache_set ---
CREATE INDEX IF NOT EXISTS cache_set_id_idx ON public.cache_set (id DESC NULLS LAST)
CREATE INDEX IF NOT EXISTS cache_set_set_name_idx ON public.cache_set (set_name DESC NULLS LAST)

--- cache_set_node ---
CREATE INDEX IF NOT EXISTS cache_set_node_id_idx ON public.cache_set_node (cache_set_id DESC NULLS LAST)
CREATE INDEX IF NOT EXISTS cache_set_node_address_idx ON public.cache_set_node (address DESC NULLS LAST)

--- cache_set_state_range_entry ---
CREATE INDEX IF NOT EXISTS cache_set_state_range_entry_service_idx
ON public.cache_set_state_range_entry (service DESC NULLS LAST)

--- services_state ---
CREATE INDEX IF NOT EXISTS services_state_service_idx
ON public.services_state (service DESC NULLS LAST)

--- services_state_range ---
CREATE INDEX IF NOT EXISTS services_state_range_service_idx
ON public.services_state_range (service DESC NULLS LAST)

--- errors_cache_set ---
CREATE INDEX IF NOT EXISTS errors_cache_set_start_height_idx
ON public.errors_cache_set (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS errors_cache_set_end_height_idx
ON public.errors_cache_set (end_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS errors_cache_set_msg_idx
ON public.errors_cache_set (msg DESC NULLS LAST)

--- latency_cache_set ---
CREATE INDEX IF NOT EXISTS latency_cache_set_start_height_idx
ON public.latency_cache_set (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_set_end_height_idx
ON public.latency_cache_set (end_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_set_region_idx
ON public.latency_cache_set (region DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_set_avg_latency_idx
ON public.latency_cache_set (avg_latency DESC NULLS LAST)

--- location_cache_set ---
CREATE INDEX IF NOT EXISTS location_cache_set_start_height_idx
ON public.location_cache_set (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS location_cache_set_end_height_idx
ON public.location_cache_set (end_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS location_cache_set_region_idx
ON public.location_cache_set (region DESC NULLS LAST)

--- rewards_cache_set ---
CREATE INDEX IF NOT EXISTS rewards_cache_set_start_height_idx
ON public.rewards_cache_set (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS rewards_cache_set_end_height_idx
ON public.rewards_cache_set (end_height DESC NULLS LAST)

--- node_count_cache_set ---
CREATE INDEX IF NOT EXISTS node_count_cache_set_start_height_idx
ON public.node_count_cache_set (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS node_count_cache_set_end_height_idx
ON public.node_count_cache_set (end_height DESC NULLS LAST)

--- nodes_info ---
CREATE INDEX IF NOT EXISTS nodes_info_height_idx
ON public.nodes_info (height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS nodes_info_start_height_idx
ON public.nodes_info (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS nodes_info_end_height_idx
ON public.nodes_info (end_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS nodes_info_address_idx
ON public.nodes_info (address DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS nodes_info_url_idx
ON public.nodes_info (url DESC NULLS LAST)

--- location_info ---
CREATE INDEX IF NOT EXISTS location_info_height_idx
ON public.location_info (height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS location_info_start_height_idx
ON public.location_info (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS location_info_end_height_idx
ON public.location_info (end_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS location_info_address_idx
ON public.location_info (address DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS location_info_continent_idx
ON public.location_info (continent DESC NULLS LAST)

--- errors_cache ---
CREATE INDEX IF NOT EXISTS errors_cache_start_height_idx
ON public.errors_cache (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS errors_cache_end_height_idx
ON public.errors_cache (end_height DESC NULLS LAST)

--- latency_cache ---
CREATE INDEX IF NOT EXISTS latency_cache_address_idx
ON public.latency_cache (address DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_start_height_idx
ON public.latency_cache (start_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_end_height_idx
ON public.latency_cache (end_height DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_region_idx
ON public.latency_cache (region DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_avg_latency_idx
ON public.latency_cache (avg_latency DESC NULLS LAST)

CREATE INDEX IF NOT EXISTS latency_cache_chain_idx
ON public.latency_cache (chain DESC NULLS LAST)

--- rewards_info ---
-- Index: idx_height_rewards_info

-- DROP INDEX IF EXISTS public.idx_height_rewards_info;

CREATE INDEX IF NOT EXISTS idx_height_rewards_info
    ON public.rewards_info USING btree
    (height ASC NULLS LAST);
-- Index: idx_tx_hash_rewards_info

-- DROP INDEX IF EXISTS public.idx_tx_hash_rewards_info;

CREATE INDEX IF NOT EXISTS idx_tx_hash_rewards_info
    ON public.rewards_info USING btree
    (tx_hash ASC NULLS LAST);
-- Index: rewards_info_address_idx

-- DROP INDEX IF EXISTS public.rewards_info_address_idx;

CREATE INDEX IF NOT EXISTS rewards_info_address_idx
    ON public.rewards_info USING btree
    (address DESC NULLS LAST);
-- Index: rewards_info_height_idx

-- DROP INDEX IF EXISTS public.rewards_info_height_idx;

CREATE INDEX IF NOT EXISTS rewards_info_height_idx
    ON public.rewards_info USING btree
    (height DESC NULLS LAST);
