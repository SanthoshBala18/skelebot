"""Root Config Class for Skelebot YAML File"""

from schema import Schema, And, Optional
from .job import Job
from .param import Param
from .skeleYaml import SkeleYaml
from .component import Activation
from ..common import LANGUAGE_IMAGE
from ..components.componentFactory import ComponentFactory

class Config(SkeleYaml):
    """
    Root Config Class for Skelebot YAML File

    Built on top of the SkeleYaml parent Object in order to enherit and extend the functionality
    of yaml file generation and parsing
    """

    schema = Schema({
        'name': And(str, error='\'name\' must be a String'),
        Optional('description'): And(str, error='\'description\' must be a String'),
        Optional('maintainer'): And(str, error='\'maintainer\' must be a String'),
        Optional('contact'): And(str, error='\'contact\' must be a String'),
        'language': And(str, error='\'language\' must be a String'),
        Optional('baseImage'): And(str, error='\'baseImage\' must be a String'),
        Optional('primaryJob'): And(str, error='\'primaryJob\' must be a String'),
        Optional('ephemeral'): And(bool, error='\'ephemeral\' must be a Boolean'),
        Optional('dependencies'): And(list, error='\'dependencies\' must be a List'),
        Optional('ignores'): And(list, error='\'ignores\' must be a List'),
        Optional('jobs'): And(list, error='\'jobs\' must be a List'),
        Optional('ports'): And(list, error='\'ports\' must be a List'),
        Optional('components'): And(dict, error='\'components\' must be a Dictionary'),
        Optional('params'): And(list, error='\'params\' must be a List')
    }, ignore_extra_keys=True)

    name = None
    description = None
    version = None
    maintainer = None
    contact = None
    language = None
    baseImage = None
    primaryJob = None
    ephemeral = None
    dependencies = None
    ignores = None
    jobs = None
    ports = None
    components = None
    params = None

    def __init__(self, name=None, description=None, version=None, maintainer=None, contact=None,
                 language=None, baseImage=None, primaryJob=None, ephemeral=None, dependencies=None,
                 ignores=None, jobs=None, ports=None, components=None, params=None):
        """Initialize the config object with all provided optional attributes"""

        self.name = name
        self.description = description
        self.version = version
        self.maintainer = maintainer
        self.contact = contact
        self.language = language
        self.baseImage = baseImage
        self.primaryJob = primaryJob
        self.ephemeral = ephemeral
        self.dependencies = dependencies if dependencies is not None else []
        self.ignores = ignores if ignores is not None else []
        self.jobs = jobs if jobs is not None else []
        self.ports = ports if ports is not None else []
        self.components = components if components is not None else []
        self.params = params if params is not None else []

    def toDict(self):
        """
        Extends the parent function in order to logic for handling the conversion of
        components since the Class structure and yaml sctructures do not match
        """

        components_dict = {}
        for component in self.components:
            component_dict = component.toDict()
            if component_dict != {}:
                components_dict[component.__class__.__name__.lower()] = component_dict

        dct = super().toDict()
        dct["components"] = components_dict
        return dct

    def getBaseImage(self):
        """
        Returns the proper base image based on the values for language and kerberos,
        or returns the user defined base image if provided in the config yaml
        """

        if self.baseImage:
            image = self.baseImage
        else:
            language = self.language if self.language is not None else "NA"
            image = LANGUAGE_IMAGE[language]

            variant = "base"
            for component in self.components:
                if component.__class__.__name__.lower() == "kerberos":
                    variant = "krb"

            image = image[variant]

        return image

    def getImageName(self):
        """Construct and return the name for the docker image based on the project name"""
        return self.name.lower().replace(" ", "-")

    def loadComponents(self, config):
        """
        Parses the components section of skelebot.yaml config to generate the complete list of
        components for the project based on the active component list and each components'
        Activation attribute
        """

        componentFactory = ComponentFactory()
        if (config is None):
            # Build the default components for a non-skelebot project
            defaultActivations = [Activation.EMPTY, Activation.ALWAYS]
            self.components = componentFactory.buildComponents(defaultActivations)
        else:
            # Build the components that are defined in the config yaml data
            compNames = []
            components = []
            if ("components" in config):
                configComps = config["components"]
                for compName in configComps:
                    component = componentFactory.buildComponent(compName, configComps[compName])
                    if (component is not None):
                        components.append(component)
                        compNames.append(component.__class__.__name__)

            # Build the additonal components that are active without configuration data
            activations = [Activation.PROJECT, Activation.ALWAYS]
            components.extend(componentFactory.buildComponents(activations, ignores=compNames))
            self.components = components

    @classmethod
    def load(cls, config):
        """Load the config Dict from the yaml file into the Config object"""

        cfg = cls()
        if config is not None:

            cls.validate(config)
            values = {}
            for attr, value in config.items():
                if (attr in vars(Config)) and (attr != "components") and (attr != "version"):
                    if (attr == "jobs"):
                        values[attr] = Job.loadList(value)
                    elif (attr == "params"):
                        values[attr] = Param.loadList(value)
                    else:
                        values[attr] = value

            cfg = cls(**values)

        cfg.loadComponents(config)

        return cfg
