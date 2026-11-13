"""Four native 1920x1080 orthographic renders from the actual processed geometry."""
import bpy
from mathutils import Vector

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def render_views(objects,out):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
    world=bpy.data.worlds.new('ReviewWorld');world.use_nodes=True;scene.world=world
    world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.77,.8,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.8
    bpy.context.view_layer.update()
    vv=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
    lo=Vector([min(v[i] for v in vv) for i in range(3)]);hi=Vector([max(v[i] for v in vv) for i in range(3)])
    center=(lo+hi)/2;extent=max(hi-lo)
    for name,delta,power in [('Key',(-2,-3,4),120),('Fill',(3,-1,2),65)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power*extent**2;d.size=extent*4
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=center+Vector(delta)*extent;aim(o,center)
    d=bpy.data.cameras.new('ReviewCamera');d.type='ORTHO'
    camera=bpy.data.objects.new('ReviewCamera',d);scene.collection.objects.link(camera);scene.camera=camera
    scale=max(hi.x-lo.x,hi.y-lo.y,(hi.z-lo.z)*1920/1080)*1.18
    for name,delta in [('front',(0,-4,0)),('right',(4,0,0)),('back',(0,4,0)),('hero',(3,-4,2.5))]:
        camera.location=center+Vector(delta)*extent;aim(camera,center);camera.data.ortho_scale=scale
        if name=='hero':
            bpy.context.view_layer.update();inv=camera.matrix_world.inverted();view=[inv@v for v in vv]
            low=[min(v[i] for v in view) for i in range(2)];high=[max(v[i] for v in view) for i in range(2)]
            camera.location+=camera.rotation_euler.to_matrix()@Vector(((low[0]+high[0])/2,(low[1]+high[1])/2,0))
            camera.data.ortho_scale=max(high[0]-low[0],(high[1]-low[1])*1920/1080)*1.18
        scene.render.filepath=str(out/(name+'_1920x1080.png'));bpy.ops.render.render(write_still=True)
