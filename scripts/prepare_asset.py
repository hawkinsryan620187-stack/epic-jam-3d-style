"""Original Blender backend. Static meshes only; does not infer unseen geometry."""
import bpy,bmesh,json,math,re,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix

PALETTE={
 'warm_stone':('B9AD98',.78,0),'gray_stone':('827D8B',.78,0),
 'wood':('806454',.78,0),'terracotta':('A36D56',.75,0),
 'indigo':('555E7A',.75,0),'ochre':('B48A45',.78,0),
 'ivory':('D2C5A9',.76,0),'brass':('B69757',.48,1),
 'olive':('7F8654',.8,0),'yellow_green':('A5A26A',.8,0),
 'dark':('34363D',.82,0),'screen':('364D51',.38,0)}

def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def color(hex):return [linear(int(hex[i:i+2],16)/255) for i in (0,2,4)]
def select(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
def load(path):
    ext=path.suffix.lower()
    if ext=='.blend':bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    elif ext in ('.glb','.gltf'):bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext=='.fbx':bpy.ops.import_scene.fbx(filepath=str(path))
    else:bpy.ops.wm.obj_import(filepath=str(path))
    bpy.context.view_layer.update()
def bounds(objs):
    bpy.context.view_layer.update()
    v=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
    lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
    return lo,hi
def triangles(o):o.data.calc_loop_triangles();return len(o.data.loop_triangles)
def cleanup(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
def material_spec(m,mode,mapping):
    role=mapping.get(m.name)
    if role is not None:
        if role not in PALETTE:raise ValueError('Unknown palette role '+role)
        h,r,metal=PALETTE[role];return role,color(h),r,metal
    outputs=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output] if m.use_nodes else []
    if len(outputs)!=1 or not outputs[0].inputs['Surface'].is_linked:
        raise ValueError('Material needs an explicit role: '+m.name)
    output=outputs[0];node=output.inputs['Surface'].links[0].from_node
    if node.type!='BSDF_PRINCIPLED' or any(output.inputs[k].is_linked for k in ('Volume','Displacement')) or any(i.is_linked for i in node.inputs):
        raise ValueError('Textured/complex material needs baking or explicit simplification mapping: '+m.name)
    if node.inputs['Alpha'].default_value<.999 or node.inputs['Transmission Weight'].default_value>0:
        raise ValueError('Transparent material requires an explicit project role or a separate material workflow: '+m.name)
    if any(node.inputs[k].default_value>0 for k in ('Coat Weight','Subsurface Weight','Sheen Weight','Anisotropic','Diffuse Roughness','Thin Film Thickness')) or (node.inputs['Emission Strength'].default_value>0 and any(node.inputs['Emission Color'].default_value[:3])):
        raise ValueError('Additional shader effects need an explicit simplification mapping: '+m.name)
    rgb=list(node.inputs['Base Color'].default_value[:3]);rough=float(node.inputs['Roughness'].default_value);metal=float(node.inputs['Metallic'].default_value)
    if mode=='preserve':return m.name,rgb,rough,metal
    candidates=['brass'] if metal>.5 else [k for k in PALETTE if k!='brass']
    role=min(candidates,key=lambda k:sum((a-b)**2 for a,b in zip(rgb,color(PALETTE[k][0]))))
    h,r,metal=PALETTE[role];return role,color(h),r,metal
def new_material(name,rgb,rough,metal):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*rgb,1);return m

