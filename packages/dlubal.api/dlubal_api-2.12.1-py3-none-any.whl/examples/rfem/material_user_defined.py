from dlubal.api import rfem


with rfem.Application() as rfem_app:

    mat_2: rfem.structure_core.Material = rfem_app.get_object(
        rfem.structure_core.Material(no=2)
    )
    print(mat_2)

    mat_2.no = 4
    mat_2.user_defined = True
    mat_prop = mat_2.temperature.rows[0]
    mat_prop.mass_density = 2400
    mat_prop.specific_weight = 24000

    rfem_app.create_object(mat_2)

    mat_4 = rfem_app.get_object(rfem.structure_core.Material(no=4))
    print(mat_4)





