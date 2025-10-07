import requests
from .envConfigMapSecret import DevtronOverrideConfigMapSecret

class OverrideDeploymentTemplateHandler:
    def __init__(self, base_url, headers):
        self.base_url                    = base_url
        self.headers                     = headers
        self.env_override_cm_cs          = DevtronOverrideConfigMapSecret(base_url,headers)

    def get_chart_ref_id_for_env(self,app_id,env_id) -> dict:
        """
        Fetch the chart_ref_id for a given app_id and env_id from Devtron.
        Args:
            app_id (int or str): The application ID
            env_id (int or str)L The environment ID
        Returns:
            dict: {success: bool, chart_ref_id: int, error: str}
        """
        try:
            url = f"{self.base_url}/orchestrator/chartref/autocomplete/{app_id}/{env_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json().get('result', {})
                return {'success': True, 'chart_ref_id': result.get('latestEnvChartRef')}
            else:
                return {'success': False, 'error': f'API request failed: {response.text}'}
        except Exception as e:
            return {'success': False, 'error': f'Exception occurred: {str(e)}'}

    def get_env_configuration_template(self,app_id,env_id,chart_ref_id) -> dict:
        """
        Fetch the override deployment template for a given app_id env_id and chart_ref_id from Devtron.
        Args:
            app_id (int or str): The application ID
            env_id (int or str): The environment ID
            chart_ref_id (int or str): The chartRef ID
        Returns:
            dict: {success: bool, env_configuration_template: dict, error: str}
        """
        try:
            url = f"{self.base_url}/orchestrator/app/env/{app_id}/{env_id}/{chart_ref_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json().get('result', {})
                return {'success': True, 'env_config_template': result}
            else:
                return {'success': False, 'error': f'API request failed: {response.text}'}
        except Exception as e:
            return {'success': False, 'error': f'Exception occurred: {str(e)}'}

    