def main(job):
    source=Path(job['input']);out=Path(job['output'])
    name=job['asset_name']
    if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',name):raise ValueError('asset_name must be an ASCII identifier')
    mode=job.get('style_mode','project')
    if mode not in ('project','preserve'):raise ValueError('Unknown style_mode')
    ratio=float(job.get('decimate_ratio',1));budget=int(job.get('triangle_budget',5000))
    if not 0<ratio<=1 or budget<=0:raise ValueError('Invalid ratio/budget')
    collision=job.get('collision','none')
    if collision not in ('none','box'):raise ValueError('collision must be none or box')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    load(source)
    if any(o.type=='ARMATURE' or o.animation_data for o in bpy.context.scene.objects):
        raise ValueError('Rigged or animated assets require the character/animation route')
    all_mesh=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith(('UCX_','UBX_','UCP_','USP_'))]
    if not all_mesh:raise ValueError('No visible source meshes')
    if any(o.data.shape_keys for o in all_mesh):raise ValueError('Shape keys require a separate deformation route')
    unit=float(job.get('meters_per_unit',bpy.context.scene.unit_settings.scale_length if source.suffix.lower()=='.blend' else 1))
    if not math.isfinite(unit) or unit<=0:raise ValueError('Invalid source unit scale')
    scale=Matrix.Diagonal((unit,unit,unit,1))
    bpy.context.scene.unit_settings.scale_length=1
    part_defs=job.get('parts',[])
    if not part_defs:part_defs=[{'name':'Body','root':None}]
    if len({p['name'] for p in part_defs})!=len(part_defs):raise ValueError('Duplicate part names')
    for p in part_defs:
        if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*',p['name']):raise ValueError('Invalid part name')
        if p.get('root') and p['root'] not in bpy.data.objects:raise ValueError('Missing part root '+p['root'])
    groups={p['name']:[] for p in part_defs};world={};parents={}
    roots={p.get('root'):p['name'] for p in part_defs if p.get('root')}
    for p in part_defs:
        anchor=bpy.data.objects.get(p.get('root','')) if p.get('root') else None
        am=scale@anchor.matrix_world if anchor else Matrix.Identity(4)
        world[p['name']]=Matrix.LocRotScale(am.translation,am.to_quaternion(),Vector((1,1,1)))
        ancestor=anchor.parent if anchor else None
        parents[p['name']]=None
        while ancestor:
            if ancestor.name in roots:parents[p['name']]=roots[ancestor.name];break
            ancestor=ancestor.parent
    for o in all_mesh:
        lineage=[o];ancestor=o.parent;owned=None
        while ancestor:
            lineage.append(ancestor);ancestor=ancestor.parent
        for a in lineage:
            if a.name in roots:owned=roots[a.name];break
        if owned is None:
            if len(part_defs)==1:owned=part_defs[0]['name']
            else:raise ValueError('Mesh outside declared part hierarchy: '+o.name)
        groups[owned].append(o)
    if any(not v for v in groups.values()):raise ValueError('A declared part has no meshes')
    deps=bpy.context.evaluated_depsgraph_get();processed=[];material_records={};mat_cache={};part_records=[]
    for part,sources in groups.items():
        meshes=[]
        for source_obj in sources:
            data=bpy.data.meshes.new_from_object(source_obj.evaluated_get(deps),depsgraph=deps)
            ob=bpy.data.objects.new('Processed_'+source_obj.name,data);bpy.context.scene.collection.objects.link(ob)
            data.transform(world[part].inverted()@scale@source_obj.matrix_world)
            cleanup(ob)
            if ratio<1:
                select([ob]);mod=ob.modifiers.new('BudgetReduction','DECIMATE');mod.ratio=ratio
                bpy.ops.object.modifier_apply(modifier=mod.name);cleanup(ob)
                data=ob.data
            for i,m in enumerate(list(data.materials)):
                if m is None:raise ValueError('Empty material slot')
                if m.name not in mat_cache:
                    role,rgb,r,metal=material_spec(m,mode,job.get('material_map',{}))
                    ident='M_'+name+'_'+re.sub('[^A-Za-z0-9_]','_',m.name)
                    if ident in material_records:raise ValueError('Material name collision after sanitizing')
                    mat_cache[m.name]=new_material(ident,rgb,r,metal)
                    material_records[ident]={'source':m.name,'role':role,'base_color_linear':rgb,'roughness':r,'metallic':metal}
                data.materials[i]=mat_cache[m.name]
            if not data.materials:raise ValueError('Mesh has no material; assign a role before processing')
            for face in data.polygons:face.use_smooth=False if mode=='project' else face.use_smooth
            meshes.append(ob)
        select(meshes);bpy.ops.object.join();ob=bpy.context.object;ob.name='SM_'+name+'_'+part
        select([ob]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
        # A single clean UV0 atlas per part; all materials here are untextured constants.
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.03)
        bpy.ops.object.mode_set(mode='OBJECT')
        cleanup(ob)
        bm=bmesh.new();bm.from_mesh(ob.data)
        nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
        ob.data.calc_loop_triangles();degenerate=sum(t.area<1e-12 for t in ob.data.loop_triangles)
        if degenerate or nonmanifold:raise ValueError('Unresolved topology in '+ob.name+'; repair before export')
        lo,hi=bounds([ob]);dims=[hi[i]-lo[i] for i in range(3)]
        colliders=[]
        if collision=='box':
            bpy.ops.mesh.primitive_cube_add(size=1,location=[(a+b)/2 for a,b in zip(lo,hi)])
            c=bpy.context.object;c.name='UCX_'+ob.name+'_00';c.dimensions=dims
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);colliders=[c]
        select([ob]+colliders)
        fbx=ob.name+'.fbx';glb=ob.name+'.glb'
        bpy.ops.export_scene.fbx(filepath=str(out/fbx),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,mesh_smooth_type='FACE',use_triangles=True)
        select([ob]);bpy.ops.export_scene.gltf(filepath=str(out/glb),export_format='GLB',use_selection=True,export_apply=True)
        for c in colliders:bpy.data.objects.remove(c,do_unlink=True)
        rec={'name':ob.name,'part':part,'parent_part':parents[part],'fbx':fbx,'glb':glb,'triangles':triangles(ob),'dimensions_m':dims,'materials':[m.name for m in ob.data.materials],
             'anchor_world_blender_m':[list(row) for row in world[part]],'collision':collision}
        part_records.append(rec);processed.append(ob)
    total=sum(p['triangles'] for p in part_records)
    if total>budget:raise ValueError('Triangle budget exceeded: '+str(total)+' > '+str(budget))
    # Remove original scene contents. Restore processed parts to their assembly transforms.
    for o in list(bpy.context.scene.objects):
        if o not in processed:bpy.data.objects.remove(o,do_unlink=True)
    anchors={}
    for p in part_records:
        e=bpy.data.objects.new('Pivot_'+p['part'],None);bpy.context.scene.collection.objects.link(e)
        e.matrix_world=world[p['part']];anchors[p['part']]=e
    bpy.context.view_layer.update()
    for p,ob in zip(part_records,processed):
        e=anchors[p['part']]
        if p['parent_part']:
            mw=e.matrix_world.copy();e.parent=anchors[p['parent_part']];e.matrix_world=mw
        ob.parent=e;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.context.view_layer.update();assembled=bounds(processed)
    select(list(anchors.values())+processed)
    bpy.ops.export_scene.gltf(filepath=str(out/'assembly.glb'),export_format='GLB',use_selection=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'master.blend'))
    if job.get('render',True):
        sys.path.insert(0,str(Path(__file__).parent));from review_views import render_views
        render_views(processed,out)
    # Verify separate exports in clean scenes; FBX includes only one render mesh plus its collision.
    for p in part_records:
        p['roundtrip']={}
        for ext in ('glb','fbx'):
            bpy.ops.wm.read_factory_settings(use_empty=True);load(out/p[ext])
            actual=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
            if len(actual)!=1:raise ValueError('Unexpected imported mesh count')
            lo,hi=bounds(actual);dims=[hi[i]-lo[i] for i in range(3)]
            if sum(triangles(o) for o in actual)!=p['triangles']:raise ValueError('Roundtrip triangle mismatch')
            if max(abs(a-b) for a,b in zip(dims,p['dimensions_m']))>1e-4:raise ValueError('Roundtrip dimension mismatch')
            if not all(o.data.uv_layers and len(o.material_slots)==len(p['materials']) for o in actual):raise ValueError('UV/material roundtrip mismatch')
            if ext=='fbx' and collision=='box' and not any(o.name=='UCX_'+p['name']+'_00' for o in bpy.context.scene.objects):raise ValueError('Collision missing')
            p['roundtrip'][ext]='passed'
    report={'schema':1,'skill_version':'0.2.0','asset':name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'style_mode':mode,'decimate_ratio':ratio,'triangle_budget':budget,'triangles':total,'parts':part_records,'materials':material_records,'assembly_bounds_m':assembled,
        'export_roundtrip':'passed','visual_review':'pending','ue_import':'not_run','ue_assembly':'not_run','geometry_note':'Faceting/palette normalization applied; silhouette redesign is an earlier modeling stage.'}
    (out/'asset-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text(encoding='utf-8')))
