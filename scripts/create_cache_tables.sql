CREATE TABLE public.cache_set
(
    id       serial                 NOT NULL PRIMARY KEY,
    user_id  integer                NOT NULL,
    set_name character varying(255) NOT NULL
);

ALTER TABLE IF EXISTS public.cache_set
    OWNER to postgres;

CREATE TABLE public.cache_set_node
(
    cache_set_id integer                NOT NULL,
    address      character varying(255) NOT NULL
);

ALTER TABLE IF EXISTS public.cache_set_node
    OWNER to postgres;

CREATE TABLE public.rewards_cache_set
(
    cache_set_id  integer          NOT NULL,
    rewards_total double precision NOT NULL,
    start_height  integer          NOT NULL,
    end_height    integer          NOT NULL
);

ALTER TABLE IF EXISTS public.rewards_cache_set
    OWNER to postgres;

CREATE TABLE public.node_count_cache_set
(
    cache_set_id integer NOT NULL,
    node_count   integer NOT NULL,
    start_height integer NOT NULL,
    end_height   integer NOT NULL
);

ALTER TABLE IF EXISTS public.node_count_cache_set
    OWNER to postgres;

CREATE TABLE public.latency_cache_set
(
    cache_set_id         integer           NOT NULL,
    total_relays         integer           NOT NULL,
    region               character varying NOT NULL,
    start_height         integer           NOT NULL,
    end_height           integer           NOT NULL,
    avg_latency          double precision,
    avg_p90_latency      double precision,
    avg_weighted_latency double precision,
    chain                character varying NOT NULL
);

ALTER TABLE IF EXISTS public.latency_cache_set
    OWNER to postgres;

CREATE TABLE public.errors_cache_set
(
    cache_set_id integer NOT NULL,
    errors_count integer NOT NULL,
    msg text NOT NULL,
    start_height integer NOT NULL,
    end_height integer NOT NULL,
    chain character varying NOT NULL
);

ALTER TABLE IF EXISTS public.errors_cache_set
    OWNER to postgres;

CREATE TABLE public.location_cache_set
(
    cache_set_id         integer           NOT NULL,
    node_count           integer           NOT NULL,
    region               character varying NOT NULL,
    start_height         integer           NOT NULL,
    end_height           integer           NOT NULL
);

ALTER TABLE IF EXISTS public.location_cache_set
    OWNER to postgres;


