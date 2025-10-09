from r2x.plugin_manager.defaults import PluginComponent, DefaultFile

# These will get registered into the plugin manager on module load.
from .parser import cli_arguments as parser_cli
from .exporter import cli_arguments as exporter_cli
from .sysmod import cli_arguments as sysmod_cli, update_system

_ = (parser_cli, exporter_cli, sysmod_cli, update_system)


def get_common_files():
    return {
        "config": DefaultFile.from_path("defaults/config.json", module="r2x_pypsa"),
        "plugins": DefaultFile.from_path("defaults/plugins_config.json", module="r2x_pypsa"),
    }


def create_r2x_pypsa_parser() -> PluginComponent:
    """Create components for the parser."""
    from r2x.parser.reeds import ReEDSParser as TestParser
    from r2x.config_models import ReEDSConfig as TestConfig

    # Get common defaults
    common_files = get_common_files()

    # Create input defaults
    input_defaults = [common_files["config"], common_files["plugins"]]
    input_defaults.extend([DefaultFile.from_path("defaults/reeds_input.json", module="r2x_pypsa")])

    fmap = DefaultFile.from_path("defaults/reeds_us_mapping.json", module="r2x_pypsa")
    return PluginComponent(
        config=TestConfig,
        parser=TestParser,
        parser_defaults=input_defaults,
        parser_filters=["pl_rename", "pl_filter_year"],
        fmap=fmap,
    )


def create_r2x_pypsa_exporter() -> PluginComponent:
    """Create components for the exporter."""
    from r2x.exporter.plexos import PlexosExporter as TestExporter
    from r2x.config_models import PlexosConfig as TestConfig

    # Get common defaults
    common_files = get_common_files()

    # Create export defaults
    export_defaults = [
        DefaultFile.from_path("defaults/plexos_input.json", module="r2x_pypsa"),
        DefaultFile.from_path("defaults/plexos_output.json", module="r2x_pypsa"),
        DefaultFile.from_path("defaults/plexos_simulation_objects.json", module="r2x_pypsa"),
        DefaultFile.from_path("defaults/plexos_horizons.json", module="r2x_pypsa"),
        DefaultFile.from_path("defaults/plexos_models.json", module="r2x_pypsa"),
    ]

    fmap = DefaultFile.from_path("defaults/plexos_mapping.json", module="r2x_pypsa")
    return PluginComponent(
        config=TestConfig,
        exporter=TestExporter,
        export_defaults=export_defaults,
        fmap=fmap,
    )


def create_plugin_components() -> dict[str, PluginComponent]:
    """Return all plugin components."""
    components = {
        "r2x_pypsaParser": create_r2x_pypsa_parser(),
        "r2x_pypsaExporter": create_r2x_pypsa_exporter(),
    }
    return components
