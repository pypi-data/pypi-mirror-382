from nemo_library import NemoLibrary


def getNL():
    return NemoLibrary(
        config_file="./tests/config.ini",
        migman_local_project_directory="./tests/migman",
        migman_projects=["Customers", "Ship-To Addresses (Customers)"],
        migman_mapping_fields=["S_Kunde.Kunde"],
        migman_additional_fields={},
        migman_multi_projects={},
        metadata_directory="./tests/metadata_optimate",
    )