CREATE TABLE IF NOT EXISTS public.location_info
(
    id SERIAL NOT NULL,
    address character varying(255) COLLATE pg_catalog."default" NOT NULL,
    ip character varying(255) COLLATE pg_catalog."default" NOT NULL,
    city character varying(255) COLLATE pg_catalog."default" NOT NULL,
    height integer NOT NULL,
    start_height integer,
    end_height integer,
    date_created time with time zone,
    continent character varying(255) COLLATE pg_catalog."default",
    country character varying(255) COLLATE pg_catalog."default",
    region character varying(255) COLLATE pg_catalog."default",
    lat character varying(255) COLLATE pg_catalog."default",
    lon character varying(255) COLLATE pg_catalog."default",
    isp character varying(255) COLLATE pg_catalog."default",
    org character varying(255) COLLATE pg_catalog."default",
    as_ character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT location_info_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.latency_cache
(
    address character varying(255) COLLATE pg_catalog."default" NOT NULL,
    total_relays integer NOT NULL,
    region character varying(255) COLLATE pg_catalog."default" NOT NULL,
    start_height integer NOT NULL,
    end_height integer NOT NULL,
    avg_latency double precision,
    avg_p90_latency double precision,
    avg_weighted_latency double precision,
    chain character varying NOT NULL
)

-- Table: public.rewards_info

-- DROP TABLE IF EXISTS public.rewards_info;

CREATE TABLE IF NOT EXISTS public.rewards_info
(
    tx_hash character varying NOT NULL,
    height integer NOT NULL,
    address character varying NOT NULL,
    reward double precision NOT NULL,
    chain_id character varying NOT NULL,
    relays integer NOT NULL,
    token_multiplier integer NOT NULL,
    percentage double precision,
    stake_weight double precision,
    CONSTRAINT rewards_info_pkey PRIMARY KEY (tx_hash)
)

-- Table: public.anomaly_tracked_cache_sets

-- DROP TABLE IF EXISTS public.anomaly_tracked_cache_sets;

CREATE TABLE IF NOT EXISTS public.anomaly_tracked_cache_sets
(
    cache_set_id integer NOT NULL,
    regions text COLLATE pg_catalog."default" NOT NULL,
    chains text COLLATE pg_catalog."default" NOT NULL,
    protagonist boolean NOT NULL,
    CONSTRAINT anomaly_tracked_cache_sets_pkey PRIMARY KEY (cache_set_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.anomaly_tracked_cache_sets
    OWNER to postgres;

-- Table: public.cache_set_state_range_entry

-- DROP TABLE IF EXISTS public.cache_set_state_range_entry;

CREATE TABLE IF NOT EXISTS public.cache_set_state_range_entry
(
    id SERIAL NOT NULL,
    cache_set_id integer NOT NULL,
    service character varying(255) COLLATE pg_catalog."default" NOT NULL,
    start_height integer NOT NULL,
    end_height integer NOT NULL,
    status character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT cache_set_state_range_entry_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.cache_set_state_range_entry
    OWNER to postgres;

-- Table: public.coin_prices

-- DROP TABLE IF EXISTS public.coin_prices;

CREATE TABLE IF NOT EXISTS public.coin_prices
(
    id SERIAL NOT NULL,
    coin character varying COLLATE pg_catalog."default" NOT NULL,
    vs_currency character varying COLLATE pg_catalog."default" NOT NULL,
    price double precision NOT NULL,
    height integer NOT NULL,
    CONSTRAINT prices_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.coin_prices
    OWNER to postgres;

-- Table: public.nodes_info

-- DROP TABLE IF EXISTS public.nodes_info;

CREATE TABLE IF NOT EXISTS public.nodes_info
(
    id SERIAL NOT NULL,
    address character varying(255) COLLATE pg_catalog."default" NOT NULL,
    url character varying(255) COLLATE pg_catalog."default" NOT NULL,
    domain character varying(255) COLLATE pg_catalog."default" NOT NULL,
    subdomain character varying(255) COLLATE pg_catalog."default",
    height integer NOT NULL,
    start_height integer,
    end_height integer,
    date_created timestamp with time zone NOT NULL,
    is_staked boolean DEFAULT true,
    CONSTRAINT nodes_info_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.nodes_info
    OWNER to postgres;

-- Table: public.services_state

-- DROP TABLE IF EXISTS public.services_state;

CREATE TABLE IF NOT EXISTS public.services_state
(
    id SERIAL NOT NULL,
    service character varying(255) COLLATE pg_catalog."default" NOT NULL,
    height integer NOT NULL,
    status character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT services_state_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.services_state
    OWNER to postgres;

-- Table: public.services_state_range

-- DROP TABLE IF EXISTS public.services_state_range;

CREATE TABLE IF NOT EXISTS public.services_state_range
(
    id serial NOT NULL,
    service character varying(255) COLLATE pg_catalog."default" NOT NULL,
    start_height integer NOT NULL,
    end_height integer NOT NULL,
    status character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT services_state_range_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.services_state_range
    OWNER to postgres;

-- DROP TABLE IF EXISTS public.errors_cache;

CREATE TABLE IF NOT EXISTS public.errors_cache
(
    id serial NOT NULL,
    start_height integer NOT NULL,
    end_height integer NOT NULL,
    provider character varying(255) COLLATE pg_catalog."default" NOT NULL,
    errors_count bigint NOT NULL,
    error_type character varying(255) COLLATE pg_catalog."default" NOT NULL,
    msg text COLLATE pg_catalog."default" NOT NULL,
    date_created timestamp with time zone,
    chain character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT errors_cache_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.errors_cache
    OWNER to postgres;
