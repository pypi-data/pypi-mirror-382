import copy

# Base default configuration for all detectors.
DEFAULT_GUARDRAILS_CONFIG = {
    "topic_detector": {"enabled": False, "topic": []},
    "nsfw": {"enabled": False},
    "toxicity": {"enabled": False},
    "pii": {"enabled": False, "entities": []},
    "injection_attack": {"enabled": False},
    "keyword_detector": {"enabled": False, "banned_keywords": []},
    "policy_violation": {
        "enabled": False,
        "policy_text": "Do not allow any illegal or immoral activities.",
        "need_explanation": False,
    },
    "bias": {"enabled": False},
    "copyright_ip": {"enabled": False},
    "system_prompt": {"enabled": False, "index": "system"},
    "sponge_attack": {"enabled": False},
}


class GuardrailsConfig:
    """
    A helper class to manage Guardrails configuration.

    Users can either use preset configurations or build a custom one.
    """

    def __init__(self, config=None):
        # Use a deep copy of the default to avoid accidental mutation.
        self.config = (
            copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG) if config is None else config
        )

    @classmethod
    def injection_attack(cls):
        """
        Returns a configuration instance pre-configured for injection attack detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["injection_attack"] = {"enabled": True}
        return cls(config)

    @classmethod
    def policy_violation(cls, policy_text: str = "", need_explanation: bool = False, coc_policy_name: str = ""):
        """
        Returns a configuration instance pre-configured for policy violation detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["policy_violation"] = {
            "enabled": True,
            "need_explanation": need_explanation,
        }

        if policy_text:
            config["policy_violation"]["policy_text"] = policy_text
        if coc_policy_name:
            config["policy_violation"]["coc_policy_name"] = coc_policy_name

        return cls(config)

    @classmethod
    def toxicity(cls):
        """
        Returns a configuration instance pre-configured for toxicity detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["toxicity"] = {"enabled": True}
        return cls(config)

    @classmethod
    def nsfw(cls):
        """
        Returns a configuration instance pre-configured for NSFW content detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["nsfw"] = {"enabled": True}
        return cls(config)

    @classmethod
    def bias(cls):
        """
        Returns a configuration instance pre-configured for bias detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["bias"] = {"enabled": True}
        return cls(config)

    @classmethod
    def pii(cls, entities=None):
        """
        Returns a configuration instance pre-configured for PII detection.

        Args:
            entities (list, optional): List of PII entity types to detect.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["pii"] = {
            "enabled": True,
            "entities": entities if entities is not None else [],
        }
        return cls(config)

    @classmethod
    def topic(cls, topics=None):
        """
        Returns a configuration instance pre-configured for topic detection.

        Args:
            topics (list, optional): List of topics to detect.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["topic_detector"] = {
            "enabled": True,
            "topic": topics if topics is not None else [],
        }
        return cls(config)

    @classmethod
    def keyword(cls, keywords=None):
        """
        Returns a configuration instance pre-configured for keyword detection.

        Args:
            keywords (list, optional): List of banned keywords to detect.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["keyword_detector"] = {
            "enabled": True,
            "banned_keywords": keywords if keywords is not None else [],
        }
        return cls(config)

    @classmethod
    def copyright_ip(cls):
        """
        Returns a configuration instance pre-configured for copyright/IP detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["copyright_ip"] = {"enabled": True}
        return cls(config)

    @classmethod
    def system_prompt(cls, index="system"):
        """
        Returns a configuration instance pre-configured for system prompt detection.

        Args:
            index (str, optional): Index name for system prompt detection. Defaults to "system".
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["system_prompt"] = {"enabled": True, "index": index}
        return cls(config)
    
    @classmethod
    def sponge_attack(cls):
        """
        Returns a configuration instance pre-configured for sponge attack detection.
        """
        config = copy.deepcopy(DEFAULT_GUARDRAILS_CONFIG)
        config["sponge_attack"] = {"enabled": True}
        return cls(config)

    def update(self, **kwargs):
        """
        Update the configuration with custom values.

        Only keys that exist in the default configuration can be updated.
        For example:
            config.update(nsfw={"enabled": True}, toxicity={"enabled": True})
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
            else:
                raise ValueError(f"Unknown detector config: {key}")
        return self

    def as_dict(self):
        """
        Return the underlying configuration dictionary.
        """
        return self.config

    @classmethod
    def from_custom_config(cls, config_dict: dict):
        """
        Configure guardrails from a dictionary input.

        Validates that the input dictionary matches the expected schema structure.
        Each key must exist in the default configuration, and its value must be a dictionary.

        Args:
            config_dict (dict): Dictionary containing guardrails configuration

        Returns:
            GuardrailsConfig: Returns a new GuardrailsConfig instance

        Raises:
            ValueError: If the input dictionary contains invalid keys or malformed values
        """
        instance = cls()
        for key, value in config_dict.items():
            if key not in instance.config:
                raise ValueError(f"Unknown detector config: {key}")
            if not isinstance(value, dict):
                raise ValueError(f"Config value for {key} must be a dictionary")

            # Validate that all required fields exist in the default config
            default_fields = set(DEFAULT_GUARDRAILS_CONFIG[key].keys())
            provided_fields = set(value.keys())

            if not provided_fields.issubset(default_fields):
                invalid_fields = provided_fields - default_fields
                raise ValueError(f"Invalid fields for {key}: {invalid_fields}")

            instance.config[key] = value

        return instance

    def get_config(self, detector_name: str) -> dict:
        """
        Get the configuration for a specific detector.

        Args:
            detector_name (str): Name of the detector to get configuration for

        Returns:
            dict: Configuration dictionary for the specified detector

        Raises:
            ValueError: If the detector name doesn't exist in the configuration
        """
        if detector_name not in self.config:
            raise ValueError(f"Unknown detector: {detector_name}")

        return copy.deepcopy(self.config[detector_name])


class RedTeamConfig:
    """
    A helper class to manage RedTeam configuration.
    """

    def __init__(self, config=None):
        if config is None:
            config = copy.deepcopy(DEFAULT_REDTEAM_CONFIG)
            # Only include advanced tests if dataset is not standard
            if config.get("dataset_name") != "standard":
                config["redteam_test_configurations"].update(
                    copy.deepcopy(ADVANCED_REDTEAM_TESTS)
                )
        self.config = config

    def as_dict(self):
        """
        Return the underlying configuration dictionary.
        """
        return self.config


class ModelConfig:
    def __init__(self, config=None):
        if config is None:
            config = copy.deepcopy(DETAIL_MODEL_CONFIG)
        self.config = config

    @classmethod
    def model_name(self, model_name: str):
        """
        Set the model name.
        """
        self.config["model_name"] = model_name
        return self

    @classmethod
    def testing_for(self, testing_for: str):
        """
        Set the testing for.
        """
        self.config["testing_for"] = testing_for
        return self

    @classmethod
    def model_config(self, model_config: dict):
        """
        Set the model config.
        """
        self.config["model_config"] = model_config
        return self

    def as_dict(self):
        """
        Return the underlying configuration dictionary.
        """
        return self.config
