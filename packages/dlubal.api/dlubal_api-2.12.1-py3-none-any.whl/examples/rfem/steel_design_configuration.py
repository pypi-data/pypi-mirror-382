from dlubal.api import rfem, common
import google.protobuf.json_format

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    print('=============================================================\n')
    print('ULS Configuration:')
    uls_configuration = rfem_app.get_object(rfem.steel_design_objects.SteelDesignUlsConfiguration(no=1))
    print(google.protobuf.json_format.MessageToJson(uls_configuration, ensure_ascii=False))

    print('=============================================================\n')
    print('SLS Configuration:')
    sls_configuration = rfem_app.get_object(rfem.steel_design_objects.SteelDesignSlsConfiguration(no=1))
    print(google.protobuf.json_format.MessageToJson(sls_configuration, ensure_ascii=False))

    print('=============================================================\n')
    print('FR Configuration:')
    fr_configuration = rfem_app.get_object(rfem.steel_design_objects.SteelDesignFrConfiguration(no=1))
    print(google.protobuf.json_format.MessageToJson(fr_configuration, ensure_ascii=False))

    stability_analysis_tree_path = ['general_options', 'perform_stability_analysis']
    tension_tree_path = ['limit_values_for_special_cases', 'eta_n_t']
    settings_to_set = uls_configuration.SettingsEc3Table()
    common.set_tree_value(settings_to_set, stability_analysis_tree_path, False)
    common.set_tree_value(settings_to_set, tension_tree_path, 0.042)
    rfem_app.update_object(rfem.steel_design_objects.SteelDesignUlsConfiguration(no=1, settings_ec3=settings_to_set))