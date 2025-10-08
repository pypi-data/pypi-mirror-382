from dlubal.api import rfem, common
import google.protobuf.json_format as pbjson

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # --- Design Configuration ---

    # Step 1: Retrieve the Design ULS Configuration TreeTable for Steel add-on
    steel_uls_config: rfem.steel_design_objects.SteelDesignUlsConfiguration = rfem_app.get_object(
        obj=rfem.steel_design_objects.SteelDesignUlsConfiguration(no=1)
    )
    settings_ec3 = steel_uls_config.settings_ec3
    print(f"\nSETTINGS_EC3:\n{settings_ec3}")

    # Step 2: Retrieve a specific value from the configuration
    # Path to the specific value
    elastic_design_path=[
        "options",
        "options_elastic_design_root",
        "options_elastic_design"
    ]
    # Get and print specific value
    elastic_design_val = common.get_tree_value(
        tree=settings_ec3,
        path=elastic_design_path
    )
    print(f"\nElastic Design: {elastic_design_val}")

    # Step 3: Modify the value
    common.set_tree_value(
        tree=settings_ec3,
        path=elastic_design_path,
        value=True
    )

    # --- Standard Parameters ---

    # Step 4: Retrieve and print the Standard Parameters TreeTable
    standard_params_ec3 = steel_uls_config.standard_parameters_tree
    print(f"\nSTANDARD_PARAMETERS:\n{standard_params_ec3}")

    # Step 5: Retrieve a specific value from the Standard Parameters
    # Path to the specific value
    shear_resistance_factor_path=[
        "stainless_steel_acc_to_en_1993_1_4",
        "5_ultimate_limit_state_uls",
        "5_6_shear_resistance",
        "eta"
    ]
    # Get and print specific value
    shear_resistance_factor_val = common.get_tree_value(
        tree=standard_params_ec3,
        path=shear_resistance_factor_path
    )
    print(f"\nShear Resistance Factor: {shear_resistance_factor_val}")

    # # Step 6: Modify the value
    # Temporarily commenting out due to an issue with setting standard_parameters_tree
    # common.set_tree_value(
    #     tree=standard_params_ec3,
    #     path=shear_resistance_factor_path,
    #     value=1.5
    # )

    # Step 7: Apply the updated configuration to the model
    # Temporarily clear the 'standard_parameters_tree' field - Currently required before updating the object
    steel_uls_config.ClearField("standard_parameters_tree")
    rfem_app.update_object(
        obj=steel_uls_config
    )
