import os
import json
import redis
import logging
from robokop_genetics.util import LoggingUtil
from robokop_genetics.simple_graph_components import SimpleEdge, SimpleNode


class GeneticsCache:

    logger = LoggingUtil.init_logging(__name__,
                                      logging.INFO,
                                      log_file_path=LoggingUtil.get_logging_path())

    def __init__(self,
                 use_default_credentials: bool = True,
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 redis_password: str = "",
                 prefix: str = ""):
        self.NORMALIZATION_KEY_PREFIX = f'{prefix}normalize-'

        if use_default_credentials:
            try:
                redis_host = os.environ['ROBO_GENETICS_CACHE_HOST']
                redis_port = os.environ['ROBO_GENETICS_CACHE_PORT']
                redis_db = os.environ['ROBO_GENETICS_CACHE_DB']
                redis_password = os.environ['ROBO_GENETICS_CACHE_PASSWORD']
            except KeyError:
                self.logger.warning('ROBO_GENETICS_CACHE environment variables not set. No cache activated.')
                raise Exception("Cache requested but ROBO_GENETICS_CACHE environment variables not set!")

        try:
            if redis_password:
                self.redis = redis.Redis(host=redis_host,
                                         port=int(redis_port),
                                         db=int(redis_db),
                                         password=redis_password)
            else:
                self.redis = redis.Redis(host=redis_host,
                                         port=int(redis_port),
                                         db=int(redis_db))
            self.redis.get('x')
            self.logger.info(f"Genetics cache connected to redis at {redis_host}:{redis_port}/{redis_db}")
        except Exception as e:
            self.logger.error(f"Genetics cache failed to connect to redis at {redis_host}:{redis_port}/{redis_db}.")
            raise e

    #def set_normalization(self, node_id: str, normalization: tuple):
    #    normalization_key = f'{self.NORMALIZATION_KEY_PREFIX}{node_id}'
    #    self.redis.set(normalization_key, json.dumps(normalization))

    def set_batch_normalization(self, normalization_map: dict):
        pipeline = self.redis.pipeline()
        for node_id, normalization in normalization_map.items():
            normalization_key = f'{self.NORMALIZATION_KEY_PREFIX}{node_id}'
            pipeline.set(normalization_key, json.dumps(normalization))
        pipeline.execute()

    #def get_normalization(self, node_id: str):
    #    normalization_key = f'{self.NORMALIZATION_KEY_PREFIX}{node_id}'
    #    result = self.redis.get(normalization_key)
    #    normalization = json.loads(result) if result is not None else None
    #    return normalization

    def get_batch_normalization(self, node_ids: list):
        pipeline = self.redis.pipeline()
        for node_id in node_ids:
            normalization_key = f'{self.NORMALIZATION_KEY_PREFIX}{node_id}'
            pipeline.get(normalization_key)
        results = pipeline.execute()

        normalization_map = {}
        for i, result in enumerate(results):
            if result is not None:
                normalization_map[node_ids[i]] = json.loads(result)
        return normalization_map

    def set_service_results(self, service_key: str, results_dict: dict):
        pipeline = self.redis.pipeline()
        for node_id, results in results_dict.items():
            redis_key = f'{service_key}-{node_id}'
            pipeline.set(redis_key, self.__encode_service_results(results))
        pipeline.execute()

    def __encode_service_results(self, service_results: list):
        encoded_results = []
        for (edge, node) in service_results:
            json_node = {"id": node.id, "category": node.type, "name": node.name}
            json_edge = {"source_id": edge.source_id,
                         "target_id": edge.target_id,
                         "provided_by": edge.provided_by,
                         "input_id": edge.input_id,
                         "predicate_id": edge.predicate_id,
                         "predicate_label": edge.predicate_label,
                         "ctime": edge.ctime,
                         "properties": edge.properties}
            encoded_result = {"edge": json_edge, "node": json_node}
            encoded_results.append(encoded_result)
        return json.dumps(encoded_results)

    def get_service_results(self, service_key: str, node_ids: list):
        pipeline = self.redis.pipeline()
        for node_id in node_ids:
            pipeline.get(f'{service_key}-{node_id}')
        redis_results = pipeline.execute()
        local_decode_results = self.__decode_service_results
        decoded_results = list(map(lambda result: local_decode_results(result) if result else None, redis_results))
        return decoded_results

    def __decode_service_results(self, redis_results):
        decoded_results = []
        json_object = json.loads(redis_results)
        for result in json_object:
            edge_json = result["edge"]
            edge_object = SimpleEdge(source_id=edge_json['source_id'],
                                     target_id=edge_json['target_id'],
                                     provided_by=edge_json['provided_by'],
                                     input_id=edge_json['input_id'],
                                     predicate_id=edge_json['predicate_id'],
                                     predicate_label=edge_json['predicate_label'],
                                     ctime=edge_json['ctime'],
                                     properties=edge_json['properties'])
            # note that right now we're not caching properties or synonyms for service nodes,
            # properties aren't used yet, synonyms will come from normalization after the fact
            node_json = result["node"]
            node_object = SimpleNode(id=node_json["id"],
                                     type=node_json["category"],
                                     name=node_json["name"])
            decoded_results.append((edge_object,
                                   node_object))
        return decoded_results

    def delete_all_keys_with_prefix(self, prefix: str):
        keys = self.redis.keys(f'{prefix}*')
        if keys:
            self.redis.delete(*keys)
