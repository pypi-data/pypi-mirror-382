# Copyright 2024 Confluent Inc.

import datetime

from py4j.compat import long
from pyflink.java_gateway import get_gateway
from pyflink.util.java_utils import create_url_class_loader
from pyflink.table.environment_settings import EnvironmentSettings

__all__ = ['ConfluentSettings']

class ConfluentSettings(object):
  """
  Entrypoint for Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.

  Pass these settings into a :class:`~pyflink.table.TableEnvironment`  for
  talking to Confluent Cloud.
  """

  @staticmethod
  def from_file(path: str) -> 'EnvironmentSettings':
    """
    Entrypoint for Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.

    This method parses required configuration from a properties file.

    FLINK_PROPERTIES can be used to define a file path via an environment variable.

    :return: A Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.
    """
    gateway = get_gateway()
    j_settings = gateway.jvm.ConfluentSettings.fromFile(path)
    return EnvironmentSettings(j_settings)

  @staticmethod
  def from_global_variables() -> 'EnvironmentSettings':
    """
    Entrypoint for Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.

    It reads all required configuration from global environment variables.

    FLINK_PROPERTIES can be used to define a file path via an environment variable.

    :return: A Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.
    """
    return ConfluentSettings.new_builder().build()

  @staticmethod
  def new_builder() -> 'ConfluentSettings.Builder':
    """
    Creates a builder for Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.

    Global environment variables are the fallback.

    FLINK_PROPERTIES can be used to define a path via an environment variable.

    :return: A builder of ConfluentSettings.
    """
    gateway = get_gateway()
    j_builder = gateway.jvm.ConfluentSettings.newBuilder()
    return ConfluentSettings.Builder(j_builder)

  @staticmethod
  def new_builder_from_file(path: str) -> 'ConfluentSettings.Builder':
    """
    Creates a builder for Confluent-specific :class:`~pyflink.table.EnvironmentSettings`.

    Global environment variables are the fallback.

    :return: A builder of ConfluentSettings.
    """
    gateway = get_gateway()
    j_builder = gateway.jvm.ConfluentSettings.newBuilderFromFile(path)
    return ConfluentSettings.Builder(j_builder)

  class Builder(object):
    """
    Builder pattern for a fluent definition of Confluent-specific
    :class:`~pyflink.table.EnvironmentSettings`.
    """

    def __init__(self, j_builder):
      self._j_builder = j_builder

    def set_context_name(self, name: str) -> 'ConfluentSettings.Builder':
        """
        A name for this Table API session. Optional but recommended.

        For example: 'my_table_program'.

        :return: This object.
        """
        self._j_builder = self._j_builder.setContextName(name)
        return self

    def set_organization_id(self, org_id: str) -> 'ConfluentSettings.Builder':
      """
      Sets the ID of the organization. Required.

      For example: 'b0b21724-4586-4a07-b787-d0bb5aacbf87'.

      Overrides the global variable ORG_ID.

      :return: This object.
      """
      self._j_builder = self._j_builder.setOrganizationId(org_id)
      return self

    def set_environment_id(self, env_id: str) -> 'ConfluentSettings.Builder':
      """
      Sets the ID of the environment. Required.

      For example: 'env-z3y2x1'.

      Overrides the global variable ENV_ID.

      :return: This object.
      """
      self._j_builder = self._j_builder.setEnvironmentId(env_id)
      return self

    def set_flink_api_key(self, key: str) -> 'ConfluentSettings.Builder':
      """
      Sets the API key for Flink access. Required.

      Overrides global variable FLINK_API_KEY.

      :return: This object.
      """
      self._j_builder = self._j_builder.setFlinkApiKey(key)
      return self

    def set_flink_api_secret(self, secret: str) -> 'ConfluentSettings.Builder':
      """
      Sets the API secret for Flink access. Required.

      Overrides global variable FLINK_API_SECRET.

      :return: This object.
      """
      self._j_builder = self._j_builder.setFlinkApiSecret(secret)
      return self

    def set_compute_pool_id(self, pool_id: str) -> 'ConfluentSettings.Builder':
      """
      Sets the ID of the compute pool. Required.

      For example: 'lfcp-8m03rm'.

      Overrides global variable COMPUTE_POOL_ID.

      :return: This object.
      """
      self._j_builder = self._j_builder.setComputePoolId(pool_id)
      return self

    def set_cloud(self, provider: str) -> 'ConfluentSettings.Builder':
      """
      Sets the Confluent identifier for a cloud provider. Required.

      For example: 'aws'.

      Overrides the global variable CLOUD_PROVIDER.

      :return: This object.
      """
      self._j_builder = self._j_builder.setCloud(provider)
      return self

    def set_region(self, region: str) -> 'ConfluentSettings.Builder':
      """
      Sets the Confluent identifier for a cloud provider's region. Required.

      For example: 'us-east-1'.

      Overrides the global variable CLOUD_REGION.

      :return: This object.
      """
      self._j_builder = self._j_builder.setRegion(region)
      return self

    def set_principal_id(self, principal_id: str) -> 'ConfluentSettings.Builder':
      """
      Sets the Principal that runs submitted statements. Optional.

      For example: 'sa-23kgz4' (for a service account).

      Overrides the global variable PRINCIPAL_ID.

      :return: This object.
      """
      self._j_builder = self._j_builder.setPrincipalId(principal_id)
      return self

    def set_endpoint_template(self, endpoint_template: str) -> 'ConfluentSettings.Builder':
      """
      Sets the template for the endpoint URL. Optional.

      For example: 'https://flinkpls-abc123.{region}.{cloud}.glb.confluent.cloud'.

      The template may contain the placeholders {region} and {cloud}. The placeholders will
      be replaced with the values of the variable CLOUD_REGION and CLOUD_PROVIDER respectively.

      Default value is 'https://flink.{region}.{cloud}.confluent.cloud'.

      Overrides the global variable ENDPOINT_TEMPLATE.

      :return: This object.
      """
      self._j_builder = self._j_builder.setEndpointTemplate(endpoint_template)
      return self

    def set_rest_endpoint(self, endpoint: str) -> 'ConfluentSettings.Builder':
      """
      Sets the URL to the REST endpoint. Optional.

      For example: 'confluent.cloud'.

      Overrides the global variable REST_ENDPOINT.

      :return: This object.
      """
      self._j_builder = self._j_builder.setRestEndpoint(endpoint)
      return self

    def set_catalog_cache_expiration(self, expiration: datetime.timedelta) -> 'ConfluentSettings.Builder':
      """
      Sets the expiration time for catalog objects before Confluent Cloud is called again.
      Optional.

      For example: '5 min'. '1 min' by default. '0' disables the caching.

      :return: This object.
      """
      j_duration_class = get_gateway().jvm.java.time.Duration
      j_duration = j_duration_class.ofMillis(long(round(expiration.total_seconds() * 1000)))
      self._j_builder = self._j_builder.setCatalogCacheExpiration(j_duration)
      return self

    def set_option(self, key: str, value: str) -> 'ConfluentSettings.Builder':
      """
      Sets a Confluent-specific configuration option.

      :return: This object.
      """
      self._j_builder = self._j_builder.setOption(key, value)
      return self

    def build(self) -> 'EnvironmentSettings':
      """
      Creates Confluent-specific :class:`~pyflink.table.EnvironmentSettings`
      that can be passed into :func:`~pyflink.table.TableEnvironment.create`.

      :return: an immutable instance of EnvironmentSettings.
      """
      gateway = get_gateway()
      context_classloader = gateway.jvm.Thread.currentThread().getContextClassLoader()
      new_classloader = create_url_class_loader([], context_classloader)
      gateway.jvm.Thread.currentThread().setContextClassLoader(new_classloader)
      return EnvironmentSettings(self._j_builder.build())