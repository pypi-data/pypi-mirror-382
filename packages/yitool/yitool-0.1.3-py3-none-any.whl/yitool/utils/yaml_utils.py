import yaml
from yitool.log import logger
from yitool.utils.path_utils import PathUtils
from yitool.exceptions import YiToolException

class YamlUtils:
    @staticmethod
    def load(yaml_file: str):
        """ Loads a YAML file and returns the contents as a dictionary.
        
        Args:
            yaml_file: Path to the YAML file
        
        Returns:
            The loaded YAML content as a dictionary
        
        Raises:
            FileNotFoundError: If the file does not exist
            YiToolException: If there is an error parsing the YAML file
        """
        PathUtils.raise_if_not_exists(yaml_file)
        with open(yaml_file, 'r', encoding='utf-8') as stream:
            try:
                return yaml.full_load(stream)
            except yaml.YAMLError as exc:
                logger.error(f'Error loading YAML file: {yaml_file}, {exc}')
                raise YiToolException(f'Failed to load YAML file: {yaml_file}. Error: {str(exc)}') from exc
                
    @staticmethod
    def dump(data: dict, yaml_file: str):
        """ Writes a dictionary to a YAML file.
        
        Args:
            data: The dictionary data to write
            yaml_file: Path to the output YAML file
        
        Raises:
            YiToolException: If there is an error writing the YAML file
        """
        with open(yaml_file, 'w') as stream:
            try:
                yaml.dump(data, stream, encoding='utf-8')
            except yaml.YAMLError as exc:
                logger.error(f'Error dumping YAML file: {yaml_file}, {exc}')
                raise YiToolException(f'Failed to dump data to YAML file: {yaml_file}. Error: {str(exc)}') from exc
