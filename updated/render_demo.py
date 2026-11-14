"""Build a self-contained room and render the supplied Winqi simulation in Blender.

Run with Blender's --background --factory-startup --disable-autoexec options.
All geometry is generated here; no historical scene or downloaded models are used.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def material(name, color, metallic=0.0, roughness=0.5, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Emission Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Strength'].default_value = emission
    return mat


def box(name, center, scale, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft edges', 'BEVEL')
        mod.width, mod.segments = bevel, 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def sphere(name, center, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj


def aim(obj, at):
    obj.rotation_euler = (Vector(at)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def camera(name, location, target, lens=43):
    obj = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.data.lens = lens
    aim(obj, target)
    return obj


def build_scene(simulation):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    # This changes only the factory-startup process, not saved user preferences.
    preferences = bpy.context.preferences.addons['cycles'].preferences
    try:
        preferences.compute_device_type = 'METAL'
        preferences.get_devices()
        metal = [device for device in preferences.devices if device.type == 'METAL']
        if metal:
            for device in preferences.devices:
                device.use = device.type == 'METAL'
            scene.cycles.device = 'GPU'
    except (TypeError, RuntimeError):
        pass  # Other platforms use the portable CPU default.
    scene.render.resolution_x, scene.render.resolution_y = 1120, 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.fps = simulation['fps']
    scene.frame_start, scene.frame_end = 1, simulation['frame_count']
    scene.world.color = (0.2, 0.2, 0.2)
    scene.view_settings.view_transform = 'AgX'
    mats = {
        'floor': material('Blue grey terrazzo', (0.19, 0.25, 0.30), roughness=0.7),
        'wall': material('Warm plaster', (0.64, 0.67, 0.67), roughness=0.8),
        'wood': material('Oak', (0.28, 0.14, 0.065)),
        'sofa': material('Sage upholstery', (0.15, 0.30, 0.29), roughness=0.9),
        'dark': material('Graphite', (0.025, 0.038, 0.05), metallic=0.2),
        'white': material('Ceramic mannequin', (0.72, 0.76, 0.77), roughness=0.3),
        'blue': material('Hand controller blue', (0.02, 0.30, 0.8), metallic=0.3),
        'gold': material('Head camera ochre', (0.95, 0.52, 0.06), metallic=0.35),
        'screen': material('Monitor glass', (0.015, 0.10, 0.14), emission=0.5),
    }
    box('Floor', (0, 0, -0.12), (8, 6, 0.24), mats['floor'])
    box('Back wall', (0, 3, 1.6), (8, 0.15, 3.2), mats['wall'])
    box('Left wall', (-4, 0, 1.6), (0.15, 6, 3.2), mats['wall'])
    for x in range(-3, 4):
        box('Floor seam', (x, 0, 0.005), (0.008, 6, 0.008), mats['dark'], bevel=0)
    for y in range(-2, 3):
        box('Floor seam', (0, y, 0.005), (8, 0.008, 0.008), mats['dark'], bevel=0)
    # Room composition recalls Dani Epstein's 2016 visual without copying its assets.
    box('Sofa base', (-2.45, 1.72, 0.45), (2.25, 1.1, 0.55), mats['sofa'], 0.12)
    box('Sofa back', (-2.45, 2.22, 0.95), (2.25, 0.23, 0.9), mats['sofa'], 0.12)
    for x in [-3.45, -1.45]:
        box('Sofa arm', (x, 1.72, 0.82), (0.24, 1.15, 0.6), mats['sofa'], 0.1)
    for x in [-2.92, -1.98]:
        box('Sofa cushion', (x, 1.66, 0.79), (0.89, 0.85, 0.15), mats['sofa'], 0.08)
    box('Coffee table', (-2.3, 0.12, 0.51), (1.4, 0.7, 0.08), mats['wood'])
    for x in [-2.82, -1.78]:
        for y in [-0.10, 0.34]:
            box('Table leg', (x, y, 0.25), (0.045, 0.045, 0.5), mats['dark'])
    box('Desk top', (1.9, 1.8, 0.9), (2.55, 1.05, 0.09), mats['wood'])
    for x in [0.85, 2.95]:
        for y in [1.44, 2.16]:
            box('Desk leg', (x, y, 0.45), (0.06, 0.06, 0.9), mats['dark'])
    box('Monitor stand', (1.9, 2.05, 1.16), (0.07, 0.08, 0.5), mats['dark'])
    box('Monitor frame', (1.9, 2.08, 1.58), (1.12, 0.10, 0.70), mats['dark'])
    box('Monitor display', (1.9, 2.019, 1.58), (1.03, 0.012, 0.60), mats['screen'], 0.01)
    box('Keyboard', (1.9, 1.57, 0.97), (0.57, 0.2, 0.025), mats['dark'], 0.01)
    box('Chair seat', (1.9, 0.65, 0.55), (0.6, 0.6, 0.12), mats['dark'], 0.08)
    box('Chair back', (1.9, 0.38, 0.95), (0.6, 0.1, 0.8), mats['dark'], 0.08)
    rod('Chair pedestal', (1.9, 0.65, 0.04), (1.9, 0.65, 0.5), 0.06, mats['dark'])
    # Articulated primitive mannequin: no scanned body or third-party mesh.
    for x in [-0.42, -0.08]:
        sphere('Foot', (x, -0.45, 0.12), (0.12, 0.25, 0.09), mats['white'])
        rod('Lower leg', (x, -0.34, 0.22), (x, -0.32, 0.63), 0.085, mats['white'])
        sphere('Knee', (x, -0.32, 0.65), (0.09, 0.09, 0.09), mats['white'])
        rod('Upper leg', (x, -0.32, 0.68), (x, -0.28, 1.05), 0.11, mats['white'])
    sphere('Pelvis', (-0.25, -0.28, 1.05), (0.28, 0.16, 0.20), mats['white'])
    sphere('Torso', (-0.25, -0.28, 1.38), (0.30, 0.16, 0.36), mats['white'])
    rod('Neck', (-0.25, -0.28, 1.63), (-0.25, -0.28, 1.76), 0.07, mats['white'])
    sphere('Head', (-0.25, -0.28, 1.88), (0.16, 0.145, 0.21), mats['white'])
    box('Head camera band', (-0.25, -0.30, 1.92), (0.34, 0.3, 0.12), mats['gold'], 0.04)
    for side in [-1, 1]:
        shoulder = (-0.25+side*0.34, -0.28, 1.6)
        elbow = (-0.25+side*0.53, -0.43, 1.27)
        hand = (-0.25+side*0.48, -0.78, 1.44 if side == 1 else 1.05)
        sphere('Shoulder', shoulder, (0.10,)*3, mats['white'])
        rod('Upper arm', shoulder, elbow, 0.075, mats['white'])
        sphere('Elbow', elbow, (0.075,)*3, mats['white'])
        rod('Forearm', elbow, hand, 0.065, mats['white'])
        sphere('Hand', hand, (0.075, 0.065, 0.10), mats['white'])
        if side == 1:
            box('Hand camera', hand, (0.15, 0.13, 0.2), mats['blue'])
    beacon_positions = [(-3.87, 1.4, 2.6), (-3.87, -1.5, 1.4),
                        (-2.6, 2.87, 2.7), (-0.5, 2.87, 2.4),
                        (1.55, 2.87, 2.7), (3.25, 2.87, 1.35)]
    led_materials = []
    for i, position in enumerate(beacon_positions, 1):
        led = material(f'Beacon {i} green emitter', (0.05, 0.9, 0.38), emission=0)
        led.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.003, 0.008, 0.005, 1)
        sphere(f'Beacon {i} mount', position, (0.14,)*3, mats['dark'])
        sphere(f'Beacon {i} emitter', Vector(position)+Vector((0.045, -0.045, 0)), (0.09,)*3, led)
        led_materials.append(led)
    cam = camera('Orbit camera', (8, -10, 7), (0, 0.55, 1), lens=46)
    headcam = camera('Head camera projection', (-0.25, -0.3, 1.96), (-0.9, 3, 2), lens=14)
    handcam = camera('Hand camera projection', (0.23, -0.78, 1.5), (-1.6, 3, 2.2), lens=14)
    scene.camera = cam
    for name, location, energy, size in [('Window', (1, -3, 6), 1500, 7),
                                          ('Softbox', (-1, 0, 5), 900, 5)]:
        obj = bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA'))
        scene.collection.objects.link(obj)
        obj.location = location
        obj.data.energy, obj.data.shape, obj.data.size = energy, 'DISK', size
        aim(obj, (0, 0, 0))
    # Keyframes keep the generated .blend inspectable and renderable independently.
    for index, sample in enumerate(simulation['samples']):
        first_frame = sample['frame_index']+1
        for led, beacon in zip(led_materials, sample['beacons']):
            socket = led.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
            socket.default_value = 10 if beacon['emitted_bit'] else 0
            socket.keyframe_insert(data_path='default_value', frame=first_frame)
    for frame in range(1, simulation['frame_count']+1):
        t = (frame-1)/max(1, simulation['frame_count']-1)
        angle = math.radians(-56+22*math.sin(t*math.pi))
        cam.location = (12*math.cos(angle), 12*math.sin(angle), 6.3+0.3*math.sin(2*math.pi*t))
        aim(cam, (0, 0.6, 1.0))
        cam.keyframe_insert(data_path='location', frame=frame)
        cam.keyframe_insert(data_path='rotation_euler', frame=frame)
    for led in led_materials:
        action = led.node_tree.animation_data.action
        for slot in action.slots:
            for layer in action.layers:
                for strip in layer.strips:
                    for curve in strip.channelbag(slot).fcurves:
                        for key in curve.keyframe_points:
                            key.interpolation = 'CONSTANT'
    return scene, cam, headcam, handcam, beacon_positions


def projected(scene, cam, positions):
    result = []
    for point in positions:
        p = world_to_camera_view(scene, cam, Vector(point))
        result.append([round(p.x, 6), round(1-p.y, 6), round(p.z, 6)])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--blend', type=Path)
    parser.add_argument('--frames', help='Comma-separated zero-based frame indices; default all')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    simulation = json.loads(args.simulation.read_text())
    assert len(simulation['samples'][0]['beacons']) == 6
    args.output.mkdir(parents=True, exist_ok=True)
    scene, cam, headcam, handcam, positions = build_scene(simulation)
    if args.blend:
        args.blend.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = '//frames/'
        scene.frame_set(1)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.blend.resolve()), compress=True)
    frames = [int(x) for x in args.frames.split(',')] if args.frames else range(simulation['frame_count'])
    metadata = []
    for index in frames:
        scene.frame_set(index+1)
        bpy.context.view_layer.update()
        metadata.append({'frame_index': index,
                         'orbit': projected(scene, cam, positions),
                         'head': projected(scene, headcam, positions),
                         'hand': projected(scene, handcam, positions)})
        scene.render.filepath = str((args.output/f'{index:04d}.png').resolve())
        bpy.ops.render.render(write_still=True)
    (args.output/'projections.json').write_text(json.dumps(metadata, indent=2)+'\n')


if __name__ == '__main__':
    main()
