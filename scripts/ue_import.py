"""Run in UE Editor Python, from a generated asset folder. Not runtime gameplay code.
Imports into a new subdirectory. Does not construct an articulated Blueprint.
"""
import json,re
from pathlib import Path

def run(manifest_path=None,destination='/Game/EPICJam/Generated'):
    import unreal
    path=Path(manifest_path) if manifest_path else Path(__file__).with_name('asset-manifest.json')
    info=json.loads(path.read_text(encoding='utf-8'))
    if info['export_roundtrip']!='passed':raise RuntimeError('Local export check must pass first')
    if not re.fullmatch(r'/Game(?:/[A-Za-z0-9_]+)+',destination):raise ValueError('Use a valid /Game destination')
    dest=destination+'/'+info['asset']
    if unreal.EditorAssetLibrary.does_directory_exist(dest):raise RuntimeError('Destination exists; choose a new version destination')
    tools=unreal.AssetToolsHelpers.get_asset_tools();results=[];materials={}
    report={'engine':unreal.SystemLibrary.get_engine_version(),'destination':dest,'status':'started','parts':results,'visual_review':'pending','assembly_and_collision_gameplay':'not_tested'}
    result_path=path.with_name('ue-import-report.json')
    try:
        for name,spec in info['materials'].items():
            m=tools.create_asset(name,dest+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
            if not m:raise RuntimeError('Material creation failed')
            lib=unreal.MaterialEditingLibrary
            color=lib.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-350,0)
            color.set_editor_property('constant',unreal.LinearColor(*spec['base_color_linear'],1))
            lib.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
            for j,(key,prop) in enumerate([('roughness',unreal.MaterialProperty.MP_ROUGHNESS),('metallic',unreal.MaterialProperty.MP_METALLIC)]):
                node=lib.create_material_expression(m,unreal.MaterialExpressionConstant,-350,150+j*120)
                node.set_editor_property('r',spec[key]);lib.connect_material_property(node,'',prop)
            lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);materials[name]=m
        for p in info['parts']:
            fbx=path.parent/p['fbx']
            if not fbx.is_file():raise RuntimeError('Missing FBX: '+p['fbx'])
            options=unreal.FbxImportUI();options.set_editor_property('import_mesh',True)
            options.set_editor_property('import_as_skeletal',False);options.set_editor_property('import_materials',False);options.set_editor_property('import_textures',False)
            options.set_editor_property('automated_import_should_detect_type',False)
            options.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
            data=options.static_mesh_import_data
            for k,v in {'combine_meshes':False,'transform_vertex_to_absolute':False,'generate_lightmap_u_vs':True,'auto_generate_collision':False,'convert_scene':True,'convert_scene_unit':True}.items():data.set_editor_property(k,v)
            data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
            task=unreal.AssetImportTask();task.set_editor_property('filename',str(fbx));task.set_editor_property('destination_path',dest)
            task.set_editor_property('destination_name',p['name']);task.set_editor_property('automated',True);task.set_editor_property('replace_existing',False);task.set_editor_property('save',True)
            task.set_editor_property('factory',unreal.FbxFactory());task.set_editor_property('options',options)
            tools.import_asset_tasks([task])
            imported=[unreal.EditorAssetLibrary.load_asset(x) for x in task.get_editor_property('imported_object_paths')]
            meshes=[x for x in imported if isinstance(x,unreal.StaticMesh)]
            if len(meshes)!=1:raise RuntimeError('Expected exactly one static mesh: '+p['name'])
            sm=meshes[0];slots=sm.get_editor_property('static_materials')
            if len(slots)!=len(p['materials']):raise RuntimeError('Material slot count mismatch')
            for i,slot in enumerate(slots):
                slotname=str(slot.get_editor_property('material_slot_name'))
                imported_name=str(slot.get_editor_property('imported_material_slot_name'))
                key=slotname if slotname in materials else imported_name
                if key not in materials:raise RuntimeError('Unknown material slot '+slotname+'; inspect FBX material ordering')
                sm.set_material(i,materials[key])
            # Sorted extents tolerate axis permutation while still detecting 100x unit errors.
            box=sm.get_bounding_box();delta=box.max-box.min
            actual=sorted([abs(delta.x),abs(delta.y),abs(delta.z)])
            expected=sorted([x*100 for x in p['dimensions_m']])
            if any(abs(a-b)>max(.1,b*.01) for a,b in zip(actual,expected)):raise RuntimeError('UE size differs from declared centimetres')
            unreal.EditorAssetLibrary.save_loaded_asset(sm)
            results.append({'asset_path':sm.get_path_name(),'dimensions_cm_sorted':actual,'material_assignment':'passed','pivot_visual_check':'pending','collision_visual_check':'pending'})
        report['status']='import_and_size_material_checks_passed'
    except Exception as e:
        report['status']='failed';report['error']=str(e);raise
    finally:
        result_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    unreal.log('EPIC JAM import complete. Review orientation, pivots, collision and assembly in the editor.')

if __name__=='__main__':run()
